from abc import ABCMeta, abstractmethod
import logging
from tree import MinMaxNodeData, Node
from othello import OthelloBitBoard
from features import OthelloFeatures
import random
from self_made_error import EmptyListError, ArgsError, OthelloCannotReverse
from typing import Union, TypedDict
from parse_save import parse_ql_json
from copy import deepcopy, copy
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

#NodeData = TypedDict('NodeData', {'board_0': int, 'board_1': int, 'now_turn': int, 'count': int, 'x': int, 'y': int})
#Node = TypedDict('Node', {'data': NodeData, 'next': list})

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
  tree : Node
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
    self.tree = None

  def __alpha_beta(self, othello: OthelloBitBoard, n: int, alpha: int, beta: int, node: Node) -> tuple[int, int, int]:
    """
    α-β法を行うメソッド
    """
    candidate_list = othello.get_candidate()
    if len(node.next) == len(candidate_list):
      ret_eval = 0
      ret_x = ret_y = -1

      for next_node in node.next:
        othello.past_data.append([othello.board[0], othello.board[1], othello.now_turn, othello.count, node.data['x'], node.data['y']])
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
      #candidate_list = othello.get_candidate()
      ret_eval = 0
      ret_x = ret_y = -1
      for x, y in candidate_list:
        othello.reverse(x, y, False)
        next_node = Node(MinMaxNodeData(board_0=othello.board[0], board_1=othello.board[1], now_turn=othello.now_turn, count=othello.count, x=x, y=y))
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

  def step(self, othello: OthelloBitBoard) -> bool:
    self.root_player = othello.now_turn
    #print('past_data: {}'.format(othello.past_data))
    new_node_flg = True
    if self.tree != None and self.deepth >= 3:
      i = 1
      while len(othello.past_data) >= i and othello.past_data[-i][2] != othello.now_turn:
        i += 1
      if len(othello.past_data) >= i:
        i -= 1
        #print('i: {}'.format(i))
        while i > 0:
          self.__set_next_tree(othello.past_data[-i][4], othello.past_data[-i][5])
          i -= 1
        new_node_flg = False

    if new_node_flg:
      self.tree = Node(MinMaxNodeData(board_0=othello.board[0], board_1=othello.board[1], now_turn=othello.now_turn, count=othello.count, x=-1, y=-1))
    
    #print('-init tree------------------------------------------------------------------------------------------')
    #self.tree.print()
    #l = copy(othello.past_data)
    #othello.print_board()
    _, x, y = self.__alpha_beta(othello, self.deepth, -inf, inf, self.tree)
    #othello.print_board()
    #if not othello.can(x,y):
    #  print('error')
    #  othello.print_board()
    #  self.tree.print()
    #print('x: {}, y: {}'.format(x, y))
    #print('-complete tree--------------------------------------------------------------------------------------')
    #self.tree.print()
    #print('-append tree1---------------------------------------------------------------------------------------')
    self.__set_next_tree(x, y)
    #self.tree.print()
    result = othello.reverse(x, y, False)
    #othello.print_board()
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