from logging import basicConfig, getLogger, DEBUG, ERROR, INFO
from multiprocessing.context import Process
from reward import OthelloReward, OthelloRewardv1
from parse_save import parse_ql_json
from positional_evaluation import OthelloPositionalEvaluationv2
from othello import OthelloBitBoard
from features import OthelloFeatures, OthelloFeaturesv1
from self_made_error import ArgsError, OthelloCannotReverse
import random
from agent import OthelloAgent, OthelloQLearningAgent, OthelloRandomAgent, OthelloMinMaxAgent
import json
import time
from multiprocessing import Manager, Process, Pool
import math
import matplotlib.pyplot as plt
from copy import copy

basicConfig(level=INFO)
logger = getLogger(__name__)

data_table = {}

class QLearning:
  def __init__(self, data: dict, init_value: int, alpha: float, gamma: float) -> None:
    self.alpha = alpha
    self.gamma = gamma

    self.data = data
    self.init_value = init_value

  def get(self, s: int, a: int) -> int:
    return self.data.get((s, a), self.init_value)
    
  def __set(self, s: int, a: int, value: int) -> None:
    self.data[(s, a)] = value

  def update(self, s: int, a: int, r: int, q: int) -> int:
    old_q = self.get(s, a)
    new_q = (1-self.alpha)*old_q+self.alpha*(r + self.gamma*q)
    #logger.debug('old q: {}, new q: {}, s: {}, a: {}, r: {}, q: {}'.format(self.get(s, a), new_q, s, a, r, q))
    logger.debug('Q_new: {:.4f} <= Q_old: {:.4f} (Q_t+1: {:.4f}, reward: {:.4f})'.format(new_q, old_q, q, r))
    # debug
    d = data_table.get(s, {})
    if len(d) == 0:
      data_table[s] = {}
    if len(data_table[s].get(a, {})) == 0:
      data_table[s][a] = []
    data_table[s][a].append('Q_new: '+str(new_q)+', Q_old: '+str(old_q)+', reward: '+str(r)+', Q_t+1: '+str(q))

    self.__set(s, a, new_q)

    return new_q


class OthelloQL:
  """

  Attributes
  ----------
  ql : QLearning
  features : OthelloFeatures
  epsilon : int
  agent : OthelloAgent
  """

  def __init__(self, features: OthelloFeatures, agent: OthelloAgent, data: dict, init_value: int, alpha: float, beta: float, epsilon: float, reward: OthelloReward) -> None:
    self.ql = QLearning(data, init_value, alpha, beta)
    self.features = features
    self.reward = reward
    self.epsilon = epsilon
    self.agent = agent

  def __step(self, othello: OthelloBitBoard) -> tuple[int, int, float]:
    candidate_list = othello.get_candidate()
    q_list = []
    tmp = []
    for x, y in candidate_list:
      tmp.append([self.features.get_index(othello), x*8+y])
      q_list.append(self.ql.get(tmp[-1][0], tmp[-1][1]))
    
    if random.random() > self.epsilon:
      q = max(q_list)
    else:
      q = random.choice(q_list)
    idx = q_list.index(q)
    othello.reverse(candidate_list[idx][0], candidate_list[idx][1], False)

    return tmp[idx][0], tmp[idx][1], q_list[idx]

  def __learn(self, last_q: float, action_data: list):
    before_q = last_q
    logger.debug('----head---------------------------------------')
    for s, a, q, reward in action_data[::-1]:
      before_q = self.ql.update(s, a, reward, before_q)

  def action_one_game(self, do_from_opponent = True):
    othello = OthelloBitBoard(0)
    opp_turn = do_from_opponent
    action_data = []
    while True:
      if opp_turn:
        result = self.agent.step(othello)
        if not result:
          raise OthelloCannotReverse()
      else:
        action = list(self.__step(othello))
        if do_from_opponent:
          reward = self.reward.get(othello, 1)
        else:
          reward = self.reward.get(othello, 0)
        #logger.debug('reward: {}'.format(reward))
        action.append(reward)
        action_data.append(action)
        
      next_state = othello.get_next_state()
      if next_state == 1:
        pass
      elif next_state == 2:
        break
      else:
        opp_turn = not opp_turn
        othello.change_player()

    if do_from_opponent:
      reward = self.reward.get(othello, 1)
    else:
      reward = self.reward.get(othello, 0)
    action_data[-1][-1] = reward
    if reward > 0:
      logger.info('win')
    elif reward < 0:
      logger.info('lose')
    else:
      logger.info('draw')
    #logger.debug('action_data: {}'.format(action_data))
    #last_q = self.features.get_index(othello)
    last_q = 0
    self.__learn(last_q, action_data)

  def __step_test(self, othello: OthelloBitBoard) -> None:
    candidate_list = othello.get_candidate()
    q_list = []
    tmp = []
    for x, y in candidate_list:
      tmp.append([self.features.get_index(othello), x*8+y])
      q_list.append(self.ql.get(tmp[-1][0], tmp[-1][1]))
    
    q = max(q_list)
    idx = q_list.index(q)
    othello.reverse(candidate_list[idx][0], candidate_list[idx][1], False)

  def test(self, first_agent_turn = True) -> int:
    othello = OthelloBitBoard()
    agent_turn = first_agent_turn
    while True:
      if agent_turn:
        result = self.agent.step(othello)
        if not result:
          raise OthelloCannotReverse()
      else:
        self.__step_test(othello)
      next_state = othello.get_next_state()
      if next_state == 1:
        pass
      elif next_state == 2:
        break
      else:
        agent_turn = not agent_turn
        othello.change_player()
        
    result = othello.result()
    if result == -1:
      raise ArgsError('result: {}'.format(result))
    
    return result


