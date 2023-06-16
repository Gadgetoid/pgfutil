from .ui import PGFUtil

import sys

if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) == 2 else None
    PGFUtil(filename=filename)
