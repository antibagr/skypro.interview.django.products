from django.contrib import admin

from .models import Cart, CartItem, Customer


class CustomerAdmin(admin.ModelAdmin):
    ...


class CartAdmin(admin.ModelAdmin):
    ...


class CartItemAdmin(admin.ModelAdmin):
    ...


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
