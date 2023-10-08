from django.contrib import admin

from .models import Category, Product


class CategoryAdmin(admin.ModelAdmin):
    ...


class ProductAdmin(admin.ModelAdmin):
    ...


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
