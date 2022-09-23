class ImproperAPIAnswerException(Exception):
    """Ошибка отсутствия надлежащего ответа API."""

    pass


class TokensAreNotGivenException(Exception):
    """Ошибка отсутствия необходимых параметров окружения."""

    pass


class UnknownHWStatusException(Exception):
    """Исключение неизвестного статуса домашней работы."""

    pass


class APIResponseStatusCodeException(Exception):
    """Исключение сбоя запроса к API."""

    pass
