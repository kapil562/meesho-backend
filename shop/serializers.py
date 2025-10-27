from rest_framework import serializers
from .models import Product, ProductReview, Order, Transaction, UPIConfig


# -------------------- PRODUCT REVIEW SERIALIZER --------------------
class ProductReviewSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = ["id", "reviewer_name", "rating", "comment", "image", "created_at"]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


# -------------------- PRODUCT SERIALIZER --------------------
class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    reviews = ProductReviewSerializer(many=True, read_only=True)
    available_sizes = serializers.ReadOnlyField()  # ✅ use model property

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "discount",
            "image",
            "image_url",
            "image_file",
            "available_sizes",  # ✅ replaces 'sizes'
            "sold_by",
            "occasion",
            "color",
            "fit_shape",
            "pattern",
            "fabric",
            "sleeve_length",
            "country_of_origin",
            "reviews",
        ]

    def get_image(self, obj):
        """Return uploaded file URL if exists, else fallback to image_url."""
        return obj.image


# -------------------- ORDER SERIALIZER --------------------
class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ("created_at",)

    def create(self, validated_data):
        import uuid
        validated_data["order_id"] = f"ORDER:{uuid.uuid4().hex[:12].upper()}"
        return Order.objects.create(**validated_data)


# -------------------- TRANSACTION SERIALIZER --------------------
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


# -------------------- UPI CONFIG SERIALIZER --------------------
class UPIConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UPIConfig
        fields = "__all__"
