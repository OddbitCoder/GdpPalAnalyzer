import random

from pal import Pal16R4DuPAL

pal = Pal16R4DuPAL(port="COM4")
pal.set_inputs(0)
prev_outputs = pal.read_outputs()
# open file for writing
with open("./reads/ic49/ic49_random_stream.txt", "w") as file:
    while True:
        if random.randint(0, 3) == 0:
            inputs = "clock"
            pal.clock()
        else:
            inputs = random.randint(0, 255)
            pal.set_inputs(inputs)
        pal.read_outputs()
        file.write(f"{prev_outputs} -> {inputs} -> {pal.outputs_as_byte}\n")
        outputs_str = f"{int(pal.outputs_as_byte):08b}"
        if inputs != "clock":
            file.write(
                f"{prev_outputs:08b}{int(inputs):08b} -> {outputs_str[:3]}({outputs_str[3:7]}){outputs_str[7:]}\n"
            )
        else:
            file.write(
                f"clock -> {outputs_str[:3]}({outputs_str[3:7]}){outputs_str[7:]}\n"
            )
        prev_outputs = pal.outputs_as_byte
        file.flush()
