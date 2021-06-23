"""
bit演算の補助メソッド群

Notes
-----
以下のサイトを参考にした
https://primenumber.hatenadiary.jp/entry/2016/12/03/203823
https://www.chessprogramming.org/Flipping_Mirroring_and_Rotating

bm8: bit matrix 8x8
bm4: bit matrix 4x4
"""



def delta_swap(bits: int, mask: int, delta) -> int:
  """
  bits内の部分ビット列の交換

  Parameters
  ----------
  bits : int
    もととなるビット列
  mask : int
    交換したい部分列の下位部分
  delta : int
    移動量
  """
  x = (bits ^ (bits >> delta)) & mask
  return bits ^ x ^ (x << delta)

def flip_vertical_bm8(bits: int) -> int:
  """
  bit matrixの垂直方向への反転
  """
  bits = delta_swap(bits, 0x00ff00ff00ff00ff, 8)
  bits = delta_swap(bits, 0x0000ffff0000ffff, 16)
  return delta_swap(bits, 0x00000000ffffffff, 32)

def flip_vertical_bm4(bits: int) -> int:
  """
  bit matrixの垂直方向への反転
  """
  bits = delta_swap(bits, 0x0f0f, 4)
  return delta_swap(bits, 0x00ff, 8)

def flip_horizontal_bm8(bits: int) -> int:
  """
  bit matrixの水平方向への反転
  """
  bits = delta_swap(bits, 0x5555555555555555, 1)
  bits = delta_swap(bits, 0x3333333333333333, 2)
  return delta_swap(bits, 0x0f0f0f0f0f0f0f0f, 4)

def flip_horizontal_bm4(bits: int) -> int:
  """
  bit matrixの水平方向への反転
  """
  bits = delta_swap(bits, 0x5555, 1)
  return delta_swap(bits, 0x3333, 2)

def flip_diagonal_bm8(bits: int) -> int:
  """
  bit matrixの対角線方向への反転

  Notes
  -----
  以下の対角線で反転する
  . . . /
  . . / .
  . / . .
  / . . .
  """
  bits = delta_swap(bits, 0x000000000f0f0f0f, 36)
  bits = delta_swap(bits, 0x0000333300003333, 18)
  return delta_swap(bits, 0x0055005500550055, 9)

def flip_diagonal_bm4(bits: int) -> int:
  """
  bit matrixの水平方向への反転

  Notes
  -----
  以下の対角線で反転する
  . . . /
  . . / .
  . / . .
  / . . .
  """
  bits = delta_swap(bits, 0x0033, 10)
  return delta_swap(bits, 0x0505, 5)

def flip_anti_diagonal_bm8(bits: int) -> int:
  """
  bit matrixの対角線方向への反転

  Notes
  -----
  以下の対角線で反転する
  \ . . .
  . \ . .
  . . \ .
  . . . \
  """
  bits = delta_swap(bits, 0x00000000f0f0f0f0, 28)
  bits = delta_swap(bits, 0x0000cccc0000cccc, 14)
  return delta_swap(bits, 0x00aa00aa00aa00aa, 7)

def flip_anti_diagonal_bm4(bits: int) -> int:
  """
  bit matrixの水平方向への反転

  Notes
  -----
  以下の対角線で反転する
  \ . . .
  . \ . .
  . . \ .
  . . . \
  """
  bits = delta_swap(bits, 0x00cc, 6)
  return delta_swap(bits, 0x0a0a, 3)

def rotate_180_bm8(bits: int) -> int:
  """
  bit matrixの180度回転

  Parameters
  ----------
  bits : int
    対象となるbit matrix
  """
  return flip_horizontal_bm8(flip_vertical_bm8(bits))

def rotate_180_bm4(bits: int) -> int:
  """
  bit matrixの180度回転

  Parameters
  ----------
  bits : int
    対象となるbit matrix
  """
  return flip_horizontal_bm4(flip_vertical_bm4(bits))

def rotate_90_clockwise_bm8(bits: int) -> int:
  """
  bit matrixの時計回りに90度回転

  Parameters
  ----------
  bits : int
    対象となるbit matrix
  """
  return flip_vertical_bm8(flip_diagonal_bm8(bits))

def rotate_90_clockwise_bm4(bits: int) -> int:
  """
  bit matrixの時計回りに90度回転

  Parameters
  ----------
  bits : int
    対象となるbit matrix
  """
  return flip_vertical_bm4(flip_diagonal_bm4(bits))

def rotate_90_anti_clockwise_bm8(bits: int) -> int:
  """
  bit matrixの反時計回りに90度回転

  Parameters
  ----------
  bits : int
    対象となるbit matrix
  """
  return flip_vertical_bm8(flip_anti_diagonal_bm8(bits))

def rotate_90_anti_clockwise_bm4(bits: int) -> int:
  """
  bit matrixの反時計回りに90度回転

  Parameters
  ----------
  bits : int
    対象となるbit matrix
  """
  return flip_vertical_bm4(flip_anti_diagonal_bm4(bits))

def pop_count(bits: int) -> int:
  """
  bitが1の部分を数え上げる

  Parameters
  ----------
  bits : int
    対象となる数

  Returns
  -------
  num : int
    bits内の1の数
  """
  return bin(bits).count('1')