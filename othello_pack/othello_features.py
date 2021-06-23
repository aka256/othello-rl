from abc import ABCMeta, abstractmethod
from self_made_error import ArgsError
from othello_pack.othello_board import OthelloBoard4x4, OthelloBoard8x8
from othello_pack.bit_opperation import pop_count
from othello_board import OthelloBoard

class OthelloFeatures(metaclass=ABCMeta):
  """
  盤面から特徴量を取得するための抽象クラス
  """
  @abstractmethod
  def get_index(self, othello: OthelloBoard) -> int:
    """
    盤面から特徴量のインデックスを取得するメソッド
    
    Parameters
    ----------
    othello : OthelloBoard
      盤面の状況
    
    Returns
    -------
    index : int
      盤面の特徴量のインデックス
    """
    pass


class OthelloFeaturesv1(OthelloFeatures):
  """
  盤面から特徴量を取得するためのクラス

  Notes
  -----
  以下の特徴量を利用している
  - Player1と2の取得している角の数(a_corner, b_corner)
  - Player1と2のコマの差(diff)
  - 空白マスの数(blank)

  また、インデックスは以下のように決定している
  | blank  |   diff   | b_corner | a_corner |
  | 000000 | 00000000 |   000    |   000    |
  """
  def get_index(self, othello: OthelloBoard) -> int:
    """
    盤面から特徴量のインデックスを取得するメソッド
    
    Parameters
    ----------
    othello : OthelloBitBoard
      盤面の状況
    
    Returns
    -------
    index : int
      盤面の特徴量のインデックス
    """
    if isinstance(othello, OthelloBoard4x4):
      a_corner = pop_count(othello.board[0] & 0x9009)
      b_corner = pop_count(othello.board[1] & 0x9009)
    elif isinstance(othello, OthelloBoard8x8):
      a_corner = pop_count(othello.board[0] & 0x8100000000000081)
      b_corner = pop_count(othello.board[1] & 0x8100000000000081)
    else:
      ArgsError('othello({}) isn\'t defined in {}'.format(othello, self))

    a_piece_num = pop_count(othello.board[0])
    b_piece_num = pop_count(othello.board[1])
    diff = abs(a_piece_num - b_piece_num)
    blank = othello.board_width**2 - (a_piece_num + b_piece_num)

    retval = a_corner + (b_corner << 3) + (diff << 6) + (blank << 14)

    return retval