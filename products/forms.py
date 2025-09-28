from django import forms
from .models import Review, Product, ProductImage

FORM_CONTROL_CLASS = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'


class ProductForm(forms.ModelForm):
    """Form for creating and updating products with image upload support"""
    image1 = forms.ImageField(
        required=False,
        help_text="Primary product image (recommended)",
        widget=forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'accept': 'image/*'
        })
    )
    image2 = forms.ImageField(
        required=False,
        help_text="Additional product image (optional)",
        widget=forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'accept': 'image/*'
        })
    )
    image3 = forms.ImageField(
        required=False,
        help_text="Additional product image (optional)",
        widget=forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'short_description', 'price', 'compare_price',
            'category', 'condition', 'stock_quantity', 'track_inventory', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'placeholder': 'Enter product name'
            }),
            'description': forms.Textarea(attrs={
                'class': FORM_CONTROL_CLASS,
                'rows': 5,
                'placeholder': 'Detailed product description'
            }),
            'short_description': forms.TextInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'placeholder': 'Brief product summary (optional)'
            }),
            'price': forms.NumberInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'compare_price': forms.NumberInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00 (optional)'
            }),
            'category': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
            'condition': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
            'stock_quantity': forms.NumberInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'min': '0',
                'placeholder': '0'
            }),
            'track_inventory': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make compare_price not required
        self.fields['compare_price'].required = False
        self.fields['short_description'].required = False


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=Review.RATING_CHOICES,
                attrs={'class': FORM_CONTROL_CLASS}
            ),
            'title': forms.TextInput(
                attrs={
                    'class': FORM_CONTROL_CLASS,
                    'placeholder': 'Brief summary of your review (optional)'
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': FORM_CONTROL_CLASS,
                    'rows': 4,
                    'placeholder': 'Share your experience with this product...'
                }
            ),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].empty_label = 'Select a rating'
        self.fields['title'].required = False