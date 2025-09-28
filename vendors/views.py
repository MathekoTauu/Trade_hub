from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib import messages
from django.db.models import Count, Avg, Sum
from django.urls import reverse_lazy
from products.models import Product, Review
from orders.models import OrderItem
from core.twitter_utils import post_to_twitter, generate_new_vendor_tweet
from .models import Vendor

class VendorListView(ListView):
    model = Vendor
    template_name = 'vendors/list.html'
    context_object_name = 'vendors'
    paginate_by = 20
    
    def get_queryset(self):
        # Show all vendors, not just verified ones for better user experience
        return Vendor.objects.all().order_by('-created_at')

class VendorDetailView(DetailView):
    model = Vendor
    template_name = 'vendors/detail.html'
    context_object_name = 'vendor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.object
        
        # Get vendor products and stats
        vendor_products = Product.objects.filter(vendor=vendor, is_active=True)
        context['vendor_products'] = vendor_products[:12]  # Show latest 12 products
        context['vendor_products_count'] = vendor_products.count()
        
        # Get categories with product counts for this vendor
        categories = vendor_products.values(
            'category__name', 'category__slug'
        ).annotate(
            product_count=Count('id')
        ).order_by('-product_count')
        context['vendor_categories'] = categories
        
        # Get reviews for vendor's products
        vendor_reviews = Review.objects.filter(
            product__vendor=vendor, 
            is_approved=True
        )
        context['vendor_reviews_count'] = vendor_reviews.count()
        
        # Calculate average rating
        avg_rating = vendor_reviews.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        context['vendor_rating'] = avg_rating if avg_rating else 0
        
        return context

class VendorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'vendors/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is a vendor
        if not hasattr(request.user, 'vendor'):
            messages.error(request, 'You must be a registered vendor to access the dashboard.')
            return redirect('vendors:register')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.request.user.vendor
        
        # Get vendor statistics
        context['vendor'] = vendor
        
        # Get recent orders for vendor's products
        recent_orders = OrderItem.objects.filter(
            product__vendor=vendor
        ).select_related('order', 'product').order_by('-order__created_at')[:10]
        context['recent_orders'] = recent_orders
        
        # Calculate total revenue from completed orders
        total_revenue = OrderItem.objects.filter(
            product__vendor=vendor,
            order__status__in=['delivered', 'completed']
        ).aggregate(total=Sum('total_price'))['total'] or 0
        context['total_revenue'] = total_revenue
        
        # Calculate average rating from all vendor's products
        vendor_reviews = Review.objects.filter(
            product__vendor=vendor,
            is_approved=True
        )
        avg_rating = vendor_reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        context['average_rating'] = avg_rating if avg_rating else 0
        
        return context

class VendorRegisterView(LoginRequiredMixin, CreateView):
    model = Vendor
    template_name = 'vendors/register.html'
    fields = ['store_name', 'store_description', 'store_logo', 'phone', 'address', 'twitter_handle', 'response_time', 'shipping_policy', 'return_policy']
    success_url = '/vendors/dashboard/'
    
    def form_valid(self, form):
        # Check if user already has a vendor account
        if hasattr(self.request.user, 'vendor'):
            messages.error(self.request, 'You already have a vendor store. You can only have one vendor account per user.')
            return self.form_invalid(form)
        
        form.instance.user = self.request.user
        
        # Save the vendor first to get the instance
        response = super().form_valid(form)
        vendor = self.object
        
        # Update user profile to vendor type
        if hasattr(self.request.user, 'profile'):
            profile = self.request.user.profile
            profile.user_type = 'vendor'
            profile.save()
            
            # Add user to Vendors group
            vendors_group, _ = Group.objects.get_or_create(name='Vendors')
            self.request.user.groups.add(vendors_group)
            
            # Remove from Buyers group if present
            buyers_group = Group.objects.filter(name='Buyers').first()
            if buyers_group:
                self.request.user.groups.remove(buyers_group)
        
        # Post to Twitter about the new vendor
        tweet_text = generate_new_vendor_tweet(vendor)
        post_to_twitter(tweet_text)
        
        messages.success(self.request, f'Congratulations! Your vendor store "{form.instance.store_name}" has been created successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if user already has a vendor account
        if hasattr(self.request.user, 'vendor'):
            context['existing_vendor'] = True
        return context


class VendorUpdateView(LoginRequiredMixin, UpdateView):
    model = Vendor
    template_name = 'vendors/update.html'
    fields = ['store_name', 'store_description', 'store_logo', 'phone', 'address', 'twitter_handle', 'response_time', 'shipping_policy', 'return_policy']
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user owns this vendor store
        vendor = self.get_object()
        if vendor.user != request.user:
            messages.error(request, 'You can only edit your own store.')
            return redirect('vendors:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Your store has been updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('vendors:dashboard')


class VendorDeleteView(LoginRequiredMixin, DeleteView):
    model = Vendor
    template_name = 'vendors/delete.html'
    success_url = reverse_lazy('core:home')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user owns this vendor store
        vendor = self.get_object()
        if vendor.user != request.user:
            messages.error(request, 'You can only delete your own store.')
            return redirect('vendors:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        vendor = self.get_object()
        store_name = vendor.store_name
        
        # Remove user from vendors group
        vendors_group = Group.objects.filter(name='Vendors').first()
        if vendors_group:
            request.user.groups.remove(vendors_group)
        
        # Update user profile back to buyer
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            profile.user_type = 'buyer'
            profile.save()
            
            # Add back to buyers group
            buyers_group, _ = Group.objects.get_or_create(name='Buyers')
            request.user.groups.add(buyers_group)
        
        messages.success(request, f'Store "{store_name}" has been deleted successfully.')
        return super().delete(request, *args, **kwargs)
