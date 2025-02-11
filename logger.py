import logging
import asyncio
import os
import sys
import enum
from colorama import init, Fore, Style
from platform import system
import inspect
if system() == 'Windows':
    init(autoreset=True)

class LogLevel(enum.Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

# Очередь логов
log_queue = asyncio.Queue()

class AsyncQueueHandler(logging.Handler):
    """Асинхронный обработчик логов с очередью"""
    def __init__(self, queue: asyncio.Queue):
        super().__init__()
        self.queue = queue

    def emit(self, record):
        self.queue.put_nowait(record)

async def log_writer():
    """Фоновая задача для записи логов"""
    while True:
        record = await log_queue.get()
        if record is None:
            break
        logger.handle(record)

# Настраиваем логгер
logger = logging.getLogger("project_logger")
logger.setLevel(logging.DEBUG)

class ColorFormatter(logging.Formatter):
    """Форматтер для логов с цветами"""

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA + Style.BRIGHT
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        formatted_message = super().format(record)
        return f"{log_color}{formatted_message}{Style.RESET_ALL}"

# Формат для логов
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColorFormatter("[%(asctime)s] [%(levelname)s] %(message)s"))


file_handler = logging.FileHandler("project.log", encoding="utf-8")
file_handler.setFormatter(formatter)

queue_handler = AsyncQueueHandler(log_queue)
queue_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(queue_handler)

loop = asyncio.new_event_loop()
loop.create_task(log_writer())  # Запуск фонового логгера


def extract_last_three_parts(file_path):
    # Разделяем путь на части
    parts = file_path.split(os.sep)

    # Убираем пустые строки, которые могут появиться из-за ведущего или завершающего разделителя
    parts = [part for part in parts if part]

    # Возвращаем последние три части или меньше, если их недостаточно
    return parts[-3:]
# Функция для логирования
async def log(message: str, level:LogLevel = LogLevel.INFO):
    # Получаем
    # текущий
    # фрейм(кадр)
    # выполнения
    current_frame = inspect.currentframe()

    # Получаем фрейм, который вызвал текущую функцию
    caller_frame = current_frame.f_back

    # Получаем имя файла, в котором была вызвана функция
    filename = caller_frame.f_code.co_filename

    # Получаем номер строки, на которой была вызвана функция
    lineno = caller_frame.f_lineno

    scripttext = f"[{str(os.sep).join(extract_last_three_parts(filename))}:{lineno}]"
    output = f"{scripttext} {message}"
    """Асинхронное логирование"""
    if level == LogLevel.DEBUG:
        logger.debug(output)
    elif level == LogLevel.INFO:
        logger.info(output)
    elif level == LogLevel.WARNING:
        logger.warning(output)
    elif level == LogLevel.ERROR:
        logger.error(output)
    elif level == LogLevel.CRITICAL:
        logger.critical(output)
    else:
        logger.info(f"UNKNOWN LEVEL: {output}")

def log_sync(message: str, level:LogLevel = LogLevel.INFO):
    """Синхронная функция для логирования (отправляет в event loop)"""
    asyncio.run_coroutine_threadsafe(log(message,level), loop)