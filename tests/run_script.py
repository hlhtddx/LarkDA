import subprocess
import sys
from pathlib import Path


exec_path = Path(__file__).parent.parent
exec_path = exec_path.absolute()
python_path = sys.executable
main_py = (exec_path / 'main.py').absolute()


def run_script(param):
    subprocess.run(f"{python_path} {main_py} {param}".split(' '))
