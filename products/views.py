from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from core.twitter_utils import post_to_twitter, generate_new_product_tweet
from .models import Product, Category, Review, ProductImage
from .forms import ReviewForm, ProductForm

class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:4]
        
        # Add review-related context
        reviews = self.object.reviews.filter(is_approved=True).order_by('-created_at')
        context['reviews'] = reviews[:10]  # Show first 10 reviews
        context['total_reviews'] = reviews.count()
        context['average_rating'] = self.object.average_rating
        context['verified_reviews_count'] = self.object.verified_reviews_count
        
        # Check if current user can write a review
        if self.request.user.is_authenticated:
            user_review = reviews.filter(user=self.request.user).first()
            context['user_review'] = user_review
            context['can_review'] = user_review is None  # User can review if they haven't already
            
            # Check if user has purchased this product (for verification info)
            from orders.models import OrderItem
            has_purchased = OrderItem.objects.filter(
                order__user=self.request.user,
                product=self.object,
                order__status__in=['delivered', 'completed']
            ).exists()
            context['user_has_purchased'] = has_purchased
            
            context['review_form'] = ReviewForm() if context['can_review'] else None
        
        # Create rating distribution for display
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[i] = reviews.filter(rating=i).count()
        context['rating_distribution'] = rating_distribution
        
        return context
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[i] = self.object.get_reviews_by_rating(i).count()
        context['rating_distribution'] = rating_distribution
        
        return context

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'products/category.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.filter(is_active=True)
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'products/create.html'
    form_class = ProductForm
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is a vendor
        if not hasattr(request.user, 'vendor'):
            messages.error(request, 'You must be a registered vendor to add products.')
            return redirect('vendors:register')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Process valid form - assign the vendor automatically and handle image uploads"""
        # Save the product first
        form.instance.vendor = self.request.user.vendor
        response = super().form_valid(form)
        
        # Handle individual image uploads
        image_count = 0
        for i, field_name in enumerate(['image1', 'image2', 'image3']):
            image_file = form.cleaned_data.get(field_name)
            if image_file:
                ProductImage.objects.create(
                    product=self.object,
                    image=image_file,
                    is_primary=(i == 0 and image_count == 0)  # First uploaded image is primary
                )
                image_count += 1
        
        # Post to Twitter about the new product
        tweet_text = generate_new_product_tweet(self.object)
        post_to_twitter(tweet_text)
        
        if image_count > 0:
            messages.success(self.request, f'Product created successfully with {image_count} image(s)!')
        else:
            messages.success(self.request, 'Product created successfully!')
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('vendors:dashboard')


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'products/update.html'
    fields = ['name', 'description', 'short_description', 'price', 'category', 'condition', 'stock_quantity', 'is_featured', 'is_active']
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user owns this product
        product = self.get_object()
        if not hasattr(request.user, 'vendor') or product.vendor != request.user.vendor:
            messages.error(request, 'You can only edit your own products.')
            return redirect('vendors:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('vendors:dashboard')


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user owns this product
        product = self.get_object()
        if not hasattr(request.user, 'vendor') or product.vendor != request.user.vendor:
            messages.error(request, 'You can only delete your own products.')
            return redirect('vendors:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('vendors:dashboard')


class VendorProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/vendor_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        # I check if user is a vendor
        if not hasattr(request.user, 'vendor'):
            messages.error(request, 'You must be a registered vendor to manage products.')
            return redirect('vendors:register')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user.vendor).order_by('-created_at')


# My Review Management Views
class ReviewCreateView(LoginRequiredMixin, View):
    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        
        # I check if user already reviewed this product
        existing_review = Review.objects.filter(user=request.user, product=product).first()
        if existing_review:
            messages.error(request, 'You have already reviewed this product.')
            return redirect('products:detail', slug=product.slug)
        
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            
            verification_text = " (Verified Purchase)" if review.is_verified else ""
            messages.success(request, f'Your review has been submitted{verification_text}!')
        else:
            messages.error(request, 'Please correct the errors in your review.')
        
        return redirect('products:detail', slug=product.slug)


class ReviewUpdateView(LoginRequiredMixin, View):
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user)
        
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been updated successfully!')
        else:
            messages.error(request, 'Please correct the errors in your review.')
        
        return redirect('products:detail', slug=review.product.slug)


class ReviewDeleteView(LoginRequiredMixin, View):
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user)
        product_slug = review.product.slug
        review.delete()
        messages.success(request, 'Your review has been deleted.')
        return redirect('products:detail', slug=product_slug)


class ProductReviewsView(ListView):
    model = Review
    template_name = 'products/reviews.html'
    context_object_name = 'reviews'
    paginate_by = 20
    
    def get_queryset(self):
        self.product = get_object_or_404(Product, slug=self.kwargs['slug'], is_active=True)
        return self.product.reviews.filter(is_approved=True).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        context['average_rating'] = self.product.average_rating
        context['total_reviews'] = self.product.total_reviews
        context['verified_reviews_count'] = self.product.verified_reviews_count
        
        # I create rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[i] = self.product.get_reviews_by_rating(i).count()
        context['rating_distribution'] = rating_distribution
        
        return context
