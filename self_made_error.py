class SelfMadeError(Exception):
  """
  オセロの中での例外
  """
  pass

class ArgsError(SelfMadeError):
  """
  引数にありえない数を渡された時の例外
  """
  pass

class EmptyListError(SelfMadeError):
  """
  意図せずに空リストが作成されてしまった時の例外
  """
  pass