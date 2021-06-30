from othello_rl.othello.features import Features
from othello_rl.othello.agent import Agent, QLearningAgent
from othello_rl.othello.board import OthelloBoard8x8, OthelloBoard4x4
from othello_rl.file import parse_ql_json
import matplotlib.pyplot as plt

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

def test_graph(file_name: str, board_size: int, features: Features, init_value: int, dir: str, path: str, dict_num: int, opponent_agent: Agent, count: int, ql_order: int = 1):
  result = []
  for i in range(dict_num):
    dic = parse_ql_json(dir+str(i)+path,1)
    result.append(ql_test(board_size, features, dic, init_value, opponent_agent, count, ql_order))
    print('win: {}, lose: {}, draw: {}'.format(*(result[-1])))
  
  fig, ax = plt.subplots()
  label = ['win', 'lose', 'draw']
  offset = [0]*len(result)
  for i in range(3):
    ax.bar(list(range(len(result))), [x[i] for x in result], bottom=offset)
    offset = [o+r[i] for o, r in zip(offset, result)]
  ax.legend(label)
  fig.savefig(dir+file_name)