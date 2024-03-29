from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
# from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .paginations import CustomPagination
from .serializers import (MeUserSerializer, SetPasswordSerializer,
                          TokenObtainSerializer, UserSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    # lookup_field = 'username'
    queryset = User.objects.order_by('id')
    serializer_class = UserSerializer
    # permission_classes = (IsAdminOrSuperuser,)
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = [
        'get', 'post', 'patch', 'head', 'options', 'trace'
    ]

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = self.request.user
        serializer = MeUserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        permission_classes=(IsAuthenticated,)
        # permission_classes=(IsAdminOrIsSelf,)
    )
    def set_password(self, request):
        user = self.request.user
        serializer = SetPasswordSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        if user.check_password(serializer.validated_data['current_password']):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TokenObtainView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        if 'email' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, email=request.data['email'])
        serializer = TokenObtainSerializer(
            user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        if user.check_password(serializer.validated_data['password']):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'auth_token': str(refresh.access_token)
                },
                status=status.HTTP_200_OK
            )


class LogoutView(APIView):
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)

    def post(self, request):
        user = self.request.user
        try:
            token = RefreshToken.for_user(user)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
