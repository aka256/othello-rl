from abc import ABCMeta, abstractmethod
from othello import OthelloBitBoard
from features import OthelloFeatures
import random
from self_made_error import EmptyListError, ArgsError, OthelloCannotReverse
from typing import Union, TypedDict
from parse_save import parse_ql_json
from copy import deepcopy
from positional_evaluation import OthelloPositionalEvaluation
from logging import basicConfig, getLogger, DEBUG, ERROR, INFO

logger = getLogger(__name__)
inf = float('inf')

class OthelloAgent(metaclass=ABCMeta):
  """
  オセロをプレイするagentの抽象クラス
  """
  @abstractmethod
  def step(self, othello: OthelloBitBoard) -> bool:
    """
    オセロを一手進めるメソッド

    Parameters
    ----------
    othello : OthelloBitBoard
      ゲームの現在の状況

    Returns
    -------
    result : bool
      ゲームを進めることが出来たか否か
    """
    pass

class OthelloPlayerAgent(OthelloAgent):
  """
  プレイヤーによるagent

  Notes
  -----
  動作を共通化させるために作成
  """
  def step(self, othello: OthelloBitBoard, x: int, y: int) -> bool:
    """
    オセロを一手進めるメソッド

    Parameters
    ----------
    othello : OthelloBitBoard
      ゲームの現在の状況
    x : int
      コマを設置するx座標
    y : int
      コマを設置するy座標

    Returns
    -------
    result : bool
      ゲームを進めることが出来たか否か
    """
    return othello.reverse(x, y)

class OthelloRandomAgent(OthelloAgent):
  """
  候補からランダムに次の手を選択するagent
  """
  def step(self, othello: OthelloBitBoard) -> bool:
    """
    オセロを一手進めるメソッド

    Parameters
    ----------
    othello : OthelloBitBoard
      ゲームの現在の状況

    Returns
    -------
    result : bool
      ゲームを進めることが出来たか否か
    """
    candidate_list = othello.get_candidate()
    if len(candidate_list) == 0:
      raise EmptyListError('candidate_list became empty')
    next = random.choice(candidate_list)
    result = othello.reverse(next[0], next[1], False)

    return result


class OthelloMinMaxAgent(OthelloAgent):
  """
  MinMax手法を利用したagent

  Attributes
  ----------
  deepth : int
    ゲーム木の深さ
  pos_evaluation : OthelloPositionalEvaluation
    局面評価関数
  root_player : int
    ゲーム木のrootのプレイヤー
  """
  def __init__(self, deepth: int, pos_evaluation: OthelloPositionalEvaluation) -> None:
    """
    コンストラクタ

    Parameters
    ----------
    deepth : int
      ゲーム木の深さ
    pos_evaluation : OthelloPositionalEvaluation
      局面評価関数
    """
    self.deepth = deepth
    self.pos_evaluation = pos_evaluation

  def __alpha_beta(self, othello: OthelloBitBoard, n: int, alpha: int, beta: int) -> tuple[int, int, int]:
    """
    α-β法を行うメソッド
    """
    candidate_list = othello.get_candidate()
    ret_eval = 0
    ret_x = ret_y = -1
    for x, y in candidate_list:
      if not othello.reverse(x, y, False):
        raise OthelloCannotReverse()
      
      next_state = othello.get_next_state()
      if next_state == 2 or n == 1:
        eval = self.pos_evaluation.eval(othello, True if self.root_player == othello.now_turn else False)
      else:
        if next_state == 0:
          othello.change_player()
        eval, _, _ = self.__alpha_beta(othello, n-1, alpha, beta)
      othello.undo()

      if othello.now_turn == self.root_player and eval > alpha:
        alpha = eval
        ret_eval = eval
        ret_x = x
        ret_y = y
      elif othello.now_turn != self.root_player and eval < beta:
        beta = eval
        ret_eval = eval
        ret_x = x
        ret_y = y
      if alpha >= beta:
        break
    
    return ret_eval, ret_x, ret_y


  def step(self, othello: OthelloBitBoard) -> bool:
    self.root_player = othello.now_turn
    _, x, y = self.__alpha_beta(othello, self.deepth, -inf, inf)

    result = othello.reverse(x, y, False)
    return result


class OthelloQLearningAgent(OthelloAgent):
  """
  Q Learningによる学習によって得られたデータによるagent

  Attributes
  ----------
  data : dict
    Q Learningによって得られた結果
  """
  def __init__(self, features: OthelloFeatures, arg: Union[str, dict], init_value: float = 0.0) -> None:
    """
    コンストラクタ

    Parameters
    ----------
    features : OthelloFeatures
      使用するオセロの特徴量
    arg : str or dict
      Q Learningによって得られた結果(dict)もしくはそれが保存されているファイルのパス(str)
    init_value : int
      data内に値がない場合の初期値
    """
    self.features = features
    self.init_value = init_value
    if type(arg) is str:
      self.data = parse_ql_json(arg)

    elif type(arg) is dict:
      self.data = arg

    else:
      raise ArgsError('The arg must be str or dict')

  def __get(self, s: int, a: int) -> float:
    """
    dataから指定されたkeyの値を取得するメソッド

    Parameters
    ----------
    s : int
      状態
    a : int
      行動

    Returns
    -------
    Q(s,a) : float
      Q(s,a)の値
      data内になければ、init_valueを返す
    """
    return self.data.get((s, a), self.init_value)

  def step(self, othello: OthelloBitBoard) -> bool:
    """
    オセロを一手進めるメソッド

    Parameters
    ----------
    othello : OthelloBitBoard
      ゲームの現在の状況

    Returns
    -------
    result : bool
      ゲームを進めることが出来たか否か
    """
    candidate_list = othello.get_candidate()
    q_list = []
    tmp = []
    for x, y in candidate_list:
      tmp.append([self.features.get_index(othello), x*8+y])
      q_list.append(self.__get(tmp[-1][0], tmp[-1][1]))
    
    q = max(q_list)
    idx = q_list.index(q)
    result = othello.reverse(candidate_list[idx][0], candidate_list[idx][1], False)

    return result