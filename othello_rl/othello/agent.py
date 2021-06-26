from abc import ABCMeta, abstractmethod
import random
from logging import getLogger
from othello_rl.tree import Node
from othello_rl.othello.board import OthelloBoard, OthelloData
from othello_rl.othello.features import Features
from othello_rl.othello.positional_evaluation import PositionalEvaluation

logger = getLogger(__name__)
inf = float('inf')

class Agent(metaclass=ABCMeta):
  """
  オセロをプレイするagentの抽象クラス
  """
  @abstractmethod
  def step(self, othello: OthelloBoard) -> bool:
    """
    オセロを一手進めるメソッド

    Parameters
    ----------
    othello : OthelloBoard
      ゲームの現在の状況

    Returns
    -------
    result : bool
      ゲームを進めることが出来たか否か
    """
    pass

class PlayerAgent(Agent):
  """
  プレイヤーによるagent

  Notes
  -----
  動作を共通化させるために作成
  """
  def step(self, othello: OthelloBoard, x: int, y: int) -> bool:
    """
    オセロを一手進めるメソッド

    Parameters
    ----------
    othello : OthelloBoard
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

class RandomAgent(Agent):
  """
  候補からランダムに次の手を選択するagent
  """
  def step(self, othello: OthelloBoard) -> bool:
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
    candidate_list = othello.get_candidate_list()
    next = random.choice(candidate_list)
    result = othello.reverse(next[0], next[1], False)

    return result


class MinMaxAgent(Agent):
  """
  MinMax手法を利用したagent

  Attributes
  ----------
  deepth : int
    ゲーム木の深さ
  pos_evaluation : PositionalEvaluation
    局面評価関数
  root_player : int
    ゲーム木のrootのプレイヤー
  tree : Node
  """
  def __init__(self, deepth: int, pos_evaluation: PositionalEvaluation) -> None:
    """
    コンストラクタ

    Parameters
    ----------
    deepth : int
      ゲーム木の深さ
    pos_evaluation : PositionalEvaluation
      局面評価関数
    """
    self.deepth = deepth
    self.pos_evaluation = pos_evaluation
    self.tree = None

  def __alpha_beta(self, othello: OthelloBoard, n: int, alpha: int, beta: int, node: Node) -> tuple[int, int, int]:
    """
    α-β法を行うメソッド
    """
    candidate_list = othello.get_candidate_list()
    if len(node.next) == len(candidate_list):
      ret_eval = 0
      ret_x = ret_y = -1

      for next_node in node.next:
        othello.past_data.append(OthelloData(board_0=othello.board[0], board_1=othello.board[1], turn=othello.now_turn, count=othello.count, x=node.data['x'], y=node.data['y']))
        othello.board[0] = next_node.data['board_0']
        othello.board[1] = next_node.data['board_1']
        othello.now_turn = next_node.data['now_turn']
        othello.count = next_node.data['count']
        x = next_node.data['x']
        y = next_node.data['y']
        if len(next_node.next) != 0:
          eval, _, _ = self.__alpha_beta(othello, n-1, alpha, beta, next_node)
        else:
          next_state = othello.get_next_state()
          if next_state == 2 or n == 1:
            eval = self.pos_evaluation.eval(othello, True if self.root_player == othello.now_turn else False)
          else:
            if next_state == 0:
              othello.change_player()
            eval, _, _ = self.__alpha_beta(othello, n-1, alpha, beta, next_node)
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
    else:
      ret_eval = 0
      ret_x = ret_y = -1
      for x, y in candidate_list:
        othello.reverse(x, y, False)
        next_node = Node(OthelloData(board_0=othello.board[0], board_1=othello.board[1], now_turn=othello.now_turn, count=othello.count, x=x, y=y))
        node.next.append(next_node)
        next_state = othello.get_next_state()
        if next_state == 2 or n == 1:
          eval = self.pos_evaluation.eval(othello, True if self.root_player == othello.now_turn else False)
        else:
          if next_state == 0:
            othello.change_player()
          eval, _, _ = self.__alpha_beta(othello, n-1, alpha, beta, next_node)
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
    
    #print(othello.past_data)
    #othello.print_board()
    return ret_eval, ret_x, ret_y

  def __set_next_tree(self, x: int, y: int) -> bool:
    for node in self.tree.next:
      if x == node.data['x'] and y == node.data['y']:
        self.tree = node
        return True
    return False

  def step(self, othello: OthelloBoard) -> bool:
    self.root_player = othello.now_turn
    new_node_flg = True
    if self.tree != None and self.deepth >= 3:
      i = 1
      while len(othello.past_data) >= i and othello.past_data[-i]['turn'] != othello.now_turn:
        i += 1
      if len(othello.past_data) >= i:
        i -= 1
        #print('i: {}'.format(i))
        while i > 0:
          self.__set_next_tree(othello.past_data[-i]['x'], othello.past_data[-i]['y'])
          i -= 1
        new_node_flg = False

    if new_node_flg:
      self.tree = Node(OthelloData(board_0=othello.board[0], board_1=othello.board[1], now_turn=othello.now_turn, count=othello.count, x=-1, y=-1))
    
    _, x, y = self.__alpha_beta(othello, self.deepth, -inf, inf, self.tree)
    self.__set_next_tree(x, y)
    result = othello.reverse(x, y, False)

    return result


class QLearningAgent(Agent):
  """
  Q Learningによる学習によって得られたデータによるagent

  Attributes
  ----------
  features : Features
    使用するオセロの特徴量
  data : dict
    Q Learningによって得られた結果
  init_value : int
    data内に値がない場合の初期値
  """
  def __init__(self, features: Features, data: dict, init_value: float = 0.0) -> None:
    """
    コンストラクタ

    Parameters
    ----------
    features : Features
      使用するオセロの特徴量
    data : dict
      Q Learningによって得られた結果(dict)
    init_value : int
      data内に値がない場合の初期値
    """
    self.features = features
    self.init_value = init_value
    self.data = data

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

  def step(self, othello: OthelloBoard) -> bool:
    """
    オセロを一手進めるメソッド

    Parameters
    ----------
    othello : OthelloBoard
      ゲームの現在の状況

    Returns
    -------
    result : bool
      ゲームを進めることが出来たか否か
    """
    candidate_list = othello.get_candidate_list()
    q_list = []
    tmp = []
    for x, y in candidate_list:
      tmp.append([self.features.get_index(othello), x*8+y])
      q_list.append(self.__get(tmp[-1][0], tmp[-1][1]))
    
    q = max(q_list)
    idx = q_list.index(q)
    result = othello.reverse(candidate_list[idx][0], candidate_list[idx][1], False)

    return result