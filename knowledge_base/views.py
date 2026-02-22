from django.shortcuts import render, get_object_or_404
from .models import Category, Article

def index(request):
    categories = Category.objects.all()
    recent_articles = Article.objects.filter(is_published=True).order_by('-created_at')[:5]
    context = {
        'categories': categories,
        'recent_articles': recent_articles,
        'title': 'База знаний',
        'breadcrumbs': [
            {'title': 'База знаний', 'url': ''}
        ]
    }
    return render(request, 'knowledge_base/index.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = category.articles.filter(is_published=True)
    context = {
        'category': category,
        'articles': articles,
        'title': f'Категория: {category.title}',
        'breadcrumbs': [
            {'title': 'База знаний', 'url': '/knowledge-base/'},
            {'title': category.title, 'url': ''}
        ]
    }
    return render(request, 'knowledge_base/category.html', context)

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    # Увеличиваем просмотры
    article.views += 1
    article.save(update_fields=['views'])
    
    context = {
        'article': article,
        'title': article.title,
        'breadcrumbs': [
            {'title': 'База знаний', 'url': '/knowledge-base/'},
            {'title': article.category.title, 'url': article.category.get_absolute_url()},
            {'title': article.title, 'url': ''}
        ]
    }
    return render(request, 'knowledge_base/article.html', context)
