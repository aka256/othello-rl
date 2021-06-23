from othello_pack import bit_opperation
import unittest
import othello_pack
#from .context import othello_pack as oppack
#from .context import othello_pack.bit_opperation
import othello_pack.bit_opperation

class TestBitOpperation(unittest.TestCase):
  def test_flip_vertical_bm8(self):
    """
    flip_vertical_bm8の単体テスト
    """
    self.assertEqual(0x4448507048444478, othello_pack.bit_opperation.flip_vertical_bm8(0x7844444870504844))

  def test_flip_vertical_bm4(self):
    """
    flip_vertical_bm4の単体テスト
    """
    self.assertEqual(0x4321, othello_pack.bit_opperation.flip_vertical_bm4(0x1234))

  def test_flip_horizontal_bm8(self):
    """
    flip_horizontal_bm8の単体テスト
    """
    self.assertEqual(0x1e2222120e0a1222, othello_pack.bit_opperation.flip_horizontal_bm8(0x7844444870504844))

  def test_filp_horizontal_bm4(self):
    """
    flip_horizontal_bm4の単体テスト
    """
    self.assertEqual(0x84c2, othello_pack.bit_opperation.flip_horizontal_bm4(0x1234))

  def test_flip_diagonal_bm8(self):
    self.assertEqual(0x000086493111ff00, othello_pack.bit_opperation.flip_diagonal_bm8(0x7844444870504844))

  def test_flip_diagonal_bm4(self):
    self.assertEqual(0x5680, othello_pack.bit_opperation.flip_diagonal_bm4(0x1234))

  def test_flip_anti_diagonal_bm8(self):
    self.assertEqual(0x00ff888c92610000, othello_pack.bit_opperation.flip_anti_diagonal_bm8(0x7844444870504844))

  def test_flip_anti_diagonal_bm4(self):
    self.assertEqual(0x016a, othello_pack.bit_opperation.flip_anti_diagonal_bm4(0x1234))

  def test_rotate_180_bm8(self):
    self.assertEqual(0x22120a0e1222221e, othello_pack.bit_opperation.rotate_180_bm8(0x7844444870504844))

  def test_rotate_180_bm4(self):
    self.assertEqual(0x2c48, othello_pack.bit_opperation.rotate_180_bm4(0x1234))

  def test_rotate_90_clockwise_bm8(self):
    self.assertEqual(0x00ff113149860000, othello_pack.bit_opperation.rotate_90_clockwise_bm8(0x7844444870504844))

  def test_rotate_90_clockwise_bm4(self):
    self.assertEqual(0x0865, othello_pack.bit_opperation.rotate_90_clockwise_bm4(0x1234))

  def test_rotate_90_anti_clockwise_bm8(self):
    self.assertEqual(0x000061928c88ff00, othello_pack.bit_opperation.rotate_90_anti_clockwise_bm8(0x7844444870504844))

  def test_rotate_90_anti_clockwise_bm4(self):
    self.assertEqual(0xa610, othello_pack.bit_opperation.rotate_90_anti_clockwise_bm4(0x1234))