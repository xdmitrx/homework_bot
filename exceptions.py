class ImproperAPIAnswerException(Exception):
    """Ошибка отсутствия надлежащего ответа API."""

    pass


class TokensAreNotGivenException(Exception):
    """Ошибка отсутствия необходимых параметров окружения."""

    pass
