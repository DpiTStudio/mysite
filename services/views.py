from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from django.db.models import Q, F, Count


from .models import Service, ServiceCategory, Technology

from .forms import ServiceOrderForm


def _build_service_detail_context(service, form=None, user=None, initial_plan_id=None):
    """Формирует полный контекст для лендинга услуги."""
    available_plans = service.price_plans.filter(is_available_for_order=True).order_by('order')
    
    if form is None:
        initial_data = {}
        if user and user.is_authenticated:
            full_name = f"{user.first_name} {user.last_name}".strip() or user.username
            initial_data.update({
                'full_name': full_name,
                'email': user.email,
                'phone': getattr(user, 'phone', ''),
            })
        if initial_plan_id:
            try:
                plan_pk = int(initial_plan_id)
                if available_plans.filter(pk=plan_pk).exists():
                    initial_data['selected_plan'] = plan_pk
            except (ValueError, TypeError):
                pass
                
        form = ServiceOrderForm(initial=initial_data)

    form.fields['selected_plan'].queryset = available_plans

    related_services = Service.objects.none()
    if service.category:
        related_services = Service.objects.filter(
            is_active=True,
            category=service.category
        ).exclude(pk=service.pk).order_by('?')[:4]

    return {
        'service': service,
        'form': form,
        'related_services': related_services,
        'related_portfolio': service.related_portfolio.filter(is_active=True),
        'benefits': service.benefits.all().order_by('order'),
        'steps': service.steps.all().order_by('step_number', 'order'),
        'faqs': service.faqs.all().order_by('order'),
        'price_plans': service.price_plans.all().order_by('order'),
        'tech_list': service.get_tech_requirements_display(),
    }


class ServiceListView(ListView):
    """
    Отображает список всех доступных услуг с возможностью фильтрации
    по категории, сложности, ключевым словам и используемым технологиям.
    Оптимизирован для эффективной выборки из БД.
    """
    model = Service
    template_name = 'services/list.html'
    context_object_name = 'services'
    paginate_by = 12
    
    def get_queryset(self):
        """Возвращает отфильтрованный набор данных услуг с оптимизацией ORM-запросов"""
        queryset = Service.objects.filter(is_active=True).select_related('category').prefetch_related('technologies').order_by('order', 'title')
        
        # 1. Фильтр по категории
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # 2. Фильтр по сложности
        complexity = self.request.GET.get('complexity')
        if complexity:
            queryset = queryset.filter(complexity_level=complexity)

        # 3. Фильтр по технологии
        tech_param = self.request.GET.get('tech')
        if tech_param:
            if tech_param.isdigit():
                queryset = queryset.filter(technologies__id=tech_param)
            else:
                queryset = queryset.filter(technologies__name__iexact=tech_param)

        # 4. Фильтр по поисковому запросу
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(short_description__icontains=q) |
                Q(description__icontains=q) |
                Q(technologies__name__icontains=q) |
                Q(category__name__icontains=q)
            ).distinct()

        # 5. Сортировка
        sort_param = self.request.GET.get('sort')
        if sort_param == 'price_asc':
            queryset = queryset.order_by('price_fixed', 'price_min', 'order')
        elif sort_param == 'price_desc':
            queryset = queryset.order_by('-price_fixed', '-price_max', 'order')
        elif sort_param == 'views_desc':
            queryset = queryset.order_by('-views', 'order')
        elif sort_param == 'popular':
            queryset = queryset.order_by('-is_popular', 'order')
        elif sort_param == 'title':
            queryset = queryset.order_by('title')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Добавляет в контекст аннотированные категории, технологии и активные фильтры"""
        context = super().get_context_data(**kwargs)
        
        # Категории с подсчетом активных услуг в одной агрегированной выборке
        categories = (
            ServiceCategory.objects
            .filter(is_active=True)
            .annotate(service_count=Count('services', filter=Q(services__is_active=True)))
            .order_by('order', 'name')
        )
        
        total_services_count = Service.objects.filter(is_active=True).count()
        
        # Выбранная категория для хлебных крошек/заголовка
        category_id = self.request.GET.get('category')
        selected_category = None
        if category_id and category_id.isdigit():
            selected_category = categories.filter(pk=category_id).first()

        # Список активных технологий для быстрой фильтрации
        technologies = Technology.objects.filter(services__is_active=True).distinct().order_by('name')

        # Флаг наличия активных фильтров для кнопки сброса
        active_complexity = self.request.GET.get('complexity')
        active_tech = self.request.GET.get('tech')
        search_query = self.request.GET.get('q', '').strip()
        current_sort = self.request.GET.get('sort', '')
        
        has_active_filters = bool(category_id or active_complexity or active_tech or search_query or current_sort)

        # Подготовка понятных метаданных для выбранной сложности, технологии и сортировки
        complexity_dict = dict(Service.COMPLEXITY_CHOICES)
        selected_complexity_label = complexity_dict.get(active_complexity, '') if active_complexity else ''
        
        sort_labels = {
            'price_asc': 'Сначала дешевле',
            'price_desc': 'Сначала дороже',
            'views_desc': 'Популярные (по просмотрам)',
            'title': 'По алфавиту',
        }
        selected_sort_label = sort_labels.get(current_sort, '')

        selected_tech_obj = None
        if active_tech:
            if active_tech.isdigit():
                selected_tech_obj = technologies.filter(pk=active_tech).first()
            else:
                selected_tech_obj = technologies.filter(name__iexact=active_tech).first()

        context.update({
            'service_categories': categories,
            'total_services_count': total_services_count,
            'selected_category': selected_category,
            'technologies': technologies,
            'complexity_choices': Service.COMPLEXITY_CHOICES,
            'selected_complexity': active_complexity,
            'selected_complexity_label': selected_complexity_label,
            'selected_tech': active_tech,
            'selected_tech_obj': selected_tech_obj,
            'current_sort': current_sort,
            'selected_sort_label': selected_sort_label,
            'search_query': search_query,
            'has_active_filters': has_active_filters,
            'popular_services': Service.objects.filter(
                is_active=True, 
                is_popular=True
            ).select_related('category').prefetch_related('technologies').order_by('order')[:6]
        })
        
        return context



class ServiceDetailView(DetailView):
    """
    Отображает развернутую информацию об услуге, 
    предоставляет форму заказа и выводит похожие услуги.
    """
    model = Service
    template_name = 'services/detail.html'
    context_object_name = 'service'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs
    
    def get_context_data(self, **kwargs):
        """Подготавливает контекст: форма заказа и похожие услуги"""
        context = super().get_context_data(**kwargs)
        initial_plan_id = self.request.GET.get('plan')
        detail_context = _build_service_detail_context(
            service=self.object,
            user=self.request.user,
            initial_plan_id=initial_plan_id
        )
        context.update(detail_context)
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

        if not service.can_be_ordered:
            messages.error(request, "❌ К сожалению, эта услуга в данный момент недоступна для заказа.")
            return redirect('services:detail', slug=slug)

        form = ServiceOrderForm(request.POST)
        form.fields['selected_plan'].queryset = service.price_plans.filter(is_available_for_order=True)

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
        
        context = _build_service_detail_context(service=service, form=form, user=request.user)
        return render(request, 'services/detail.html', context)



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
                Q(category__name__icontains=query)
            ).distinct()

            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        context['query'] = query
        context['results_count'] = self.get_queryset().count()
        
        return context

