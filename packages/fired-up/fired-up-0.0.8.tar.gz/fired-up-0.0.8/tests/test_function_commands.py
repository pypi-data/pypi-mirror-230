import json

from fired_up import FiredUp

def test_function_command(capture):
  def funky_command():
    return "groovy..."

  def funky_command2():
    return "baby!"
    
  with capture() as output:
    FiredUp(
      funky=funky_command,
      baby=funky_command2,
      command="funky then baby",
      all_results=True
    )
  assert output == ["groovy...", "baby!"]
