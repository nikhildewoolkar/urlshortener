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
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ShortURLSerializer, RegisterSerializer
from .services import *
from drf_spectacular.utils import extend_schema

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
        responses={201: ShortURLSerializer}
    )
    def post(self, request):
        original_url = request.data.get("original_url")

        if not original_url:
            return Response({"error": "original_url is required"}, status=status.HTTP_400_BAD_REQUEST)

        short_obj, created = get_or_create_short_url(original_url, request.user)

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(ShortURLSerializer(short_obj).data, status=status_code)

class RedirectURLView(APIView):
    permission_classes = []  # Public endpoint

    @extend_schema(
        parameters=[],
        responses={302: None, 404: "Short URL not found"}
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

        # 2️⃣ Fallback DB lookup
        try:
            short_obj = ShortURL.objects.get(short_code=short_code)
        except ShortURL.DoesNotExist:
            return Response({"error": "Short URL not found"}, status=status.HTTP_404_NOT_FOUND)

        # Cache result for future requests
        cache_short_url(short_code, short_obj.original_url)  # 1 day cache

        # Update analytics
        record_click(short_obj)
        return redirect(short_obj.original_url)


class AdminShortURLPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class AdminURLListView(ListAPIView):
    """
    Admin-only endpoint:
    - Paginated list of all shortened URLs
    - Includes metadata
    """
    queryset = ShortURL.objects.all().order_by('-created_at')
    serializer_class = ShortURLSerializer
    pagination_class = AdminShortURLPagination
    permission_classes = [permissions.IsAdminUser]
