from django.urls import path

from order.views.order import Checkout
from order.views.order import OrderViewSet

urlpatterns = [
    path(
        "order/",
        OrderViewSet.as_view({"get": "list", "post": "create"}),
        name="order-list",
    ),
    path(
        "order/<int:pk>/",
        OrderViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="order-detail",
    ),
    path(
        "checkout/",
        Checkout.as_view(),
        name="checkout",
    ),
]
