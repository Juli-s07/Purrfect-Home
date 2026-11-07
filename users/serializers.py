from django.contrib.auth import password_validation
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(max_length = 128, write_only = True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password_confirmation']
        extra_kwargs = {"password": {"write_only": True,
                                     "min_length": 8},
                        "email": {"required": True,
                                  "allow_blank": False}}

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({"password_confirmation": "Passwords don't match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirmation")
        return User.objects.create_user(**validated_data)




