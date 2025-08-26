from django import template
from django.db.models import Sum

register = template.Library()


@register.filter
def sum_portfolio_count(categories):
    """Суммирует количество портфолио во всех категориях"""
    return categories.aggregate(total=Sum("portfolio_count"))["total"] or 0
