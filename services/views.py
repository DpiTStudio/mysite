from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from django.db.models import Q, F


from .models import Service
from .forms import ServiceOrderForm


class ServiceListView(ListView):
    """
    Отображает список всех доступных услуг с возможностью фильтрации
    по категории, сложности и используемым технологиям.
    """
    model = Service
    template_name = 'services/list.html'
    context_object_name = 'services'
    paginate_by = 12
    
    def get_queryset(self):
        """Возвращает отфильтрованный набор данных услуг"""
        queryset = Service.objects.filter(is_active=True).order_by('order')
        
        filters = {
            'category__icontains': self.request.GET.get('category'),
            'complexity_level': self.request.GET.get('complexity'),
            'technologies__name__icontains': self.request.GET.get('tech'),
        }
        
        # Применяем только те фильтры, значения которых были переданы
        active_filters = {k: v for k, v in filters.items() if v}
        if active_filters:
            queryset = queryset.filter(**active_filters)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Добавляет в контекст категории и блок популярных услуг для правой панели/фильтров"""
        context = super().get_context_data(**kwargs)
        
        context['service_categories'] = (
            Service.objects
            .filter(is_active=True)
            .exclude(category='')
            .values_list('category', flat=True)
            .distinct()
        )
        
        context['popular_services'] = Service.objects.filter(
            is_active=True, 
            is_popular=True
        ).order_by('order')[:6]
        
        return context


class ServiceDetailView(DetailView):
    """
    Отображает развернутую информацию об услуге, 
    предоставляет форму заказа и выводит похожие услуги.
    """
    model = Service
    template_name = 'services/detail.html'
    context_object_name = 'service'
    
    def get_context_data(self, **kwargs):
        """Подготавливает контекст: форма заказа и похожие услуги"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        initial_data = {}
        
        # Предзаполняем поля, если пользователь авторизован
        if user.is_authenticated:
            full_name = f"{user.first_name} {user.last_name}".strip() or user.username
            initial_data.update({
                'full_name': full_name,
                'email': user.email,
                'phone': getattr(user, 'phone', ''),
            })
        
        context['form'] = ServiceOrderForm(initial=initial_data)
        
        # Похожие услуги из той же категории
        if self.object.category:
            context['related_services'] = Service.objects.filter(
                is_active=True,
                category=self.object.category
            ).exclude(pk=self.object.pk).order_by('?')[:4]
        else:
            context['related_services'] = Service.objects.none()
        
        context['tech_list'] = self.object.get_tech_requirements_display()
        return context
    
    def get(self, request, *args, **kwargs):
        """Увеличиваем счетчик просмотров при каждом GET-запросе"""
        self.object = self.get_object()
        
        # Используем F() для атомарного обновления счетчика минуя состояние гонки
        Service.objects.filter(pk=self.object.pk).update(views=F('views') + 1)
        self.object.refresh_from_db(fields=['views'])
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ServiceOrderView(View):
    """
    Обрабатывает POST запрос формы заказа услуги.
    """
    def post(self, request, slug):
        service = get_object_or_404(Service, slug=slug)
        form = ServiceOrderForm(request.POST)
        
        if form.is_valid():
            order = form.save(commit=False)
            order.service = service
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            
            messages.success(
                request, 
                f"✅ Заказ на «{service.title}» успешно оформлен! "
                f"Ваш номер заказа: {order.short_id}. Ожидайте звонка менеджера."
            )
            return redirect('services:detail', slug=slug)
            
        messages.error(
            request, 
            "❌ Возникла ошибка при оформлении заказа. Пожалуйста, проверьте корректность данных."
        )
        
        related_services = Service.objects.none()
        if service.category:
            related_services = Service.objects.filter(
                is_active=True, category=service.category
            ).exclude(pk=service.pk).order_by('?')[:4]
            
        return render(request, 'services/detail.html', {
            'service': service, 
            'form': form,
            'related_services': related_services,
            'tech_list': service.get_tech_requirements_display()
        })


class ServiceSearchView(ListView):
    """
    Представление для поиска по каталогу услуг.
    Использует ListView для встроенной пагинации.
    """
    model = Service
    template_name = 'services/search.html'
    context_object_name = 'services'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        queryset = Service.objects.filter(is_active=True)
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(short_description__icontains=query) |
                Q(description__icontains=query) |
                Q(technologies__name__icontains=query) |
                Q(category__icontains=query)
            ).distinct()
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        context['query'] = query
        context['results_count'] = self.get_queryset().count()
        
        return context

