from fired_up import FiredUp, Group, Menu

class SomeGroup(Group):
  def __init__(self, name, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._name = name

  def get_name(self):
    return self._name

def test_tuple_handler(capture):
  with capture() as output:
    FiredUp(
      group1=(SomeGroup, { "name": "group 1" } ),
      group2=(SomeGroup, { "name": "group 2" } ),
      group3=(SomeGroup, { "name": "group 3" } ),
      all_results=True,
      command="group1 get_name then group2 get_name then group3 get_name"
    )
  assert output == [ "group 1", "group 2", "group 3" ]
