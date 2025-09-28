from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from vendors.models import Vendor
import time
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    sku = models.CharField(max_length=50, unique=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    track_inventory = models.BooleanField(default=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True)
    is_digital = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.vendor.store_name}")
            self.slug = self._generate_unique_slug(base_slug)
        if not self.sku:
            # make a unique sku using timestamp and random stuff
            timestamp = int(time.time())
            random_part = str(uuid.uuid4())[:8]
            vendor_prefix = str(self.vendor.id).zfill(3)
            self.sku = f"{vendor_prefix}-{timestamp}-{random_part}"
        super().save(*args, **kwargs)

    def _generate_unique_slug(self, base_slug):
        """make sure slug is unique by adding numbers if needed"""
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0

    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0

    @property
    def average_rating(self):
        """Calculate average rating from all approved reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return round(total_rating / reviews.count(), 1)
        return 0

    @property
    def total_reviews(self):
        """Count of all approved reviews"""
        return self.reviews.filter(is_approved=True).count()

    @property
    def verified_reviews_count(self):
        """Count of verified purchase reviews only"""
        return self.reviews.filter(is_approved=True, is_verified=True).count()

    def get_reviews_by_rating(self, rating):
        """Get reviews filtered by specific rating"""
        return self.reviews.filter(is_approved=True, rating=rating)

    class Meta:
        ordering = ['-created_at']

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"

    class Meta:
        ordering = ['order']

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku_suffix = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"

    class Meta:
        unique_together = ['product', 'name', 'value']


class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_verified = models.BooleanField(default=False, help_text="Verified if user has purchased this product")
    is_approved = models.BooleanField(default=True, help_text="Admin approval for content moderation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Check if user has purchased this product to set verification status
        if not self.pk:  # Only check on creation
            from orders.models import OrderItem
            has_purchased = OrderItem.objects.filter(
                order__user=self.user,
                product=self.product,
                order__status__in=['delivered', 'completed']
            ).exists()
            self.is_verified = has_purchased
        super().save(*args, **kwargs)

    def __str__(self):
        verified_status = "✓ Verified" if self.is_verified else "Unverified"
        return f"{self.product.name} - {self.rating}★ by {self.user.username} ({verified_status})"

    @property
    def is_verified_purchase(self):
        """Check if this review is from a verified purchase"""
        return self.is_verified

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'product']  # Ensure one review per user per product
