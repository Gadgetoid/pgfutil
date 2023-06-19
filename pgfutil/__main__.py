import sys

from .ui import PGFUtil

if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) == 2 else None
    PGFUtil(filename=filename)
