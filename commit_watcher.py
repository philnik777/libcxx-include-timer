import os
import time
import subprocess

CMakeCommand = 'CC=clang CXX=clang++ cmake -G Ninja -DLLVM_ENABLE_RUNTIMES="libcxx;libcxxabi;libunwind" ../runtimes'

def run_command(command : str) -> str:
  result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
  return result.stdout.decode("utf-8")

while True:
  os.system("(cd repo && git fetch)")
  if os.system("(cd repo && git diff origin/main --quiet)") == 0:
    print("no commit to check")
    time.sleep(60)
    continue
  commits = run_command("(cd repo && git rev-list HEAD..origin -- libcxx/)").splitlines()
  for commit in commits[::-1]:
    print(f"Checking commit {commit}")
    os.system(f"(cd repo && git checkout {commit})")
    if os.system(f"(cd repo && rm -rf build/ && mkdir build && cd build && {CMakeCommand} && ninja)") != 0:
      print("libc++ build failed!")
    else:
      os.system(f"python include_times.py > ../include_time_db/{commit}")

  os.system("(cd repo && git checkout origin/main)")
