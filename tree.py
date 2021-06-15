from __future__ import annotations
from typing import TypedDict

class NodeData(TypedDict):
  pass

class NumData(NodeData):
  num: int

class MinMaxNodeData(NodeData):
  board_0: int
  board_1: int
  now_turn: int
  count: int
  x: int
  y: int

class Node:
  def __init__(self, data: NodeData, *next_node: Node) -> None:
    self.data = data
    self.next = []
    for n in next_node:
      self.next.append(n)

  def set_next(self, *next_node: Node) -> None:
    for n in next_node:
      self.next.append(n)

  def is_leaf(self):
    if len(self.next) == 0:
      return True
    
    return False

  def __print(self, node: Node, deepth: int):
    print('{}deepth: {}, node: {}'.format('  '*deepth, deepth, node.data))
    for n in node.next:
      self.__print(n, deepth+1)

  def print(self):
    self.__print(self, 0)


if __name__ == '__main__':
  tree = Node(NumData(num=0))
  n1 = Node(NumData(num=1))
  n2 = Node(NumData(num=2))
  tree.set_next(n1,n2)
  n3 = Node(NumData(num=3))
  n4 = Node(NumData(num=4))
  n1.set_next(n3, n4)
  tree.print()
