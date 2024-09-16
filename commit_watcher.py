import os
import time
from utils import run_command

CMakeCommand = 'CC=clang-18 CXX=clang++-18 cmake -G Ninja -DLLVM_ENABLE_RUNTIMES="libcxx;libcxxabi;libunwind" ../runtimes'

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
    if os.system(f"(cd repo && rm -rf build/ && mkdir build && cd build && {CMakeCommand} && ninja generate-cxx-headers)") != 0:
      print("libc++ build failed!")
    else:
      os.system(f"python include_times.py > ../include_time_db/{commit}")

  os.system("(cd repo && git checkout origin/main)")
