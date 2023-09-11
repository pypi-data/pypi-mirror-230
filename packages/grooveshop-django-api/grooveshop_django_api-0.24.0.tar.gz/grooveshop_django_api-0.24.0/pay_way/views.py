from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.filters.custom_filters import PascalSnakeCaseOrderingFilter
from core.utils.views import TranslationsProcessingMixin
from pay_way.models import PayWay
from pay_way.paginators import PayWayPagination
from pay_way.serializers import PayWaySerializer


class PayWayViewSet(TranslationsProcessingMixin, ModelViewSet):
    queryset = PayWay.objects.all()
    serializer_class = PayWaySerializer
    pagination_class = PayWayPagination
    filter_backends = [DjangoFilterBackend, PascalSnakeCaseOrderingFilter, SearchFilter]
    filterset_fields = ["active", "cost", "free_for_order_amount"]
    ordering_fields = [
        "cost",
        "free_for_order_amount",
        "created_at",
    ]
    ordering = ["-created_at"]
    search_fields = []

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs) -> Response:
        request = self.process_translations_data(request)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs) -> Response:
        pay_way = get_object_or_404(PayWay, pk=pk)
        serializer = self.get_serializer(pay_way)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs) -> Response:
        pay_way = get_object_or_404(PayWay, pk=pk)
        request = self.process_translations_data(request)
        serializer = self.get_serializer(pay_way, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None, *args, **kwargs) -> Response:
        pay_way = get_object_or_404(PayWay, pk=pk)
        serializer = self.get_serializer(pay_way, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs) -> Response:
        pay_way = get_object_or_404(PayWay, pk=pk)
        pay_way.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
