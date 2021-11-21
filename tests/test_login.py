import os
import shutil
from pathlib import Path

from tests.run_script import run_script

run_script("tenant --add ts --app_id=cli_a118840434781013 --app_secret=RTP8uNM9xb38j9U6SxCuCeHnoN4oqkDT")
run_script("tenant --add dx --app_id=cli_a11889b35179d013 --app_secret=yC4AJt2jM7FV2gIc1CEIVhryiWoc21B8")

p = Path.home() / 'tmp/fda/new_ws'
p.mkdir(exist_ok=True, parents=True)
os.chdir(p)

run_script("init")
run_script('info --all')

run_script("login -n ts")
run_script('info --all')

run_script("login -o")
run_script('info --all')

run_script("login -n dx")
run_script('info --all')

run_script("login -o")
run_script('info --all')

run_script("login -n dx")
run_script('info --all')

os.chdir(p.parent)
shutil.rmtree(p)
