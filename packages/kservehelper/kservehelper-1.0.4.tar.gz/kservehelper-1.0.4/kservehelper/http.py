import os
import signal
import uvicorn
import threading
import socket


class Server(uvicorn.Server):
    def start(self) -> None:
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def stop(self) -> None:
        self.should_exit = True
        self._thread.join(timeout=5)
        if not self._thread.is_alive():
            return

        self.force_exit = True
        self._thread.join(timeout=5)
        if not self._thread.is_alive():
            return
        os.kill(os.getpid(), signal.SIGKILL)


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0
