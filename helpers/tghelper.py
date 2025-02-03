"""
Модуль для работы с телеграмом, в первую очередь - для создания клавиатур.

Classes
--------
Paginator
    Дает список объектов на определенной странице и соответствующую инлайн-клавиатуру.
    Методы класса неплохо покрыты тестами.
"""
import datetime
import math
import random
from typing import Optional, BinaryIO

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, Message, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from helpers.texthelper import get_word_ending

THINKING_PHRASES = [
    "Запрос обрабатывается...",
    "Секундочку...",
    "Я не зависла, просто стараюсь получше ответить...",
    "Мысли медленно крутятся в моей голове...",
    "Я размышляю о вашем запросе, подождите немножко, пожалуйста...",
    "Ожиданье - самый скучный повод...",
    "Это будет леген... подожди-подожди..."
]


async def send_text_any_size(message: Message, text: str, mode: ParseMode = ParseMode.MARKDOWN) -> None:
    for x in range(0, len(text), 4096):
        await message.answer(text=text[x:x + 4096], parse_mode=mode)


def process_file_for_tg(file: BinaryIO, file_format: str) -> BufferedInputFile:
    file_name = f"{datetime.datetime.now().strftime(r'%H_%M_%S')}.{file_format}"
    return BufferedInputFile(file, file_name)  # type: ignore


def get_random_processing_phrase() -> str:
    return random.choice(THINKING_PHRASES)


async def get_voice_from_tg(message: Message) -> BinaryIO:
    """Достает из сообщения файл и загружает его в память"""
    original_file = await message.bot.get_file(message.voice.file_id)
    in_memory_file = await message.bot.download(file=original_file)  # type: ignore
    in_memory_file.name = original_file.file_path  # type: ignore
    return in_memory_file


def get_reply_keyboard(elements: list[str]) -> ReplyKeyboardMarkup:
    """Возвращает стандартную клавиатуру с вариантами ответа"""
    builder = ReplyKeyboardBuilder()
    for element in elements:
        builder.button(text=f"{element}")
    builder.adjust(2)
    return builder.as_markup()


def get_inline_keyboard(elements: list[str], callback_data: str) -> InlineKeyboardMarkup:
    """Возвращает стандартную инлайн-клавиатуру"""
    builder = InlineKeyboardBuilder()
    for element in elements:
        builder.row(types.InlineKeyboardButton(
            text=f"{element}",
            callback_data=f"{callback_data}_{element}")
        )
    builder.adjust(2)
    return builder.as_markup()


class Paginator:
    """Класс, который по списку объектов формирует срез и клавиатуру"""

    def __repr__(self) -> str:
        return f"Paginator(page={self.page}, " \
               f"visible_results={self.visible_results}, " \
               f"page_elements={self.page_elements}, " \
               f"pages={self.pages}, " \
               f"len objects={len(self.objects)})"

    def __str__(self) -> str:
        return f"Пагинатор для страницы {self.page}: " \
               f"количество элементов {self.page_elements}, " \
               f"количество видимых страниц {self.visible_results}"

    def __init__(self, page: int, objects: list, visible_results: int = 5, page_elements: int = 5):
        self.objects = objects
        self.pages = math.ceil(len(objects) / visible_results)
        self.visible_results = visible_results
        self.page_elements = page_elements
        self.page = page

    def get_pages_numbers(self) -> tuple[Optional[int], ...]:
        """Возвращает кортеж номеров страниц, например (1, 2, 3) или (None, None, None)"""
        if self.page > self.pages:
            raise AssertionError("Номер страницы не может быть выше максимального")
        if self.page == self.pages == 1:
            return tuple([None] * self.page_elements)
        result = [i + self.page for i in range(self.page_elements)]
        while result[-1] > min(self.pages, self.page + int(self.page_elements / 2)) and result[-1] > self.page_elements:
            result = list(map(lambda x: x - 1, result))
        return tuple(map(lambda x: x if x <= self.pages else None, result))

    def create_keyboard(self, page_handle: str, query: str = '') -> InlineKeyboardMarkup:
        """Формирует клавиатуру с определенными номерами страниц и page_handle для коллбэка"""
        builder = InlineKeyboardBuilder()
        page_numbers = self.get_pages_numbers()
        [self._create_page_button(builder, number, page_handle, query) for number in page_numbers if number]
        builder.adjust(self.page_elements)
        return builder.as_markup()

    def _create_page_button(self, builder: InlineKeyboardBuilder, number: int,
                            page_handle: str, query: str = '') -> InlineKeyboardBuilder:
        """Формирует кнопку с цифрой"""
        builder.row(types.InlineKeyboardButton(
            text=f"{number}" if number != self.page else f"-{number}-",
            callback_data=f"{page_handle} {number} {query}"))
        return builder

    def get_objects_on_page(self) -> list:
        """Возвращает список объектов на странице"""
        left, right = self.get_array_indexes()
        return self.objects[left: right + 1]

    def get_array_indexes(self) -> tuple[int, int]:
        """Возвращает индексы левой и правой границы для объектов на странице"""
        left_index = 0 + self.visible_results * (self.page - 1)
        right_index = min((self.visible_results - 1) + self.visible_results * (self.page - 1), len(self.objects) - 1)
        return left_index, right_index

    def result_message(self) -> str:
        """Формирует сообщение о результате поиска"""
        count = len(self.objects)
        return f"Всего найден{get_word_ending(count, ['', 'о', 'о'])} " \
               f"{count} результат{get_word_ending(count, ['', 'а', 'ов'])}:\r\n\r\n"
