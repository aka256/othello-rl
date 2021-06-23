class OthelloError(Exception):
  """othello_pack内での例外の基底クラス"""
  pass

class CannotReverseError(OthelloError):
  """指定された座標にコマを設置できなかった時の例外"""
  pass

class ArgsError(OthelloError):
  """引数にありえない数を渡された時の例外"""
  pass