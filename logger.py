import logging
import asyncio
import sys
import enum
from colorama import init, Fore, Style
from platform import system
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

# Функция для логирования
async def log(message: str, level:LogLevel = LogLevel.INFO):
    """Асинхронное логирование"""
    if level == LogLevel.DEBUG:
        logger.debug(message)
    elif level == LogLevel.INFO:
        logger.info(message)
    elif level == LogLevel.WARNING:
        logger.warning(message)
    elif level == LogLevel.ERROR:
        logger.error(message)
    elif level == LogLevel.CRITICAL:
        logger.critical(message)
    else:
        logger.info(f"UNKNOWN LEVEL: {message}")

def log_sync(message: str, level:LogLevel = LogLevel.INFO):
    """Синхронная функция для логирования (отправляет в event loop)"""
    asyncio.run_coroutine_threadsafe(log(message,level), loop)