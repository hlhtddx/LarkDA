import os
import shutil
from pathlib import Path

from tests.run_script import run_script
p = Path.home() / 'tmp/fda/new_ws_ts'
p.mkdir(exist_ok=True, parents=True)
os.chdir(p)

run_script("init")
run_script("login -n ts")
run_script("pull -r -s -m")
run_script("pull -r -m")
