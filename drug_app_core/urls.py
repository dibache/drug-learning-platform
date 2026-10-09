from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome'),  # صفحه اصلی و خوش‌آمدگویی
    path('dashboard/', views.dashboard, name='dashboard'),  # داشبورد بعد از ورود
    path(
        'module/<int:module_id>/', views.module_detail, name='module_detail'
    ),
    path('flashcards/', views.flashcards_view, name='flashcards'),
    path('ranking/', views.ranking_view, name='ranking'),
    path('login/', views.login_view, name='login'),  # صفحه اختصاصی ورود
    path('register/', views.register_view, name='register'),  # صفحه اختصاصی ثبت‌نام
    path(
        'logout/', auth_views.LogoutView.as_view(next_page='welcome'), name='logout'
    ),
    path('profile/', views.profile_view, name='profile'),
    path('learning/', views.learning_view, name='learning'),
    path('custom-admin/', views.custom_admin_dashboard, name='custom_admin'),
    path(
        'custom-admin/modules/',
        views.admin_modules_view,
        name='admin_modules',
    ),
    path(
        'custom-admin/questions/',
        views.admin_questions_view,
        name='admin_questions',
    ),
    path('custom-admin/users/', views.admin_users_view, name='admin_users'),
    path('custom-admin/flashcards/', views.admin_flashcards_view, name='admin_flashcards'),
]