import sys
from single_task import run_with_spinner
from agent import run_agent_multiturn


def main():
    args = sys.argv[1:]

    if not args:
        task = input("what we doin??: ").strip()
        if task:
            run_with_spinner(task)
        else:
            print("Bye")

    elif args[0].lower() == "convo":
        run_agent_multiturn()

    else:
        # everything else is treated as a task
        task = " ".join(args)
        run_with_spinner(task)


if __name__ == "__main__":
    main()