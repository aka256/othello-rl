from logging import basicConfig, getLogger, DEBUG, ERROR, INFO
from othello import OthelloBitBoard, OthelloState
from self_made_error import ArgsError
import random
from agent import OthelloAgent, OthelloRandomAgent
import json

basicConfig(level=DEBUG)
logger = getLogger(__name__)

class QLearning:
  def __init__(self, init_value: int, alpha: float, gamma: float) -> None:
    self.alpha = alpha
    self.gamma = gamma
    #self.epsilon = epsilon

    self.data = {}
    #self.state = state
    self.init_value = init_value

  def get(self, s: int, a: int) -> int:
    return self.data.get((s, a), self.init_value)
    
  def __set(self, s: int, a: int, value: int) -> None:
    self.data[(s, a)] = value

  def update(self, s: int, a: int, r: int, q: int) -> None:
    new_q = (1-self.alpha)*self.get(s, a)+self.alpha*(r + self.gamma*q)
    self.__set(s, a, new_q)


class OthelloQL:
  def __init__(self, state: OthelloState, agent: OthelloAgent, epsilon: float) -> None:
    self.ql = QLearning(0, 0.5, 0.5)
    self.state = state
    self.epsilon = epsilon
    self.agent = agent

  def __step(self, othello: OthelloBitBoard) -> OthelloBitBoard:
    candidate_list = othello.get_candidate()
    q_list = []
    tmp = []
    for x, y in candidate_list:
      tmp.append([self.state.get_index(othello), x*8+y])
      q_list.append(self.ql.get(tmp[-1][0], tmp[-1][1]))
    
    if random.random() > self.epsilon:
      q = max(q_list)
    else:
      q = random.choice(q_list)
    idx = q_list.index(q)
    othello.reverse(candidate_list[idx][0], candidate_list[idx][1])
    self.action_data.append([tmp[idx][0], tmp[idx][1], q_list[idx]])

    return othello

  def __learn(self, reward: int, last_q: float):
    #print(len(self.action_data))
    #print(self.action_data)
    before_q = last_q
    for s, a, q in self.action_data:
      self.ql.update(s, a, reward, before_q)
      before_q = q

  def action_one_game(self, first_agent_turn = True):
    othello = OthelloBitBoard()
    agent_turn = first_agent_turn
    self.action_data = []
    while True:
      #print(othello.count)
      if agent_turn:
        othello = self.agent.step(othello)
      else:
        othello = self.__step(othello)
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
    
    last_q = self.state.get_index(othello)
    self.__learn(reward, last_q)

  def __step_test(self, othello: OthelloBitBoard) -> OthelloBitBoard:
    candidate_list = othello.get_candidate()
    q_list = []
    tmp = []
    for x, y in candidate_list:
      tmp.append([self.state.get_index(othello), x*8+y])
      q_list.append(self.ql.get(tmp[-1][0], tmp[-1][1]))
    
    q = max(q_list)
    idx = q_list.index(q)
    othello.reverse(candidate_list[idx][0], candidate_list[idx][1])

    return othello

  def test(self, first_agent_turn = True) -> OthelloBitBoard:
    othello = OthelloBitBoard()
    agent_turn = first_agent_turn
    while True:
      if agent_turn:
        othello = self.agent.step(othello)
      else:
        othello = self.__step_test(othello)
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

if __name__ == '__main__':

  epsilon = 0.3
  ql = OthelloQL(OthelloState(), OthelloRandomAgent(), epsilon)


  print('Learning')
  for i in range(10000):
    if (i+1)%2000 == 0:
      print('count: {}'.format(i))
      print('Test')
      win = lose = draw = 0
      for i in range(500):
        result = ql.test()
        if result == 0:
          win += 1
        elif result == 1:
          lose += 1
        else:
          draw += 1
      print('win: {}, lose: {}, draw: {}'.format(win, lose, draw))
    ql.action_one_game()

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

  save_dict('test.json', ql.ql.data, True)
