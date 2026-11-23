
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import (
    RegisterAPIView,
    AddressAPIView,
    CategoryAPIView,
    ProductAPIView,
    ProductImageAPIView,
    ProductVariantAPIView,
    ProductAttributeAPIView,
    AttributeValueAPIView,
    InventoryAPIView,
    StockMovementAPIView,
    CartAPIView,
    CartItemAPIView,
    WishlistAPIView,
    WishlistItemAPIView,
    OrderAPIView,
    OrderItemAPIView,
    OrderStatusHistoryAPIView,
    PaymentAPIView,
    PaymentTransactionAPIView,
    ShipmentAPIView,
    ShipmentTrackingAPIView,
    CouponAPIView,
    CouponUsageAPIView,
    ReviewAPIView,
    ProductRatingAPIView
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", RegisterAPIView.as_view()),

    path("addresses/", AddressAPIView.as_view()),
    path("addresses/<int:pk>/", AddressAPIView.as_view()),

    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("categories/", CategoryAPIView.as_view()),
    path("categories/<int:pk>/", CategoryAPIView.as_view()),

    path("products/", ProductAPIView.as_view()),
    path("products/<int:pk>/", ProductAPIView.as_view()),

    path("product-images/", ProductImageAPIView.as_view()),
    path("product-images/<int:pk>/", ProductImageAPIView.as_view()),

    path("product-variants/", ProductVariantAPIView.as_view()),
    path("product-variants/<int:pk>/", ProductVariantAPIView.as_view()),

    path("product-attributes/", ProductAttributeAPIView.as_view()),
    path("product-attributes/<int:pk>/", ProductAttributeAPIView.as_view()),

    path("attribute-values/", AttributeValueAPIView.as_view()),
    path("attribute-values/<int:pk>/", AttributeValueAPIView.as_view()),

    path("inventory/", InventoryAPIView.as_view()),
    path("inventory/<int:pk>/", InventoryAPIView.as_view()),

    path("stock-movements/", StockMovementAPIView.as_view()),
    path("stock-movements/<int:pk>/", StockMovementAPIView.as_view()),

    path("carts/", CartAPIView.as_view()),
    path("carts/<int:pk>/", CartAPIView.as_view()),

    path("cart-items/", CartItemAPIView.as_view()),
    path("cart-items/<int:pk>/", CartItemAPIView.as_view()),

    path("wishlists/", WishlistAPIView.as_view()),
    path("wishlists/<int:pk>/", WishlistAPIView.as_view()),

    path("wishlist-items/", WishlistItemAPIView.as_view()),
    path("wishlist-items/<int:pk>/", WishlistItemAPIView.as_view()),

    path("orders/", OrderAPIView.as_view()),
    path("orders/<int:pk>/", OrderAPIView.as_view()),

    path("order-items/", OrderItemAPIView.as_view()),
    path("order-items/<int:pk>/", OrderItemAPIView.as_view()),

    path("order-status-history/", OrderStatusHistoryAPIView.as_view()),
    path("order-status-history/<int:pk>/", OrderStatusHistoryAPIView.as_view()),

    path("payments/", PaymentAPIView.as_view()),
    path("payments/<int:pk>/", PaymentAPIView.as_view()),

    path("payment-transactions/", PaymentTransactionAPIView.as_view()),
    path("payment-transactions/<int:pk>/", PaymentTransactionAPIView.as_view()),

    path("shipments/", ShipmentAPIView.as_view()),
    path("shipments/<int:pk>/", ShipmentAPIView.as_view()),

    path("shipment-tracking/", ShipmentTrackingAPIView.as_view()),
    path("shipment-tracking/<int:pk>/", ShipmentTrackingAPIView.as_view()),


    path("coupons/", CouponAPIView.as_view()),
    path("coupons/<int:pk>/", CouponAPIView.as_view()),

    path("coupon-usages/", CouponUsageAPIView.as_view()),
    path("coupon-usages/<int:pk>/", CouponUsageAPIView.as_view()),

    path("reviews/", ReviewAPIView.as_view()),
    path("reviews/<int:pk>/", ReviewAPIView.as_view()),

    path("product-ratings/", ProductRatingAPIView.as_view()),
    path("product-ratings/<int:pk>/", ProductRatingAPIView.as_view()),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)