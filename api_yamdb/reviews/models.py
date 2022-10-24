from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import year_validation


class User(AbstractUser):
    ROLE_USER = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'

    USER_STATUS = [
        (ROLE_USER, ROLE_USER),
        (ROLE_MODERATOR, ROLE_MODERATOR),
        (ROLE_ADMIN, ROLE_ADMIN)
    ]

    email = models.EmailField(max_length=254, blank=False, unique=True)
    bio = models.CharField(max_length=150, blank=True)
    role = models.CharField(choices=USER_STATUS, default='user', max_length=10)
    is_active = models.BooleanField(
        ('active'),
        default=True,
    )

    @property
    def is_admin(self):
        return self.is_superuser or self.role == "admin" or self.is_staff

    @property
    def is_moder(self):
        return self.role == 'moderator'

    class Meta:
        verbose_name = 'Пользователи'
        ordering = ['-id']


class CategoryGenre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)


class Category(CategoryGenre):

    class Meta:
        ordering = ['-name']
        verbose_name = 'Категории'

    def __str__(self):
        return self.name.truncate(15)


class Genre(CategoryGenre):

    class Meta:
        verbose_name = 'Жанры произведений'
        ordering = ['name']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField()
    year = models.IntegerField(validators=[year_validation])
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="titles",
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name="titles",
        blank=True,
        verbose_name="Жанр произведения",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведения'


class CommentReview(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)


class Review(CommentReview):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews')
    score = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)])

    class Meta:
        verbose_name = 'Отзывы'
        ordering = ["-pub_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title_id"], name="unique_titile_author"
            )
        ]


class Comment(CommentReview):
    review_id = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments')

    class Meta:
        verbose_name = 'Комментарии'
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text
