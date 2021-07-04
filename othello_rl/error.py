class OthelloRLError(Exception):
  """othello_rl内での例外の基底クラス"""
  pass

class CannotReverseError(OthelloRLError):
  """指定された座標にコマを設置できなかった時の例外"""
  pass

class ArgsError(OthelloRLError):
  """引数にありえない数を渡された時の例外"""
  pass

class GenFileNumError(OthelloRLError):
  """ファイルの生成数が規定値を超えた時の例外"""
  pass