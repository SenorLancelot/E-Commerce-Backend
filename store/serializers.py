from rest_framework import serializers

from .models import Cart, Category, Product, ProductImage


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "alt_text"]


class ProductSerializer(serializers.ModelSerializer):
    product_image = ImageSerializer(many=True, read_only=True)
    category = serializers.CharField()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "product_type",
            "title",
            "description",
            "slug",
            "regular_price",
            "discount_price",
            "product_image",
        ]

    def create(self, validated_data):
        category = validated_data.pop("category")
        category = Category.objects.get(name=category)
        p = Product.objects.create(category=category, **validated_data)


class ProductSerializerResponse(serializers.ModelSerializer):
    product_image = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "product_type",
            "title",
            "description",
            "slug",
            "regular_price",
            "discount_price",
            "product_image",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug"]


class CartSerializer(serializers.ModelSerializer):
    products = ProductSerializerResponse(many=True)

    class Meta:
        model = Cart
        fields = ["products"]
