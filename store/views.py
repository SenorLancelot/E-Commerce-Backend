import json

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models
from .models import Cart, Category, Product
from .serializers import (
    CartSerializer,
    CategorySerializer,
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
        userid = self.kwargs["pk"]

        cart = Cart.objects.get(user=userid)
        cart.products.add(productid)
        cart.save()
        return Response(data=productid, status=status.HTTP_200_OK)
