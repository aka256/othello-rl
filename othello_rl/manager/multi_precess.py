from multiprocessing import Manager, Pool
from logging import getLogger
import time
from othello_rl.manager.othello import OthelloQLearningManager

logger = getLogger(__name__)

def learn_mp(pool_size: int, count: int, ql_manager: OthelloQLearningManager, save_dir: str, save_file_name: str, save_regularly: bool = False, save_interval: int = 0):
  """
  Poolを用いて、学習を行う

  Parameters
  ----------
  pool_size : int
    Poolのサイズ, 1~6くらい?
  count : int
    学習回数
  ql_manager : OthelloQLearningManager
  save_dir : str
    ファイルをセーブするディレクトリ
  save_file_name : str
    セーブするファイル名
  save_regularly : bool, default False
    定期的に学習結果を書き出すか否か
  save_interval : int, default 0
    学習結果を書き出す間隔
  """
  startTime = time.time()
  with Manager() as manager:
    ql_manager.ql.data = manager.dict()
    for i in range(save_interval):
      with Pool(pool_size) as pool:  
        l =[True, False]*(count//save_interval//2)
        pool.map(ql_manager.learn_one_game, l)
      print('count: {}, time: {}'.format(count//save_interval*i, time.time()-startTime))

      if save_regularly:
        ql_manager.save_data(save_dir+str(i)+save_file_name, True)