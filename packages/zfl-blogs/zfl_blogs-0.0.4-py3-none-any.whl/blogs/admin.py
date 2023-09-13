from django.contrib import admin
from .models import Category, Blog
from markdownx.admin import MarkdownxModelAdmin
from django.db import models
from markdownx.widgets import AdminMarkdownxWidget


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')

class BlogAdmin(admin.ModelAdmin):
    formfield_overrides = {
            models.TextField: {'widget': AdminMarkdownxWidget},
    }


admin.site.register(Category, CategoryAdmin)
admin.site.register(Blog, BlogAdmin)
# admin.site.register(Popular)
