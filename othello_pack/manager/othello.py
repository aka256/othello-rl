import random
import json
from logging import getLogger
from ..qlearning.qlearning import QLearning
from ..error import CannotReverseError
from ..othello.board import OthelloBoard
from ..othello.features import Features
from ..othello.agent import Agent
from ..othello.reward import Reward

logger = getLogger(__name__)

class OthelloQLearningManager:
  """
  OthelloBoardのQLearning管理クラス
  ε-Greedy法を採用

  Attributes
  ----------
  features : othello.features.Features
    盤面の特徴量選択方法
  opp_agent : othello.agent.Agent
    相手のエージェント
  ql : qlearning.qlearning.QLearning
    Q-Learning用のクラス
  epsilon : float
    ε-Greedy法でのε
  reward : othello.reward.Reward
    報酬選択方法
  game : othello.board.OthelloBoard
    扱っているゲーム
  """

  def __init__(self, features: Features, opp_agent: Agent, ql: QLearning, epsilon: float, reward: Reward) -> None:
    """
    コンストラクタ

    features : othello.features.Features
      盤面の特徴量選択方法
    opp_agent : othello.agent.Agent
      相手のエージェント
    ql : qlearning.qlearning.QLearning
      Q-Learning用のクラス
    epsilon : float
      ε-Greedy法でのε
    reward : othello.reward.Reward
      報酬選択方法
    """
    self.features = features
    self.agent = opp_agent
    self.ql = ql
    self.epsilon = epsilon
    self.reward = reward

  def __step(self) -> tuple[int, int, float]:
    """
    ε-Greedy法に基づいて、オセロを一手進める

    Returns
    -------
    s : int
      状態、特徴量
    a : int
      行動
    q_old : float
      Q値, Q(s, a)
    """
    candidate_list = self.game.get_candidate_list()
    q_list = []
    tmp = []
    for x, y in candidate_list:
      tmp.append([self.features.get_index(self.game), x*8+y])
      q_list.append(self.ql.get(tmp[-1][0], tmp[-1][1]))
    
    if random.random() > self.epsilon:
      q = max(q_list)
    else:
      q = random.choice(q_list)
    idx = q_list.index(q)
    self.game.reverse(candidate_list[idx][0], candidate_list[idx][1], False)

    return tmp[idx][0], tmp[idx][1], q_list[idx]

  def learn_one_game(self, do_from_opponent: bool = True) -> None:
    """
    1ゲーム分の学習を行う

    Parameters
    ----------
    do_from_opponent : bool, dafault True
      相手のagentからゲームを開始するか否か
    """
    self.game = OthelloBoard(0)
    opp_turn = do_from_opponent
    action_data = []
    while True:
      if opp_turn:
        result = self.agent.step(self.game)
        if not result:
          raise CannotReverseError()
      else:
        action = list(self.__step(self.game))
        if do_from_opponent:
          reward = self.reward.get(self.game, 1)
        else:
          reward = self.reward.get(self.game, 0)
        action.append(reward)
        action_data.append(action)
        
      next_state = self.game.get_next_state()
      if next_state == 1:
        pass
      elif next_state == 2:
        break
      else:
        opp_turn = not opp_turn
        self.game.change_player()

    if do_from_opponent:
      reward = self.reward.get(self.game, 1)
    else:
      reward = self.reward.get(self.game, 0)
    action_data[-1][-1] = reward

    # learning
    before_q = 0
    for s, a, q_old, reward in action_data[::-1]:
      before_q = self.ql.update(s, a, reward, before_q, q_old)

  def learn(self, count: int, do_from_opponent: bool) -> None:
    for _ in range(count):
      self.learn_one_game(do_from_opponent)

  def save_data(self, path: str, use_json: bool = False) -> None:
    """
    dataの書き出し

    Parameters
    ----------
    path : str
      ファイルの保存場所
    use_json : bool, default False
      json形式で保存するか否か
    """
    with open(path, 'w') as f:
      if use_json:
        new_dict = {}
        for k, v in self.ql.data.items():
          new_dict[str(k)] = v
        json.dump(new_dict, f, indent=2)
      else:
        f.write(str(self.ql.data))