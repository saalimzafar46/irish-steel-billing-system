from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from io import BytesIO
from datetime import datetime
from models.company import Company
from models.invoice import Invoice
from models.client import Client
import os

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Normal'],
            fontSize=24,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyHeader',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=colors.black
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceDetails',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.white
        ))
    
    def generate_invoice_pdf(self, invoice: Invoice, company: Company, client: Client) -> BytesIO:
        """Generate a professional invoice PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        
        # Company Header
        story.append(self._create_company_header(company))
        story.append(Spacer(1, 20))
        
        # Invoice Title and Details
        story.append(Paragraph("INVOICE", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Invoice and Client Details Table
        story.append(self._create_invoice_details_table(invoice, client))
        story.append(Spacer(1, 20))
        
        # Items Table
        story.append(self._create_items_table(invoice))
        story.append(Spacer(1, 20))
        
        # Summary Table
        story.append(self._create_summary_table(invoice))
        story.append(Spacer(1, 20))
        
        # Payment Terms and Notes
        if invoice.payment_terms or invoice.notes:
            story.append(self._create_terms_and_notes(invoice))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(self._create_footer(company))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_company_header(self, company: Company):
        """Create company header section"""
        data = [
            [Paragraph(f"<b>{company.name}</b>", self.styles['CompanyHeader'])],
            [Paragraph(company.address, self.styles['InvoiceDetails'])],
            [Paragraph(f"{company.city}, {company.county} {company.postal_code}", self.styles['InvoiceDetails'])],
            [Paragraph(f"Phone: {company.phone} | Email: {company.email}", self.styles['InvoiceDetails'])],
        ]
        
        if company.vat_number:
            data.append([Paragraph(f"VAT Number: {company.vat_number}", self.styles['InvoiceDetails'])])
        
        table = Table(data, colWidths=[6*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return table
    
    def _create_invoice_details_table(self, invoice: Invoice, client: Client):
        """Create invoice and client details table"""
        # Left side - Client details
        client_data = [
            ["Bill To:", ""],
            [f"{client.name}", f"Invoice #: {invoice.invoice_number}"],
            [f"{client.contact_person}", f"Date: {invoice.issue_date}"],
            [f"{client.address}", f"Due Date: {invoice.due_date}"],
            [f"{client.city}, {client.county}", f"Terms: {invoice.payment_terms}"],
            [f"{client.postal_code}", ""],
        ]
        
        if client.vat_number:
            client_data.append([f"VAT: {client.vat_number}", ""])
        
        table = Table(client_data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, 4), 'Helvetica-Bold'),
        ]))
        
        return table
    
    def _create_items_table(self, invoice: Invoice):
        """Create items table"""
        # Headers
        headers = ['Description', 'Qty', 'Unit Price', 'Cuts', 'Cutting Cost', 'Discount', 'Total']
        
        data = [headers]
        
        for item in invoice.items:
            cutting_cost = item.cuts_required * item.cutting_charge_per_cut
            discount_text = ""
            if item.discount_percentage > 0:
                discount_text += f"{item.discount_percentage}%"
            if item.discount_amount > 0:
                if discount_text:
                    discount_text += f" + €{item.discount_amount:.2f}"
                else:
                    discount_text = f"€{item.discount_amount:.2f}"
            
            row = [
                f"{item.product_name}\n{item.description}",
                f"{item.quantity:.2f}",
                f"€{item.unit_price:.2f}",
                str(item.cuts_required) if item.cuts_required > 0 else "-",
                f"€{cutting_cost:.2f}" if cutting_cost > 0 else "-",
                discount_text if discount_text else "-",
                f"€{item.line_total:.2f}"
            ]
            data.append(row)
        
        table = Table(data, colWidths=[2.5*inch, 0.5*inch, 0.8*inch, 0.4*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Description left-aligned
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Alternate row colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))
        
        table.setStyle(TableStyle(style))
        return table
    
    def _create_summary_table(self, invoice: Invoice):
        """Create invoice summary table"""
        data = [
            ['Subtotal:', f"€{invoice.subtotal:.2f}"],
        ]
        
        # Additional charges
        if invoice.shipping_cost > 0:
            data.append(['Shipping Cost:', f"€{invoice.shipping_cost:.2f}"])
        if invoice.handling_cost > 0:
            data.append(['Handling Cost:', f"€{invoice.handling_cost:.2f}"])
        if invoice.other_charges > 0:
            desc = invoice.other_charges_description or "Other Charges"
            data.append([f'{desc}:', f"€{invoice.other_charges:.2f}"])
        
        # Global discounts
        if invoice.global_discount_percentage > 0 or invoice.global_discount_amount > 0:
            data.append(['Discount:', f"-€{invoice.global_discount_total:.2f}"])
        
        data.extend([
            ['Total Before VAT:', f"€{invoice.total_before_vat:.2f}"],
            [f'VAT ({invoice.vat_rate}%):', f"€{invoice.vat_amount:.2f}"],
            ['Total Amount:', f"€{invoice.total_amount:.2f}"],
        ])
        
        table = Table(data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table
    
    def _create_terms_and_notes(self, invoice: Invoice):
        """Create payment terms and notes section"""
        elements = []
        
        if invoice.payment_terms:
            elements.append(Paragraph(f"<b>Payment Terms:</b> {invoice.payment_terms}", self.styles['InvoiceDetails']))
        
        if invoice.notes:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Notes:</b> {invoice.notes}", self.styles['InvoiceDetails']))
        
        return elements
    
    def _create_footer(self, company: Company):
        """Create footer with bank details"""
        footer_text = "Thank you for your business!"
        
        if company.bank_name or company.iban:
            footer_text += "<br/><br/><b>Payment Details:</b><br/>"
            if company.bank_name:
                footer_text += f"Bank: {company.bank_name}<br/>"
            if company.iban:
                footer_text += f"IBAN: {company.iban}<br/>"
            if company.bank_sort_code:
                footer_text += f"Sort Code: {company.bank_sort_code}<br/>"
        
        return Paragraph(footer_text, self.styles['InvoiceDetails'])
