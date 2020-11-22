from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.views.generic import FormView, TemplateView, RedirectView, UpdateView
from django.urls import reverse_lazy


from .models import Users
from .forms import RegisterUserForm, PhotoForm


class LoginView(FormView):
    """Вход на сайт"""
    form_class = AuthenticationForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('users:profile')


class LogoutView(RedirectView):
    """Выход"""
    pattern_name = 'users:login'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return super().get_redirect_url(*args, **kwargs)


class ProfileView(TemplateView):
    """Личный кабинет"""
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        pk = user.pk
        adv_qs = Users.objects.get(pk=pk)
        context['usersI'] = adv_qs
        return context



class RegisterView(FormView):
    """Регистрация на сайте"""
    template_name = 'users/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super().form_valid(form)


def edit_photo(request):
    if request.method == 'POST':
        photo_form = PhotoForm(instance=request.user, data=request.POST, files=request.FILES)
        if photo_form.is_valid():
            photo_form.save()
            return redirect('users:profile')
    else:
        photo_form = PhotoForm(instance=request.user)
    return render(request, 'users/photo_update_form.html', {'photo_form': photo_form})


def edit_profile(request):
    pass

class ChangeProfileView(UpdateView):
    """Редактирование имени пользователя"""
    model = Users
    template_name = 'users/prof_update_form.html'
    fields = ['first_name', 'last_name', 'birth_date', 'description']