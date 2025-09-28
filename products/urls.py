from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='list'),
    path('create/', views.ProductCreateView.as_view(), name='create'),
    path('my-products/', views.VendorProductListView.as_view(), name='vendor_list'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='update'),
    path('<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='delete'),
    path('<slug:slug>/reviews/', views.ProductReviewsView.as_view(), name='reviews'),
    path('<slug:slug>/review/add/', views.ReviewCreateView.as_view(), name='review_add'),
    path('review/<int:review_id>/edit/', views.ReviewUpdateView.as_view(), name='review_edit'),
    path('review/<int:review_id>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category'),
]