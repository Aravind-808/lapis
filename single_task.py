import argparse
import sys
import time
import threading
from agent import run_agent

SPINNER_CHARS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

def spinner(stop_event):
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{SPINNER_CHARS[idx % len(SPINNER_CHARS)]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write("\r ")
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