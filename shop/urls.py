from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import verify_transaction

from .views import (
    ProductViewSet,
    OrderViewSet,
    ProductReviewViewSet,   # ✅ Added for reviews
    get_active_upi,
    create_transaction,
    generate_upi,
)

# ✅ Router for all model viewsets
router = DefaultRouter()
router.register(r"products", ProductViewSet)
router.register(r"orders", OrderViewSet)
router.register(r"reviews", ProductReviewViewSet)  # ✅ New review endpoint

# ✅ Custom API endpoints
urlpatterns = [
    path("", include(router.urls)),

    # 🔹 Fetch currently active UPI ID
    path("get-upi/", get_active_upi, name="get_active_upi"),

    # 🔹 Log and save a new transaction
    path("create-transaction/", create_transaction, name="create_transaction"),

    # 🔹 Generate UPI payment link dynamically for given order
    path("generate-upi/<str:order_id>/", generate_upi, name="generate_upi"),

    path("verify-transaction/<str:transaction_id>/", verify_transaction, name="verify_transaction"),

]
