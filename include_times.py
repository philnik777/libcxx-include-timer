import os
import time
import sys

def printerr(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

program_time = time.time()

include_path_base = "repo/build"
include_paths = f"-I {include_path_base}/include/c++/v1/ -I {include_path_base}/include/x86_64-unknown-linux-gnu/c++/v1/"

headers = ["algorithm", "any", "array", "atomic", "barrier", "bit", "bitset", "cassert", "ccomplex", "cctype", "cerrno",
           "cfenv", "cfloat", "charconv", "chrono", "cinttypes", "ciso646", "climits", "clocale", "cmath", "codecvt",
           "compare", "complex", "concepts", "condition_variable", "coroutine", "csetjmp", "csignal", "cstdarg",
           "cstdbool", "cstddef", "cstdint", "cstdio", "cstdlib", "cstring", "ctgmath", "ctime", "cuchar", "cwchar",
           "cwctype", "deque", "exception", "execution", "expected", "filesystem", "format", "forward_list", "fstream",
           "functional", "future", "initializer_list", "iomanip", "ios", "iosfwd", "iostream", "istream", "iterator",
           "latch", "limits", "list", "locale", "map", "mdspan", "memory", "memory_resource", "mutex", "new", "numbers",
           "numeric", "optional", "ostream", "print", "queue", "random", "ranges", "ratio", "regex", "scoped_allocator",
           "semaphore", "set", "shared_mutex", "source_location", "span", "sstream", "stack", "stdexcept", "stop_token",
           "streambuf", "string", "string_view", "strstream", "syncstream", "system_error", "thread", "tuple",
           "type_traits", "typeindex", "typeinfo", "unordered_map", "unordered_set", "utility", "valarray", "variant",
           "vector", "version"]

cxx_versions = ["c++03", "c++11", "c++14", "c++17", "c++20", "c++23", "c++26"]

print(f"header,{','.join(cxx_versions)}")

def time_command(command : str, rerun_count = 10) -> int:
  nums = []
  for _ in range(rerun_count):
    start_time = time.time()
    os.system(command)
    nums.append((time.time() - start_time) * 1000)
  return int(sum(nums) / len(nums))

for header in headers:
  print(f"{header},", end="")
  with open("testfile.cpp", "w") as file:
    file.write(f"#include <{header}>")
    file.close()

  for cxx_version in cxx_versions:
    printerr(f"Benchmarking <{header}>/{cxx_version}" + 20 * " ", end="\r")
    command = f"clang++ -std={cxx_version} -D_LIBCPP_REMOVE_TRANSITIVE_INCLUDES -nostdinc++ {include_paths} ./testfile.cpp -c"
    print(f"{time_command(command)}", end="\n" if cxx_version == "c++26" else ",")

print(f"Overall time: {int((time.time() - program_time) / 60)}")
