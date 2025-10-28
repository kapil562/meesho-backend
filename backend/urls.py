from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static


# -------------------- ROOT HEALTH CHECK --------------------
def home(request):
    """Simple root endpoint to confirm the backend is running."""
    return JsonResponse({
        "status": "ok",
        "message": "Django backend is running ✅",
        "api_base": "/api/",
        "admin_panel": "/admin/"
    })


# -------------------- URL PATTERNS --------------------
urlpatterns = [
    # Health check
    path("", home, name="home"),

    # Admin site
    path("admin/", admin.site.urls),

    # API routes (shop app)
    path("api/", include("shop.urls")),
]


# -------------------- MEDIA FILE SERVING --------------------
# ✅ Serve media files (uploaded images) in development & Render
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# -------------------- ADMIN PANEL BRANDING --------------------
admin.site.site_header = "🛍️ E-Commerce Admin"
admin.site.site_title = "E-Commerce Admin Panel"
admin.site.index_title = "Welcome to Product & Payment Dashboard"
