import tkinter as tk
import othello
from logging import basicConfig, getLogger, DEBUG, ERROR, INFO
from typing import Union, Optional

basicConfig(level=DEBUG)
logger = getLogger(__name__)

class OthelloApp(tk.Frame):
  """
  オセロのデバッグ用ソフトのGUI管理クラス

  Attributes
  ----------
  width : int
    windowの幅
  height : int
    windowの高さ
  line_width : int
    オセロ盤の線の幅
  board_width : int
    オセロ盤の幅、高さ
  game : othello.OthelloBitBoard
    オセロクラスを保持している変数
  othello_board : tk.Canvas
    オセロ盤を表示しているキャンバス
  """
  width = 800
  height = 600
  line_width = 4

  board_width = 600

  def __init__(self, master: Optional[tk.Tk] = None) -> None:
    """
    コンストラクタ

    Parameters
    ----------
    master : tk.Tk or None, default None
      tkのトップレベルのwidget
    """
    # 親クラスのコンストラクタを実行
    super().__init__(master, width = self.width, height= self.height, background='lightgray')
    self.pack()

    # タイトル
    self.master.title('Othell debug')

    # メニュー
    menu = tk.Menu(self)

    file_menu = tk.Menu(menu, tearoff=0)
    file_menu.add_command(label='New game', command=self.__on_new_game)
    file_menu.add_command(label='Undo', command=self.__on_undo)
    file_menu.add_separator()
    file_menu.add_command(label='Exit', command=quit)
    menu.add_cascade(label='Menu', menu=file_menu)

    self.master.configure(menu=menu)
    
    # ショートカットキーの指定
    self.bind('<Control-Key-n>', self.__on_new_game)
    self.bind('<Control-Key-z>', self.__on_undo)
    self.bind('<Control-Key-q>', quit)
    self.focus_set()

    # オセロ盤の表示
    self.__draw_othello_board(0, 0)
    self.__on_new_game()

    # stateのラベル
    #self

  def __on_new_game(self, event: Optional[tk.Event] = None) -> None:
    """
    メニューのNew gameをクリックしたときに呼び出されるメソッド

    Parameters
    ----------
    event : tk.Event or None, default None
      イベントのプロパティ
    """
    self.game = othello.OthelloBitBoard(0)
    self.__draw_othello_state(self.game)

  def __on_undo(self, event: Optional[tk.Event] = None) -> None:
    """
    メニューのUndoをクリックしたときに呼び出されるメソッド

    Parameters
    ----------
    event : tk.Event or None, default None
      イベントのプロパティ
    """
    self.game.undo()
    self.__draw_othello_state(self.game)

  def __draw_othello_board(self, _x: int, _y: int) -> None:
    """
    オセロ盤の表示を行うメソッド

    Parameters
    ----------
    _x : int
      表示するオセロ盤のx座標
    _y : int
      表示するオセロ盤のy座標
    """
    # メインとなるキャンバス
    self.othello_board = tk.Canvas(self, highlightthickness=0, background='green')
    self.othello_board.place(x=_x, y=_y, width=self.board_width, height=self.board_width)

    # キャンバスに左クリックをバインド(オセロ盤内なら全ての場所でクリックイベントを取得する)
    self.othello_board.bind('<1>', self.__click_board)

    # オセロ盤の線
    for i in range(9):
      self.othello_board.create_line(0, (self.board_width-self.line_width)/8*i+self.line_width/2, self.board_width, (self.board_width-self.line_width)/8*i+self.line_width/2, width=self.line_width, fill='black')
      self.othello_board.create_line((self.board_width-self.line_width)/8*i+self.line_width/2, 0, (self.board_width-self.line_width)/8*i+self.line_width/2, self.board_width, width=self.line_width, fill='black')
  
  def __click_board(self, event: tk.Event) -> None:
    """
    オセロ盤をクリックしたときに呼び出されるメソッド

    Parameters
    ----------
    event : tk.Event
      イベントのプロパティ
    """
    # クリックした位置を取得
    x = y = -1
    for i in range(8):
      if event.x-self.board_width/16*(2*i+1)-25 <= x <= event.x-self.board_width/16*(2*i+1)+25:
        x = i
      if event.y-self.board_width/16*(2*i+1)-25 <= y <= event.y-self.board_width/16*(2*i+1)+25:
        y = i
    
    if x != -1 and y != -1:
      if self.game.reverse(x, y):
        next = self.game.get_next_state()
        logger.debug('Next State: {}'.format(next))
        if next == 0:
          self.game.change_player()
        elif next == 1:
          pass
        else:
          logger.debug('Fin')
        self.__draw_othello_state(self.game)
      else:
        pass

  def __get_frame_tag(self, x: int, y: int) -> str:
    """
    コマのタグを返すメソッド

    Parameters
    ----------
    x : int
      盤上でのx座標
    y : int
      盤上でのy座標

    Returns
    -------
    frame_tag : str
      (x, y)のタグ

    Notes
    -----
    タグはコマの座標に依存し、コマの種類もしくは候補用の矩形にはよらない
    """
    return 'frame-'+str(x)+'.'+str(y)

  def __set_frame(self, x: int, y: int, state: int) -> None:
    """
    指定された座標上にコマを設置するメソッド

    Parameters
    ----------
    x : int
      コマのx座標
    y : int
      コマのy座標
    state : int
      コマの種類
      0: 黒駒
      1: 白駒
      2: 候補マス
    """
    frame_tag = self.__get_frame_tag(x, y)
    x1 = self.board_width/8*x+self.board_width/16-25
    y1 = self.board_width/8*y+self.board_width/16-25
    x2 = self.board_width/8*x+self.board_width/16+25
    y2 = self.board_width/8*y+self.board_width/16+25

    self.othello_board.delete(frame_tag)
    if state == 1:
      self.othello_board.create_oval(x1, y1, x2, y2, fill='black', tags=frame_tag)
    elif state == 2:
      self.othello_board.create_oval(x1, y1, x2, y2, fill='white', tags=frame_tag)
    elif state == 3:
      self.othello_board.create_rectangle(x1, y1, x2, y2, fill='blue', tags=frame_tag)
    else:
      pass

  def __draw_othello_state(self, othello_board: othello.OthelloBitBoard, _show_candidate: bool = True) -> None:
    """
    othello_boardの現在の状態を表示するメソッド

    Parameters
    ----------
    othello_board : othello.OthelloBitBoard
      表示したいオセロ盤のクラス
    _show_candidate : bool
      候補マスを表示するか
    """
    l = othello_board.get_board_state(show_candidate=_show_candidate)
    for idx_i, i in enumerate(l):
      for idx_j, j in enumerate(i):
        self.__set_frame(idx_i, idx_j, j)


if __name__ == '__main__':
  root = tk.Tk()
  app = OthelloApp(master=root)
  app.mainloop()

