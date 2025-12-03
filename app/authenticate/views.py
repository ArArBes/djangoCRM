from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer,LoginSerializer
from company.serializers import CompanySerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


class RegisterUserView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()

            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                "detail": "Пользователь успешно зарегистрирован.",
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            raise AuthenticationFailed('Email and password are required')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid credentials')

        if not user.check_password(password):
            raise AuthenticationFailed('Invalid credentials')

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)

class CreateCompanyView(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = CompanySerializer

    def post(self, request, *args, **kwargs):
        user = request.user

        if user.company:
            return Response({"detail": "На вас уже зарегистрирована компания."}, status=status.HTTP_400_BAD_REQUEST)

        company_data = request.data
        company_serializer = CompanySerializer(data=company_data)

        if company_serializer.is_valid():
            company = company_serializer.save(owner=user)
            user.company = company
            user.save()
            return Response({"detail": "Компания создана."}, status=status.HTTP_201_CREATED)
        return Response(company_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetCompanyView(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = CompanySerializer
    def get(self, request, *args, **kwargs):
        user = self.request.user
        if not user.company:
            return Response({"detail": "У вас нет привязанных компаний."}, status=status.HTTP_400_BAD_REQUEST)

        company_serializer = CompanySerializer(user.company)
        return Response(company_serializer.data)