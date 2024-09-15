import serial
import time
import re
from typing import Optional


class DuPalClient:
    def __init__(self, port: str, delay: float = 0.01):
        self._serial = serial.Serial(port, baudrate=57600)
        self._delay = delay

    def init_board(self):
        self.reset_board()
        self.send_command("x")
        self.receive_response()  # "DuPAL - 0.1.2"
        self.receive_response()  # empty line
        self.receive_response()  # "REMOTE_CONTROL_ENABLED"
        self.control_led(1, 1)  # WARNME: we only support 20-pin PALs

    def reset_board(self):
        if self._serial.is_open:
            self._serial.dtr = True
            time.sleep(1)
            self._serial.dtr = False

    def send_command(self, command: str) -> str:
        self._serial.write(command.encode())
        time.sleep(self._delay)  # Allow some time for the response
        return self.receive_response()

    def receive_response(self) -> str:
        response: str = self._serial.read_until().decode().strip()
        return response

    def write_status(self, status: int) -> str:
        command: str = f">W {status:08X}<"
        response: str = self.send_command(command)
        expected_response: str = f"[W {status:08X}]"
        if response != expected_response:
            raise ValueError(f"Unexpected response: {response}")
        return response

    def read_status(self) -> int:
        response: str = self.send_command(">R<")
        match = re.match(r"\[R ([0-9A-F]{2})\]", response)
        if not match:
            raise ValueError(f"Unexpected response: {response}")
        return int(match.group(1), 16)

    def reset(self) -> None:
        response: Optional[str] = self.send_command(">L<")
        if response:
            raise ValueError(f"Unexpected response on reset: {response}")

    def exit(self) -> None:
        response: Optional[str] = self.send_command(">X<")
        if response:
            raise ValueError(f"Unexpected response on exit: {response}")

    def model(self) -> int:
        response: str = self.send_command(">M<")
        match = re.match(r"\[M ([0-9A-F]{2})\]", response)
        if not match:
            raise ValueError(f"Unexpected response: {response}")
        return int(match.group(1), 16)

    def control_led(self, led_bit: int, on_off: int) -> str:
        led_status: int = (led_bit << 1) | on_off
        command: str = f">L {led_status:02X}<"
        response: str = self.send_command(command)
        expected_response: str = f"[L {led_status:02X}]"
        if response != expected_response:
            raise ValueError(f"Unexpected response: {response}")
        return response

    def close(self):
        self._serial.close()
