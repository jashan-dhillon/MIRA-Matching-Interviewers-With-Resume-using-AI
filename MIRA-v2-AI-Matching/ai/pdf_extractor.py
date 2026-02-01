"""
MIRA DRDO - PDF Advertisement Extractor

This module extracts structured data from DRDO recruitment advertisement PDFs:
- Advertisement Number
- Title & Total Vacancies
- Closing Date
- Items (Job Roles) with details:
  - Item No, Discipline, Organization
  - Vacancy breakdown (UR, EWS, OBC, SC, ST, Total)
  - Essential Qualification
  - GATE Paper Code
  - Equivalent Acceptable Degrees
"""

import pdfplumber
import re
from datetime import datetime
from typing import Dict, List, Any, Optional


class AdvertisementExtractor:
    """Extract structured data from DRDO advertisement PDFs."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf = None
        self.full_text = ""
        self.tables = []
        
    def __enter__(self):
        self.pdf = pdfplumber.open(self.pdf_path)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pdf:
            self.pdf.close()
    
    def extract_all(self) -> Dict[str, Any]:
        """Extract all data from the advertisement PDF."""
        # Extract text and tables from all pages
        for page in self.pdf.pages:
            text = page.extract_text()
            if text:
                self.full_text += text + "\n"
            
            tables = page.extract_tables()
            if tables:
                self.tables.extend(tables)
        
        # Extract structured data
        result = {
            "advertisementNo": self._extract_advertisement_number(),
            "title": self._extract_title(),
            "totalVacancies": self._extract_total_vacancies(),
            "closingDate": self._extract_closing_date(),
            "organizations": self._extract_organizations(),
            "items": self._extract_items(),
            "generalInfo": self._extract_general_info(),
            "extractedAt": datetime.now().isoformat(),
            "sourceFile": self.pdf_path
        }
        
        return result
    
    def _extract_advertisement_number(self) -> Optional[int]:
        """Extract the advertisement number."""
        # Look for "Advertisement No." followed by number
        patterns = [
            r'Advertisement\s+No\.?\s*[:\-]?\s*(\d+)',
            r'(\d+)\s*Advertisement\s+No\.',
            r'Advt\.?\s*No\.?\s*[:\-]?\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.full_text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Try to find from tables
        for table in self.tables:
            for row in table:
                if row:
                    for cell in row:
                        if cell and 'Advertisement No' in str(cell):
                            # Extract number from same cell or nearby
                            num_match = re.search(r'(\d{2,4})', str(cell))
                            if num_match:
                                return int(num_match.group(1))
        return None
    
    def _extract_title(self) -> str:
        """Extract the main title of the advertisement."""
        patterns = [
            r'DIRECT RECRUITMENT FOR THE POSTS? OF\s+(.+?)(?:\n|IN DRDO)',
            r'RECRUITMENT FOR\s+(.+?)(?:\n|VACANCIES)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.full_text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return "DRDO Scientist Recruitment"
    
    def _extract_total_vacancies(self) -> int:
        """Extract total number of vacancies."""
        patterns = [
            r'\((\d+)\s+VACANCIES?\)',
            r'Total\s+Vacancies?\s*[:\-]?\s*(\d+)',
            r'(\d+)\s+vacancies',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.full_text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0
    
    def _extract_closing_date(self) -> Optional[str]:
        """Extract the closing date."""
        patterns = [
            r'Closing\s+date\s*[:\-]?\s*(\d{1,2}[-/]\w+[-/]\d{4})',
            r'last\s+date\s*[:\-]?\s*(\d{1,2}[-/]\w+[-/]\d{4})',
            r'(\d{1,2}[-/][A-Za-z]+[-/]\d{4})\s*\(\d+:\d+\s*hrs',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.full_text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_organizations(self) -> Dict[str, int]:
        """Extract organization-wise vacancy breakdown."""
        orgs = {}
        
        # Common DRDO organizations
        org_patterns = {
            "DRDO": r'DRDO[^0-9]*(\d+)\s*(?:vacancies|posts)?',
            "ADA": r'ADA[^0-9]*(\d+)\s*(?:vacancies|posts)?',
            "WESEE": r'WESEE[^0-9]*(\d+)\s*(?:vacancies|posts)?',
            "CME": r'CME[^0-9]*(\d+)\s*(?:vacancies|posts)?',
            "AFMC": r'AFMC[^0-9]*(\d+)\s*(?:vacancies|posts)?',
        }
        
        # Look for summary table
        for pattern_name, pattern in org_patterns.items():
            match = re.search(pattern, self.full_text, re.IGNORECASE)
            if match:
                orgs[pattern_name] = int(match.group(1))
        
        return orgs
    
    def _extract_items(self) -> List[Dict[str, Any]]:
        """Extract individual items (job roles) from the tables.
        
        Handles multi-row cells by accumulating text from continuation rows
        for discipline (col 1), essential qualification (col 9), and 
        equivalent degrees (col 10).
        """
        items = []
        current_item = None
        
        # Collect all EQ text and degrees text for current item
        current_eq_parts = []
        current_degree_parts = []
        current_discipline_parts = []
        
        for table in self.tables:
            for row in table:
                if not row or len(row) < 5:
                    continue
                
                # Check if this row starts a new item (has item number)
                first_cell = str(row[0]).strip() if row[0] else ""
                
                if first_cell.isdigit() and int(first_cell) <= 50:
                    # Before starting new item, finalize the previous item's text
                    if current_item is not None:
                        self._finalize_item_text(current_item, current_discipline_parts, 
                                                 current_eq_parts, current_degree_parts)
                    
                    # Reset accumulators for new item
                    current_eq_parts = []
                    current_degree_parts = []
                    current_discipline_parts = []
                    
                    # Start of a new item
                    item_no = int(first_cell)
                    
                    # Extract discipline/subject (start accumulating)
                    if len(row) > 1 and row[1]:
                        current_discipline_parts.append(self._clean_text(row[1]))
                    
                    # Extract organization
                    organization = self._clean_text(row[2]) if len(row) > 2 else ""
                    
                    # Extract vacancies
                    vacancies = self._extract_vacancies_from_row(row)
                    
                    # Start accumulating essential qualification (col 9)
                    if len(row) > 9 and row[9]:
                        eq_text = self._clean_text(row[9])
                        # Skip if it's just the header
                        if eq_text and not eq_text.startswith("Essential Qualification"):
                            current_eq_parts.append(eq_text)
                    
                    # Start accumulating equivalent degrees (col 10)
                    if len(row) > 10 and row[10]:
                        degree_text = self._clean_text(row[10])
                        if degree_text:
                            current_degree_parts.append(degree_text)
                    
                    item = {
                        "itemNo": item_no,
                        "discipline": "",  # Will be finalized later
                        "organization": organization if organization else "DRDO",
                        "vacancies": vacancies,
                        "essentialQualification": "",  # Will be finalized later
                        "gateCode": None,  # Will be extracted later
                        "equivalentDegrees": []  # Will be finalized later
                    }
                    
                    # Check if same item number exists (different organizations)
                    existing_item = next((i for i in items if i["itemNo"] == item_no), None)
                    if existing_item and organization and organization != existing_item.get("organization"):
                        # This is a sub-entry for different organization
                        if "subOrganizations" not in existing_item:
                            existing_item["subOrganizations"] = []
                        existing_item["subOrganizations"].append({
                            "organization": organization,
                            "vacancies": vacancies
                        })
                        current_item = existing_item  # Continue accumulating for parent item
                    elif not existing_item:
                        items.append(item)
                        current_item = item
                    else:
                        current_item = existing_item
                    
                elif current_item:
                    # This is a continuation row for the current item
                    # Accumulate discipline text from col 1
                    if len(row) > 1 and row[1]:
                        text = self._clean_text(row[1])
                        if text and text not in ["Discipline", "Subject/", "Subject"]:
                            current_discipline_parts.append(text)
                    
                    # Check if this is a sub-organization row
                    if len(row) > 2 and row[2]:
                        org = self._clean_text(row[2])
                        if org in ["ADA", "WESEE", "CME", "AFMC", "SCN", "SCC", "SCE"]:
                            vacancies = self._extract_vacancies_from_row(row)
                            if "subOrganizations" not in current_item:
                                current_item["subOrganizations"] = []
                            current_item["subOrganizations"].append({
                                "organization": org,
                                "vacancies": vacancies
                            })
                    
                    # Accumulate EQ text from col 9
                    if len(row) > 9 and row[9]:
                        eq_text = self._clean_text(row[9])
                        # Filter out header text and accumulate actual qualification text
                        if eq_text and not eq_text.startswith("Essential Qualification") \
                           and eq_text not in ["Details of corresponding", "Graduate Aptitude Test in Engineering (GATE)"]:
                            current_eq_parts.append(eq_text)
                    
                    # Accumulate equivalent degrees from col 10
                    if len(row) > 10 and row[10]:
                        degree_text = self._clean_text(row[10])
                        if degree_text and not degree_text.startswith("Equivalent"):
                            current_degree_parts.append(degree_text)
        
        # Finalize the last item
        if current_item is not None:
            self._finalize_item_text(current_item, current_discipline_parts, 
                                     current_eq_parts, current_degree_parts)
        
        return items
    
    def _finalize_item_text(self, item: Dict[str, Any], discipline_parts: List[str],
                            eq_parts: List[str], degree_parts: List[str]) -> None:
        """Finalize accumulated text for an item."""
        # Combine discipline parts
        if discipline_parts:
            item["discipline"] = " ".join(discipline_parts)
        
        # Combine EQ parts into full qualification text
        if eq_parts:
            full_eq = " ".join(eq_parts)
            item["essentialQualification"] = full_eq
            # Extract GATE code from the full EQ text
            item["gateCode"] = self._extract_gate_code(full_eq)
        
        # Parse equivalent degrees from accumulated text
        if degree_parts:
            degrees = []
            # Headers and junk to filter out
            skip_phrases = [
                "Essential Qualification", "Equivalent acceptable", 
                "graduate aptitude", "GATE", "Paper code"
            ]
            for part in degree_parts:
                # Remove numbering like "1.", "2.", etc.
                cleaned = re.sub(r'^\d+\.\s*', '', part).strip()
                # Skip if empty, too short, or contains header text
                if cleaned and len(cleaned) > 2:
                    should_skip = any(phrase.lower() in cleaned.lower() for phrase in skip_phrases)
                    if not should_skip:
                        degrees.append(cleaned)
            item["equivalentDegrees"] = degrees
    
    def _extract_vacancies_from_row(self, row: List) -> Dict[str, int]:
        """Extract vacancy breakdown from a table row."""
        vacancies = {
            "UR": 0,
            "EWS": 0,
            "OBC": 0,
            "SC": 0,
            "ST": 0,
            "Total": 0
        }
        
        # Typically columns 3-8 contain vacancy data
        try:
            if len(row) > 3:
                vacancies["UR"] = self._parse_vacancy_number(row[3])
            if len(row) > 4:
                vacancies["EWS"] = self._parse_vacancy_number(row[4])
            if len(row) > 5:
                vacancies["OBC"] = self._parse_vacancy_number(row[5])
            if len(row) > 6:
                vacancies["SC"] = self._parse_vacancy_number(row[6])
            if len(row) > 7:
                vacancies["ST"] = self._parse_vacancy_number(row[7])
            if len(row) > 8:
                vacancies["Total"] = self._parse_vacancy_number(row[8])
        except:
            pass
        
        return vacancies
    
    def _parse_vacancy_number(self, value) -> int:
        """Parse vacancy number from cell value."""
        if value is None:
            return 0
        value_str = str(value).strip()
        if value_str == '-' or value_str == '':
            return 0
        # Extract first number
        match = re.search(r'(\d+)', value_str)
        if match:
            return int(match.group(1))
        return 0
    
    def _extract_gate_code(self, text: str) -> Optional[str]:
        """Extract GATE paper code from text."""
        if not text:
            return None
        
        patterns = [
            r'Paper\s+code\s*[:\-]?\s*([A-Z]{2})',  # Paper code EC or Paper code: EC
            r'\[Paper\s+code\s*[:\-]?\s*([A-Z]{2})\]',  # [Paper code: EC]
            r'Paper\s+Code\s+([A-Z]{2})',  # Paper Code EC (case sensitive)
            r'\(([A-Z]{2})\)\s*$',  # (EC) at end
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None
    
    def _extract_equivalent_degrees(self, text) -> List[str]:
        """Extract list of equivalent acceptable degrees."""
        if not text:
            return []
        
        text_str = str(text)
        degrees = []
        
        # Split by numbered list
        parts = re.split(r'\d+\.\s*', text_str)
        for part in parts:
            cleaned = self._clean_text(part)
            if cleaned and len(cleaned) > 3:
                degrees.append(cleaned)
        
        return degrees
    
    def _extract_general_info(self) -> Dict[str, Any]:
        """Extract general information about the recruitment."""
        info = {}
        
        # Pay Level
        pay_match = re.search(r'Level[-\s]*(\d+)', self.full_text)
        if pay_match:
            info["payLevel"] = int(pay_match.group(1))
        
        # Basic Pay
        basic_match = re.search(r'Basic\s+Pay\s+of\s+Rs\.?\s*([\d,]+)', self.full_text)
        if basic_match:
            info["basicPay"] = basic_match.group(1).replace(',', '')
        
        # Total Emoluments
        emol_match = re.search(r'approximately\s+Rs\.?\s*([\d,]+)', self.full_text)
        if emol_match:
            info["totalEmoluments"] = emol_match.group(1).replace(',', '')
        
        # Age limits
        age_info = {}
        age_patterns = [
            (r'Un\s*Reserved.*?(\d+)\s*years', 'UR'),
            (r'EWS.*?(\d+)\s*years', 'EWS'),
            (r'OBC.*?(\d+)\s*years', 'OBC'),
            (r'SC/?ST.*?(\d+)\s*years', 'SC_ST'),
        ]
        for pattern, category in age_patterns:
            match = re.search(pattern, self.full_text, re.IGNORECASE)
            if match:
                age_info[category] = int(match.group(1))
        
        if age_info:
            info["ageLimits"] = age_info
        
        # Application fee
        fee_match = re.search(r'application\s+fee\s+of\s+Rs\.?\s*(\d+)', self.full_text, re.IGNORECASE)
        if fee_match:
            info["applicationFee"] = int(fee_match.group(1))
        
        return info
    
    def _clean_text(self, text) -> str:
        """Clean extracted text."""
        if text is None:
            return ""
        text_str = str(text)
        # Remove extra whitespace
        text_str = ' '.join(text_str.split())
        # Remove special characters but keep basic punctuation
        text_str = re.sub(r'[^\w\s\-\(\)\&\.,/]', '', text_str)
        return text_str.strip()


def extract_advertisement(pdf_path: str) -> Dict[str, Any]:
    """
    Main function to extract advertisement data from PDF.
    
    Args:
        pdf_path: Path to the advertisement PDF file
        
    Returns:
        Dictionary containing extracted advertisement data
    """
    with AdvertisementExtractor(pdf_path) as extractor:
        return extractor.extract_all()


# Test function
if __name__ == "__main__":
    import json
    
    # Test with the sample PDF
    result = extract_advertisement("advt_156.pdf")
    print(json.dumps(result, indent=2, default=str))
