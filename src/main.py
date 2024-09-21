import threading

import uvicorn

from worker.requestListener import app
from worker.gui.app import MainApp


def start_ui_app():
    ui_app = MainApp()
    ui_app.mainloop()


def start_request_listener(ip: str = "127.0.0.1", port: int = 5555):
    uvicorn.run(app, host=ip, port=port, log_level="info")


if __name__ == '__main__':
    ui_app_thread = threading.Thread(target=start_ui_app, daemon=True)
    request_listener_thread = threading.Thread(target=start_request_listener)

    ui_app_thread.start()
    request_listener_thread.start()
