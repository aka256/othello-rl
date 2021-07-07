import random
import json
import math
from logging import getLogger
from othello_rl.qlearning.qlearning import QLearning
from othello_rl.error import CannotReverseError
from othello_rl.othello.board import OthelloBoard4x4, OthelloBoard8x8
from othello_rl.othello.features import Features
from othello_rl.othello.agent import Agent
from othello_rl.othello.reward import Reward
import matplotlib.pyplot as plt

logger = getLogger(__name__)

class OthelloQLearningManager:
  """
  OthelloBoardのQLearning管理クラス
  ε-Greedy法を採用

  Attributes
  ----------
  board_size : int
    盤のサイズ
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

  def __init__(self, board_size: int, features: Features, opp_agent: Agent, ql: QLearning, reward: Reward, policy_type: str, policy_option: list[float]) -> None:
    """
    コンストラクタ

    Parameters
    ----------
    board_size : int
      盤のサイズ
    features : othello.features.Features
      盤面の特徴量選択方法
    opp_agent : othello.agent.Agent
      相手のエージェント
    ql : qlearning.qlearning.QLearning
      Q-Learning用のクラス
    reward : othello.reward.Reward
      報酬選択方法
    policy_type : str
      手法の種類
    policy_option : list[float]
      手法の定数等
    """
    self.board_size = board_size
    self.features = features
    self.agent = opp_agent
    self.ql = ql
    self.reward = reward
    self.policy_type = policy_type
    if self.policy_type == 'e':
      self.epsilon = policy_option[0]
    elif self.policy_type == 'b':
      self.temperature = policy_option[0]

    self.learning_results = []

  def __step_epsilon_greedy(self) -> tuple[int, int, float]:
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

  def __step_boltzmann(self) -> tuple[int, int, float]:
    """
    Boltzmann手法に基づいて、オセロを一手進める

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
    
    p = [math.exp(x/self.temperature) for x in q_list]
    p_sum = sum(p)
    p = [x/p_sum for x in p]
    idx = p.index(max(p))
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
    if self.board_size == 4:
      self.game = OthelloBoard4x4(0)
    elif self.board_size == 8:
      self.game = OthelloBoard8x8(0)
    opp_turn = do_from_opponent
    action_data = []
    reward_sum = 0
    self_count = 0

    while True:
      if opp_turn:
        result = self.agent.step(self.game)
        if not result:
          raise CannotReverseError()
      else:
        if self.policy_type == 'e':
          action = list(self.__step_epsilon_greedy())
        elif self.policy_type == 'b':
          action = list(self.__step_boltzmann())

        if do_from_opponent:
          reward = self.reward.get(self.game, 1)
        else:
          reward = self.reward.get(self.game, 0)
        action.append(reward)
        action_data.append(action)
        reward_sum += reward
        self_count += 1
        
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

    self.learning_results.append([reward, reward_sum/self_count]) # [result, reward_ave]

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

  def gen_learned_trend_graph(self, path, span):
    win_rate = []
    lose_rate = []
    draw_rate = []
    reward = []
    x = list(range(0,len(self.learning_results),span))
    for i in range(len(self.learning_results)//span):
      r = 0
      l = [0, 0, 0]
      for j in self.learning_results[i*span:(i+1)*span]:
        l[j[0]+1] += 1
        r += j[1]

      win_rate.append(l[2]/span)
      draw_rate.append(l[1]/span)
      lose_rate.append(l[0]/span)
      reward.append(r/span)
    
    plt.plot(x, win_rate, label='win')
    plt.plot(x, draw_rate, label='draw')
    plt.plot(x, lose_rate, label='lose')
    plt.plot(x, reward, label='reward')
    plt.legend()
    plt.savefig(path)