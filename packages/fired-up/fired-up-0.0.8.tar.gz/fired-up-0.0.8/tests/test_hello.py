import json

from fired_up import FiredUp, Group

class Generator(Group):
  def a_reversed_list(self, lst):
    return list(reversed(lst))

class Dumper(Group):
  def as_json(self):
    return json.dumps(self.paste(), indent=2)

def test_hello(capture):
  with capture() as output:
    FiredUp(
      generate=Generator, dump=Dumper,
      command="generate a_reversed_list 1,a,2,b then dump as_json"
    )
  assert output == ['[', '  "b",', '  2,', '  "a",', '  1', ']']
