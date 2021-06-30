from logging import basicConfig, getLogger, DEBUG, ERROR, INFO
from othello_rl.othello.reward import Reward4x4v1
from othello_rl.qlearning.qlearning import QLearning
from othello_rl.othello.positional_evaluation import PositionalEvaluation4x4v1
from othello_rl.othello.agent import MinMaxAgent
from othello_rl.othello.features import Featuresv2
from othello_rl.manager.multi_precess import learn_mp
from othello_rl.manager.othello import OthelloQLearningManager

logger = getLogger(__name__)

def main():
  learn_mp( 2, 
            100, 
            OthelloQLearningManager(4, 
                                    Featuresv2(), 
                                    MinMaxAgent(3, PositionalEvaluation4x4v1()), 
                                    QLearning(0.5, 0.8, {}), 
                                    0.3, 
                                    Reward4x4v1()), 
            './save/test1/', 
            'test.json', 
            True, 
            10)

if __name__ == '__main__':
  basicConfig(level=ERROR)
  main()