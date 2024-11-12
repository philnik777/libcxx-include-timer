import http.client as hc
import os

from utils import run_command

"""
This script generates an environment for testing the webserver and commit watcher locally. It assumes that the public
page is available to download a chunk of the database instead of actually generating it with the commit watcher.
"""

def query_page(path : str) -> str:
  connection = hc.HTTPConnection("libcxx.klauser.berlin", 80)
  connection.request("GET", path)
  response = connection.getresponse()
  return response.read().decode("utf-8")


run_command("rm -rf webenv")
os.makedirs("webenv/include_time_db", exist_ok=True)

run_command("(cd webenv && git clone https://github.com/llvm/llvm-project.git repo)", timeout=None)

commits = query_page("/raw/latest_commits/100").split("\n")
for commit in commits[:-1]:
  with open(f"webenv/include_time_db/{commit}", "w") as file:
    file.write(query_page(f"/raw/commit/{commit}"))
