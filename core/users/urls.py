from django.urls import path

from .views import LoginView, LogoutView, ProfileView, RegisterView, edit_photo, ChangeProfileView

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('edit_photo/edit', edit_photo, name='edit_photo'),
    path('edit_prof/<int:pk>/edit', ChangeProfileView.as_view(), name='edit_prof'),

]