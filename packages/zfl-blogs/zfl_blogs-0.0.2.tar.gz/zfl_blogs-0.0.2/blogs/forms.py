from django import forms  # type: ignore
from .models import Blog

from markdownx.widgets import MarkdownxWidget  # type: ignore


class BlogForm(forms.ModelForm):
    """
    Blog作成自作フォームの作成

    """
    
    class Meta:
        model = Blog
        fields = ('category', 'title', 'text', 'is_publick')
        widgets = {
                'category': forms.Select(attrs={
                    'class': 'form-control',
                    'placeholder': 'カテゴリー',
                }),
                'title': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'タイトル',
                }),
                'text': MarkdownxWidget(attrs={
                    'class': 'form-control',
                    'placeholder': 'ブログ内容を入力',
                }),
                'is_publick': forms.RadioSelect,
        }

