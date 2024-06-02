from pal import Pal16R4DuPAL

pal = Pal16R4DuPAL(port="COM5")
# open file for writing
with open("stream_no_clock.txt", "w") as file:
    while True:
        if False:  # random.randint(0, 3) == 0:
            pal.clock()
            file.write("Clock\n")
        else:
            inputs = random.randint(0, 255)
            inputs = inputs | 0b10000000
            file.write(f"{str(inputs)}\n")
            pal.set_inputs(inputs)
        pal.read_outputs()
        file.write(f"{str(pal.outputs_as_byte)}\n")
        print(pal)
        time.sleep(0.1)
        file.flush()
