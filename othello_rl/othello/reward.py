from abc import ABCMeta, abstractmethod
from othello_rl.othello.board import OthelloBoard, OthelloBoard4x4, OthelloBoard8x8

class Reward(metaclass=ABCMeta):
  """
  指定された盤面に対して、適切な報酬を与える抽象クラス
  """
  @abstractmethod
  def get(self, othello: OthelloBoard, ql_num: int) -> float:
    """
    盤面に対して報酬を与える

    Parameters
    ----------
    othello : OthelloBoard
      盤面
    ql_num : int
      QLearningAgentの番号, 0 or 1
    """
    pass


class Rewardv1(Reward):
  """
  ゲーム終了時にのみ報酬を与えるクラスその1
  win : +1
  draw : +0
  lose : -1
  """
  def get(self, othello: OthelloBoard, ql_num: int) -> float:
    result = othello.get_result()
    if result != -1:
      if result == 0:
        reward = 1
      elif result == 1:
        reward = -1
      else:
        reward = 0
    else:
      reward = 0

    if ql_num != 0:
      reward *= -1

    return reward


class Rewardv2(Reward):
  """
  ゲーム終了時にのみ報酬を与えるクラスその2
  reward = result*abs(p_0 - p_1)/(p_0 + p_1)
  result = 1(win), 0(draw), -1(lose)
  p_n = (n番のコマの数)
  """
  def get(self, othello: OthelloBoard, ql_num: int) -> float:
    result = othello.get_result()
    if result != -1:
      if result == 0:
        reward = 1
      elif result == 1:
        reward = -1
      else:
        reward = 0
      
      if reward != 0:
        p_0 = othello.get_piece_num(0)
        p_1 = othello.get_piece_num(1)
        diff = abs(p_0 - p_1)
        reward *= diff/(p_0 + p_1)
    else:
      reward = 0

    if ql_num != 0:
      reward *= -1

    return reward

class Reward8x8v1(Reward):
  """
  全ての時に報酬を与えるクラス
  """
  scale = 1
  def get(self, othello: OthelloBoard8x8, ql_num: int) -> float:
    result = othello.get_result()
    if result != -1:
      if result == 0:
        reward = 1
      elif result == 1:
        reward = -1
      else:
        reward = 0
    else:
      d_0 = othello.get_determine_piece_line(0)
      d_1 = othello.get_determine_piece_line(1)
      p_0 = othello.get_piece_num(0)
      p_1 = othello.get_piece_num(1)
      reward = (d_0-d_1)/28
      if p_0-p_1 != 0:
        reward += (p_0-p_1)/abs(p_0-p_1)*othello.count/64
      reward /= 2
    if ql_num != 0:
      reward *= -1

    return reward*self.scale

class Reward4x4v1(Reward):
  """
  全ての時に報酬を与えるクラス
  """
  def get(self, othello: OthelloBoard4x4, ql_num: int) -> float:
    result = othello.get_result()
    if result != -1:
      if result == 0:
        reward = 1
      elif result == 1:
        reward = -1
      else:
        reward = 0

      if reward != 0:
        p_0 = othello.get_piece_num(0)
        p_1 = othello.get_piece_num(1)
        diff = abs(p_0 - p_1)
        reward *= diff/(p_0 + p_1)
    else:
      d_0 = othello.get_determine_piece(0)
      d_1 = othello.get_determine_piece(1)
      reward = (d_0 - d_1)/16

    if ql_num != 0:
      reward *= -1

    return reward