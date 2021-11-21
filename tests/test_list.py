import os
import shutil
from pathlib import Path

from tests.run_script import run_script
p = Path.home() / 'tmp/fda/new_ws_ts'
p.mkdir(exist_ok=True, parents=True)
os.chdir(p)

# run_script("init")
# run_script("login -n ts")
# run_script("list")
# run_script("list -r -s")
run_script("list -r . MySpace/doc MySpace")
run_script("list -r -s MySpace")
run_script("list -s MySpace")
