p2_board = 0x0000000810000000
p1_board = 0x0000001008000000
horizontal_pivot = p2_board & 0x7e7e7e7e7e7e7e7e
blank = ~(p1_board | p2_board)
print('%x' % p1_board)
print('%x' % (p1_board << 1))
tmp = horizontal_pivot & (p1_board << 1)
for _ in range(5):
  tmp |= horizontal_pivot & (tmp << 1)
retval = blank & (tmp << 1)

print('%x' % retval)

if 0x0:
  print(0)

if 0x1:
  print(1)

if 0x2:
  print(2)

if -1:
  print(-1)