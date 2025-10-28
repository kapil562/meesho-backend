from django.db import models


# -------------------- PRODUCT --------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(default=0, help_text="Percentage discount")

    # Image (upload or external link)
    image_url = models.URLField(blank=True, null=True, help_text="External image link (optional)")
    image_file = models.ImageField(upload_to="products/", blank=True, null=True, help_text="Upload product image")

    # Size options
    size_s = models.BooleanField(default=False)
    size_m = models.BooleanField(default=False)
    size_l = models.BooleanField(default=False)
    size_xl = models.BooleanField(default=False)
    size_xxl = models.BooleanField(default=False)
    size_3xl = models.BooleanField(default=False)
    size_4xl = models.BooleanField(default=False)
    size_5xl = models.BooleanField(default=False)
    size_6xl = models.BooleanField(default=False)
    size_7xl = models.BooleanField(default=False)
    size_8xl = models.BooleanField(default=False)

    sold_by = models.CharField(max_length=255, default="Unknown Seller", help_text="Store or seller name")

    # Highlights
    occasion = models.CharField(max_length=100, blank=True, help_text="Example: Casual")
    color = models.CharField(max_length=100, blank=True, help_text="Example: Red / Random")
    fit_shape = models.CharField(max_length=100, blank=True, help_text="Example: Regular")
    pattern = models.CharField(max_length=100, blank=True, help_text="Example: Printed")

    # Details
    fabric = models.CharField(max_length=100, blank=True, help_text="Example: Cotton Blend")
    sleeve_length = models.CharField(max_length=100, blank=True, help_text="Example: Long Sleeves")
    country_of_origin = models.CharField(max_length=100, default="India")

    class Meta:
        ordering = ["-id"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} - ₹{self.price}"

    @property
    def image(self):
        """Return uploaded file URL if exists, else fallback to image_url."""
        if self.image_file:
            return self.image_file.url
        return self.image_url or ""

    @property
    def available_sizes(self):
        """Return list of enabled sizes (for frontend)."""
        all_sizes = {
            "S": self.size_s,
            "M": self.size_m,
            "L": self.size_l,
            "XL": self.size_xl,
            "XXL": self.size_xxl,
            "3XL": self.size_3xl,
            "4XL": self.size_4xl,
            "5XL": self.size_5xl,
            "6XL": self.size_6xl,
            "7XL": self.size_7xl,
            "8XL": self.size_8xl,
        }
        return [size for size, enabled in all_sizes.items() if enabled]


# -------------------- PRODUCT REVIEW --------------------
class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    reviewer_name = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.TextField(blank=True)
    image = models.ImageField(upload_to="reviews/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return f"{self.reviewer_name} ({self.rating}★)"


# -------------------- ORDER --------------------
class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=32, default="Free Size")
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, unique=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"{self.order_id} - {self.product.name}"


# -------------------- UPI CONFIG --------------------
class UPIConfig(models.Model):
    upi_id = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "UPI Configuration"
        verbose_name_plural = "UPI Configurations"

    def __str__(self):
        return f"{self.upi_id} ({'Active' if self.is_active else 'Inactive'})"


# -------------------- TRANSACTION --------------------
class Transaction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    product_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transaction_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-transaction_time"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.product_name} - ₹{self.amount} ({self.status})"
