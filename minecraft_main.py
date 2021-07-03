import othello_rl.minecraft.storage as storage
import othello_rl.minecraft.function as function
from nbt import nbt

if __name__ == '__main__':
  #storage.gen_ql_data_storage('./save/test1/0test.json', 'name_space', 'name', './save/test1/')

  function.gen_ql_data_search(list(range(100)), 120)