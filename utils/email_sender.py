
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from utils.pdf_invitation import generate_invitation_pdf


def send_invitation_email(recipient_email, expert_name, item_title, panel_role,
                          item_no=None, adv_no=None, discipline=None):
    """
    Send an interview invitation email to the expert with a formal PDF attachment.
    
    Args:
        recipient_email: Expert's email address
        expert_name: Full name of the expert
        item_title: Title of the item/position
        panel_role: Role on the panel (e.g., "Chairperson", "Expert Member")
        item_no: Item number (optional)
        adv_no: Advertisement number (optional)
        discipline: Discipline name (optional, defaults to item_title)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    
    if not username or not password:
        print(f"⚠️ SKIPPING EMAIL: Credentials not found in .env. Target: {recipient_email}")
        return False, "Email credentials not configured"

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = recipient_email
        msg['Subject'] = f"INVITATION: Interview Board for {item_title} - DRDO RAC"

        # Generate a dynamic date (next Tuesday, at least 2 weeks out)
        today = datetime.now()
        future = today + timedelta(days=14)
        next_tuesday = future + timedelta(days=(1 - future.weekday() + 7) % 7)
        date_str = next_tuesday.strftime("%d %B %Y")

        body = f"""Dear {expert_name},

Greetings from the Recruitment and Assessment Centre (RAC), DRDO.

You are cordially invited to serve as {panel_role} on the Interview Board for {item_title}{f' (Advertisement No. {adv_no}, Item No. {item_no})' if adv_no and item_no else ''}, to be conducted as per the details mentioned below:

Position:  {item_title}
Date:      {date_str}
Venue:     RAC, DRDO Headquarters, Lucknow Road, Timarpur, New Delhi - 110054
Mode:      Offline (In-Person)

Your expertise and experience in the relevant domain would greatly contribute to the effective evaluation of candidates and the overall success of the interview process.

Please find attached the formal invitation letter for your reference and records.

We kindly request you to log in to the MIRA Expert Portal at your convenience and update your availability for the above-mentioned date. This will help us finalize the Interview Board and make necessary arrangements in advance.

Portal Link: http://localhost:5001/fe/login.html

In case of any queries or assistance regarding the portal or interview schedule, please feel free to contact us.

We look forward to your esteemed participation and support.

Thanking you.

Yours sincerely,
Director
Recruitment and Assessment Centre (RAC)
Defence Research and Development Organisation (DRDO)
Ministry of Defence, Government of India
"""
        msg.attach(MIMEText(body, 'plain'))

        # Generate and attach formal PDF invitation
        try:
            pdf_path = generate_invitation_pdf(
                expert_name=expert_name,
                item_title=item_title,
                panel_role=panel_role,
                item_no=item_no,
                adv_no=adv_no,
                interview_date=date_str,
                discipline=discipline or item_title
            )
            
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_attachment = MIMEApplication(pdf_file.read(), _subtype='pdf')
                    pdf_filename = f"DRDO_RAC_Invitation_{expert_name.replace(' ', '_')}.pdf"
                    pdf_attachment.add_header(
                        'Content-Disposition', 'attachment',
                        filename=pdf_filename
                    )
                    msg.attach(pdf_attachment)
                    print(f"📎 PDF attached: {pdf_filename}")
                
                # Clean up temp file
                try:
                    os.remove(pdf_path)
                except:
                    pass
            else:
                print(f"⚠️ PDF generation returned no file, sending email without attachment")
                
        except Exception as pdf_error:
            print(f"⚠️ PDF generation failed: {pdf_error}. Sending email without attachment.")

        # Connect to Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ EMAIL SENT successfully to {recipient_email}")
        return True, "Email sent successfully"
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ FAILED to send email to {recipient_email}: {error_msg}")
        return False, error_msg
