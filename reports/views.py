from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
import csv
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch

from .services import ReportService
from .models import ReportCache, ReportAccess
from home.models import Order, Product


def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def reports_dashboard(request):
    """Main reports dashboard"""
    context = {
        'page_title': 'Reports Dashboard',
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def daily_sales_report(request):
    """Daily sales report"""
    date_str = request.GET.get('date')
    
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = timezone.now().date()
    else:
        date = timezone.now().date()
    
    # Get report data
    report_data = ReportService.get_daily_sales_report(date)
    
    # Log access
    ReportAccess.objects.create(
        user=request.user,
        report_type='daily_sales'
    )
    
    context = {
        'report_data': report_data,
        'report_date': date,
        'page_title': 'Daily Sales Report',
    }
    
    return render(request, 'reports/daily_sales.html', context)


@login_required
@user_passes_test(is_admin)
def order_status_report(request):
    """Order status report"""
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    
    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            date_from = timezone.now().date() - timedelta(days=30)
    else:
        date_from = timezone.now().date() - timedelta(days=30)
    
    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            date_to = timezone.now().date()
    else:
        date_to = timezone.now().date()
    
    # Get report data
    report_data = ReportService.get_order_status_report(date_from, date_to)
    
    # Log access
    ReportAccess.objects.create(
        user=request.user,
        report_type='order_status'
    )
    
    context = {
        'report_data': report_data,
        'date_from': date_from,
        'date_to': date_to,
        'page_title': 'Order Status Report',
    }
    
    return render(request, 'reports/order_status.html', context)


@login_required
@user_passes_test(is_admin)
def product_sales_report(request):
    """Product sales report"""
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    
    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            date_from = timezone.now().date() - timedelta(days=30)
    else:
        date_from = timezone.now().date() - timedelta(days=30)
    
    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            date_to = timezone.now().date()
    else:
        date_to = timezone.now().date()
    
    # Get report data
    report_data = ReportService.get_product_sales_report(date_from, date_to)
    
    # Log access
    ReportAccess.objects.create(
        user=request.user,
        report_type='product_sales'
    )
    
    context = {
        'report_data': report_data,
        'date_from': date_from,
        'date_to': date_to,
        'page_title': 'Product Sales Report',
    }
    
    return render(request, 'reports/product_sales.html', context)


@login_required
@user_passes_test(is_admin)
def stock_level_report(request):
    """Stock level report"""
    # Get report data
    report_data = ReportService.get_stock_level_report()
    
    # Log access
    ReportAccess.objects.create(
        user=request.user,
        report_type='stock_level'
    )
    
    context = {
        'report_data': report_data,
        'page_title': 'Stock Level Report',
    }
    
    return render(request, 'reports/stock_level.html', context)


@login_required
@user_passes_test(is_admin)
def customer_growth_report(request):
    """Customer growth report"""
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    
    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            date_from = timezone.now().date() - timedelta(days=30)
    else:
        date_from = timezone.now().date() - timedelta(days=30)
    
    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            date_to = timezone.now().date()
    else:
        date_to = timezone.now().date()
    
    # Get report data
    report_data = ReportService.get_customer_growth_report(date_from, date_to)
    
    # Log access
    ReportAccess.objects.create(
        user=request.user,
        report_type='customer_growth'
    )
    
    context = {
        'report_data': report_data,
        'date_from': date_from,
        'date_to': date_to,
        'page_title': 'Customer Growth Report',
    }
    
    return render(request, 'reports/customer_growth.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def export_report(request):
    """Export report to CSV or PDF"""
    report_type = request.GET.get('type')
    format_type = request.GET.get('format', 'csv')  # csv or pdf
    
    if format_type == 'csv':
        return export_to_csv(request, report_type)
    elif format_type == 'pdf':
        return export_to_pdf(request, report_type)
    else:
        return JsonResponse({'error': 'Invalid format'}, status=400)


def export_to_csv(request, report_type):
    """Export report to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{report_type}_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    
    if report_type == 'daily_sales':
        date_str = request.GET.get('date', str(timezone.now().date()))
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        report_data = ReportService.get_daily_sales_report(date)
        
        writer.writerow(['Daily Sales Report', date])
        writer.writerow([])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Sales', report_data['total_sales']])
        writer.writerow(['Total Revenue', f"ZMW {report_data['total_revenue']:.2f}"])
        writer.writerow(['Unique Customers', report_data['unique_customers']])
        writer.writerow(['Average Order Value', f"ZMW {report_data['average_order_value']:.2f}"])
        
    elif report_type == 'order_status':
        date_from_str = request.GET.get('date_from', str(timezone.now().date() - timedelta(days=30)))
        date_to_str = request.GET.get('date_to', str(timezone.now().date()))
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        report_data = ReportService.get_order_status_report(date_from, date_to)
        
        writer.writerow(['Order Status Report', f'{date_from} to {date_to}'])
        writer.writerow([])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Orders', report_data['total_orders']])
        writer.writerow(['Total Revenue', f"ZMW {report_data['total_revenue']:.2f}"])
        writer.writerow(['Pending Orders', report_data['pending_orders']])
        writer.writerow(['Cancellation Rate', f"{report_data['cancellation_rate']:.1f}%"])
        
    elif report_type == 'product_sales':
        date_from_str = request.GET.get('date_from', str(timezone.now().date() - timedelta(days=30)))
        date_to_str = request.GET.get('date_to', str(timezone.now().date()))
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        report_data = ReportService.get_product_sales_report(date_from, date_to)
        
        writer.writerow(['Product Sales Report', f'{date_from} to {date_to}'])
        writer.writerow([])
        writer.writerow(['Product Name', 'Category', 'Units Sold', 'Revenue', 'Average Price'])
        for product in report_data['products']:
            writer.writerow([
                product['name'],
                product['category'],
                product['units_sold'],
                f"ZMW {product['revenue']:.2f}",
                f"ZMW {product['average_price']:.2f}",
            ])
    
    elif report_type == 'stock_level':
        report_data = ReportService.get_stock_level_report()
        
        writer.writerow(['Stock Level Report'])
        writer.writerow([])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Products', report_data['total_products']])
        writer.writerow(['In Stock', report_data['in_stock']])
        writer.writerow(['Out of Stock', report_data['out_of_stock']])
        writer.writerow(['Low Stock', report_data['low_stock']])
        writer.writerow(['Total Inventory Value', f"ZMW {report_data['total_inventory_value']:.2f}"])
        
    elif report_type == 'customer_growth':
        date_from_str = request.GET.get('date_from', str(timezone.now().date() - timedelta(days=30)))
        date_to_str = request.GET.get('date_to', str(timezone.now().date()))
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        report_data = ReportService.get_customer_growth_report(date_from, date_to)
        
        writer.writerow(['Customer Growth Report', f'{date_from} to {date_to}'])
        writer.writerow([])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['New Customers', report_data['new_customers']])
        writer.writerow(['Total Active Customers', report_data['total_customers']])
        writer.writerow(['Customers with Orders', report_data['customers_with_orders']])
        writer.writerow(['Repeat Customers', report_data['repeat_customers']])
        writer.writerow(['Average LTV', f"ZMW {report_data['average_ltv']:.2f}"])
    
    # Log access
    ReportAccess.objects.create(
        user=request.user,
        report_type=report_type,
        export_format='csv'
    )
    
    return response


def export_to_pdf(request, report_type):
    """Export report to PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#d4af37'),
        spaceAfter=30,
    )
    
    # Heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#d4af37'),
        spaceAfter=12,
    )
    
    if report_type == 'daily_sales':
        date_str = request.GET.get('date', str(timezone.now().date()))
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        report_data = ReportService.get_daily_sales_report(date)
        
        elements.append(Paragraph(f'Daily Sales Report - {date}', title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Sales', str(report_data['total_sales'])],
            ['Total Revenue', f"ZMW {report_data['total_revenue']:.2f}"],
            ['Unique Customers', str(report_data['unique_customers'])],
            ['Average Order Value', f"ZMW {report_data['average_order_value']:.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4af37')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Top products
        if report_data.get('top_products'):
            elements.append(Paragraph('Top 5 Products Sold', heading_style))
            products_data = [['Product Name', 'Quantity', 'Revenue']]
            for product in report_data['top_products']:
                products_data.append([
                    product['name'][:30],
                    str(product['quantity']),
                    f"ZMW {product['revenue']:.2f}"
                ])
            
            products_table = Table(products_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            products_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4af37')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(products_table)
    
    elif report_type == 'order_status':
        date_from_str = request.GET.get('date_from', str(timezone.now().date() - timedelta(days=30)))
        date_to_str = request.GET.get('date_to', str(timezone.now().date()))
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        report_data = ReportService.get_order_status_report(date_from, date_to)
        
        elements.append(Paragraph(f'Order Status Report - {date_from} to {date_to}', title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_data = [
            ['Metric', 'Value'],
            ['Total Orders', str(report_data['total_orders'])],
            ['Total Revenue', f"ZMW {report_data['total_revenue']:.2f}"],
            ['Pending Orders', str(report_data['pending_orders'])],
            ['Cancellation Rate', f"{report_data['cancellation_rate']:.1f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4af37')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(summary_table)
    
    elif report_type == 'product_sales':
        date_from_str = request.GET.get('date_from', str(timezone.now().date() - timedelta(days=30)))
        date_to_str = request.GET.get('date_to', str(timezone.now().date()))
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        report_data = ReportService.get_product_sales_report(date_from, date_to)
        
        elements.append(Paragraph(f'Product Sales Report - {date_from} to {date_to}', title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_data = [
            ['Metric', 'Value'],
            ['Products Sold', str(report_data['total_products_sold'])],
            ['Total Units', str(report_data['total_units'])],
            ['Total Revenue', f"ZMW {report_data['total_revenue']:.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4af37')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(summary_table)
    
    elif report_type == 'stock_level':
        report_data = ReportService.get_stock_level_report()
        
        elements.append(Paragraph('Stock Level Report', title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_data = [
            ['Metric', 'Value'],
            ['Total Products', str(report_data['total_products'])],
            ['In Stock', str(report_data['in_stock'])],
            ['Out of Stock', str(report_data['out_of_stock'])],
            ['Low Stock', str(report_data['low_stock'])],
            ['Total Inventory Value', f"ZMW {report_data['total_inventory_value']:.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4af37')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(summary_table)
    
    elif report_type == 'customer_growth':
        date_from_str = request.GET.get('date_from', str(timezone.now().date() - timedelta(days=30)))
        date_to_str = request.GET.get('date_to', str(timezone.now().date()))
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        report_data = ReportService.get_customer_growth_report(date_from, date_to)
        
        elements.append(Paragraph(f'Customer Growth Report - {date_from} to {date_to}', title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_data = [
            ['Metric', 'Value'],
            ['New Customers', str(report_data['new_customers'])],
            ['Total Active Customers', str(report_data['total_customers'])],
            ['Customers with Orders', str(report_data['customers_with_orders'])],
            ['Repeat Customers', str(report_data['repeat_customers'])],
            ['Average LTV', f"ZMW {report_data['average_ltv']:.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4af37')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(summary_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{report_type}_{timezone.now().date()}.pdf"'
    
    # Log access
    ReportAccess.objects.create(
        user=request.user,
        report_type=report_type,
        export_format='pdf'
    )
    
    return response
