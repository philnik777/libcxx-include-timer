from http.server import BaseHTTPRequestHandler, HTTPServer
import copy
import time
import os
from utils import run_command

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

def data_to_table(table : str) -> [[str]]:
  out = []

  for row in table.splitlines():
    out.append(row.split(','))

  return out

def to_html_row(name, row) -> str:
  out = "<tr class=\"tr_sub\">"
  out += f"<th>{name}</th>"
  for entry in row:
    out += f"<th>{entry}</th>"
  out += "</tr>"

  return out

def load_table(commit : str) -> Data:
  file = open(f"../include_time_db/{commit}", "r")
  return Data(data_to_table(file.read()))

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
      recent_commits = run_command(recent_commits_command).splitlines()

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
          recent_commits_list += to_html_row(first_commit, data)
        except FileNotFoundError:
          pass
        except IndexError:
          pass

      recent_commits_list += "</table>"

      self.wfile.write(bytes(f"<!DOCTYPE html><html>{header}{body.format(commits=recent_commits_list)}</html>", "utf-8"))

  def detailed_commit_info(self, commits : str):
    commits = commits.split('/')
    if len(commits) != 2 or "{:x}".format(int(commits[0], 16)) != commits[0] or "{:x}".format(int(commits[1], 16)) != commits[1]:
      self.send_response(404)
      return

    commit_info = to_html_table(table_diff(load_table(commits[0]), load_table(commits[1])))

    self.wfile.write(bytes(f"<!DOCTYPE html><html>{header}{body.format(commits=commit_info)}</html>", "utf-8"))

  def invalid_response(self):
    self.send_response(404)

  def do_GET(self):
    if self.path in ['/', '/index.html']:
      self.main_page_response()
    elif self.path.startswith('/diff/'):
      self.detailed_commit_info(self.path.removeprefix('/diff/'))
    else:
      self.invalid_response()

if __name__ == "__main__":
  webserver = HTTPServer((hostname, port), MyServer)
  print("Server Started!")

  webserver.serve_forever()
