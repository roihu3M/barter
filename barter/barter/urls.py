"""
URL configuration for barter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from ads.views import Register, create, search, index, viewad, edit, delete, logout
from ads.views import make_offer, offers_list, pending_offers, offer, offer_accept, offer_decline

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', Register.as_view(), name='register'),
    path('create/', create, name='create'),
    path('create/success/', TemplateView.as_view(template_name='create_success.html'), name='create_success'),
    path('search/', search, name='search'),
    path('ad/<int:ad_id>/', viewad, name='viewad'),
    path('ad/<int:ad_id>/edit/', edit, name='edit'),
    path('ad/<int:ad_id>/delete/', delete, name='delete'),
    path('ad/<int:ad_id>/make_offer/', make_offer, name='make_offer'),
    path('offers_list/', offers_list, name='offers_list'),
    path('pending_offers/', pending_offers, name='pending_offers'),
    path('offer/<int:offer_id>/', offer, name='offer'),
    path('offer/<int:offer_id>/accept/', offer_accept, name='offer_accept'),
    path('offer/<int:offer_id>/decline/', offer_decline, name='offer_decline'),
    path('logout/', logout, name='logout')
]
