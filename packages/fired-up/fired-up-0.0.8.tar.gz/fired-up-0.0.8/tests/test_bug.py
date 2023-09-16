from fired_up import Group

class IsolatedGroup(Group):
  def set_global_var(self):
    self._globals["test"] = "hello"

def test_hello():
  # triggers bug where self._shared is None
  g = IsolatedGroup()
  g.set_global_var()
