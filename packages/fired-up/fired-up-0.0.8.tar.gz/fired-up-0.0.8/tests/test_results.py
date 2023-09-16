from fired_up import FiredUp, Group, Menu

class SomeClass():
  def __str__(self):
    return "some class"

def get_value():
  return SomeClass()

def test_non_group_output(capture):
  with capture() as output:
    FiredUp(
      group1=get_value,
      command="group1"
    )
  assert output == [ "some class" ]


class AnotherClass(Group):
  @property
  def some_property(self):
    return SomeClass()

def test_non_group_output_using_property(capture):
  with capture() as output:
    FiredUp(
      group1=AnotherClass,
      command="group1 some_property"
    )
  assert output == [ "some class" ]
