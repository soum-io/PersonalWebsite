from django.contrib import admin
from django.urls import path

from landing import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('video/<video_id>', views.video_detail, name='video-detail'),
    path('contact/', views.contact, name='contact'),
]
