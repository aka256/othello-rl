from logging import getLogger
import math
from os import write
from othello_rl.file import parse_ql_json

logger = getLogger(__name__)

def gen_btree(data: list[int], order: int, save_path: str, function_path: str, objective_name: str, score_holder_name: str, ret_objective_name: str, ret_score_holder_name: str, storage_path: str, storage_array_name: str):
  """
  B-treeを作成する

  Parameters
  ----------
  data : list[int]
    配置するデータ
  order : int
    B-treeのorder, 2以上を指定する, 2であればBinary search tree, 3であれば2-3木となる
  save_path : str
    生成した.mcfunctionの配置場所
  function_path : str
    datapack内でのfunctionの配置場所, `hoge:foo/`など
  objective_name : str
    検索したいキーのObjective
  score_holder_name : str
    検索したいキーのScore holder
  ret_objective_name : str
    検索された値を保存するObjective
  ret_score_holder_name : str
    検索された値を保存するScore holder
  storage_path : str
    検索対象となるデータを保持しているStorageのパス, `hoge:foo`など
  storage_array_name : str
    検索対象となるデータを保持しているIntArrayTag
  """
  def rec(l: int, r: int, deepth: int):
    nonlocal deepth_num_list
    if r-l <= order:
      write_str_list = []
      for i in range(l,r):
        write_str_list.append('execute if score '+score_holder_name+' '+objective_name+' matches '+str(data[i])+' store result score '+ret_score_holder_name+' '+ret_objective_name+' run data get storage '+storage_path+' '+storage_array_name+'['+str(i)+'] 1')

      with open(save_path+str(deepth)+'-'+str(deepth_num_list[deepth])+'.mcfunction', 'w') as f:
        f.write('\n'.join(write_str_list))
      
      deepth_num_list[deepth] += 1
    else:
      # make file
      write_str_list = []
      for i in range(order):
        if i != 0 and i != order-1:
          write_str_list.append('execute if score '+score_holder_name+' '+objective_name+' matches '+str(data[l+(r-l)*i//order])+'..'+str(data[l+(r-l)*(i+1)//order-1])+' run function '+function_path+str(deepth+1)+'-'+str(deepth_num_list[deepth+1]+i))
        elif i == 0:
          write_str_list.append('execute if score '+score_holder_name+' '+objective_name+' matches ..'+str(data[l+(r-l)*(i+1)//order-1])+' run function '+function_path+str(deepth+1)+'-'+str(deepth_num_list[deepth+1]+i))
        else:
          write_str_list.append('execute if score '+score_holder_name+' '+objective_name+' matches '+str(data[l+(r-l)*i//order])+'.. run function '+function_path+str(deepth+1)+'-'+str(deepth_num_list[deepth+1]+i))
      
      with open(save_path+str(deepth)+'-'+str(deepth_num_list[deepth])+'.mcfunction', 'w') as f:
        f.write('\n'.join(write_str_list))
      
      deepth_num_list[deepth] += 1
    
      for i in range(order):
        if i == 0:
          rec(l, l+(r-l)//order, deepth+1)
        elif i != order-1:
          rec(l+(r-l)*i//order, l+(r-l)*(i+1)//order, deepth+1)
        else:
          rec(l+(r-l)*i//order, r, deepth+1)

  deepth_num_list = [0]*1000  # TODO: 1000->max deepthに修正
  rec(0, len(data), 0)

def gen_ql_data_search(ql_data_keys: list[int], file_num_limit: int):
  i = 2   # TODO: order算出の改善
  while True:
    p = 1
    p_sum = 0
    while p < len(ql_data_keys) and p_sum < file_num_limit:
      p_sum += p
      p *= i
    if p_sum > file_num_limit:
      i += 1
      continue
    order = i
    break

  gen_btree(ql_data_keys, order, './tmp/datapack/', 'test:test', 'Args', '$0', 'Return', '$0', 'othello_data:', 'ql_data')
  