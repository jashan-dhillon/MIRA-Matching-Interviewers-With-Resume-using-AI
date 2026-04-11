"""
MIRA DRDO - Formal PDF Invitation Letter Generator

Generates official DRDO-style invitation letters for interview board experts.
Uses fpdf2 to create professional PDF documents with:
- Official DRDO/RAC header with logos
- Government reference number and date formatting
- Formal letter body with expert/item details
- Official signature block
"""

import os
import tempfile
from datetime import datetime, timedelta
from fpdf import FPDF


# Path to logos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAC_LOGO_PATH = os.path.join(BASE_DIR, 'fe', 'rac_logo.png')
EMBLEM_PATH = os.path.join(BASE_DIR, 'fe', 'emblem.png')


class DRDOInvitationPDF(FPDF):
    """Custom PDF class for DRDO formal invitation letters."""

    def __init__(self, expert_name, item_title, panel_role, item_no=None,
                 adv_no=None, interview_date=None, discipline=None):
        super().__init__()
        self.expert_name = expert_name
        self.item_title = item_title
        self.panel_role = panel_role
        self.item_no = item_no or ''
        self.adv_no = adv_no or ''
        self.discipline = discipline or item_title
        self.interview_date = interview_date or self._next_weekday()

    def _next_weekday(self):
        """Calculate next Tuesday as default interview date."""
        today = datetime.now()
        days_ahead = (1 - today.weekday() + 7) % 7 + 7  # Next Tuesday
        next_date = today + timedelta(days=days_ahead)
        return next_date.strftime("%d %B %Y")

    def _generate_ref_number(self):
        """Generate a government-style reference number."""
        now = datetime.now()
        return f"RAC/MIRA/{now.strftime('%Y')}/{now.strftime('%m%d')}/{self.adv_no or '000'}"

    def header(self):
        """Create official DRDO/RAC letterhead."""
        # Top border line
        self.set_draw_color(0, 51, 102)  # Dark blue
        self.set_line_width(0.8)
        self.line(10, 8, 200, 8)

        # RAC Logo (left)
        if os.path.exists(RAC_LOGO_PATH):
            self.image(RAC_LOGO_PATH, 12, 10, 22)

        # Emblem (right)
        if os.path.exists(EMBLEM_PATH):
            self.image(EMBLEM_PATH, 178, 10, 20)

        # Header text - centered
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 51, 102)
        self.set_y(11)
        self.cell(0, 4, 'GOVERNMENT OF INDIA', align='C', new_x="LMARGIN", new_y="NEXT")

        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(80, 80, 80)
        self.cell(0, 3.5, 'MINISTRY OF DEFENCE', align='C', new_x="LMARGIN", new_y="NEXT")

        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 51, 102)
        self.cell(0, 5, 'DEFENCE RESEARCH AND DEVELOPMENT ORGANISATION', align='C', new_x="LMARGIN", new_y="NEXT")

        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(178, 34, 34)  # Dark red
        self.cell(0, 5, 'RECRUITMENT AND ASSESSMENT CENTRE (RAC)', align='C', new_x="LMARGIN", new_y="NEXT")

        self.set_font('Helvetica', '', 7)
        self.set_text_color(100, 100, 100)
        self.cell(0, 3, 'Lucknow Road, Timarpur, Delhi - 110054', align='C', new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 3, 'An ISO 9001 Certified Establishment', align='C', new_x="LMARGIN", new_y="NEXT")

        # Bottom border line
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.5)
        self.line(10, 42, 200, 42)

        # Thin accent line
        self.set_draw_color(178, 34, 34)
        self.set_line_width(0.3)
        self.line(10, 43, 200, 43)

        self.ln(8)

    def footer(self):
        """Create page footer."""
        self.set_y(-25)

        # Footer line
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())

        self.ln(2)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 3, 'This is a system-generated letter from MIRA (Manpower Intelligence & Recruitment Automation).', align='C', new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 3, 'Recruitment and Assessment Centre, DRDO | Ministry of Defence, Government of India', align='C', new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 3, f'Page {self.page_no()}/{{nb}}', align='C')

    def build(self):
        """Build the complete PDF invitation letter."""
        self.alias_nb_pages()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=30)

        ref_no = self._generate_ref_number()
        today_date = datetime.now().strftime("%d %B %Y")

        # === Reference Number & Date ===
        self.set_y(48)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 0, 0)
        self.cell(95, 5, f'No. {ref_no}', new_x="RIGHT")
        self.set_font('Helvetica', '', 9)
        self.cell(95, 5, f'Date: {today_date}', align='R', new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        # === SUBJECT LINE ===
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 51, 102)
        subject_text = f"Subject: Invitation to serve as Expert Member on Interview Board"
        if self.adv_no:
            subject_text += f" - Advertisement No. {self.adv_no}"
        self.multi_cell(0, 5, subject_text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        # Thin separator
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

        # === ADDRESSEE ===
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, f'Dear {self.expert_name},', new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # === BODY PARAGRAPH 1 ===
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 30, 30)
        para1 = (
            "Greetings from the Recruitment and Assessment Centre (RAC), "
            "Defence Research and Development Organisation (DRDO), New Delhi."
        )
        self.multi_cell(0, 5, para1, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        # === BODY PARAGRAPH 2 ===
        para2 = (
            f"With reference to the above subject, the undersigned is directed to inform you that "
            f"the Recruitment & Assessment Centre (RAC), DRDO proposes to hold an Interview Board "
            f"for the recruitment of Scientists 'B' in the discipline of "
            f"{self.discipline}. "
            f"In this regard, you are cordially invited to serve as "
            f"{self.panel_role} on the said Interview Board."
        )
        self.multi_cell(0, 5, para2, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # === DETAILS TABLE ===
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 51, 102)
        self.cell(0, 6, 'Details of the Interview:', new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        # Table with details
        details = [
            ('Advertisement No.', str(self.adv_no) if self.adv_no else 'As notified'),
            ('Item No.', str(self.item_no) if self.item_no else 'As per schedule'),
            ('Discipline', self.discipline),
            ('Your Role', self.panel_role),
            ('Proposed Date', str(self.interview_date)),
            ('Venue', 'RAC, DRDO Headquarters, Lucknow Road, Timarpur, New Delhi - 110054'),
            ('Mode', 'Offline (In-Person)'),
        ]

        self.set_font('Helvetica', '', 9)
        self.set_text_color(0, 0, 0)

        for label, value in details:
            # Label column (shaded)
            x_start = self.get_x()
            y_start = self.get_y()

            self.set_fill_color(240, 244, 255)
            self.set_font('Helvetica', 'B', 9)
            self.cell(55, 7, f'  {label}', border=1, fill=True, new_x="RIGHT")

            self.set_font('Helvetica', '', 9)
            self.cell(135, 7, f'  {value}', border=1, new_x="LMARGIN", new_y="NEXT")

        self.ln(4)

        # === BODY PARAGRAPH 3 ===
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 30, 30)
        para3 = (
            "Your expertise and distinguished experience in the relevant domain would "
            "greatly contribute to the fair and effective evaluation of candidates and "
            "the overall success of the interview process."
        )
        self.multi_cell(0, 5, para3, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        # === PORTAL INSTRUCTIONS ===
        para4 = (
            "You are kindly requested to log in to the MIRA Expert Portal and update your "
            "availability for the above-mentioned date at your earliest convenience. This will "
            "help us finalize the Interview Board and make the necessary arrangements in advance."
        )
        self.multi_cell(0, 5, para4, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        # Portal link box
        self.set_fill_color(235, 245, 255)
        self.set_draw_color(0, 82, 204)
        self.set_line_width(0.3)
        y_box = self.get_y()
        self.rect(10, y_box, 190, 12, style='DF')

        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 82, 204)
        self.set_y(y_box + 2)
        self.cell(0, 4, 'MIRA Expert Portal:', align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', 'U', 9)
        self.cell(0, 4, 'http://localhost:5001/fe/login.html', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(6)

        # === CLOSING ===
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 30, 30)
        para5 = (
            "In case of any queries or assistance regarding the portal or interview schedule, "
            "please feel free to contact the RAC office."
        )
        self.multi_cell(0, 5, para5, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        self.cell(0, 5, 'We look forward to your esteemed participation and support.', new_x="LMARGIN", new_y="NEXT")
        self.ln(6)

        # === SIGNATURE BLOCK ===
        self.cell(0, 5, 'Yours faithfully,', new_x="LMARGIN", new_y="NEXT")
        self.ln(12)

        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 5, 'Director', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 9)
        self.cell(0, 5, 'Recruitment and Assessment Centre (RAC)', new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, 'Defence Research and Development Organisation (DRDO)', new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, 'Ministry of Defence, Government of India', new_x="LMARGIN", new_y="NEXT")


def generate_invitation_pdf(expert_name, item_title, panel_role,
                            item_no=None, adv_no=None,
                            interview_date=None, discipline=None):
    """
    Generate a formal DRDO invitation PDF letter.

    Args:
        expert_name: Name of the expert (e.g., "Dr. Ashok Kumar")
        item_title: Title/name of the item/position
        panel_role: Role on the panel (e.g., "Chairperson", "External Expert")
        item_no: Item number (optional)
        adv_no: Advertisement number (optional)
        interview_date: Proposed interview date string (optional, defaults to next Tuesday)
        discipline: Discipline name (optional, defaults to item_title)

    Returns:
        str: Path to the generated PDF file in temp directory
    """
    pdf = DRDOInvitationPDF(
        expert_name=expert_name,
        item_title=item_title,
        panel_role=panel_role,
        item_no=item_no,
        adv_no=adv_no,
        interview_date=interview_date,
        discipline=discipline
    )
    pdf.build()

    # Save to temp file
    safe_name = expert_name.replace(' ', '_').replace('.', '')
    filename = f"DRDO_RAC_Invitation_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    pdf.output(filepath)

    print(f"📄 PDF generated: {filepath}")
    return filepath
