import os
import time
from utils import run_command, get_recent_commits, load_table
from matplotlib import pyplot as plt
import pandas as pd

CMakeCommand = 'CC=clang-18 CXX=clang++-18 cmake -G Ninja -DLLVM_ENABLE_RUNTIMES="libcxx;libcxxabi;libunwind" ../runtimes'

def generate_time_plots():
  header_info = {}
  recent_commits = get_recent_commits(200)[::-1]

  for commit in recent_commits:
    try:
      print(f"Commit: {commit}")
      table = load_table(commit)
    except FileNotFoundError:
      continue
    for (name, row) in zip(table.row_names, table.rows):
      if not name in header_info:
          header_info[name] = []
      header_info[name].append((table.header[1::], row))

  for (name, data) in header_info.items():
    by_version = {}
    for (versions, values) in data:
      for (version, value) in zip(versions, values):
        if version not in by_version:
          by_version[version] = []
        by_version[version].append(value)
    print(pd.DataFrame(by_version))
    plt.ticklabel_format(style="plain")
    plt.plot(pd.DataFrame(by_version), label=name)
    plt.legend(by_version.keys())
    plt.title(name)
    plt.savefig(f"dashboard/{name}.png")
    plt.close()

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
      os.system(f"python ../include_times.py > include_time_db/{commit}")

  if len(commits) != 0:
    generate_time_plots()

  os.system("(cd repo && git checkout origin/main)")
