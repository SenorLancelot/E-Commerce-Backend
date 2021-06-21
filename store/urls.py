from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("api/products/", views.ProductListView.as_view(), name="store_home"),
    path("api/category/", views.CategoryListView.as_view(), name="categories"),
    path("api/products/<slug:slug>/", views.Product.as_view(), name="product"),
    path("api/category/<slug:slug>/", views.CategoryItemView.as_view(), name="category_item"),
    path("api/<int:pk>/cart/", views.CartView.as_view(), name="cart"),
    path("api/<int:pk>/order/", views.OrderView.as_view(), name="order"),
]
