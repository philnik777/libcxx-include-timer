import os
import time
import sys
from utils import run_command

def printerr(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

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

def time_command(command : str) -> int:
  os.system(command)

for header in headers:
  print(f"{header},", end="")
  with open("testfile.cpp", "w") as file:
    file.write(f"#include <{header}>")
    file.close()

  for cxx_version in cxx_versions:
    printerr(f"Benchmarking <{header}>/{cxx_version}" + 20 * " ", end="\r")
    command = f"clang++-18 -std={cxx_version} -D_LIBCPP_REMOVE_TRANSITIVE_INCLUDES -nostdinc++ {include_paths} ./testfile.cpp -E -P | wc -c"
    print(f"{run_command(command)[:-1]}", end="\n" if cxx_version == "c++26" else ",")
