from logging import basicConfig, getLogger, DEBUG, ERROR, INFO
from othello_rl.othello.reward import Reward4x4v1, Reward8x8v1, Reward8x8v2
from othello_rl.qlearning.qlearning import QLearning
from othello_rl.othello.positional_evaluation import PositionalEvaluation4x4v1, PositionalEvaluation4x4v2, PositionalEvaluation8x8v2
from othello_rl.othello.agent import MinMaxAgent, RandomAgent
from othello_rl.othello.features import Featuresv1, Featuresv2
from othello_rl.manager.multi_precess import learn_mp
from othello_rl.manager.othello import OthelloQLearningManager
from othello_rl.qlearning.test import test_graph

logger = getLogger(__name__)

def main():
  ql_manager = OthelloQLearningManager(board_size=8, 
                                      features=Featuresv1(), 
                                      opp_agent=MinMaxAgent(3, PositionalEvaluation8x8v2()), 
                                      ql=QLearning(alpha=0.1, gamma=0.8, data={}),  
                                      reward=Reward8x8v2(),
                                      policy_type='e',
                                      policy_option=[0.2])
  
  learn_mp( 2, 
            1000, 
            ql_manager, 
            './save/test13/', 
            'test.json', 
            True, 
            10)
  
  ql_manager.gen_learned_trend_graph('./save/test13/trend.png', 50)

  #test_graph('vsRandom_alt.png', 4, Featuresv2(), 0, './save/test10/', 'test.json', 10, RandomAgent(), 10000, 2)

if __name__ == '__main__':
  basicConfig(level=ERROR)
  main()