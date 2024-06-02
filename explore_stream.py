# initial state
outputs_prev = 0b11101100
# open output.txt and read all the lines
with open("C:\\Work\\pal_tester\\stream_no_clock.txt", "r") as file:
    lines = file.readlines()
# process lines two by two
for inputs, outputs in zip(lines[0::2], lines[1::2]):
    if inputs == "Clock\n":
        print("clock")
        print(f"registers: {int(outputs)[3:7]}")
    # otherwise, set the inputs and read the outputs
    else:
        # print outputs in binary
        print(f"{outputs_prev} -> {int(inputs)} -> {int(outputs)}")
        outputs_str = f"{int(outputs):08b}"
        # print(outputs_str)
        print(f"{outputs_prev:08b}{int(inputs):08b} -> {outputs_str[:3]}({outputs_str[3:7]}){outputs_str[7:]}")
        outputs_prev = int(outputs)
    # wait for a key press
    input("Press Enter to continue...")
