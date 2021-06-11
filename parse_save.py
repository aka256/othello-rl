import json
from os import name
import re
import nbt.nbt
import collections

def str_to_tuple(dic, value_scale = 1):
  new_dict = {}
  p = re.compile(r'([0-9]+)\, ([0-9]+)')
  for k, v in dic.items():
    t = p.match(k[1:-1])
    t = t.groups()
    t = (int(t[0]), int(t[1]))
    new_dict[t] = v*value_scale

  return new_dict


def parse_ql_json(path, scale = 1):
  with open(path, 'r') as f:
    l = json.load(f)
  
  dic = str_to_tuple(l, scale)

  return dic

def tuple_to_int(t):
  return (t[0] << 6) + (t[1]-1)

def dict_sort(dic):
  retval = []
  for k,v in dic.items():
    retval.append([tuple_to_int(k),int(v)])

  retval.sort()

  return retval


def dict_to_storage(l, storage_name, name_space_name = ''):
  storage_file = nbt.nbt.NBTFile()
  storage_file.name = 'command_storage_'+storage_name+'.dat'
  data = nbt.nbt.TAG_Compound()
  data.name = 'data'
  storage_file.tags.append(data)
  contents = nbt.nbt.TAG_Compound()
  contents.name = 'contents'
  data.tags.append(contents)
  name_space = nbt.nbt.TAG_Compound()
  name_space.name = name_space_name
  contents.tags.append(name_space)
  data_list = nbt.nbt.TAG_List(type=nbt.nbt.TAG_Int, name='q_learning_data')
  name_space.tags.append(data_list)
  for _, v in l:
    data_list.tags.append(nbt.nbt.TAG_Int(v))

  storage_file.write_file('command_storage_'+storage_name+'.dat')



if __name__ == '__main__':

  dic = parse_ql_json('./save/test.json', 10**5)
  l = dict_sort(dic)

  co = collections.Counter(list(dic.values()))
  for k, v in co.most_common()[:10]:
    print(k,v)

  dict_to_storage(l, 'test')
