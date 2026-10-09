from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drug_app_core import views  # ۱. اضافه کردن این خط برای دسترسی به ویوهای اپلیکیشن

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', views.logout_view, name='logout'),  # ۲. اضافه کردن مسیر خروج اینجا
    path('', include('drug_app_core.urls')),
]

# اضافه کردن این بخش برای نمایش عکس‌ها در حالت لوکال و توسعه
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)