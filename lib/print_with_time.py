import time


def time_print(print_str: str) -> None:
    print('[' + time.strftime('%m/%d-%H:%M:%S') + ']' + print_str)
