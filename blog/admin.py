from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Post, Tag


class PostAdmin(admin.ModelAdmin):
    list_filter = ('author', 'date')
    list_display = ('title', 'date', 'author')
    readonly_fields = ['content_preview', 'date']
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag)