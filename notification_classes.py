from abc import ABC, abstractmethod
from datetime import datetime


class ParentNotification(ABC):
    """Базовый абстрактный класс для всех типов уведомлений."""

    def __init__(self, label: str):
        self.label = label           # человекочитаемое имя типа
        self.items = []              # список (timestamp, message)

    @abstractmethod
    def create_notification(self, msg: str, timestamp: datetime = None):
        pass

    def get_all_notifications(self):
        return list(self.items)

    def clear(self):
        self.items = []

    def _add(self, msg: str, timestamp: datetime = None):
        if timestamp is None:
            timestamp = datetime.now()
        self.items.append((timestamp, msg))


class ErrorNotification(ParentNotification):
    """Ошибки — мешают работе программы (некорректный ввод, отсутствие файла и т.п.)."""
    def __init__(self):
        super().__init__("ERROR")

    def create_notification(self, msg: str, timestamp: datetime = None):
        self._add(msg, timestamp)


class WarningNotification(ParentNotification):
    """Ворнинги — мешают, но не фатально (петли, кратные рёбра, дубликаты)."""
    def __init__(self):
        super().__init__("WARNING")

    def create_notification(self, msg: str, timestamp: datetime = None):
        self._add(msg, timestamp)


class MessageNotification(ParentNotification):
    """Сообщения — информируют об уже сделанном (успешные действия)."""
    def __init__(self):
        super().__init__("MESSAGE")

    def create_notification(self, msg: str, timestamp: datetime = None):
        self._add(msg, timestamp)


class NoteNotification(ParentNotification):
    """Заметки — альтернативные методы, советы, дополнительная информация."""
    def __init__(self):
        super().__init__("NOTE")

    def create_notification(self, msg: str, timestamp: datetime = None):
        self._add(msg, timestamp)


class Notification:
    """
    Единый менеджер всех видов уведомлений.
    Хранит объекты всех 4 типов и предоставляет к ним доступ.
    """
    def __init__(self):
        self.error   = ErrorNotification()
        self.warning = WarningNotification()
        self.message = MessageNotification()
        self.note    = NoteNotification()

    # --- Добавление уведомлений ---
    def add_error(self, msg: str, timestamp: datetime = None):
        self.error.create_notification(msg, timestamp)

    def add_warning(self, msg: str, timestamp: datetime = None):
        self.warning.create_notification(msg, timestamp)

    def add_message(self, msg: str, timestamp: datetime = None):
        self.message.create_notification(msg, timestamp)

    def add_note(self, msg: str, timestamp: datetime = None):
        self.note.create_notification(msg, timestamp)

    # --- Получение всех уведомлений ---
    def get_all(self):
        return {
            'error':   self.error.get_all_notifications(),
            'warning': self.warning.get_all_notifications(),
            'message': self.message.get_all_notifications(),
            'note':    self.note.get_all_notifications(),
        }

    def count_all(self) -> int:
        return sum(
            len(items)
            for items in self.get_all().values()
        )

    # --- Очистка ---
    def clear_all(self):
        self.error.clear()
        self.warning.clear()
        self.message.clear()
        self.note.clear()