from django.contrib import admin

from .models import Category, Location, Post
# Register your models here.


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'description',
        'slug',
        'is_published'
    )
    list_editable = (
        'is_published',
    )

    search_fields = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'name',
    )
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'is_published',
        'created_at',
        'author',
        'location',
        'category'
    )
    list_editable = (
        'is_published',
        'text'
    )
    search_fields = ('title',)
    list_filter = ('category', 'location', 'author')
    list_display_links = ('title',)


admin.site.empty_value_display = 'Не задано'
