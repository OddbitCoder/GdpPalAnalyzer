from itertools import combinations


def bstr8(number: int, hi_z_mask: int = 0) -> str:
    binary_str = f"{number:08b}"
    mask_str = f"{hi_z_mask:08b}"
    result_str = "".join("Z" if mask_str[i] == "1" else binary_str[i] for i in range(8))
    return f"{result_str[:3]}_{result_str[3:7]}_{result_str[7:8]}"


def bstr18(number: int, hi_z_mask: int = 0):
    binary_str = f"{number:018b}"
    mask_str = f"{hi_z_mask:018b}"
    result_str = "".join(
        "Z" if mask_str[i] == "1" else binary_str[i] for i in range(18)
    )
    return f"{result_str[:2]}_{result_str[2:8]}_{result_str[8:]}"


def binv18(number):
    bit_length = 18
    mask = (1 << bit_length) - 1
    return number ^ mask


def bcomb(number):
    # Get positions of all "1" bits in the binary representation of the number
    ones_positions = [i for i in range(number.bit_length()) if number & (1 << i)]
    # Generate all subsets of these positions
    combinations_list = []
    for r in range(len(ones_positions) + 1):
        combinations_list.extend(combinations(ones_positions, r))
    # Generate numbers for each subset
    results = []
    for subset in combinations_list:
        new_number = number
        for pos in subset:
            new_number &= binv18(1 << pos)  # Set the bit at position "pos" to 0
        results.append(new_number)
    return sorted(results)
