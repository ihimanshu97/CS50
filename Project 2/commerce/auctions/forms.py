from django import forms
from auctions.models import *

class NewListing(forms.Form):
    title = forms.CharField(max_length=150)
    description = forms.CharField(widget=forms.Textarea)
    current_price = forms.IntegerField(min_value=1)
    image = forms.URLField()
    category = forms.ModelChoiceField(queryset=Category.objects.all())

class NewComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]