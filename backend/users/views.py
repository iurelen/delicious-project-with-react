from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Follow
from .paginations import CustomPagination
from .serializers import (
    SubscriptionsSerializer, SetPasswordSerializer,
    TokenObtainSerializer, UserGetSerializer, UserPostSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    # lookup_field = 'username'
    queryset = User.objects.order_by('-id')
    serializer_class = UserPostSerializer
    # permission_classes = (IsAdminOrSuperuser,)
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    # http_method_names = [
    #    'get', 'post', 'patch', 'head', 'options', 'trace'
    # ]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return UserGetSerializer
        return self.serializer_class

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = self.request.user
        # serializer = UserGetSerializer(user, data=request.data, partial=True)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        serializer = UserGetSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        # permission_classes=(IsAdminOrIsSelf,)
        serializer_class=SetPasswordSerializer()
    )
    def set_password(self, request):
        user = self.request.user
        serializer = SetPasswordSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        if user.check_password(serializer.validated_data['current_password']):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {
                    'errors': 'Ошибка пароля.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = self.request.user.follower.order_by('-id')
        serializer = SubscriptionsSerializer(
            queryset, many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def subscriptions(self, request):
    #    pages = self.paginate_queryset(
    #         self.request.user.follower.all()
    #    )
    #    serializer = SubscriptionsSerializer(
    #        pages, many=True,
    #        context={'request': request}
    #    )
    #    return self.get_paginated_response(serializer.data)


class SubscriptionsViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = SubscriptionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.follower.all()


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
        else:
            return Response(
                {
                    'detail': 'Учетные данные не были предоставлены.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,)

    def post(self, request):
        user = self.request.user
        try:
            token = RefreshToken.for_user(user)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exept:
            return Response(exept, status=status.HTTP_401_UNAUTHORIZED)


class FollowView(APIView):
    permission_classes = (IsAuthenticated,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('following__username',)

    def post(self, request, user_id):
        following = get_object_or_404(User, id=user_id)
        serializer = SubscriptionsSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        if following == request.user:
            return Response(
                {
                    'errors': 'Нельзя подписаться на самого себя.',
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user.follower.filter(following_id=user_id).exists():
            return Response(
                {
                    'errors': 'Подписка уже создана.',
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(user=request.user, following=following)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        following = get_object_or_404(User, id=user_id)
        instance = get_object_or_404(Follow, user=self.request.user,
                                     following=following)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
