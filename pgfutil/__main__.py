import sys

from .ui import PGFUtil


def gui():
    filename = sys.argv[1] if len(sys.argv) == 2 else None
    PGFUtil(filename=filename)


if __name__ == '__main__':
    gui()
