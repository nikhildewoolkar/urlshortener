from django.shortcuts import get_object_or_404, redirect
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from .models import ShortURL
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ShortURLSerializer, RegisterSerializer
from .services import *
from drf_spectacular.utils import extend_schema, OpenApiExample


class RegisterView(APIView):
    """
    Simple registration so users can log in and get higher rate limits.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"})
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=400)


class ShortenURLView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ShortURLSerializer,
        responses={201: ShortURLSerializer},
        examples=[
            OpenApiExample(
                "Shorten basic URL",
                summary="Shorten URL",
                value={"original_url": "https://google.com"},
            ),
            OpenApiExample(
                "Shorten with custom alias",
                summary="Custom alias",
                value={
                    "original_url": "https://example.com/landing",
                    "custom_alias": "mybrand",
                },
            ),
        ],
    )
    def post(self, request):
        serializer = ShortURLSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        original_url = serializer.validated_data["original_url"]
        custom_alias = serializer.validated_data.get("custom_alias")

        try:
            short_obj, created = get_or_create_short_url(
                original_url=original_url,
                user=request.user,
                custom_alias=custom_alias,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(ShortURLSerializer(short_obj).data, status=status_code)


class RedirectURLView(APIView):
    permission_classes = []

    @extend_schema(
        responses={302: None, 404: {"example": {"error": "Short URL not found"}}},
    )
    def get(self, request, short_code):
        original_url = get_cached_url(short_code)
        if original_url:
            try:
                short_obj = ShortURL.objects.get(short_code=short_code)
                record_click(short_obj)
            except ShortURL.DoesNotExist:
                return Response({"error": "Short URL not found"}, status=status.HTTP_404_NOT_FOUND)
            return redirect(original_url)

        try:
            short_obj = ShortURL.objects.get(short_code=short_code)
        except ShortURL.DoesNotExist:
            return Response({"error": "Short URL not found"}, status=status.HTTP_404_NOT_FOUND)

        cache_short_url(short_code, short_obj.original_url)

        record_click(short_obj)
        return redirect(short_obj.original_url)


class AdminShortURLPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminURLListView(ListAPIView):
    """
    Admin listing of all URLs with pagination.
    """
    permission_classes = [IsAdminUser]
    serializer_class = ShortURLSerializer
    queryset = ShortURL.objects.select_related("user").order_by("-created_at")
    pagination_class = AdminShortURLPagination


class URLAnalyticsView(APIView):
    """
    Simple analytics per short code.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiExample(
                "Analytics example",
                value={
                    "short_code": "abc123",
                    "original_url": "https://google.com",
                    "click_count": 42,
                    "created_at": "2025-11-29T18:13:56Z",
                    "last_accessed_at": "2025-11-29T19:00:00Z",
                },
            )
        }
    )
    def get(self, request, short_code):
        qs = ShortURL.objects
        if not request.user.is_staff:
            qs = qs.filter(user=request.user)

        try:
            obj = qs.get(short_code=short_code)
        except ShortURL.DoesNotExist:
            return Response({"error": "Short URL not found"}, status=404)

        data = {
            "short_code": obj.short_code,
            "original_url": obj.original_url,
            "click_count": obj.click_count,
            "created_at": obj.created_at,
            "last_accessed_at": obj.last_accessed_at,
        }
        return Response(data)