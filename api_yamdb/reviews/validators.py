import datetime as dt
from django.core.exceptions import ValidationError


def year_validation(data):
    if data > dt.date.today().year:
        raise ValidationError(
            """Путешествия во времени запрещены!
            Год создания произведения не может быть позже текущего!
            """
        )
