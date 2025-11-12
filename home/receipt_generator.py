"""
Receipt Generator for Montclair Wardrobe
Generates PDF receipts for completed orders
"""
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.conf import settings
from datetime import datetime


class ReceiptGenerator:
    """Generate professional PDF receipts for orders"""
    
    def __init__(self, checkout):
        """
        Initialize receipt generator
        
        Args:
            checkout: Checkout instance
        """
        self.checkout = checkout
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#D4AF37'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1A202C'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2D3748'),
            spaceAfter=6
        )
    
    def _add_header(self):
        """Add company header to receipt"""
        # Company name
        company_name = Paragraph(
            "<b>MONTCLAIR WARDROBE</b>",
            self.title_style
        )
        self.story.append(company_name)
        
        # Company details
        company_info = Paragraph(
            "Luxury Fashion Boutique<br/>"
            "Lusaka, Zambia<br/>"
            "Phone: +260 XXX XXX XXX<br/>"
            "Email: info@montclairwardrobe.com",
            ParagraphStyle(
                'CompanyInfo',
                parent=self.normal_style,
                alignment=TA_CENTER,
                fontSize=9,
                textColor=colors.HexColor('#718096')
            )
        )
        self.story.append(company_info)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Receipt title
        receipt_title = Paragraph(
            "<b>PAYMENT RECEIPT</b>",
            ParagraphStyle(
                'ReceiptTitle',
                parent=self.heading_style,
                alignment=TA_CENTER,
                fontSize=16,
                textColor=colors.HexColor('#D4AF37')
            )
        )
        self.story.append(receipt_title)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _add_receipt_info(self):
        """Add receipt information"""
        # Receipt details
        receipt_data = [
            ['Receipt Number:', f"MW{self.checkout.id:06d}"],
            ['Date:', self.checkout.created_at.strftime('%B %d, %Y %I:%M %p')],
            ['Payment Method:', self.checkout.get_payment_method_display()],
            ['Payment Status:', self.checkout.get_payment_status_display().upper()],
        ]
        
        if self.checkout.transaction_id:
            receipt_data.append(['Transaction ID:', self.checkout.transaction_id])
        
        receipt_table = Table(receipt_data, colWidths=[2*inch, 4*inch])
        receipt_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4A5568')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2D3748')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(receipt_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_customer_info(self):
        """Add customer information"""
        customer_heading = Paragraph("<b>Customer Information</b>", self.heading_style)
        self.story.append(customer_heading)
        
        user = self.checkout.user
        customer_data = [
            ['Name:', user.get_full_name() or user.username],
            ['Email:', user.email],
            ['Phone:', self.checkout.phone_number],
            ['Location:', self.checkout.get_location_display()],
        ]
        
        if self.checkout.room_number:
            customer_data.append(['Room Number:', self.checkout.room_number])
        
        customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4A5568')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2D3748')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(customer_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_order_items(self):
        """Add order items table"""
        items_heading = Paragraph("<b>Order Items</b>", self.heading_style)
        self.story.append(items_heading)
        
        # Table header
        items_data = [
            ['Item', 'Quantity', 'Unit Price', 'Total']
        ]
        
        # Add order items
        orders = self.checkout.orders.all()
        subtotal = 0
        
        for order in orders:
            items_data.append([
                order.product.name,
                str(order.quantity),
                f"ZMW {order.product.price:,.2f}",
                f"ZMW {order.total_price:,.2f}"
            ])
            subtotal += order.total_price
        
        # Create table
        items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D4AF37')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1A202C')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body style
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2D3748')),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#B8941F')),
        ]))
        
        self.story.append(items_table)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Add totals
        totals_data = [
            ['', '', 'Subtotal:', f"ZMW {subtotal:,.2f}"],
            ['', '', 'Delivery Fee:', f"ZMW {self.checkout.delivery_fee:,.2f}"],
            ['', '', 'TOTAL:', f"ZMW {subtotal + self.checkout.delivery_fee:,.2f}"],
        ]
        
        totals_table = Table(totals_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('FONTNAME', (2, 0), (2, 1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (3, 1), 'Helvetica'),
            ('FONTNAME', (2, 2), (3, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (2, 0), (3, 1), 10),
            ('FONTSIZE', (2, 2), (3, 2), 12),
            ('TEXTCOLOR', (2, 0), (3, 1), colors.HexColor('#4A5568')),
            ('TEXTCOLOR', (2, 2), (3, 2), colors.HexColor('#D4AF37')),
            ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
            ('BOTTOMPADDING', (2, 0), (3, 1), 6),
            ('TOPPADDING', (2, 2), (3, 2), 12),
            ('BOTTOMPADDING', (2, 2), (3, 2), 12),
            ('LINEABOVE', (2, 2), (3, 2), 2, colors.HexColor('#D4AF37')),
        ]))
        
        self.story.append(totals_table)
        self.story.append(Spacer(1, 0.4*inch))
    
    def _add_footer(self):
        """Add receipt footer"""
        footer_text = Paragraph(
            "<b>Thank you for shopping with Montclair Wardrobe!</b><br/>"
            "For any inquiries, please contact us at info@montclairwardrobe.com<br/>"
            "<i>This is a computer-generated receipt and does not require a signature.</i>",
            ParagraphStyle(
                'Footer',
                parent=self.normal_style,
                alignment=TA_CENTER,
                fontSize=9,
                textColor=colors.HexColor('#718096'),
                spaceAfter=0
            )
        )
        self.story.append(footer_text)
    
    def generate(self):
        """
        Generate the PDF receipt
        
        Returns:
            BytesIO: PDF file buffer
        """
        # Build receipt
        self._add_header()
        self._add_receipt_info()
        self._add_customer_info()
        self._add_order_items()
        self._add_footer()
        
        # Generate PDF
        self.doc.build(self.story)
        
        # Get PDF value
        pdf = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf


def generate_receipt(checkout):
    """
    Convenience function to generate receipt
    
    Args:
        checkout: Checkout instance
    
    Returns:
        bytes: PDF content
    """
    generator = ReceiptGenerator(checkout)
    return generator.generate()
