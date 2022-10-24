from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User


class JwsTokenSerializer(serializers.Serializer):
    """Получение основнова токена для работы с сервисом."""

    username = serializers.CharField(max_length=256)
    confirmation_code = serializers.CharField(max_length=512)


class AuthorizationTokenSerializer(serializers.Serializer):
    """Генерация и получение токена,
    отправляемого в письме пользователю при регистрации."""

    username = serializers.CharField(max_length=256)
    email = serializers.EmailField(max_length=254)


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username',
                  'email',
                  'bio',
                  'last_name',
                  'first_name',
                  'role')
        model = User
        lookup_field = 'username'


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('title',)

    def validate(self, data):
        title = self.context['request'].parser_context['kwargs']['title']
        author = self.context.get('request').user
        title = get_object_or_404(Title, id=title)
        if (title.reviews.filter(author=author).exists()
           and self.context.get('request').method != 'PATCH'):
            raise serializers.ValidationError(
                'Можно оставлять только один отзыв!'
            )
        return data

    def validate_rating(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError('Рейтинг может быть от 1 до 10.')
        return value


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('review_id',)


class CategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Category
        lookup_field = 'slug'


class SlugCategorySerializer(serializers.SlugRelatedField):
    def to_representation(self, instance):
        return CategoriesSerializer(instance).data


class GenresSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id',)
        lookup_field = 'slug'
        model = Genre


class SlugGenresSerializer(serializers.SlugRelatedField):
    def to_representation(self, instance):
        return GenresSerializer(instance).data


class TitlesSerializer(serializers.ModelSerializer):
    category = SlugCategorySerializer(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False
    )
    genre = SlugGenresSerializer(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    rating = serializers.IntegerField(
        source='reviews__score__avg',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Title
