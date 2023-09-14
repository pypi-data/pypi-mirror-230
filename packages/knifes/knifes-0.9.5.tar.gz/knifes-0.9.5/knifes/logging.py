import logging
from knifes import alarm
from knifes.envconfig import config


class CriticalAlarmFilter(logging.Filter):
    def filter(self, record):
        if record.levelno == logging.CRITICAL:
            msg = f"[{record.module}]{record.getMessage()}"
            if config('NODE_ID'):
                msg = f"[{config('NODE_ID')}]" + msg
            alarm.async_send_msg(msg)
        return True
