"""
Receipt generation utilities for Montclair Wardrobe
Generates PDF receipts for completed orders
"""
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import os
from django.conf import settings


class ReceiptGenerator:
    """Generate PDF receipts for orders"""
    
    def __init__(self, checkout):
        """
        Initialize receipt generator
        
        Args:
            checkout: Checkout instance
        """
        self.checkout = checkout
        self.orders = checkout.orders.all().select_related('product')
        self.payment = None
        
        # Try to get associated payment
        from payment.models import Payment
        if checkout.transaction_id:
            self.payment = Payment.objects.filter(reference=checkout.transaction_id).first()
    
    def generate_pdf(self):
        """
        Generate PDF receipt
        
        Returns:
            BytesIO buffer containing PDF data
        """
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#D4AF37'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1A202C'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2D3748'),
            spaceAfter=6
        )
        
        # Header - Company Name
        title = Paragraph("MONTCLAIR WARDROBE", title_style)
        elements.append(title)
        
        subtitle = Paragraph("Luxury Fashion Boutique", normal_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*inch))
        
        # Receipt Title
        receipt_title = Paragraph("RECEIPT", heading_style)
        elements.append(receipt_title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Receipt Information
        receipt_info = [
            ['Receipt Number:', f"MW{self.checkout.id:06d}"],
            ['Date:', self.checkout.created_at.strftime('%B %d, %Y %I:%M %p')],
            ['Payment Method:', self.checkout.get_payment_method_display()],
            ['Payment Status:', self.checkout.get_payment_status_display().upper()],
        ]
        
        if self.payment:
            receipt_info.append(['Transaction ID:', self.payment.reference])
        
        info_table = Table(receipt_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2D3748')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Customer Information
        customer_heading = Paragraph("Customer Information", heading_style)
        elements.append(customer_heading)
        
        customer_info = [
            ['Name:', self.checkout.user.get_full_name() or self.checkout.user.username],
            ['Email:', self.checkout.user.email],
            ['Phone:', self.checkout.phone_number],
            ['Location:', self.checkout.get_location_display()],
        ]
        
        customer_table = Table(customer_info, colWidths=[2*inch, 4*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2D3748')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Order Items
        items_heading = Paragraph("Order Items", heading_style)
        elements.append(items_heading)
        elements.append(Spacer(1, 0.1*inch))
        
        # Items table header
        items_data = [['Item', 'Qty', 'Unit Price', 'Total']]
        
        # Add each order item
        for order in self.orders:
            items_data.append([
                order.product.name[:40],  # Truncate long names
                str(order.quantity),
                f"ZMW {order.product.price:.2f}",
                f"ZMW {order.total_price:.2f}"
            ])
        
        # Calculate totals
        subtotal = sum(order.total_price for order in self.orders)
        delivery_fee = self.checkout.delivery_fee
        total = subtotal + delivery_fee
        
        # Add subtotal, delivery, and total rows
        items_data.append(['', '', 'Subtotal:', f"ZMW {subtotal:.2f}"])
        items_data.append(['', '', 'Delivery Fee:', f"ZMW {delivery_fee:.2f}"])
        items_data.append(['', '', 'TOTAL:', f"ZMW {total:.2f}"])
        
        items_table = Table(items_data, colWidths=[3.5*inch, 0.75*inch, 1.25*inch, 1.25*inch])
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D4AF37')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1A202C')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -4), 10),
            ('TEXTCOLOR', (0, 1), (-1, -4), colors.HexColor('#2D3748')),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 1), (-1, -4), 8),
            ('TOPPADDING', (0, 1), (-1, -4), 8),
            
            # Subtotal and delivery rows
            ('FONTNAME', (2, -3), (-1, -2), 'Helvetica-Bold'),
            ('FONTSIZE', (2, -3), (-1, -2), 10),
            ('TOPPADDING', (0, -3), (-1, -3), 12),
            
            # Total row
            ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#F7FAFC')),
            ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (2, -1), (-1, -1), 12),
            ('TEXTCOLOR', (2, -1), (-1, -1), colors.HexColor('#D4AF37')),
            ('TOPPADDING', (0, -1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
            
            # Grid
            ('GRID', (0, 0), (-1, -4), 1, colors.HexColor('#E2E8F0')),
            ('LINEABOVE', (0, -3), (-1, -3), 1, colors.HexColor('#CBD5E0')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#D4AF37')),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#718096'),
            alignment=TA_CENTER
        )
        
        footer_text = """
        <para align=center>
        Thank you for shopping with Montclair Wardrobe!<br/>
        For inquiries, contact us at support@montclairwardrobe.com<br/>
        <br/>
        <i>This is a computer-generated receipt and does not require a signature.</i>
        </para>
        """
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def generate_html_receipt(self):
        """
        Generate HTML receipt for email or web display
        
        Returns:
            str: HTML content
        """
        subtotal = sum(order.total_price for order in self.orders)
        total = subtotal + self.checkout.delivery_fee
        
        context = {
            'checkout': self.checkout,
            'orders': self.orders,
            'payment': self.payment,
            'subtotal': subtotal,
            'total': total,
            'receipt_number': f"MW{self.checkout.id:06d}",
        }
        
        return render_to_string('receipts/receipt_template.html', context)


def generate_receipt_pdf(checkout):
    """
    Generate and return PDF receipt as HTTP response
    
    Args:
        checkout: Checkout instance
    
    Returns:
        HttpResponse with PDF content
    """
    generator = ReceiptGenerator(checkout)
    pdf_data = generator.generate_pdf()
    
    # Create response
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_MW{checkout.id:06d}.pdf"'
    
    return response


def generate_receipt_html(checkout):
    """
    Generate HTML receipt
    
    Args:
        checkout: Checkout instance
    
    Returns:
        str: HTML content
    """
    generator = ReceiptGenerator(checkout)
    return generator.generate_html_receipt()
