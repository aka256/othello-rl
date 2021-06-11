from abc import ABCMeta, abstractmethod
from othello import OthelloBitBoard

class OthelloFeatures(metaclass=ABCMeta):
  """
  盤面から特徴量を取得するための抽象クラス
  """
  @abstractmethod
  def get_index(self, othello: OthelloBitBoard) -> int:
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
  def get_index(self, othello: OthelloBitBoard) -> int:
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
    l = othello.get_board_state(show_candidate=False)
    a_corner = 0  # 0~4 3bit
    b_corner = 0  # 0~4 3bit
    diff = 64     # 0~128 8bit
    blank = 0     # 0~60 6bit   total: 20bit -> 1,048,576
    for i in range(8):
      for j in range(8):
        if (i == 0 or i == 7) and (j == 0 or j == 7):
          if l[i][j] == 1:
            a_corner += 1
          elif l[i][j] == 2:
            b_corner += 1
        if l[i][j] == 0:
          blank += 1
        elif l[i][j] == othello.now_turn+1:
          diff += 1
        else:
          diff -= 1
    
    retval = a_corner + (b_corner << 3) + (diff << 6) + (blank << 14)

    return retval