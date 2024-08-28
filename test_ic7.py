import random
import time

from dupal_client import DuPALClient

client = DuPALClient(port="COM4")


def _reset_board():
    if client._serial.is_open:
        client._serial.dtr = True
        time.sleep(1)
        client._serial.dtr = False


_reset_board()
client.send_command("x")
client.receive_response()  # "DuPAL - 0.1.2"
client.receive_response()  # empty line
client.receive_response()  # "REMOTE_CONTROL_ENABLED"
client.control_led(1, 1)

cache = {}

for input in range(2**10):
    client.write_status(input)
    out = client.read_status()
    print(".", end="")
    cache[input] = out
# try all possible outputs
out_to_in = {}
for key, val in cache.items():
    if val not in out_to_in:
        out_to_in[val] = key
for output, first_input in out_to_in.items():
    print(f"Processing output: {output}...")
    for second_input in range(2 ** 10):
        client.write_status(first_input)  # set desired output
        client.write_status(second_input)
        out = client.read_status()
        if cache[second_input] != out:
            print("*** MISMATCH!")
            with open('C:\\Work\\pal_tester\\ic7.txt', 'a', encoding="utf-8") as file:
                file.write("*** MISMATCH!\n")
        print(f"{first_input} {second_input} {out}")
        with open('C:\\Work\\pal_tester\\ic7.txt', 'a', encoding="utf-8") as file:
            file.write(f"{first_input} {second_input} {out}\n")
