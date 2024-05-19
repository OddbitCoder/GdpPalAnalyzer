import serial
import time
import re
from typing import Optional


class DuPALClient:
    def __init__(self, port: str):
        self.serial = serial.Serial(port, baudrate=57600)

    def send_command(self, command: str) -> str:
        self.serial.write(command.encode())
        time.sleep(0.1)  # Allow some time for the response
        return self.receive_response()

    def receive_response(self) -> str:
        response: str = self.serial.read_until().decode().strip()
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
        self.serial.close()


# Example of using the DuPALClient with structured return types
if __name__ == "__main__":
    client = DuPALClient("/dev/ttyUSB0")  # Change the port as necessary

    try:
        print("Model number: ", client.model())
        print("Pin Status as integer: ", client.read_status())
        print("Write Status: ", client.write_status(0x12345678))
        print("LED Control: ", client.control_led(1, 1))  # Turn on LED for 20 pin PAL
        client.reset()
        client.exit()
    except ValueError as e:
        print("Error: ", e)
    finally:
        client.close()
