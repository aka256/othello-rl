from abc import ABCMeta, abstractmethod
from othello import OthelloBitBoard

class OthelloPositionalEvaluation(metaclass=ABCMeta):
  """
  局面評価クラスの抽象クラス
  """
  @abstractmethod
  def eval(self, othello: OthelloBitBoard, reverse_eval: bool) -> int:
    """
    局面評価
    
    Parameters
    ----------
    othello : OthelloBitBoard
      評価したい局面
    reverse_eval : bool
      評価値を反転するか否か

    Returns
    -------
    eval : int
      評価値
    """
    pass

class OthelloPositionalEvaluationv1(OthelloPositionalEvaluation):
  """
  局面評価v1

  Attributes
  ----------
  weight : list[list[int]]
    盤面の重みづけ

  Notes
  -----
  以下のサイトを参考にした
  https://uguisu.skr.jp/othello/5-1.html
  """
  weight = [[120, -20, 20, 5, 5, 20, -20, 120],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [120, -20, 20, 5, 5, 20, -20, 120]]
  def eval(self, othello: OthelloBitBoard, reverse_eval: bool = False) -> int:
    """
    局面評価

    Parameters
    ----------
    othello : OthelloBitBoard
      評価したい局面
    reverse_eval : bool
      評価値を反転するか否か

    Returns
    -------
    eval : int
      評価値
    """
    retval = 0
    idx = 1
    for i in range(8):
      for j in range(8):
        #idx = 1 << (i*8+j)
        if othello.board[0] & idx:
          retval += self.weight[i][j]
        elif othello.board[1] & idx:
          retval -= self.weight[i][j]
        idx <<= 1

    if reverse_eval:
      retval *= -1
    
    return retval


class OthelloPositionalEvaluationv2(OthelloPositionalEvaluation):
  """
  局面評価v2

  Attributes
  ----------
  weight : list[list[int]]
    盤面の重みづけ

  Notes
  -----
  以下のサイトを参考にした
  https://uguisu.skr.jp/othello/5-1.html
  """
  weight = [[30, -12, 0, -1, -1, 0, -12, 30],
            [-12, -15, -3, -3, -3, -3, -15, -12],
            [0, -3, 0, -1, -1, 0, -3, 0],
            [-1, -3, -1, -1, -1, -1, -3, -1],
            [-1, -3, -1, -1, -1, -1, -3, -1],
            [0, -3, 0, -1, -1, 0, -3, 0],
            [-12, -15, -3, -3, -3, -3, -15, -12],
            [30, -12, 0, -1, -1, 0, -12, 30]]
  def eval(self, othello: OthelloBitBoard, reverse_eval: bool = False) -> int:
    """
    局面評価
    
    Parameters
    ----------
    othello : OthelloBitBoard
      評価したい局面
    reverse_eval : bool
      評価値を反転するか否か

    Returns
    -------
    eval : int
      評価値
    """
    retval = 0
    idx = 1
    for i in range(8):
      for j in range(8):
        #idx = 1 << (i*8+j)
        if othello.board[0] & idx:
          retval += self.weight[i][j]
        elif othello.board[1] & idx:
          retval -= self.weight[i][j]
        idx <<= 1

    if reverse_eval:
      retval *= -1

    return retval