class TokensAreNotGivenException(Exception):
    """Ошибка отсутствия необходимых параметров окружения."""

    pass


class UnknownHWStatusException(Exception):
    """Исключение неизвестного статуса домашней работы."""

    pass


class APIResponseStatusCodeException(Exception):
    """Исключение сбоя запроса к API."""

    pass


class CheckResponseException(Exception):
    """Исключение неверного формата ответа API."""

    pass


class SendMessageFailure(Exception):
    """Исключение отправки сообщения."""

    pass


class BotNotSendMessage(Exception):
    """Исключение отправки сообщения в ТГ.
    При ошибке отправки сообщения об ошибке.
    """

    pass
