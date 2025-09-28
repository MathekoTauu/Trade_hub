from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=200)
    store_description = models.TextField(blank=True)
    store_logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    twitter_handle = models.CharField(max_length=50, blank=True, help_text="Twitter username without @")
    response_time = models.CharField(max_length=100, blank=True, default="Usually responds within 24 hours")
    shipping_policy = models.TextField(blank=True, default="Standard shipping rates apply")
    return_policy = models.TextField(blank=True, default="30-day return policy")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.store_name

    def get_absolute_url(self):
        return reverse('vendors:detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']

class VendorProfile(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    business_license = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    bank_account = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.vendor.store_name} Profile"
