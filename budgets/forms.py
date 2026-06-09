from django import forms
from .models import Budget
from transactions.models import Category

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'month': forms.Select(attrs={'class': 'form-select'}, choices=[(i, f'{i:02d}') for i in range(1, 13)]),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        from django.utils import timezone
        now = timezone.now()
        self.fields['month'].initial = now.month
        self.fields['year'].initial = now.year
