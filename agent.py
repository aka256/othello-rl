from abc import ABCMeta, abstractmethod
from othello import OthelloBitBoard
from features import OthelloFeatures
import random
from self_made_error import EmptyListError, ArgsError
from typing import Union
from parse_save import parse_ql_json

class OthelloAgent(metaclass=ABCMeta):
  """
  オセロをプレイするagentの抽象クラス
  """
  @abstractmethod
  def step(self, othello: OthelloBitBoard) -> tuple[OthelloBitBoard, bool]:
    """
    オセロを一手進めるメソッド

    Parameters
    ----------
    othello : OthelloBitBoard
      ゲームの現在の状況

    Returns
    -------
    othello : OthelloBitBoard
      ゲームを一手進めた状態
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
  def step(self, othello: OthelloBitBoard, x: int, y: int) -> tuple[OthelloBitBoard, bool]:
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
    othello : OthelloBitBoard
      ゲームを一手進めた状態
    result : bool
      ゲームを進めることが出来たか否か
    """
    if othello.reverse(x, y):
      return othello, True
    
    return othello, False

class OthelloRandomAgent(OthelloAgent):
  """
  候補からランダムに次の手を選択するagent
  """
  def step(self, othello: OthelloBitBoard) -> tuple[OthelloBitBoard, bool]:
    """
    オセロを一手進めるメソッド

    Parameters
    ----------
    othello : OthelloBitBoard
      ゲームの現在の状況

    Returns
    -------
    othello : OthelloBitBoard
      ゲームを一手進めた状態
    result : bool
      ゲームを進めることが出来たか否か
    """
    candidate_list = othello.get_candidate()
    #print(candidate_list)
    if len(candidate_list) == 0:
      raise EmptyListError('candidate_list became empty')
    next = random.choice(candidate_list)
    result = othello.reverse(next[0], next[1])

    return othello, result

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

  def step(self, othello: OthelloBitBoard) -> tuple[OthelloBitBoard, bool]:
    """
    オセロを一手進めるメソッド

    Parameters
    ----------
    othello : OthelloBitBoard
      ゲームの現在の状況

    Returns
    -------
    othello : OthelloBitBoard
      ゲームを一手進めた状態
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
    result = othello.reverse(candidate_list[idx][0], candidate_list[idx][1])

    return othello, result