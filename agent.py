from abc import ABCMeta, abstractmethod
from othello import OthelloBitBoard, OthelloState
import random
from self_made_error import EmptyListError, ArgsError
from typing import Union
from parse_save import parse_ql_json

class OthelloAgent(metaclass=ABCMeta):
  @abstractmethod
  def step(self, othello: OthelloBitBoard) -> OthelloBitBoard:
    pass

class OthelloRandomAgent(OthelloAgent):
  def step(self, othello: OthelloBitBoard) -> OthelloBitBoard:
    candidate_list = othello.get_candidate()
    #print(candidate_list)
    if len(candidate_list) == 0:
      raise EmptyListError('candidate_list became empty')
    next = random.choice(candidate_list)
    othello.reverse(next[0], next[1])

    return othello

class OthelloQLearningAgent(OthelloAgent):
  def __init__(self, state: OthelloState, arg: Union[str, dict], init_value: int = 0) -> None:
    self.state = state
    self.init_value = init_value
    if type(arg) is str:
      self.data = parse_ql_json(arg)

    elif type(arg) is dict:
      self.data = arg

    else:
      raise ArgsError()

  def __get(self, s: int, a: int) -> int:
    return self.data.get((s, a), self.init_value)

  def step(self, othello: OthelloBitBoard) -> OthelloBitBoard:
    candidate_list = othello.get_candidate()
    q_list = []
    tmp = []
    for x, y in candidate_list:
      tmp.append([self.state.get_index(othello), x*8+y])
      q_list.append(self.__get(tmp[-1][0], tmp[-1][1]))
    
    q = max(q_list)
    idx = q_list.index(q)
    othello.reverse(candidate_list[idx][0], candidate_list[idx][1])

    return othello