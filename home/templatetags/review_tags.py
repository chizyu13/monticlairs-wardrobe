"""
Template tags for displaying product reviews and ratings.
"""

from django import template

register = template.Library()


@register.filter
def star_rating(rating):
    """
    Convert a numeric rating to star display.
    
    Usage: {{ product.get_average_rating|star_rating }}
    Returns: HTML string with filled and empty stars
    """
    try:
        rating = float(rating)
    except (ValueError, TypeError):
        rating = 0
    
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    html = ''
    
    # Full stars
    for _ in range(full_stars):
        html += '<i class="fas fa-star" style="color: #d4af37;"></i>'
    
    # Half star
    if half_star:
        html += '<i class="fas fa-star-half-alt" style="color: #d4af37;"></i>'
    
    # Empty stars
    for _ in range(empty_stars):
        html += '<i class="far fa-star" style="color: #d4af37;"></i>'
    
    return html


@register.filter
def star_rating_text(rating):
    """
    Convert numeric rating to text with stars.
    
    Usage: {{ product.get_average_rating|star_rating_text }}
    Returns: "4.5 ★★★★☆"
    """
    try:
        rating = float(rating)
    except (ValueError, TypeError):
        rating = 0
    
    full_stars = int(rating)
    half_star = '½' if (rating - full_stars) >= 0.5 else ''
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    stars = '★' * full_stars + half_star + '☆' * empty_stars
    
    return f"{rating:.1f} {stars}"


@register.simple_tag
def rating_percentage(rating_value, total_reviews):
    """
    Calculate percentage of reviews for a specific rating.
    
    Usage: {% rating_percentage 5 total_reviews %}
    """
    if total_reviews == 0:
        return 0
    
    try:
        percentage = (rating_value / total_reviews) * 100
        return round(percentage, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.inclusion_tag('home/includes/star_rating.html')
def show_star_rating(rating, show_count=False, review_count=0):
    """
    Display star rating with optional review count.
    
    Usage: {% show_star_rating product.get_average_rating True product.get_rating_count %}
    """
    try:
        rating = float(rating)
    except (ValueError, TypeError):
        rating = 0
    
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    return {
        'rating': rating,
        'full_stars': range(full_stars),
        'half_star': half_star,
        'empty_stars': range(empty_stars),
        'show_count': show_count,
        'review_count': review_count,
    }


@register.inclusion_tag('home/includes/rating_bar.html')
def show_rating_bar(star_value, count, total, percentage):
    """
    Display a rating distribution bar.
    
    Usage: {% show_rating_bar 5 count total percentage %}
    """
    return {
        'star_value': star_value,
        'count': count,
        'total': total,
        'percentage': percentage,
    }
