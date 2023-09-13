import os
import pandas as pd 
import glob
from fpdf import FPDF
from pathlib import Path

class InvoicePDF:
    """A class to handle the creation of invoice PDFs from Excel files."""
    
    def __init__(self, invoices_path, pdfs_path, company_name, logo_path):
        """
        Initializes the InvoicePDF class.
        
        Args:
            invoices_path (str): Path to the directory containing Excel invoices.
            pdfs_path (str): Path to the directory where the generated PDFs should be saved.
            company_name (str): Name of the company.
            logo_path (str): Path to the company's logo image.
        """
        self.invoices_path = invoices_path
        self.pdfs_path = pdfs_path
        self.company_name = company_name
        self.logo_path = logo_path
        
    def _fetch_data_from_excel(self, filepath, product_id, product_name, amount_purchased, price_per_unit, total_price):
        """Fetches data from the Excel file."""
        df = pd.read_excel(filepath)
        return df[[product_id, product_name, amount_purchased, price_per_unit, total_price]]

        
    def _generate_pdf(self, filepath, product_id, product_name, amount_purchased, price_per_unit, total_price):
        """Generate a single PDF from the provided Excel filepath."""
        pdf = FPDF(orientation="P", unit="mm", format= "A4")
        pdf.add_page()

        filename = Path(filepath).stem
        invoice_nr, date = filename.split("-")

        # Header
        pdf.set_font(family="Times", style="B", size=16)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=50, h=8, txt=f"Invoice nr. {invoice_nr}", ln=1)
        pdf.set_font(family="Times", style="I", size=14)
        pdf.cell(w=50, h=8, txt=f"Date: {date}", ln=1)

        # Fetch data from Excel
        data = self._fetch_data_from_excel(filepath, product_id, product_name, amount_purchased, price_per_unit, total_price)
        
        # Add table header
        col_widths = [30, 60, 40, 30, 30]  # Adjust these values based on your requirements
        columns = [product_id, product_name, amount_purchased, price_per_unit, total_price]
        
        pdf.set_fill_color(200, 200, 200)  # Gray fill for headers
        pdf.set_font(family="Times", style="B", size=12)  # Adjusting the font size for the header
        
        for i, column in enumerate(columns):
            pdf.cell(col_widths[i], 10, column, 1, 0, 'C', 1)
        pdf.ln()

        # Set font for table data
        pdf.set_font(family="Times", style="", size=12)  # Set to font size for data in table
        
        # Add table data
        for _, row in data.iterrows():
            for i, item in enumerate(row):
                pdf.cell(col_widths[i], 10, str(item), 1)
            pdf.ln()

        # Save PDF
        os.makedirs(self.pdfs_path, exist_ok=True)
        pdf.output(f"{self.pdfs_path}/{filename}.pdf")

    def generate_all(self, product_id, product_name, amount_purchased, price_per_unit, total_price):
        """
        Generates PDF invoices for all Excel files in the invoices path.
        
        Args:
            product_id (str): Column name for product IDs.
            product_name (str): Column name for product names.
            amount_purchased (str): Column name for amounts purchased.
            price_per_unit (str): Column name for unit prices.
            total_price (str): Column name for total prices.
        """
        filepaths = glob.glob(f"{self.invoices_path}/*.xlsx")
        for filepath in filepaths:
            self._generate_pdf(filepath, product_id, product_name, amount_purchased, price_per_unit, total_price)