def save_dict(path, dict: dict, use_json: bool = False) -> None:
  with open('./save/'+path, 'w') as f:
    if use_json:
      new_dict = {}
      for k, v in dict.items():
        new_dict[str(k)] = v
      json.dump(new_dict, f)
    else:
      f.write(str(dict))

def do_multiprocess(process_size: int, count: int):
  epsilon = 0.3

  with Manager() as manager:
    shared_dict = manager.dict()
    ql = OthelloQL(OthelloFeaturesv1(), OthelloMinMaxAgent(3, OthelloPositionalEvaluationv2()), shared_dict, 0, 0.5, 0.5, epsilon)
    for i in range(math.ceil(count/process_size)):
      if i*process_size%100 == 0:
        logger.info('count: {}, time: {}'.format(i*process_size, time.time()-startTime))
      p_list = []
      for i in range(min(process_size, count-i*process_size)):
        p = Process(target=ql.action_one_game)
        p.start()
        p_list.append(p)
      for p in p_list:
        p.join()
    
    save_dict('test.json', ql.ql.data, True)

def do_pool(pool_size: int, count: int, epsilon: int, init_value: int, alpha: int, beta: int, opponent_agent: OthelloAgent, save_dir: str, save_path: str, save_regularly: bool, save_interval: int):
  with Manager() as manager:
    shared_dict = manager.dict()
    ql = OthelloQL(OthelloFeaturesv1(), opponent_agent, shared_dict, init_value, alpha, beta, epsilon, OthelloRewardv1())
    for i in range(save_interval):
      with Pool(pool_size) as pool:  
        l =[True, False]*(count//save_interval//2)
        pool.map(ql.action_one_game, l)
      logger.info('count: {}'.format(count//save_interval*i))
    
      save_dict(save_dir+str(i)+save_path, ql.ql.data, True)

def ql_test(features: OthelloFeatures, dic: dict, init_value: int, opponent_agent: OthelloAgent, count: int, ql_order: int = 1):
  ql_agent = OthelloQLearningAgent(features, dic, init_value)
  result_sum = [0, 0, 0]
  for _ in range(count):
    othello = OthelloBitBoard(ql_order)
    while True:
      if othello.now_turn == 0:
        ql_agent.step(othello)
      else:
        opponent_agent.step(othello)
      
      next_state = othello.get_next_state()
      if next_state == 0:
        othello.change_player()
      elif next_state == 1:
        pass
      else:
        result = othello.result()
        result_sum[result] += 1
        break

  return result_sum
  #print('win: {}, lose: {}, draw: {}'.format(result_sum[0], result_sum[1], result_sum[2]))
  
def test_graph(file_name: str, features: OthelloFeatures, init_value: int, dir: str, path: str, dict_num: int, opponent_agent: OthelloAgent, count: int, ql_order: int = 1):
  result = []
  for i in range(dict_num):
    dic = parse_ql_json('./save'+dir+str(i)+path,1)
    result.append(ql_test(features, dic, init_value, opponent_agent, count, ql_order))
    print('win: {}, lose: {}, draw: {}'.format(*(result[-1])))
  
  fig, ax = plt.subplots()
  label = ['win', 'lose', 'draw']
  offset = [0]*len(result)
  for i in range(3):
    ax.bar(list(range(len(result))), [x[i] for x in result], bottom=offset)
    offset = [o+r[i] for o, r in zip(offset, result)]
  ax.legend(label)
  fig.savefig('./save'+dir+file_name+'.png')

def do_ql_for_debug():
  ql = OthelloQL(OthelloFeaturesv1(), OthelloMinMaxAgent(3, OthelloPositionalEvaluationv2()), {}, 0, 0.5, 0.5, 0.3, OthelloRewardv1())
  for i in range(100):
    ql.action_one_game()

  with open('test.json', 'w') as f:
    json.dump(data_table, f)

if __name__ == '__main__':

  startTime = time.time()
  #do_multiprocess(6, 1000)
  #do_pool(6, 5000, 0.3, 0, 0.5, 0.5, OthelloMinMaxAgent(3, OthelloPositionalEvaluationv2()), 'serial10/', 'test.json', True, 50)

  print(time.time()-startTime)
  do_ql_for_debug()
  #test_graph('vsRandom', OthelloFeaturesv1(), 0, '/serial10/', 'test.json', 50, OthelloRandomAgent(), 1000)