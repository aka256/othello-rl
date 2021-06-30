from othello_rl.othello.features import Features
from othello_rl.othello.agent import Agent, QLearningAgent
from othello_rl.othello.board import OthelloBoard8x8, OthelloBoard4x4
from othello_rl.file import parse_ql_json
import matplotlib.pyplot as plt

def tester(board_size: int, agent1: Agent, agent2: Agent, do_from_agent1: bool = True):
  """
  オセロを1ゲーム行う

  Parameters
  ----------
  board_size : int
    盤のサイズ
  agent1 : Agent
    agent1
  agent2 : Agent
    agent2
  do_from_agent1 : bool, dafault True
    agent1からゲームを始めるか否か

  Returns
  -------
  result : int
    0: agent1, 1: agent2, 2: draw
  """
  if board_size == 8:
    othello = OthelloBoard8x8(0)
  elif board_size == 4:
    othello = OthelloBoard4x4(0)

  agent = [agent1, agent2]

  if not do_from_agent1:
    othello.change_player()

  while True:
    agent[othello.now_turn].step(othello)
    
    next_state = othello.get_next_state()
    if next_state == 0:
      othello.change_player()
    elif next_state == 1:
      pass
    else:
      result = othello.get_result()
      return result

def ql_test(board_size: int, features: Features, dic: dict, init_value: int, opponent_agent: Agent, count: int, ql_order: int = 1):
  ql_agent = QLearningAgent(features, dic, init_value)
  result_sum = [0, 0, 0]
  for _ in range(count):
    if board_size == 8:
      othello = OthelloBoard8x8(ql_order)
    elif board_size == 4:
      othello = OthelloBoard4x4(ql_order)
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
        result = othello.get_result()
        if result == -1:
          exit()
        result_sum[result] += 1
        break

  return result_sum

def test_graph(file_name: str, board_size: int, features: Features, init_value: int, dir: str, path: str, dict_num: int, opponent_agent: Agent, count: int, order_type : int):
  """
  
  Parameters
  ----------
  order_type : int
    0: 先手ql
    1: 先手opp_agent
    2: 交互
  """
  result = []
  for i in range(dict_num):
    dic = parse_ql_json(dir+str(i)+path,1)
    l = [0, 0, 0]
    for j in range(count):
      if order_type == 0:
        r = tester(board_size, QLearningAgent(features, dic, init_value), opponent_agent, True)
      elif order_type == 1:
        r = tester(board_size, QLearningAgent(features, dic, init_value), opponent_agent, False)
      elif order_type == 2:
        r = tester(board_size, QLearningAgent(features, dic, init_value), opponent_agent, True if j%2==0 else False)
      l[r] += 1
    #result.append(ql_test(board_size, features, dic, init_value, opponent_agent, count, ql_order))
    result.append(l)
    print('win: {}, lose: {}, draw: {}'.format(*(result[-1])))
  
  fig, ax = plt.subplots()
  label = ['win', 'lose', 'draw']
  offset = [0]*len(result)
  for i in range(3):
    ax.bar(list(range(len(result))), [x[i] for x in result], bottom=offset)
    offset = [o+r[i] for o, r in zip(offset, result)]
  ax.legend(label)
  fig.savefig(dir+file_name)