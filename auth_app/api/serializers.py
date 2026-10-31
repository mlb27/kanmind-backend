from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True, max_length=150)
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(
        write_only=True, trim_whitespace=False
    )
    repeated_password = serializers.CharField(
        write_only=True, trim_whitespace=False
    )

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )
        return attrs

    def validate_email(self, value):
        """Reject email addresses that are already registered."""
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )
        return value

    def create(self, validated_data):
        """Create a user with a hashed password."""
        validated_data.pop("repeated_password")
        fullname = validated_data.pop("fullname")
        first_name, _, last_name = fullname.partition(" ")
        return User.objects.create_user(
            username=validated_data["email"],
            first_name=first_name,
            last_name=last_name,
            **validated_data,
        )


class LoginSerializer(serializers.Serializer):
    """Validate the credentials of an existing user."""

    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(
        write_only=True, trim_whitespace=False
    )

    def validate(self, attrs):
        """Authenticate the user without creating a new account."""
        user = authenticate(
            username=attrs["email"].lower(), password=attrs["password"]
        )
        if user is None:
            raise serializers.ValidationError(
                "Invalid email or password."
            )
        attrs["user"] = user
        return attrs
