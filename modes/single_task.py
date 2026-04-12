import argparse
import sys
import time
import threading
import itertools
from agent import run_agent

SPINNER_CHARS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

SPINNER_PHRASES = [
    "cooking up a response...",
    "thinking hard...",
    "giving you the best answer...",
    "on it...",
    "brewing something good...",
    "connecting the dots...",
    "working my magic...",
    "almost there...",
]

def spinner(stop_event):
    char_cycle = itertools.cycle(SPINNER_CHARS)
    phrase_cycle = itertools.cycle(SPINNER_PHRASES)
    phrase = next(phrase_cycle)
    phrase_timer = time.time()
    while not stop_event.is_set():
        if time.time() - phrase_timer > 3:
            phrase = next(phrase_cycle)
            phrase_timer = time.time()
        char = next(char_cycle)
        sys.stdout.write(f"\r{char} {phrase:<50}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 55 + "\r")
    sys.stdout.flush()

def run_with_spinner(task):
    stop_event = threading.Event()
    t = threading.Thread(target=spinner, args=(stop_event,), daemon=True)
    t.start()
    try:
        run_agent(task)
    finally:
        stop_event.set()
        t.join()

def main():
    parser = argparse.ArgumentParser("lapis")
    parser.add_argument("task", type=str, nargs='?', help="The task for the agent")
    args = parser.parse_args()

    if args.task:
        task = args.task
    else:
        task = input("what we doin??: ")

    if task:
        run_with_spinner(task)
    else:
        print("Bye")

if __name__ == '__main__':
    main()