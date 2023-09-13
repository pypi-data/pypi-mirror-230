# =====================================
# generator=datazen
# version=3.1.2
# hash=fdf8a0f3e1e695c22194c690e11a432f
# =====================================
"""
userfs - Package's default entry-point.
"""

# built-in
import sys

# internal
from userfs.entry import main

if __name__ == "__main__":
    sys.exit(main(sys.argv))
