from django import forms
from .models import ArticlePost

class ArticlePostForms(forms.ModelForm):
    class Meta:
        model = ArticlePost
        fields = ('title', 'body','tags','avatar')