from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from urllib.parse import urlencode
from django.utils import timezone
import random

from .models import Product, Order, Transaction, UPIConfig, ProductReview
from .serializers import (
    ProductSerializer,
    OrderSerializer,
    TransactionSerializer,
    ProductReviewSerializer,
)


# -------------------- PRODUCT --------------------
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for listing and retrieving products.
    Includes nested reviews for each product.
    """
    queryset = Product.objects.all().order_by("-id")
    serializer_class = ProductSerializer


# -------------------- ORDER --------------------
class OrderViewSet(viewsets.ModelViewSet):
    """
    API for creating and viewing customer orders.
    """
    queryset = Order.objects.all().select_related("product").order_by("-created_at")
    serializer_class = OrderSerializer


# -------------------- PRODUCT REVIEW --------------------
class ProductReviewViewSet(viewsets.ModelViewSet):
    """
    API to create and list product reviews.
    """
    queryset = ProductReview.objects.all().select_related("product").order_by("-created_at")
    serializer_class = ProductReviewSerializer


# -------------------- GET ACTIVE UPI --------------------
@api_view(["GET"])
def get_active_upi(request):
    """
    Fetch the currently active merchant UPI ID.
    """
    active_upi = UPIConfig.objects.filter(is_active=True).first()
    if active_upi:
        return Response(
            {
                "status": "success",
                "upi_id": active_upi.upi_id,
                "updated_at": active_upi.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            status=status.HTTP_200_OK,
        )
    return Response(
        {"status": "error", "message": "No active UPI found"},
        status=status.HTTP_404_NOT_FOUND,
    )


# -------------------- CREATE TRANSACTION --------------------
@api_view(["POST"])
def create_transaction(request):
    """
    Create a transaction record when the user initiates payment.
    Initially marked as 'pending'. The frontend will later verify the status.
    """
    try:
        data = request.data
        transaction_id = f"TID{random.randint(100000, 999999)}"

        transaction = Transaction.objects.create(
            product_name=data.get("product_name", "Unknown Product"),
            amount=float(data.get("amount", 0)),
            payment_method=data.get("payment_method", "Unknown"),
            transaction_id=transaction_id,
            status="pending",
            transaction_time=timezone.now(),
        )

        serializer = TransactionSerializer(transaction)
        return Response(
            {
                "status": "success",
                "message": "Transaction created successfully (pending).",
                "transaction": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


# -------------------- VERIFY TRANSACTION --------------------
@api_view(["POST"])
def verify_transaction(request, transaction_id):
    """
    Update a transaction's status to 'success' or 'failed'
    after payment confirmation.
    """
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        new_status = request.data.get("status", "").lower()

        if new_status not in ["success", "failed"]:
            return Response(
                {"error": "Invalid status. Must be 'success' or 'failed'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transaction.status = new_status
        transaction.save()

        serializer = TransactionSerializer(transaction)
        return Response(
            {
                "status": "success",
                "message": f"Transaction marked as {new_status}.",
                "transaction": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Transaction.DoesNotExist:
        return Response(
            {"status": "error", "message": "Transaction not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


# -------------------- GENERATE UPI LINK --------------------
@api_view(["GET"])
def generate_upi(request, order_id):
    """
    Generate a ready-to-use UPI deep link for a specific order.
    Returns PhonePe & Paytm formatted URLs.
    """
    try:
        active_upi = UPIConfig.objects.filter(is_active=True).first()
        if not active_upi:
            return Response(
                {"status": "error", "message": "No active UPI configured"},
                status=status.HTTP_404_NOT_FOUND,
            )

        order = get_object_or_404(Order, order_id=order_id)
        params = {
            "pa": active_upi.upi_id,
            "pn": "MerchantName",
            "am": str(order.final_price),
            "cu": "INR",
            "tid": order.order_id,
        }
        base = urlencode(params)

        return Response(
            {
                "status": "success",
                "upi_params": params,
                "upi_query": base,
                "phonepe_link": f"phonepe://pay?{base}",
                "paytm_link": f"paytmmp://pay?{base}",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
