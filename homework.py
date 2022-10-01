import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv
from http import HTTPStatus

import exceptions
import constants


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s - строка %(lineno)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)

logger.addHandler(handler)
handler.setFormatter(formatter)


def get_bot():
    """Создаёт бота.
    Для обращения к нему из любой части кода.
    """
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        logger.debug('Бот успешно инициализирован')
        return bot
    except Exception as error:
        logger.error(
            f'Бота не удалось запустить по причине {error}'
        )


def send_message(bot, message):
    """Отправка сообщения ботом."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        logger.info('Сообщение в чат отправлено')
    except Exception as error:
        logger.error(
            f'Ошибка при отправке сообщения в чат {error}'
        )
        error = 'Ошибка при отправке сообщения в чат'
        raise exceptions.SendMessageFailure(error)


def get_api_answer(current_timestamp):
    """Получение ответа API в формате python."""
    bad_format = False
    if isinstance(int, float):
        logger.warning(
            ('Тип current_timestamp не соответствует '
             f'ожидаемому: {type}')
        )
        bad_format = True
    if len(str(int(current_timestamp))) != constants.FALSE_CURRENT_TIMESTAMP:
        logger.warning(
            ('В переменную current_timestamp передано '
             f'некорректное число: {current_timestamp}')
        )
        bad_format = True
    if bad_format:
        timestamp = int(time.time())
    else:
        timestamp = current_timestamp
    params = {'from_date': timestamp}
    logger.debug(params)

    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except exceptions.APIResponseStatusCodeException:
        logger.error('Сбой при запросе к эндпоинту')
    if response.status_code != HTTPStatus.OK:
        msg = 'Ответ от эндпойнта отличается от 200'
        logger.error(msg)
        raise ConnectionError(msg)
    return response.json()


def check_response(response):
    """Проверка ответа на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Ответ от Домашки не словарь')

    try:
        response['current_date']
        homeworks = response['homeworks']
    except KeyError as e:
        msg = f'Ошибка доступа по ключу "{e}"'
        logger.error(msg)
        raise exceptions.CheckResponseException(msg)

    if not isinstance(homeworks, list):
        raise ValueError('Тип ключа homeworks не list')
    return homeworks


def parse_status(homework):
    """Определяет статус последней работы."""
    if 'homework_name' not in homework:
        raise KeyError('Отсутствует ключ "homework_name" в ответе API')
    if 'status' not in homework:
        raise Exception('Отсутствует ключ "status" в ответе API')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    logger.info('Запущена функция "parse_status"')
    logger.debug(f'Получен статус домашней работы: {homework_status}')
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except Exception as error:
        message = f'Недокументированный статус домашней работы({error})'
        logger.error(message)
        raise exceptions.UnknownHWStatusException(
            'Недокументированный статус домашней работы'
        )
    else:
        homework_name = homework['homework_name']
        return f'Изменился статус проверки работы "{homework_name}".{verdict}'


def check_tokens():
    """Проверка полноты набора необходимых данных.
    Для авторизации и доступа к чату.
    """
    tokens_dict = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }

    if None in tokens_dict.values():
        no_tokens_list = []
        for key in tokens_dict:
            if tokens_dict[key] is None:
                no_tokens_list.append(key)
        count = len([value for value in tokens_dict.values() if value is None])
        message = f'Нет переменных окружения: {",".join(no_tokens_list)}'
        if tokens_dict['PRACTICUM_TOKEN'] is None and count == 1:
            logger.critical(message)
            send_message(get_bot(), message)
            raise SystemError('Ошибка отправки сообщения')
        logger.critical(message)
        return False
    logger.debug('Все переменные окружения доступны')
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Переданы не все обязательные переменные окружения')
        sys.exit()

    while True:
        try:
            current_timestamp = int(time.time())
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            raise exceptions.BotNotSendMessage

        except exceptions.BotNotSendMessage as exc:
            denied_message = f'Ошибка отправки сообщения: {exc}'
            logger.error(denied_message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            denied_message != message
            send_message(get_bot(), message)

            if not homeworks:
                wrong_response = 'Получен некорректный ответ API'
                logger.error(wrong_response)
            if len(homeworks) != 0:
                new_status = parse_status(homeworks[0])
                logger.debug(f'parse_status выдала "{new_status}"')
            else:
                same_parse_status = 'Новый статус не обнаружен'
                logger.debug(same_parse_status)
                current_timestamp = response.get('current_date')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
