import json

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users import models as usermodels

from . import models
from .models import Cart, Cart_membership, Category, Order, Product
from .serializers import (
    CartSerializer,
    CategorySerializer,
    OrderSerializer,
    ProductSerializer,
    ProductSerializerResponse,
)


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serialized = ProductSerializerResponse(queryset, many=True)

        return Response(data=serialized.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        serialized = ProductSerializer(data=request.data, many=True)
        if serialized.is_valid():
            serialized.save()
            return Response(data=serialized.data, status=status.HTTP_200_OK)

        return Response(data=serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):

        models.Product.objects.filter(id__in=request.data["products"]).delete()

        return Response(data=request.data, status=status.HTTP_200_OK)


class Product(generics.RetrieveAPIView):
    lookup_field = "slug"
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryItemView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return models.Product.objects.filter(
            category__in=Category.objects.get(slug=self.kwargs["slug"]).get_descendants(include_self=True)
        )


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(level=1)
    serializer_class = CategorySerializer


class CartView(APIView):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get(self, request, pk):
        try:
            cart = Cart.objects.get(user=self.kwargs["pk"])
        except Cart.DoesNotExist:
            return Response(data={"err": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        serialized = CartSerializer(cart)
        return Response(data=serialized.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        productid = request.GET.get("productid", "")
        quantity = request.GET.get("quantity", "1")
        userid = self.kwargs["pk"]

        cart = Cart.objects.get(user=userid)
        product = models.Product.objects.get(productid=productid)
        price = product.discount_price * int(quantity)
        cart_membership = Cart_membership(cart=cart, product=product, quantity=quantity, price=price)

        cart_membership.save()
        return Response(data=productid, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        userid = self.kwargs["pk"]
        productid = request.GET.get("productid", "")
        cart = Cart.objects.get(user=userid)
        cart.products.remove(models.Product.objects.get(productid=productid))
        return Response(data=request.data, status=status.HTTP_200_OK)


class OrderView(APIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def post(self, request, *args, **kwargs):

        userid = self.kwargs["pk"]
        user = usermodels.NewUser.objects.get(id=userid)
        payment_type = request.GET.get("payment_type", "COD")
        cart = Cart.objects.get(user=userid)

        totalcost = 0

        for product in cart.products.all():

            cart_membership = Cart_membership.objects.get(product=product)

            totalcost = totalcost + cart_membership.price

        order = Order(user=user, totalcost=totalcost, payment_type=payment_type)

        order.save()

        for product in cart.products.all():

            order.products.add(product)

        order.save()

        return Response(data=request.data, status=status.HTTP_200_OK)
