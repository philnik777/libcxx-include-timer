import subprocess


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

def run_command(command : str, timeout=60) -> str:
  result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, timeout=timeout)
  return result.stdout.decode("utf-8")

def get_recent_commits_string(count : int) -> str:
  return run_command(f"(cd repo && git rev-list --max-count={count} HEAD -- libcxx/)")

def get_recent_commits(count : int) -> [str]:
  return get_recent_commits_string(count).splitlines()

def data_to_table(table : str) -> [[str]]:
  out = []

  for row in table.splitlines():
    out.append(row.split(','))

  return out

class Data:

  def __init__(self, table : [[str]]):
    self.header = []
    self.row_names = []
    self.rows = []

    self.header = table[0]
    for row in table[1:]:
      self.row_names.append(row[0])
      a_row = []
      for el in row[1:]:
        a_row.append(int(el))
      self.rows.append(a_row)

def load_table(commit : str) -> Data:
  file = open(f"include_time_db/{commit}", "r")
  return Data(data_to_table(file.read()))
