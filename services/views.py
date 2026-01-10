# views.py - Улучшенная версия
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib import messages
from django.db.models import Q
from django.db import models
from django.core.paginator import Paginator
from .models import Service, ServiceOrder
from .forms import ServiceOrderForm

class ServiceListView(ListView):
    model = Service
    template_name = 'services/list.html'
    context_object_name = 'services'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True).order_by('order')
        
        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        # Фильтрация по уровню сложности
        complexity = self.request.GET.get('complexity')
        if complexity:
            queryset = queryset.filter(complexity_level=complexity)
        
        # Поиск по технологиям
        tech = self.request.GET.get('tech')
        if tech:
            queryset = queryset.filter(technical_requirements__icontains=tech)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем уникальные категории для фильтра
        context['service_categories'] = Service.objects.filter(
            is_active=True
        ).values_list('category', flat=True).distinct()
        
        # Считаем популярные услуги
        context['popular_services'] = Service.objects.filter(
            is_active=True, 
            is_popular=True
        )[:6]
        
        return context


class ServiceDetailView(DetailView):
    model = Service
    template_name = 'services/detail.html'
    context_object_name = 'service'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pre-fill form if user is authenticated
        initial = {}
        if self.request.user.is_authenticated:
            # Try to get full name, fallback to username
            full_name = f"{self.request.user.first_name} {self.request.user.last_name}".strip()
            if not full_name:
                full_name = self.request.user.username
            
            initial['full_name'] = full_name
            initial['email'] = self.request.user.email
            initial['phone'] = getattr(self.request.user, 'phone', '')
        
        context['form'] = ServiceOrderForm(initial=initial)
        
        # Получаем похожие услуги
        context['related_services'] = Service.objects.filter(
            is_active=True,
            category=self.object.category
        ).exclude(pk=self.object.pk)[:4]
        
        # Преобразуем технические требования в список
        context['tech_list'] = self.object.get_tech_requirements_display()
        
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Увеличиваем счетчик просмотров
        self.object.views = models.F('views') + 1
        self.object.save(update_fields=['views'])
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ServiceOrderView(View):
    def post(self, request, slug):
        service = get_object_or_404(Service, slug=slug)
        form = ServiceOrderForm(request.POST)
        
        if form.is_valid():
            order = form.save(commit=False)
            order.service = service
            
            if request.user.is_authenticated:
                order.user = request.user
            
            order.save()
            
            # Отправка уведомлений (если настроена система уведомлений)
            self.send_notifications(order)
            
            messages.success(
                request, 
                f"✅ Ваш заказ на услугу '{service.title}' успешно оформлен! "
                f"Номер заказа: {order.short_id}. "
                "С вами свяжутся в ближайшее время."
            )
            
            return redirect('services:detail', slug=slug)
        else:
            messages.error(
                request, 
                "❌ Ошибка при оформлении заказа. Пожалуйста, проверьте введенные данные."
            )
            return render(
                request, 
                'services/detail.html', 
                {'service': service, 'form': form}
            )
    
    def send_notifications(self, order):
        """Отправка уведомлений о новом заказе"""
        # Здесь можно добавить отправку email или уведомлений
        # Например, через Django signals или Celery
        pass


class ServiceSearchView(TemplateView):
    template_name = 'services/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        query = self.request.GET.get('q', '')
        services = Service.objects.filter(is_active=True)
        
        if query:
            services = services.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(technical_requirements__icontains=query) |
                Q(category__icontains=query)
            )
        
        # Пагинация
        paginator = Paginator(services, 12)
        page = self.request.GET.get('page')
        context['services'] = paginator.get_page(page)
        context['query'] = query
        context['results_count'] = services.count()
        
        return context