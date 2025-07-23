import os
import sys


def main():
    # Always run the GUI app from the GUI/main.py entry point
    gui_main = os.path.join(os.path.dirname(__file__), "GUI", "main.py")
    sys.argv = [gui_main] + sys.argv[1:]
    with open(gui_main) as f:
        code = compile(f.read(), gui_main, "exec")
        exec(code, {"__name__": "__main__"})


if __name__ == "__main__":
    main()
