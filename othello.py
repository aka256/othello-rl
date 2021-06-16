from logging import basicConfig, getLogger, DEBUG, ERROR, INFO
from typing import Optional
from copy import copy
from self_made_error import ArgsError

#basicConfig(level=ERROR)
logger = getLogger(__name__)

class OthelloBitBoard:
  """
  ビットボードをベースとしたオセロの運用を行うクラス

  Attributes
  ----------
  board : list
    player1と2のコマの状況を保持しているリスト
  now_turn : int
    現在手番であるプレイヤー
  count : int
    手番の総数
  past_data : list
    過去の盤面をスタックしているリスト
  past_data_len : int
    past_dataの長さの最大値
  legal_board_cache : list
    leagal_boardのキャッシュ

  Notes
  -----
  以下のサイトを参考にした
  https://qiita.com/sensuikan1973/items/459b3e11d91f3cb37e43
  """

  def __init__(self, turn: int = 0, past_len: Optional[int] = None) -> None:
    """
    コンストラクタ

    Parameters
    ----------
    turn : int
      最初のプレイヤー
    past_len : int or None
      past_data_lenの長さ
    """
    self.board = [0x0000000810000000, 0x0000001008000000]
    self.now_turn = turn
    self.count = 0
    self.past_data = []
    if past_len == None:
      self.past_data_len = 100
    else:
      self.past_data_len = past_len
    self.legal_board_cache = [{'count': -1, 'legal_board': -1}, {'count': -1, 'legal_board': -1}]

  def __make_legal_board(self, player_num: int) -> int:
    """
    合成手ボードの作成を行うメソッド

    Parameters
    ----------
    player_num : int
      合成手ボードを作成するプレイヤー

    Returns
    -------
    legal_board : int
      合成手ボード
    """
    if self.legal_board_cache[player_num]['count'] == self.count:
      return self.legal_board_cache[player_num]['legal_board']

    horizontal_pivot = self.board[player_num-1] & 0x7e7e7e7e7e7e7e7e
    vertical_pivot = self.board[player_num-1] & 0x00ffffffffffff00
    all_pivot = self.board[player_num-1] & 0x007e7e7e7e7e7e00
  
    blank = ~(self.board[0] | self.board[1])
    #retval = 0

    tmp = horizontal_pivot & (self.board[player_num] << 1)
    for i in range(5):
      tmp |= horizontal_pivot & (tmp << 1)
    retval = blank & (tmp << 1)

    tmp = horizontal_pivot & (self.board[player_num] >> 1)
    for i in range(5):
      tmp |= horizontal_pivot & (tmp >> 1)
    retval |= blank & (tmp >> 1)

    tmp = vertical_pivot & (self.board[player_num] << 8)
    for i in range(5):
      tmp |= vertical_pivot & (tmp << 8)
    retval |= blank & (tmp << 8)

    tmp = vertical_pivot & (self.board[player_num] >> 8)
    for i in range(5):
      tmp |= vertical_pivot & (tmp >> 8)
    retval |= blank & (tmp >> 8)

    tmp = all_pivot & (self.board[player_num] << 7)
    for i in range(5):
      tmp |= all_pivot & (tmp << 7)
    retval |= blank & (tmp << 7)

    tmp = all_pivot & (self.board[player_num] << 9)
    for i in range(5):
      tmp |= all_pivot & (tmp << 9)
    retval |= blank & (tmp << 9)

    tmp = all_pivot & (self.board[player_num] >> 9)
    for i in range(5):
      tmp |= all_pivot & (tmp >> 9)
    retval |= blank & (tmp >> 9)

    tmp = all_pivot & (self.board[player_num] >> 7)
    for i in range(5):
      tmp |= all_pivot & (tmp >> 7)
    retval |= blank & (tmp >> 7)

    self.legal_board_cache[player_num]['count'] = self.count
    self.legal_board_cache[player_num]['legal_board'] = retval

    return retval

  def __can_put(self, x: int, y: int) -> bool:
    """
    指定された座標上にコマを置けるかを返すメソッド

    Parameters
    ----------
    x : int
      指定するx座標
    y : int
      指定するy座標

    Returns
    -------
    can_put : bool
      指定された場所にコマが置けるか
    """
    legal_board = self.__make_legal_board(self.now_turn)

    return (1 << (8*x+y) & legal_board) == 1 << (8*x+y)

  def can(self, x, y):
    return self.__can_put(x, y)

  def __transfer(self, put: int, k: int) -> int:
    """
    コマを裏返す位置を返すメソッド

    Parameters
    ----------
    put : int
      コマを置く位置を定めてあるビット値
    k : int
      コマの探索方向

    Returns
    -------
    transfered : int
      裏返されたビット値
    """
    if k == 0:
      return (put << 8) & 0xffffffffffffff00
    elif k == 1:
      return (put << 7) & 0x7f7f7f7f7f7f7f00
    elif k == 2:
      return (put >> 1) & 0x7f7f7f7f7f7f7f7f
    elif k == 3:
      return (put >> 9) & 0x007f7f7f7f7f7f7f
    elif k == 4:
      return (put >> 8) & 0x00ffffffffffffff
    elif k == 5:
      return (put >> 7) & 0x00fefefefefefefe
    elif k == 6:
      return (put << 1) & 0xfefefefefefefefe
    elif k == 7:
      return (put << 9) & 0xfefefefefefefe00
    
    raise ArgsError('k (= {}) is out of range'.format(k))

  def reverse(self, x: int, y: int, check_can_put: bool = True) -> bool:
    """
    指定された座標のコマを裏返すメソッド

    Parameters
    ----------
    x : int
      設置するコマのx座標
    y : int
      設置するコマのy座標
    check_can_put : bool, default True
      コマが置けるか確認するかどうか

    Returns
    -------
    is_reversed : bool
      コマを裏返すことに成功したか否か
    """
    if check_can_put and not self.__can_put(x, y):
      return False

    self.past_data.append([self.board[0], self.board[1], self.now_turn, self.count, x, y])
    if len(self.past_data) > self.past_data_len:
      self.past_data.pop(0)
    
    put = 1 << (x*8+y)
    rev = 0
    for i in range(8):
      _rev = 0
      mask = self.__transfer(put, i)
      while mask and mask & self.board[self.now_turn-1]:
        _rev |= mask
        mask = self.__transfer(mask, i)
      
      if mask & self.board[self.now_turn]:
        rev |= _rev
    
    self.board[self.now_turn] ^= put | rev
    self.board[self.now_turn-1] ^= rev

    self.count += 1

    return True

  def get_next_state(self) -> int:
    """
    次の手番での状態を取得する

    Returns
    -------
    next_state : int
      - 0: 次の相手に切り替える
      - 1: パスする
      - 2: ゲームを終了する
    """
    player_legal_board = self.__make_legal_board(abs(self.now_turn-1))
    opponent_legal_board = self.__make_legal_board(self.now_turn)

    if player_legal_board == 0x0000000000000000 and opponent_legal_board != 0x0000000000000000:
      return 1
    elif player_legal_board == 0x0000000000000000 and opponent_legal_board == 0x0000000000000000:
      return 2
    
    return 0

  def is_pass(self) -> bool:
    """
    次の手番にてパスをするか否かを返すメソッド

    Returns
    -------
    is_pass : bool
      次の手番にてパスをするか否か

    Notes
    -----
    is_finished()と併用する場合はget_next_state()の方が計算量が少なくなる
    """
    player_legal_board = self.__make_legal_board(self.now_turn)
    opponent_legal_board = self.__make_legal_board(abs(self.now_turn-1))

    return player_legal_board == 0x0000000000000000 and opponent_legal_board != 0x0000000000000000

  def is_finished(self) -> bool:
    """
    ゲームが終了しているか否かを返すメソッド

    Returns
    -------
    is_finished : bool
      ゲームが終了しているか否か
    
    Notes
    -----
    is_pass()と併用する場合はget_next_state()の方が計算量が少なくなる
    """
    player1_legal_board = self.__make_legal_board(0)
    player2_legal_board = self.__make_legal_board(1)

    return player1_legal_board == 0x0000000000000000 and player2_legal_board == 0x0000000000000000

  def change_player(self) -> None:
    """
    プレイヤーを交代する
    """
    self.now_turn = abs(self.now_turn - 1)

  def print_board(self, player_num: int = -1) -> None:
    """
    現在の盤の状態を標準出力に表示するメソッド

    Parameters
    ----------
    player_num : int, default -1
      候補マスを表示するプレイヤー
      -1であれば候補マスを表示しない
    """
    if player_num != -1:
      legal_board = self.__make_legal_board(player_num)
    else:
      legal_board = 0
    print(' 01234567')
    n = 1
    for i in range(8):
      print(str(i), end='')
      for j in range(8):
        #n = 1 << (i*8+j)
        if self.board[0] & n:
          print('●', end='')
        elif self.board[1] & n:
          print('○', end='')
        elif legal_board & n:
          print('□', end='')
        else:
          print(' ', end='')
        n <<= 1
      print()

  def get_board_state(self, show_candidate: bool = False) -> list[list[int]]:
    """
    現在の盤の状態を返すメソッド

    Parameters
    ----------
    show_candidate : bool
      候補マスも含めるか否か

    Returns
    -------
    board_state : list[list[int]]
      現在の盤の状態
      - 0: blank
      - 1: now_turn
      - 2: opponent
      - 3: candidate

    Notes
    -----
    show_candidate = Falseであるならば、self.boardを用いた方が高速になる
    """
    if show_candidate:
      legal_board = self.__make_legal_board(self.now_turn)
      #logger.debug('legal board: {}'.format(legal_board))
    retval = [[0]*8 for _ in range(8)]
    idx = 1
    for i in range(8):
      for j in range(8):
        if self.board[0] & idx:
          retval[i][j] = 1
        elif self.board[1] & idx:
          retval[i][j] = 2
        elif show_candidate and legal_board & idx:
          retval[i][j] = 3
        idx <<= 1
    
    return retval

  def undo(self) -> None:
    """
    盤面を一つ前に戻す
    """
    if len(self.past_data) > 0:
      self.board[0], self.board[1], self.now_turn, self.count, _, _ = self.past_data.pop(-1)

  def get_candidate(self) -> list[list[int]]:
    """
    候補マスのリストを返すメソッド

    Returns
    -------
    candidate_list : list[list[int]]
      候補マスの座標のリスト
    """
    legal_board = self.__make_legal_board(self.now_turn)
    retval = []
    idx = 1
    for i in range(64):
      if idx & legal_board:
        retval.append([i//8, i%8])
      idx <<= 1
    
    return retval

  def get_piece_num(self, player_num: int) -> int:
    i = 1
    retval = 0
    while i<=self.board[player_num]:
      if self.board[player_num] & i:
        retval += 1
      i <<= 1

    return retval

  def result(self) -> int:
    """
    ゲームの結果を返すメソッド

    Returns
    -------
    result : int
      ゲームの結果
      - 0 : Player1の勝利
      - 1 : Player2の勝利
      - 2 : 引き分け
      - -1: ゲームがまだ終了していない
    """
    if not self.is_finished():
      return -1
    
    a_count = self.get_piece_num(0)
    b_count = self.get_piece_num(1)
    
    if a_count > b_count:
      return 0
    if a_count < b_count:  
      return 1
    return 2

  def get_determine_piece_line(self, player_num: int) -> int:
    retval = 0
    i = 0x00_00_00_00_00_00_00_01
    count = 0
    while self.board[player_num] & i:
      i <<= 8
      count += 1
    retval += count
    if i != 0x01_00_00_00_00_00_00_00_00 and self.board[player_num] & 0x01_00_00_00_00_00_00_00:
      i = 0x00_01_00_00_00_00_00_00
      count = 0
      while self.board[player_num] & i:
        i >>= 8
        count += 1
      retval += count
      
    i = 0x01_00_00_00_00_00_00_00
    count = 0
    while self.board[player_num] & i:
      i <<= 1
      count += 1
    retval += count
    if i != 0x01_00_00_00_00_00_00_00_00_00 and self.board[player_num] & 0x80_00_00_00_00_00_00_00:
      i = 0x40_00_00_00_00_00_00_00
      count = 0
      while self.board[player_num] & i:
        i >>= 1
        count += 1
      retval += count

    i = 0x80_00_00_00_00_00_00_00
    count = 0
    while self.board[player_num] & i:
      i >>= 8
      count += 1
    retval += count
    if i != 0x00_00_00_00_00_00_00_00_00 and self.board[player_num] & 0x00_00_00_00_00_00_00_80:
      i = 0x00_00_00_00_00_00_80_00
      count = 0
      while self.board[player_num] & i:
        i <<= 8
        count += 1
      retval += count
    
    i = 0x00_00_00_00_00_00_00_80
    count = 0
    while self.board[player_num] & i:
      i >>= 1
      count += 1
    retval += count
    if i != 0x00_00_00_00_00_00_00_00 and self.board[player_num] & 0x00_00_00_00_00_00_00_01:
      i = 0x00_00_00_00_00_00_00_02
      count = 0
      while self.board[player_num] & i:
        i <<= 1
        count += 1
      retval += count

    return retval

  def get_determine_piece(self, player_num: int) -> int:
    pass


def do_othello(first_player_num):
  othello = OthelloBitBoard(first_player_num)
  now_player_num = first_player_num
  while not othello.is_finished():
    othello.print_board(now_player_num)
    x = int(input('x = '))
    y = int(input('y = '))
    if not othello.reverse(x, y):
      print('Please enter right place')
    else:
      if othello.is_pass():
        if othello.now_turn == 0:
          print('Player1 is skipped')
        else:
          print('Player2 is skipped')
      elif othello.is_finished():
        print('Finish')
        break
      else:
        othello.change_player()
        print('Change player')
    now_player_num = abs(now_player_num - 1)


if __name__ == '__main__':
  do_othello(0)