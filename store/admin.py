from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from users.models import NewUser

from .models import (
    Cart,
    Cart_membership,
    Category,
    Order,
    Product,
    ProductImage,
    ProductSpecification,
    ProductSpecificationValue,
    ProductType,
)

admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Cart_membership)


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationInline,
    ]


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class ProductSpecificationValueInline(admin.TabularInline):
    model = ProductSpecificationValue


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationValueInline,
        ProductImageInline,
    ]

    list_display = ["title", "productid"]


class CartInline(admin.TabularInline):
    model = Cart


@admin.register(NewUser)
class UserAdmin(admin.ModelAdmin):
    inlines = [CartInline]
