from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product, ProductReview, Order, Transaction, UPIConfig


# -------------------- INLINE REVIEWS (Inside Product) --------------------
class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 1
    fields = ("reviewer_name", "rating", "comment", "image", "created_at")
    readonly_fields = ("created_at",)


# -------------------- PRODUCT --------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "discount",
        "sold_by",
        "country_of_origin",
        "image_preview",
    )
    search_fields = ("name", "sold_by")
    list_filter = ("country_of_origin",)
    readonly_fields = ("image_preview",)
    inlines = [ProductReviewInline]

    fieldsets = (
        ("🧾 Basic Info", {
            "fields": ("name", "price", "discount", "sold_by"),
        }),
        ("🖼️ Product Images", {
            "fields": ("image_url", "image_file", "image_preview"),
        }),
        ("📏 Available Sizes", {
            "fields": (
                "size_s", "size_m", "size_l", "size_xl", "size_xxl",
                "size_3xl", "size_4xl", "size_5xl", "size_6xl", "size_7xl", "size_8xl",
            ),
        }),
        ("✨ Product Highlights", {
            "fields": ("occasion", "color", "fit_shape", "pattern"),
        }),
        ("📋 Product Details", {
            "fields": ("fabric", "sleeve_length", "country_of_origin"),
        }),
    )

    def image_preview(self, obj):
        """Show small image preview in admin panel."""
        if obj.image:
            return mark_safe(
                f"<img src='{obj.image}' width='80' height='80' "
                "style='object-fit:contain;border-radius:6px;border:1px solid #ccc;' />"
            )
        return "No image"
    image_preview.short_description = "Preview"


# -------------------- PRODUCT REVIEW --------------------
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "reviewer_name", "rating", "created_at")
    search_fields = ("reviewer_name", "product__name")
    list_filter = ("rating", "created_at")
    readonly_fields = ("created_at",)


# -------------------- ORDER --------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "product",
        "quantity",
        "size",
        "final_price",
        "payment_status",
        "created_at",
    )
    list_filter = ("payment_status", "created_at")
    search_fields = ("order_id", "product__name")
    readonly_fields = ("created_at",)

    fieldsets = (
        ("🛍️ Order Details", {
            "fields": ("order_id", "product", "quantity", "size", "final_price"),
        }),
        ("💳 Payment", {
            "fields": ("payment_status",),
        }),
        ("🕒 Timestamps", {
            "fields": ("created_at",),
        }),
    )


# -------------------- TRANSACTION --------------------
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("product_name", "amount", "payment_method", "transaction_time")
    list_filter = ("payment_method", "transaction_time")
    search_fields = ("product_name",)
    readonly_fields = ("transaction_time",)


# -------------------- UPI CONFIG --------------------
@admin.register(UPIConfig)
class UPIConfigAdmin(admin.ModelAdmin):
    list_display = ("upi_id", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("upi_id",)
    readonly_fields = ("created_at",)

    def save_model(self, request, obj, form, change):
        """
        Ensure only one UPI configuration is active at a time.
        """
        if obj.is_active:
            UPIConfig.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)
