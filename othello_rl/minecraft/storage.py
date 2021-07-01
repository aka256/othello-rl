from nbt import nbt
from othello_rl.file import parse_ql_json

def get_empty_storage(name_space: str, data_ver: int = 2724) -> nbt.NBTFile:
  """
  空のStorageの作成

  Parameters
  ----------
  name_space : str
    command_storage_`name_space`.dat
  data_ver : int, default 2724
    DataVersion

  Returns
  -------
  storage : NBTFile
    空のStorage
  """
  f = nbt.NBTFile()
  f.name = 'command_storage_'+name_space+'.dat'

  data_com = nbt.TAG_Compound()
  data_com.name = 'data'
  data_version_int = nbt.TAG_Int(data_ver, 'DataVersion')
  f.tags.append(data_com)
  f.tags.append(data_version_int)

  contents_com = nbt.TAG_Compound()
  contents_com.name = 'contents'
  data_com.tags.append(contents_com)

  return f

def gen_ql_data_storage(path: str, name_space: str, name: str, save_path: str, scale: int) -> None:
  """
  QLearning用のStorageの生成

  Parameters
  ----------
  path : str
    保存場所
  name_space : str
    `name_space`:`name`
  name : str
    `name_space`:`name`
  save_path : str
    storageの保存場所
  scale : int
    Q値をInt32にする際の倍率
  """
  data = parse_ql_json(path, scale)
  f = get_empty_storage(name_space)
  
  name_com = nbt.TAG_Compound()
  name_com.name = name
  f['data']['contents'].tags.append(name_com)
  
  text_tag = nbt.TAG_String('test','ql_data')
  data_list = nbt.TAG_List(name='data', type=nbt.TAG_Int)
  for v in data.values():
    data_list.tags.append(nbt.TAG_Int(value=int(v)))
  name_com.tags.append(text_tag)
  name_com.tags.append(data_list)

  f.write_file(save_path+'command_storage_'+name_space+'.dat')