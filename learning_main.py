from logging import basicConfig, getLogger, DEBUG, ERROR, INFO
from othello_rl.othello.reward import Reward4x4v1
from othello_rl.qlearning.qlearning import QLearning
from othello_rl.othello.positional_evaluation import PositionalEvaluation4x4v1, PositionalEvaluation4x4v2
from othello_rl.othello.agent import MinMaxAgent, RandomAgent
from othello_rl.othello.features import Featuresv2
from othello_rl.manager.multi_precess import learn_mp
from othello_rl.manager.othello import OthelloQLearningManager
from othello_rl.qlearning.test import test_graph

logger = getLogger(__name__)

def main():
  ql_manager = OthelloQLearningManager(board_size=4, 
                                      features=Featuresv2(), 
                                      opp_agent=MinMaxAgent(3, PositionalEvaluation4x4v2()), 
                                      ql=QLearning(alpha=0.3, gamma=0.6, data={}), 
                                      epsilon=0.5, 
                                      reward=Reward4x4v1())

  learn_mp( 2, 
            10000, 
            ql_manager, 
            './save/test10/', 
            'test.json', 
            True, 
            10)
  
  ql_manager.gen_learned_trend_graph('./save/test10/trend.png', 100)
  #ql_manager.gen_result_graph('lose_line', './save/test8/lose.png')
  #ql_manager.gen_result_graph('win_line', './save/test8/win.png')
  #test_graph('vsRandom_alt.png', 4, Featuresv2(), 0, './save/test7/', 'test.json', 10, RandomAgent(), 10000, 2)

if __name__ == '__main__':
  basicConfig(level=ERROR)
  main()