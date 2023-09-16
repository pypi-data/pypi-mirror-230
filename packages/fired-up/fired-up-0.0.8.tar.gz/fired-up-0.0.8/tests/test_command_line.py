import sys
from unittest.mock import patch

from fired_up import FiredUp, Group, Menu

class SomeGroup(Group):
  def get_value(self):
    return "ok"

def test_all_from_command_line(capture):
  with patch.object(sys, "argv", ["test", "--all"]):
    with capture() as output:
      FiredUp(
        group1=SomeGroup,
        group2=SomeGroup,
        group3=SomeGroup,
        command="group1 get_value then group2 get_value then group3 get_value"
      )
    assert output == [ "ok" ] * 3
