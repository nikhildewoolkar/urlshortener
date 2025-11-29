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
from .services import generate_short_code

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
    """
    Core: Submit long URL -> receive short_code.
    - Idempotent: same URL returns same ShortURL record.
    - Handles duplicates gracefully via get_or_create().
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        original_url = request.data.get("original_url")
        if not original_url:
            return Response({"error": "original_url is required"}, status=status.HTTP_400_BAD_REQUEST)

        # get_or_create: if the URL already exists, returns existing record (idempotent)
        short_obj, created = ShortURL.objects.get_or_create(
            original_url=original_url,
            defaults={"short_code": generate_short_code(original_url)},
        )

        serializer = ShortURLSerializer(short_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RedirectURLView(APIView):
    """
    Public redirect:
    - Try Redis cache first (for <100ms)
    - Fallback to DB
    - Update click_count + last_accessed_at
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, short_code):
        cache_key = f"short:{short_code}"
        cached_url = cache.get(cache_key)
        if cached_url:
            return redirect(cached_url)

        url_obj = get_object_or_404(ShortURL, short_code=short_code)

        url_obj.click_count += 1
        url_obj.last_accessed_at = timezone.now()
        url_obj.save()

        cache.set(cache_key, url_obj.original_url, timeout=60 * 60 * 24 * 30)  # 30 days

        return redirect(url_obj.original_url)

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
