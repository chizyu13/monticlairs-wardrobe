"""
Reports generation module for Montclair Wardrobe
Handles sales reports, analytics, and data exports
"""
import csv
from datetime import datetime, timedelta
from io import BytesIO
from django.db.models import Sum, Count, Avg, Q
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from home.models import Sale, Order, Checkout, Product


class ReportGenerator:
    """Generate various reports for the e-commerce system"""
    
    @staticmethod
    def get_sales_summary(start_date=None, end_date=None, seller=None):
        """Get sales summary for a date range"""
        sales = Sale.objects.all()
        
        if seller:
            sales = sales.filter(seller=seller)
        if start_date:
            sales = sales.filter(sale_date__gte=start_date)
        if end_date:
            sales = sales.filter(sale_date__lte=end_date)
        
        summary = sales.aggregate(
            total_sales=Sum('total_amount'),
            total_orders=Count('id'),
            total_quantity=Sum('quantity'),
            average_order=Avg('total_amount')
        )
        
        return {
            'total_sales': summary['total_sales'] or 0,
            'total_orders': summary['total_orders'] or 0,
            'total_quantity': summary['total_quantity'] or 0,
            'average_order': summary['average_order'] or 0,
            'sales': sales
        }
    
    @staticmethod
    def get_monthly_report(year, month, seller=None):
        """Generate monthly sales report"""
        from calendar import monthrange
        
        start_date = datetime(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59)
        
        return ReportGenerator.get_sales_summary(start_date, end_date, seller)
    
    @staticmethod
    def get_annual_report(year, seller=None):
        """Generate annual sales report"""
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
        
        return ReportGenerator.get_sales_summary(start_date, end_date, seller)
    
    @staticmethod
    def get_product_performance(start_date=None, end_date=None):
        """Get product performance metrics"""
        sales = Sale.objects.all()
        
        if start_date:
            sales = sales.filter(sale_date__gte=start_date)
        if end_date:
            sales = sales.filter(sale_date__lte=end_date)
        
        products = sales.values('product__name', 'product__id').annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('-total_revenue')
        
        return products
    
    @staticmethod
    def export_to_csv(data, filename='report.csv'):
        """Export report data to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        
        # Write headers
        if data:
            writer.writerow(data[0].keys())
            
            # Write data
            for row in data:
                writer.writerow(row.values())
        
        return response
    
    @staticmethod
    def export_to_pdf(report_data, filename='report.pdf', title='Sales Report'):
        """Export report data to PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#d4af37'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Report info
        info_style = styles['Normal']
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", info_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary section
        if 'summary' in report_data:
            summary = report_data['summary']
            summary_data = [
                ['Metric', 'Value'],
                ['Total Sales', f"ZMW {summary.get('total_sales', 0):,.2f}"],
                ['Total Orders', str(summary.get('total_orders', 0))],
                ['Total Items Sold', str(summary.get('total_quantity', 0))],
                ['Average Order Value', f"ZMW {summary.get('average_order', 0):,.2f}"],
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4af37')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.5*inch))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


def generate_sales_csv(sales_queryset, filename='sales_report.csv'):
    """Generate CSV export for sales data"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Product', 'Buyer', 'Seller', 'Date', 'Quantity', 'Amount', 'Status'])
    
    for sale in sales_queryset:
        writer.writerow([
            sale.id,
            sale.product.name,
            sale.buyer.username,
            sale.seller.username,
            sale.sale_date.strftime('%Y-%m-%d %H:%M'),
            sale.quantity,
            f"ZMW {sale.total_amount}",
            'Completed'
        ])
    
    return response


def generate_product_performance_csv(products, filename='product_performance.csv'):
    """Generate CSV for product performance"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['Product', 'Units Sold', 'Total Revenue', 'Number of Orders'])
    
    for product in products:
        writer.writerow([
            product['product__name'],
            product['total_sold'],
            f"ZMW {product['total_revenue']}",
            product['order_count']
        ])
    
    return response
