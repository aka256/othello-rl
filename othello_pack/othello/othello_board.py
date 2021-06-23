from abc import ABCMeta, abstractmethod
from typing import TypedDict
from ..bit_opperation import pop_count, flip_horizontal_bm4, flip_vertical_bm4, flip_diagonal_bm4, flip_anti_diagonal_bm4

class OthelloData(TypedDict):
  """
  ある時間でのオセロの盤面データ

  Attributes
  ----------
  board_0 : int
    player0のコマの位置
  board_1 : int
    player1のコマの位置
  turn : int
    この盤面にコマを置くプレイヤー
  count : int
    この盤目までの着手数
  x : int
    この盤面に至る最後の着手位置x
  y : int
    この盤面に至る最後の着手位置y
  """
  board_0: int
  board_1: int
  turn: int
  count: int
  x: int
  y: int

class OthelloBoard(metaclass=ABCMeta):
  """
  オセロの管理クラス

  Attributes
  ----------
  board : list
    player1と2のコマの状況を保持しているリスト
  board_width : int
    盤面の長さ
  now_turn : int
    現在手番であるプレイヤー
  count : int
    手番の総数
  legal_board_cache : list
    leagal_boardのキャッシュ

  Notes
  -----
  以下のサイトを参考にした
  https://qiita.com/sensuikan1973/items/459b3e11d91f3cb37e43
  """
  board: list[int]
  board_width: int
  horizontal_pivot_coff: int
  vertical_pivot_coff: int
  all_pivot_coff: int
  transfer_coff: list[int]

  @abstractmethod
  def __init__(self, first_player_num: int = 0) -> None:    
    self.now_turn = first_player_num
    self.count = 0
    self.past_data = []
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
    
    horizontal_pivot = self.board[player_num-1] & self.horizontal_pivot_coff
    vertical_pivot = self.board[player_num-1] & self.vertical_pivot_coff
    all_pivot = self.board[player_num-1] & self.all_pivot_coff
  
    blank = ~(self.board[0] | self.board[1])

    tmp = horizontal_pivot & (self.board[player_num] << 1)
    for _ in range(self.board_width-2):
      tmp |= horizontal_pivot & (tmp << 1)
    retval = blank & (tmp << 1)

    tmp = horizontal_pivot & (self.board[player_num] >> 1)
    for _ in range(self.board_width-2):
      tmp |= horizontal_pivot & (tmp >> 1)
    retval |= blank & (tmp >> 1)

    tmp = vertical_pivot & (self.board[player_num] << self.board_width)
    for _ in range(self.board_width-2):
      tmp |= vertical_pivot & (tmp << self.board_width)
    retval |= blank & (tmp << self.board_width)

    tmp = vertical_pivot & (self.board[player_num] >> self.board_width)
    for _ in range(self.board_width-2):
      tmp |= vertical_pivot & (tmp >> self.board_width)
    retval |= blank & (tmp >> self.board_width)

    tmp = all_pivot & (self.board[player_num] << (self.board_width-1))
    for _ in range(self.board_width-2):
      tmp |= all_pivot & (tmp << (self.board_width-1))
    retval |= blank & (tmp << (self.board_width-1))

    tmp = all_pivot & (self.board[player_num] << (self.board_width+1))
    for _ in range(self.board_width-2):
      tmp |= all_pivot & (tmp << (self.board_width+1))
    retval |= blank & (tmp << (self.board_width+1))

    tmp = all_pivot & (self.board[player_num] >> (self.board_width+1))
    for _ in range(self.board_width-2):
      tmp |= all_pivot & (tmp >> (self.board_width+1))
    retval |= blank & (tmp >> (self.board_width+1))

    tmp = all_pivot & (self.board[player_num] >> (self.board_width-1))
    for _ in range(self.board_width-2):
      tmp |= all_pivot & (tmp >> (self.board_width-1))
    retval |= blank & (tmp >> (self.board_width-1))

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
    put = 1 << (self.board_width*x+y)
  
    return (put & legal_board) == put

  def reverse(self, x: int, y: int, check_can_put: bool) -> bool:
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
    can_reversed : bool
      コマを裏返すことに成功したか否か
    """
    if check_can_put and not self.__can_put(x, y):
      return False
    
    self.past_data.append(OthelloData(board_0=self.board[0], board_1=self.board[1], turn=self.now_turn, count=self.count, x=x, y=y))
    
    put = 1 << (x*self.board_width+y)
    rev = 0
    for i in range(8):
      _rev = 0
      if i//2 == 0 or i//2 == 3:
        mask = (put << self.transfer_coff[i][0]) & self.transfer_coff[i][1]
      else:
        mask = (put >> self.transfer_coff[i][0]) & self.transfer_coff[i][1]
      while mask and mask & self.board[self.now_turn-1]:
        _rev |= mask
        if i//2 == 0 or i//2 == 3:
          mask = (mask << self.transfer_coff[i][0]) & self.transfer_coff[i][1]
        else:
          mask = (mask >> self.transfer_coff[i][0]) & self.transfer_coff[i][1]
      
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

    if player_legal_board == 0 and opponent_legal_board != 0:
      return 1
    elif player_legal_board == 0 and opponent_legal_board == 0:
      return 2
    
    return 0

  def change_player(self) -> None:
    """
    プレイヤーを交代する
    """
    self.now_turn = abs(self.now_turn - 1)

  def get_board_str(self, show_candidate_player_num: int = -1) -> str:
    """
    現在の盤の状態を返すメソッド

    Parameters
    ----------
    player_num : int, default -1
      候補マスを表示するプレイヤー
      -1であれば候補マスを表示しない

    Returns
    -------
    board_str : str
      盤面の状態
    """
    retstr = ' '
    if show_candidate_player_num != -1:
      legal_board = self.__make_legal_board(show_candidate_player_num)
    else:
      legal_board = 0
    retstr += ''.join(list(range(self.board_width)))
    n = 1
    for i in range(self.board_width):
      retstr += str(i)
      for j in range(self.board_width):
        if self.board[0] & n:
          retstr += '●'
        elif self.board[1] & n:
          retstr += '○'
        elif legal_board & n:
          retstr += '□'
        else:
          retstr += ' '
        n <<= 1
      retstr += '\n'

    return retstr

  def __str__(self):
    return self.get_board_str(-1)

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
    retval = [[0]*self.board_width for _ in range(self.board_width)]
    idx = 1
    for i in range(self.board_width):
      for j in range(self.board_width):
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
      data = self.past_data.pop(-1)
      self.board[0] = data['board_0']
      self.board[1] = data['board_1']
      self.now_turn = data['turn']
      self.count = data['count']
  
  def get_candidate_list(self) -> list[list[int]]:
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
    for i in range(self.board_width**2):
      if idx & legal_board:
        retval.append([i//self.board_width, i%self.board_width])
      idx <<= 1
    
    return retval

  def get_piece_num(self, player_num: int) -> int:
    """
    指定したプレイヤーのコマの総数を返すメソッド

    Parameters
    ----------
    player_num : int
      コマの総数を得たいプレイヤー

    Returns
    -------
    piece_num : int
      コマの総数
    """
    i = 1
    retval = 0
    while i<=self.board[player_num]:
      if self.board[player_num] & i:
        retval += 1
      i <<= 1

    return retval

  def get_result(self) -> int:
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
    if self.get_next_state() == 2:
      return -1
    
    a_count = self.get_piece_num(0)
    b_count = self.get_piece_num(1)
    
    if a_count > b_count:
      return 0
    if a_count < b_count:  
      return 1
    return 2

  @abstractmethod
  def get_determine_piece_line(self, player_num: int) -> int:
    pass

  @abstractmethod
  def get_determine_piece(self, player_num: int) -> int:
    pass


class OthelloBoard4x4(OthelloBoard):
  """
  4x4のオセロの管理クラス

  Attributes
  ----------
  board : list
    player1と2のコマの状況を保持しているリスト
  board_width : int
    盤面の長さ
  now_turn : int
    現在手番であるプレイヤー
  count : int
    手番の総数
  legal_board_cache : list
    leagal_boardのキャッシュ
  """
  board_width = 4
  transfer_coff = [[4, 0xfff0], [3, 0x7770], [1, 0x7777], [5, 0x0777], [4, 0x0fff], [3, 0x0eee], [1, 0xeeee], [5, 0xeee0]]
  
  def __init__(self, first_player_num: int) -> None:
    super().__init__(first_player_num=first_player_num)

    self.board = [0x0_4_2_0, 0x0_2_4_0]
    
  def get_determine_piece_line(self, player_num: int) -> int:
    pass
  
  def get_determine_piece(self, player_num: int) -> int:
    """
    確定石を数え上げるメソッド

    Parameters
    ----------
    player_num : int
      確定石を数えるプレイヤー

    Returns
    -------
    determine_piece_num : int
      確定石の数
    """
    retval = 0
    line_list = [False]*4
    if self.board[player_num] & 0x000f == 0x000f:
      line_list[0] = True
    if self.board[player_num] & 0x1111 == 0x1111:
      line_list[1] = True
    if self.board[player_num] & 0x8888 == 0x8888:
      line_list[2] = True
    if self.board[player_num] & 0xf000 == 0xf000:
      line_list[3] = True
    
    if line_list.count(True) == 4:
      retval = 12
      retval += pop_count(self.board[player_num] & 0x0aa0)
    elif line_list.count(True) == 3:
      if line_list[0] == False:
        bits = flip_vertical_bm4(self.board[player_num])
      elif line_list[1] == False:
        bits = flip_diagonal_bm4(self.board[player_num])
      elif line_list[2] == False:
        bits = flip_anti_diagonal_bm4(self.board[player_num])
      else:
        bits = self.board[player_num]

      retval = 10
      retval += pop_count(bits & 0xa0a0)
      if (bits & 0x4000 or bits & 0x0040) and bits & 0x0400:
        retval += 1
      if (bits & 0x2000 or bits & 0x0020) and bits & 0x0200:
        retval += 1
    elif line_list.count(True) == 2:
      if line_list[0] == line_list[3]:
        if line_list[0] == True:
          bits = flip_diagonal_bm4(self.board[player_num])
        else:
          bits = self.board[player_num]

        retval = 8
        retval += pop_count(bits & 0xa00a)
        if bits & 0x4400 == 0x4400 or bits & 0x0444 == 0x0444:
          retval += 1
        if bits & 0x0044 == 0x0044 or bits & 0x4440 == 0x4440:
          retval += 1
        if bits & 0x2200 == 0x2200 or bits & 0x0222 == 0x0222:
          retval += 1
        if bits & 0x0022 == 0x0022 or bits & 0x2220 == 0x2220:
          retval += 1
      else:
        if line_list[0] and line_list[1]:
          bits = self.board[player_num]
        elif line_list[1] and line_list[3]:
          bits = flip_vertical_bm4(self.board[player_num])
        elif line_list[3] and line_list[2]:
          bits = flip_diagonal_bm4(self.board[player_num])
        else:
          bits = flip_horizontal_bm4(self.board[player_num])

        retval = 7
        retval += pop_count(bits & 0xa0a0)
        if bits & 0xc000 == 0xc000 or bits & 0x6000 == 0x6000:
          retval += 1
        if bits & 0x8800 == 0x8800 or bits & 0x0880 == 0x0880:
          retval += 1
        if bits & 0x2200 == 0x2200 or bits & 0x0220 == 0x0220:
          retval += 1
        if bits & 0x00c0 == 0x00c0 or bits & 0x0060 == 0x0060:
          retval += 1
    elif line_list.count(True) == 1:
      if line_list[0]:
        bits = self.board[player_num]
      elif line_list[1]:
        bits = flip_anti_diagonal_bm4(self.board[player_num])
      elif line_list[2]:
        bits = flip_diagonal_bm4(self.board[player_num])
      else:
        bits = flip_vertical_bm4(self.board[player_num])

      retval = 4
      retval += pop_count(bits & 0x9090)
      if bits & 0x00c0 == 0x00c0 or bits & 0x0070 == 0x0070:
        retval += 1
      if bits & 0x0070 == 0x0070 or bits & 0x0030 == 0x0030:
        retval += 1
      if bits & 0xc000 == 0xc000 or bits & 0x7000 == 0x7000:
        retval += 1
      if bits & 0xe000 == 0xe000 or bits & 0x3000 == 0x3000:
        retval += 1
      if bits & 0x8800 == 0x8800 or bits & 0x0880 == 0x0880:
        retval += 1
      if bits & 0x1100 == 0x1100 or bits & 0x0110 == 0x0110:
        retval += 1
      if bits & 0xec00 == 0xec00:
        retval += 1
      if bits & 0x7300 == 0x7300:
        retval += 1
    else:
      bits = self.board[player_num]
      if bits & 0xc000 == 0xc000 or bits & 0x7000 == 0x7000:
        retval += 1
      if bits & 0x3000 == 0x3000 or bits & 0xe000 == 0xe000:
        retval += 1
      if bits & 0x8800 == 0x8800 or bits & 0x0888 == 0x0888:
        retval += 1
      if bits & 0xec00 == 0xec00 or bits & 0xcc80 == 0xcc80:
        retval += 1
      if bits & 0x7300 == 0x7300 or bits & 0x0331 == 0x0331:
        retval += 1
      if bits & 0x1100 == 0x1100 or bits & 0x0111 == 0x0111:
        retval += 1
      if bits & 0x0011 == 0x0011 or bits & 0x1110 == 0x1110:
        retval += 1
      if bits & 0x08cc == 0x08cc or bits & 0x00ce == 0x00ce:
        retval += 1
      if bits & 0x0133 == 0x0133 or bits & 0x0037 == 0x0037:
        retval += 1
      if bits & 0x000c == 0x000c or bits & 0x0007 == 0x0007:
        retval += 1
      if bits & 0x0003 == 0x0003 or bits & 0x000e == 0x000e:
        retval += 1

    return retval
  

class OthelloBoard8x8(OthelloBoard):
  """
  8x8のオセロの管理クラス

  Attributes
  ----------
  board : list
    player1と2のコマの状況を保持しているリスト
  board_width : int
    盤面の長さ
  now_turn : int
    現在手番であるプレイヤー
  count : int
    手番の総数
  legal_board_cache : list
    leagal_boardのキャッシュ
  """
  board_width = 8
  transfer_coff = [[8, 0xffffffffffffff00], [7, 0x7f7f7f7f7f7f7f00], [1, 0x7f7f7f7f7f7f7f7f], [9, 0x007f7f7f7f7f7f7f], [8, 0x00ffffffffffffff], [7, 0x00fefefefefefefe], [1, 0xfefefefefefefefe], [9, 0xfefefefefefefe00]]
  
  def __init__(self, first_player_num: int) -> None:
    super().__init__(first_player_num=first_player_num)

    self.board = [0x0000000810000000, 0x0000001008000000]
    
  def get_determine_piece_line(self, player_num: int) -> int:
    """
    盤面の縁にある確定石を数え上げるメソッド

    Parameters
    ----------
    player_num : int
      確定石を数えるプレイヤー
    
    Returns
    -------
    determine_piece_num : int
      確定石の数
    """
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