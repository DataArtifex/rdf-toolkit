# SPDX-FileCopyrightText: 2024-present kulnor <pascal.heus@gmail.com>
#
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
