from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('', views.VendorListView.as_view(), name='list'),
    path('<int:pk>/', views.VendorDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.VendorUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.VendorDeleteView.as_view(), name='delete'),
    path('dashboard/', views.VendorDashboardView.as_view(), name='dashboard'),
    path('register/', views.VendorRegisterView.as_view(), name='register'),
]