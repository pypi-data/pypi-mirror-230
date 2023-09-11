from typing import List


def input_bounded_int(msg: str, lower: int, upper: int) -> int:
    while True:
        # ask for number and convert to integer
        try:
            num = int(input(msg))
        except ValueError:
            print("invalid integer")
            continue
        # check number lower and upper bounds
        if num < lower or num > upper:
            print(f"out of bounds - number must be between {lower} and {upper}")
            continue

        # return validated number
        return num

def input_from_list(msg: str, choices: List[str]) -> str:
    while True:
        ret = input(msg)
        if ret not in choices:
            print(f"your choice must be either of the following: {choices}")
            continue
        return ret