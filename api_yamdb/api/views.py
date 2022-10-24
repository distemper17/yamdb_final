from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly,
                          IsAuthorAdminModerOrReadOnly,
                          UserMePermission,
                          UserPermission)
from .serializers import (AuthorizationTokenSerializer,
                          CategoriesSerializer,
                          CommentsSerializer,
                          GenresSerializer,
                          JwsTokenSerializer,
                          ReviewsSerializer,
                          TitlesSerializer,
                          UsersSerializer)


class GetPostDeleteViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GetUserAPIView(APIView):
    """"Отправка кода подтверждения на указанную электронную почту."""
    def post(self, request):
        def send_message(token_code, created, email):
            text_massege = 'Валидация прошла успешно. Ваш код авторизации:'
            if not created:
                text_massege = 'Код авторизации выслан повторно:'
            print(text_massege)
            send_mail(
                'код активации',
                f'{text_massege} {token_code}',
                'admin@django.com',
                [email],
                fail_silently=False,
            )
        serializer = AuthorizationTokenSerializer(data=request.data)
        if serializer.initial_data.get('username') == 'me':
            return Response(
                'Невозможно получить Token',
                status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            try:
                user, created = User.objects.get_or_create(username=username,
                                                           email=email)
            except Exception:
                return Response('Указаны неверные данные',
                                status=status.HTTP_400_BAD_REQUEST)
            token_code = default_token_generator.make_token(user)
            send_message(token_code, created, email)
            return Response(serializer.data, status=status.HTTP_200_OK)


class GetWorkingTokenAPIView(TokenObtainPairView):
    """Генерация основного ключа token с проверкой кода из письма."""
    def post(self, request):
        serializers = JwsTokenSerializer(data=request.data)
        if serializers.is_valid(raise_exception=True):
            user = get_object_or_404(
                User,
                username=request.data.get('username'))
            confirmation_code = serializers.validated_data.get(
                'confirmation_code')
            if default_token_generator.check_token(user, confirmation_code):
                token = RefreshToken.for_user(user)
                response = {}
                response['access_token'] = str(token.access_token)
                return Response(response)
            return Response(
                'Невозможно получить Token',
                status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (UserPermission, )
    search_fields = ('username',)
    lookup_field = 'username'

    @action(detail=False,
            url_path='me',
            methods=['get', 'patch'],
            permission_classes=[UserMePermission, ])
    def only_user(self, request):
        if request.method == 'PATCH':
            serializer = UsersSerializer(
                request.user, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                role = request.user.role
                assignable_role = serializer.validated_data.get('role')
                if (role == 'user'
                    and assignable_role == ('admin'
                                            or 'moderator'
                                            or None)):
                    return Response(
                        serializer.data,
                        status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UsersSerializer(request.user)
        return Response(serializer.data)


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = [IsAuthorAdminModerOrReadOnly, ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title'))
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthorAdminModerOrReadOnly, ]

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review_id=review)


class CategoriesViewSet(GetPostDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(GetPostDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')).order_by('name')
    serializer_class = TitlesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
