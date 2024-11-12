from http.server import BaseHTTPRequestHandler, HTTPServer
import copy
import time
import os
import re
from utils import run_command, get_recent_commits, load_table, Data, headers

hostname = ""
port = 80

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

recent_commits_command = "(cd repo && git rev-list --max-count=50 HEAD -- libcxx/)"

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

class MyServer(BaseHTTPRequestHandler):
  def main_page_response(self):
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      recent_commits = get_recent_commits(50)

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
    if len(commits) != 2 or "{:0>40x}".format(int(commits[0], 16)) != commits[0] or "{:0>40x}".format(int(commits[1], 16)) != commits[1]:
      print(f"Invalid commits: {commits}, {f1}, {f2}")
      self.send_response(404)
      return

    commit_info = to_html_table(table_diff(load_table(commits[0]), load_table(commits[1])))

    self.wfile.write(bytes(f"<!DOCTYPE html><html>{header}{body.format(commits=commit_info)}</html>", "utf-8"))

  def dashboard(self):
    body = ""
    for file in sorted(os.listdir("../dashboard")):
      file_name = file
      body += f"<img src=\"/dashboard/{file_name}\">"
    self.wfile.write(bytes(f"<!DOCTYPE html><html>{header}{body.format(commits=body)}</html>", "utf-8"))

  def dashboard_png(self, pic : str):
    pic = pic.removeprefix("/dashboard/")
    if not pic.endswith(".png") or pic.removesuffix(".png") not in headers:
      self.send_response(404)
      return
    print(pic)
    self.send_response(200)
    self.send_header("Content-type", "image/png")
    self.end_headers()
    self.wfile.write(open(f"../dashboard/{pic}", "rb").read())

  def invalid_response(self):
    self.send_response(404)

  def do_GET(self):
    if self.path in ['/', '/index.html']:
      self.main_page_response()
    elif self.path.startswith('/diff/'):
      self.detailed_commit_info(self.path.removeprefix('/diff/'))
    elif self.path in ["/dashboard", "/dashboard/"]:
      self.dashboard()
    elif self.path.startswith("/dashboard/"):
      self.dashboard_png(self.path)
    else:
      self.invalid_response()

if __name__ == "__main__":
  webserver = HTTPServer((hostname, port), MyServer)
  print("Server Started!")

  webserver.serve_forever()
