
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

def send_invitation_email(recipient_email, expert_name, item_title, panel_role):
    """
    Send an interview invitation email to the expert.
    """
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    
    if not username or not password:
        print(f"⚠️ SKIPPING EMAIL: Credentials not found in .env. Target: {recipient_email}")
        return False

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = recipient_email
        msg['Subject'] = f"INVITATION: Interview Board for {item_title} - DRDO RAC"

        # Generate a dynamic date (e.g., next Tuesday)
        today = datetime.now()
        next_tuesday = today + timedelta(days=(1-today.weekday() + 7) % 7 + 7)
        date_str = next_tuesday.strftime("%B %d, %Y")

        body = f"""Dear Sir/Madam,

Greetings from the Recruitment and Assessment Centre (RAC), DRDO.

You are cordially invited to serve as an **Expert Member on the Interview Panel** for a **{item_title}** to be conducted as per the details mentioned below:

**Position:** {item_title}
**Date:** {date_str}
**Venue:** RAC, DRDO Headquarters, Lucknow Road, Timarpur, New Delhi - 110054
**Mode:** Offline (In-Person)

Your expertise and experience in the relevant domain would greatly contribute to the effective evaluation of candidates and the overall success of the interview process.

We kindly request you to **log in to the MIRA Expert Portal** at your convenience and **update your availability** for the above-mentioned date. This will help us finalize the interview panel and make necessary arrangements in advance.

**Portal Link:** http://localhost:5001/fe/login.html

In case of any queries or assistance regarding the portal or interview schedule, please feel free to contact us.

We look forward to your esteemed participation and support.

Thanking you.

Yours sincerely,
**Director**
Recruitment and Assessment Centre (RAC)
Defence Research and Development Organisation (DRDO)
"""
        msg.attach(MIMEText(body, 'plain'))

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
