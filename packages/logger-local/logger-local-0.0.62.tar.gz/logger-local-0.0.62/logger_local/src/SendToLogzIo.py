from logzio.handler import LogzioHandler
import sys
import os
LOGZIO_URL = "https://listener.logz.io:8071"
LOGZIO_TOKEN = os.getenv("LOGZIO_TOKEN")
class SendTOLogzIo():
    def __init__(self) -> None:
        self.logzio_handler = LogzioHandler(token=LOGZIO_TOKEN, url=LOGZIO_URL)
    
    def send_to_logzio(self, data):
            try:
                log_record = CustomLogRecord(
                    name="log",
                    level=data.get('severity_id'),
                    pathname=LOGZIO_URL,
                    lineno=data.get("line_number"),
                    msg=data.get('record'),
                    args=data,
                )
                self.logzio_handler.emit(log_record)
            except Exception as e:
                print(f"Failed to send log to Logz.io: {e}", file=sys.stderr)
class CustomLogRecord:
    def __init__(self, name, level, pathname, lineno, msg, args):
        self.name = name
        self.levelname = level
        self.pathname = pathname
        self.lineno = lineno
        self.msg = msg
        self.args = args
        self.exc_info = None
        self.exc_text = None
        self.stack_info = None

    def getMessage(self):
        msg = str(self.msg)
        if self.args:
            try:
                msg = self.msg.format(*self.args)
            except Exception as e:
                pass
        return msg
