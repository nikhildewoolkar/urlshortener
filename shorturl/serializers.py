from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ShortURL

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user



class ShortURLSerializer(serializers.ModelSerializer):
    original_url = serializers.URLField(required=True)
    class Meta:
        model = ShortURL
        fields = ['short_code', 'original_url']
        read_only_fields = ['short_code']