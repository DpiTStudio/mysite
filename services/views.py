from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from .models import Service, ServiceOrder
from .forms import ServiceOrderForm

class ServiceListView(ListView):
    model = Service
    template_name = 'services/list.html'
    context_object_name = 'services'
    queryset = Service.objects.filter(is_active=True).order_by('order')

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
        return context

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
            messages.success(request, f"Ваш заказ на услугу '{service.title}' успешно оформлен! Вы можете отслеживать его в личном кабинете.")
            return redirect('services:detail', slug=slug)
        else:
            messages.error(request, "Ошибка при оформлении заказа. Проверьте введенные данные.")
            return render(request, 'services/detail.html', {'service': service, 'form': form})