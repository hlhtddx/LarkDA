import os
import shutil
from pathlib import Path

from tests.run_script import run_script
p = Path.home() / 'tmp/fda/new_ws'
p.mkdir(exist_ok=True, parents=True)
os.chdir(p)

run_script("info")
