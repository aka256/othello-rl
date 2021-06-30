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
  '''
  learn_mp( 4, 
            10000, 
            OthelloQLearningManager(board_size=4, 
                                    features=Featuresv2(), 
                                    opp_agent=MinMaxAgent(12, PositionalEvaluation4x4v2()), 
                                    ql=QLearning(alpha=0.6, gamma=0.6, data={}), 
                                    epsilon=0.5, 
                                    reward=Reward4x4v1()), 
            './save/test5/', 
            'test.json', 
            True, 
            10)
  '''
  test_graph('vsRandom_ql-opp.png', 4, Featuresv2(), 0, './save/test5/', 'test.json', 10, RandomAgent(), 1000, 0)

if __name__ == '__main__':
  basicConfig(level=ERROR)
  main()