from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import copy
import time
import os
import re
from utils import *

hostname = ""

header = """
<head>
  <title>libc++ Include Timer</title>
  <style>
  table {
    border: 1px solid black;
  }

  .tr_sub:nth-child(even) {
    background-color: #D6EEEE;
  }

  @media (prefers-color-scheme: dark) {
    body {
      background-color: grey;
    }

    .tr_sub:nth-child(even) {
      background-color: #AAAAAA;
    }
  }
  </style>
</head>
"""

body = """
<body>
  <h1>libc++ Include Timer</h1>
  {commits}
</body>
"""

def accumulate_table(table : Data) -> Data:
  out = Data([table.header])
  out.row_names = ["Accumulated"]
  out.rows = [table.rows[0]]

  for row in table.rows[1:]:
    for (index, el) in enumerate(row):
      out.rows[0][index] += el

  return out

def table_diff(lhs : Data, rhs : Data) -> Data:
  out = Data([lhs.header])
  out.row_names = lhs.row_names

  for (x, (lhs_row, rhs_row)) in enumerate(zip(lhs.rows, rhs.rows)):
    new_row = []
    for (y, (lhs_el, rhs_el)) in enumerate(zip(lhs_row, rhs_row)):
      new_row.append("{:.2f}".format((float(rhs_el - lhs_el) / lhs_el) * 100))
    out.rows.append(new_row)

  return out

def to_html_row(name, row) -> str:
  out = "<tr class=\"tr_sub\">"
  out += f"<th>{name}</th>"
  for entry in row:
    out += f"<th>{entry}</th>"
  out += "</tr>"

  return out

def to_html_table(table : Data) -> str:
  out = "<table>"

  out += "<tr class=\"tr_sub\">"
  for el in table.header:
    out += f"<th>{el}</th>"
  out += "</tr>"

  for (index, row) in enumerate(table.rows):
    out += to_html_row(table.row_names[index], row)

  out += "</table>"
  return out

def is_valid_commit(commit : str) -> bool:
  return "{:0>40x}".format(int(commit, 16)) == commit

class MyServer(BaseHTTPRequestHandler):
  def main_page_response(self):
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      recent_commits = get_recent_commits(75)

      recent_commits_list = "<table>"
      header_generated = False

      for (first_commit, second_commit) in zip(recent_commits, recent_commits[1:]):
        try:
          fc_content = load_table(first_commit)

          if not header_generated:
            recent_commits_list += to_html_row("commit", fc_content.header[1:])
            header_generated = True

          sc_content = load_table(second_commit)

          data = table_diff(accumulate_table(sc_content), accumulate_table(fc_content)).rows[0]
          data.append(f"<a href=\"/diff/{second_commit}/{first_commit}\">details</a>")
          commit_str = "<code><a href=\"https://github.com/llvm/llvm-project/commit/{0}\">{0}</a></code>".format(first_commit)
          recent_commits_list += to_html_row(commit_str, data)
        except FileNotFoundError:
          pass
        except IndexError:
          pass

      recent_commits_list += "</table>"

      self.wfile.write(bytes(f"<!DOCTYPE html><html>{header}{body.format(commits=recent_commits_list)}</html>", "utf-8"))

  def detailed_commit_info(self, commits : str):
    commits = commits.split('/')
    if len(commits) != 2 or not is_valid_commit(commits[0]) or not is_valid_commit(commits[1]):
      print(f"Invalid commits: {commits}, {f1}, {f2}")
      self.send_response(404)
      return

    commit_info = to_html_table(table_diff(load_table(commits[0]), load_table(commits[1])))

    self.wfile.write(bytes(f"<!DOCTYPE html><html>{header}{body.format(commits=commit_info)}</html>", "utf-8"))

  def dashboard(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    images = ""
    for file in sorted(os.listdir("dashboard")):
      file_name = file
      images += f"<img src=\"/dashboard/{file_name}\" style=\"width: 19vw\">"
    self.wfile.write(bytes(f"<!DOCTYPE html><html>{header}{body.format(commits=images)}</html>", "utf-8"))

  def dashboard_png(self, pic : str):
    pic = pic.removeprefix("/dashboard/")
    if not pic.endswith(".png") or pic.removesuffix(".png") not in headers:
      self.send_response(404)
      return
    print(pic)
    self.send_response(200)
    self.send_header("Content-type", "image/png")
    self.end_headers()
    self.wfile.write(open(f"dashboard/{pic}", "rb").read())

  def raw(self, file : str):
    file = file.removeprefix("/raw/")

    self.send_response(200)
    self.send_header("Content-type", "text/plain")
    self.end_headers()

    if (file.startswith("latest_commits/")):
      self.wfile.write(get_recent_commits_string(int(file.removeprefix("latest_commits/"))).encode())
      return

    if (file.startswith("commit/")):
      commit = file.removeprefix("commit/")
      if not is_valid_commit(commit):
        return
      self.wfile.write(open(f"include_time_db/{commit}", "r").read().encode())

  def do_GET(self):
    if self.path in ['/', '/index.html']:
      self.main_page_response()
    elif self.path.startswith('/diff/'):
      self.detailed_commit_info(self.path.removeprefix('/diff/'))
    elif self.path in ["/dashboard", "/dashboard/"]:
      self.dashboard()
    elif self.path.startswith("/dashboard/"):
      self.dashboard_png(self.path)
    elif self.path.startswith("/raw/"):
      self.raw(self.path)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--port", default=80)
  args = parser.parse_args()

  webserver = HTTPServer((hostname, int(args.port)), MyServer)
  print("Server Started!")

  webserver.serve_forever()
