"""
(c) ZL-2020.
@author ZhaoLei
@since 2020.07.23 12:27
"""
import os
import logging


class Logger(object):
    class COLOR():
        WHITE = '\033[0m'
        BLACK = '\033[30m'
        DARK_GRAY = '\033[90m'
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        PINK = '\033[95m'
        LIGHT_BLUE = '\033[96m'
        GRAY = '\033[98m'
        TRANSPARENT = '\033[8m'  # HIDEN
        REVERSE = '\033[7m'  # similar to Logger.BG_WHITE + Logger.BLACK
        BG_GRAY = '\033[100m'
        BG_RED = '\033[101m'
        BG_YELLOW = '\033[103m'
        BG_BLUE = '\033[104m'
        BG_PINK = '\033[105m'
        BG_LIGHT_BLUE = '\033[106m'
        BG_WHITE = '\033[107m'

        END = WHITE
        OK = GREEN
        INFO = BLUE
        WARNING = YELLOW
        CRITICAL = RED
        ERROR = RED
        EXCEPTION = RED
        ASSERT = PINK

    class TYPE():
        # can be combined with above (test on gnome terminal)
        BOLD = '\033[1m'
        ITALIC = '\033[3m'
        UNDERLINE = '\033[4m'
        DELLINE = '\033[9m'

    def __init__(self, log_dir, local_rank=0, log_name='train.log'):
        self.local_rank = local_rank
        if self.local_rank > 0:
            return
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.file_log = logging.FileHandler(f'{log_dir}/{log_name}', mode='a+')
        self.file_log.setLevel(logging.INFO)  # record above INFO level log
        formatter = logging.Formatter('%(asctime)s %(message)s', '%m-%d %H:%M:%S')
        self.file_log.setFormatter(formatter)
        console_log = logging.StreamHandler()
        console_log.setLevel(logging.DEBUG)
        formatter = logging.Formatter(f'{Logger.COLOR.GREEN}%(asctime)s{Logger.COLOR.END} %(message)s', "%m-%d %H:%M:%S")
        console_log.setFormatter(formatter)
        self.logger.addHandler(self.file_log)
        self.logger.addHandler(console_log)
        self.logger.propagate = False  # avoid duplicated logger msg

    @staticmethod
    def zstr(mstr, style='\033[95m'):  # default pink; color str
        return f'{style}{mstr}{Logger.COLOR.END}'

    @staticmethod
    def zprint(msg, local_rank=0, style='\033[98m'):  # default gray; only use it before instantiating Logger
        if local_rank > 0:
            return
        msg = f'{style}{msg}{Logger.COLOR.END}'
        print(msg)

    def debug(self, msg, style='\033[98m'):  # default gray; no record
        if self.local_rank > 0:
            return
        self.logger.debug(f'{style}{msg}{Logger.COLOR.END}')

    def info(self, msg, rec=True):
        if self.local_rank > 0:
            return
        msg = f'{(Logger.COLOR.INFO + " ") if rec else Logger.INFO}{msg}{Logger.COLOR.END}'
        self.logger.info(msg) if rec else print(msg)

    def warning(self, msg, rec=True):
        if self.local_rank > 0:
            return
        msg = f'{(Logger.COLOR.WARNING + " ") if rec else Logger.COLOR.WARNING}WRN: {msg}{Logger.COLOR.END}'
        self.logger.warning(msg) if rec else print(msg)

    def critical(self, msg, rec=True):
        if self.local_rank > 0:
            return
        msg = f'{(Logger.COLOR.CRITICAL + " ") if rec else Logger.COLOR.CRITICAL}CRI: {msg}{Logger.COLOR.END}'
        self.logger.critical(msg) if rec else print(msg)

    def error(self, msg, rec=True):
        if self.local_rank > 0:
            return
        msg = f'{(Logger.COLOR.ERROR + " ") if rec else Logger.COLOR.ERROR}ERR: {msg}{Logger.COLOR.END}'
        self.logger.error(msg) if rec else print(msg)

    # record try/except Exception StackTrace, like traceback.print_exc()
    def exception(self, msg, rec=True):
        if self.local_rank > 0:
            return
        msg = f'{(Logger.COLOR.EXCEPTION + " ") if rec else Logger.COLOR.EXCEPTION}EXCEP: {msg}{Logger.COLOR.END}'
        self.logger.exception(msg) if rec else print(msg)

    def blank_line(self):
        if self.local_rank > 0:
            return
        self.logger.info('\n')

    def enable_record_log(self, enable):
        if self.local_rank > 0:
            return
        if enable:
            self.file_log.setLevel(logging.INFO)
        else:
            self.file_log.setLevel(logging.CRITICAL)


if __name__ == "__main__":
    Logger.zprint('test 10086 hahaha',
        style=Logger.COLOR.BG_GRAY + Logger.COLOR.PINK + Logger.TYPE.UNDERLINE + Logger.TYPE.BOLD + Logger.TYPE.ITALIC)
