from abc import ABCMeta, abstractmethod
from othello_pack.othello_board import OthelloBoard4x4, OthelloBoard8x8
from othello_board import OthelloBoard

class Reward(metaclass=ABCMeta):
  @abstractmethod
  def get(self, othello: OthelloBoard, ql_num: int):
    pass

class Rewardv1(Reward):
  scale = 10
  def get(self, othello: OthelloBoard8x8, ql_num: int) -> int:
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
  def get(self, othello: OthelloBoard4x4, ql_num: int) -> int:
    result = othello.get_result()
    if result != -1:
      if result == 0:
        reward = 1
      elif result == 1:
        reward = -1
      else:
        reward = 0
    else:
      d_0 = othello.get_determine_piece(0)
      d_1 = othello.get_determine_piece(1)
      reward = (d_0 - d_1)/16

    if ql_num != 0:
      reward *= -1

    return reward