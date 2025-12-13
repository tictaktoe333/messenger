
import os
import signal
import sys


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def signal_handler(_signum, _frame):
    """signal handler for SIGINT (Ctrl+C)"""
    clear_screen()
    print("Exiting...")
    sys.exit(0)


def setup_signal_handler():
    """sets up signal handler for SIGINT (Ctrl+C)"""
    signal.signal(signal.SIGINT, signal_handler)
