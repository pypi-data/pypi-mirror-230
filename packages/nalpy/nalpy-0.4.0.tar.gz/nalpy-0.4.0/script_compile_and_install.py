from glob import glob
from subprocess import call

CYAN = "\033[36m"
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

cython_path: str = "cython"
pip_path: str = "pip"

cython_files: list[str] = glob("**/*.pyx", recursive=True)
print(f"Found {len(cython_files)} Cython files.")
for file in cython_files:
    print(CYAN + f"Compiling file '{file}'..." + RESET)
    retcode = call(f"{cython_path} \"{file}\"")
    if retcode == 0:
        print(GREEN + "Compilation successful." + RESET)
    else:
        print(RED + "Compilation failed." + RESET)
        exit(retcode)

print(CYAN + "Installing package..." + RESET)
retcode = call(f"{pip_path} install .")
if retcode == 0:
    print(GREEN + "Install successful." + RESET)
else:
    print(RED + "Install failed." + RESET)
    exit(retcode)
