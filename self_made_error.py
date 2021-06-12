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

class OthelloError(SelfMadeError):
  """
  オセロ関係の例外
  """
  pass

class OthelloCannotReverse(OthelloError):
  """
  指定された座標にコマを設置できなかった時の例外
  """
  pass