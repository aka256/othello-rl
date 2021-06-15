from logging import basicConfig, getLogger, DEBUG, ERROR, INFO
from multiprocessing.context import Process
from parse_save import parse_ql_json
from positional_evaluation import OthelloPositionalEvaluationv2
from othello import OthelloBitBoard
from features import OthelloFeatures, OthelloFeaturesv1
from self_made_error import ArgsError, OthelloCannotReverse
import random
from agent import OthelloAgent, OthelloQLearningAgent, OthelloRandomAgent, OthelloMinMaxAgent
import json
import time
from multiprocessing import Manager, Process, Pool, pool
import math

basicConfig(level=INFO)
logger = getLogger(__name__)

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

  def update(self, s: int, a: int, r: int, q: int) -> None:
    new_q = (1-self.alpha)*self.get(s, a)+self.alpha*(r + self.gamma*q)
    self.__set(s, a, new_q)


class OthelloQL:
  """

  Attributes
  ----------
  ql : QLearning
  features : OthelloFeatures
  epsilon : int
  agent : OthelloAgent
  """

  def __init__(self, features: OthelloFeatures, agent: OthelloAgent, data: dict, init_value: int, alpha: float, beta: float, epsilon: float) -> None:
    self.ql = QLearning(data, init_value, alpha, beta)
    self.features = features
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

  def __learn(self, reward: int, last_q: float, action_data: list):
    before_q = last_q
    for s, a, q in action_data:
      self.ql.update(s, a, reward, before_q)
      before_q = q

  def action_one_game(self, first_agent_turn = True):
    othello = OthelloBitBoard()
    agent_turn = first_agent_turn
    action_data = []
    while True:
      if agent_turn:
        result = self.agent.step(othello)
        if not result:
          raise OthelloCannotReverse()
      else:
        action = self.__step(othello)
        action_data.append(action)
      next_state = othello.get_next_state()
      if next_state == 1:
        pass
      elif next_state == 2:
        break
      else:
        agent_turn = not agent_turn
        othello.change_player()

    result = othello.result()
    if result == 0:
      reward = 1
    elif result == 1:
      reward = -1
    elif result == 2:
      reward = 0
    else:
      raise ArgsError('result: {}'.format(result))
    #logger.debug('action_data: {}'.format(action_data))
    last_q = self.features.get_index(othello)
    self.__learn(reward, last_q, action_data)

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

def do_pool(pool_size: int, count: int, epsilon: int, init_value: int, alpha: int, beta: int, opponent_agent: OthelloAgent):
  with Manager() as manager:
    shared_dict = manager.dict()
    ql = OthelloQL(OthelloFeaturesv1(), opponent_agent, shared_dict, init_value, alpha, beta, epsilon)
    with Pool(pool_size) as pool:  
      l =[True]*count
      pool.map(ql.action_one_game, l)
    
    save_dict('test.json', ql.ql.data, True)

def ql_test(features: OthelloFeatures, dic: dict, init_value: int, opponent_agent: OthelloAgent, count: int, ql_order: int = 0):
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

  
  print('win: {}, lose: {}, draw: {}'.format(result_sum[0], result_sum[1], result_sum[2]))
  


if __name__ == '__main__':

  startTime = time.time()
  #do_multiprocess(6, 1000)
  do_pool(2, 100)
  '''
  tpe = ProcessPoolExecutor(max_workers=3)
  startTime = time.time()
  print('Learning')
  for i in range(100):
    if (i+1)%100 == 0:
      print('count: {}, time: {}'.format(i, time.time()-startTime))
      
      print('Test')
      win = lose = draw = 0
      for i in range(20):
        result = ql.test()
        if result == 0:
          win += 1
        elif result == 1:
          lose += 1
        else:
          draw += 1
      print('win: {}, lose: {}, draw: {}'.format(win, lose, draw))
      
    future = tpe.submit(ql.action_one_game)
    print(future)
    print(future.result())
    

  tpe.shutdown()
  '''
  print(time.time()-startTime)
  #ql_test(OthelloFeaturesv1(), parse_ql_json('./save/minmax-3-5000-multi6.json'), 0, OthelloMinMaxAgent(3, OthelloPositionalEvaluationv2()), 100, 1)
  #print('Test')
  #win = lose = draw = 0
  #for i in range(200):
  #  result = ql.test()
  #  if result == 0:
  #    win += 1
  #  elif result == 1:
  #    lose += 1
  #  else:
  #    draw += 1
  
  #print('win: {}, lose: {}, draw: {}'.format(win, lose, draw))
  #print(ql.ql.data)
  #save_dict('test.json', ql.ql.data, True)
