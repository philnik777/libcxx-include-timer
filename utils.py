import subprocess

def run_command(command : str) -> str:
  result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
  return result.stdout.decode("utf-8")
