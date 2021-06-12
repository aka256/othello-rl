from positional_evaluation import OthelloPositionalEvaluationv2
import tkinter as tk
import othello
from logging import basicConfig, getLogger, DEBUG, ERROR, INFO
from typing import Union, Optional
from agent import OthelloAgent, OthelloPlayerAgent, OthelloQLearningAgent, OthelloRandomAgent, OthelloMinMaxAgent
from features import OthelloFeaturesv1

basicConfig(level=INFO)
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
  othello_main : OthelloBoardGUI
    メインのオセロ盤を保持している変数
  """
  width = 800
  height = 600

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
    self.othello_main = OthelloBoardGUI(self, 0, 0, 600)
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
    self.othello_main.start_new_game(OthelloPlayerAgent(), OthelloMinMaxAgent(5, OthelloPositionalEvaluationv2()))

  def __on_undo(self, event: Optional[tk.Event] = None) -> None:
    """
    メニューのUndoをクリックしたときに呼び出されるメソッド

    Parameters
    ----------
    event : tk.Event or None, default None
      イベントのプロパティ
    """
    self.othello_main.undo()


class OthelloBoardGUI(tk.Canvas):
  """
  オセロの盤面を管理するクラス

  Attributes
  ----------
  line_width : int
    オセロ盤の線の幅
  board_width : int
    オセロ盤の幅、高さ
  frame_width : int
    コマの幅、高さ
    候補マスの表示もこれによる
  game : othello.OthelloBitBoard
    OthelloBitBoardを管理する変数
  agent1 : OthelloAgent
    agent1
  agent2 : OthelloAgent
    agent2
  """

  def __init__(self, parent: tk.Tk, place_x: int, place_y: int, board_width: int) -> None:
    """
    コンストラクタ

    Parameters
    ----------
    place_x : int
      設置するキャンバスのx座標
    place_y : int
      設置するキャンバスのy座標
    board_width : int
      オセロ盤の幅、高さ
    """
    self.board_width = board_width
    self.line_width = board_width//150
    self.frame_width = board_width//12
    self.enable_click_board = False

    # メインとなるキャンバス
    super().__init__(parent, highlightthickness=0, background='green')
    self.place(x=place_x, y=place_y, width=self.board_width, height=self.board_width)

    # キャンバスに左クリックをバインド(オセロ盤内なら全ての場所でクリックイベントを取得する)
    self.bind('<1>', self.__click_board)

    # オセロ盤の線
    for i in range(9):
      self.create_line(0, (self.board_width-self.line_width)/8*i+self.line_width/2, self.board_width, (self.board_width-self.line_width)/8*i+self.line_width/2, width=self.line_width, fill='black')
      self.create_line((self.board_width-self.line_width)/8*i+self.line_width/2, 0, (self.board_width-self.line_width)/8*i+self.line_width/2, self.board_width, width=self.line_width, fill='black')
    

  def start_new_game(self, agent1: OthelloAgent, agent2: OthelloAgent, first_player_num: int = 0) -> None:
    """
    新しくゲームを始めるメソッド

    Parameters
    ----------
    agent1 : OthelloAgent
      agent1
    agent2 : OthelloAgent
      agent2
    first_player_num : int, dafault 0
      最初のプレイヤー
    """
    self.agent1 = agent1
    self.agent2 = agent2

    self.game = othello.OthelloBitBoard(first_player_num)
    self.__draw_othello_state(self.game)

    self.__step()

  def __step(self):
    if hasattr(self, 'game'):
      if self.game.now_turn == 0:
        if type(self.agent1) is OthelloPlayerAgent:
          self.enable_click_board = True
        else:
          self.game, result = self.agent1.step(self.game)
      else:
        if type(self.agent2) is OthelloPlayerAgent:
          self.enable_click_board = True
        else:
          self.game, result = self.agent2.step(self.game)
      
      if not self.enable_click_board and result:
        next = self.game.get_next_state()
        logger.debug('Next State: {}'.format(next))
        if next == 0:
          self.game.change_player()
        elif next == 1:
          pass
        else:
          logger.debug('Fin')
        self.__draw_othello_state(self.game)
        if next == 0 or next == 1:
          return self.__step()
      elif not self.enable_click_board and not result:
        pass
    else:
      pass

  def __click_board(self, event: tk.Event) -> None:
    """
    オセロ盤をクリックしたときに呼び出されるメソッド

    Parameters
    ----------
    event : tk.Event
      イベントのプロパティ
    """
    if not self.enable_click_board:
      return

    # クリックした位置を取得
    x = y = -1
    for i in range(8):
      if event.x-self.board_width/16*(2*i+1)-self.frame_width/2 <= x <= event.x-self.board_width/16*(2*i+1)+self.frame_width/2:
        x = i
      if event.y-self.board_width/16*(2*i+1)-self.frame_width/2 <= y <= event.y-self.board_width/16*(2*i+1)+self.frame_width/2:
        y = i
    
    if x != -1 and y != -1:
      if self.game.now_turn == 0:
        self.game, result = self.agent1.step(self.game, x, y)
      else:
        self.game, result = self.agent2.step(self.game, x, y)
      
      if result:
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
    
    self.enable_click_board = False
    self.__step()

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
    x1 = self.board_width/8*x+self.board_width/16-self.frame_width/2
    y1 = self.board_width/8*y+self.board_width/16-self.frame_width/2
    x2 = self.board_width/8*x+self.board_width/16+self.frame_width/2
    y2 = self.board_width/8*y+self.board_width/16+self.frame_width/2

    self.delete(frame_tag)
    if state == 1:
      self.create_oval(x1, y1, x2, y2, fill='black', tags=frame_tag)
    elif state == 2:
      self.create_oval(x1, y1, x2, y2, fill='white', tags=frame_tag)
    elif state == 3:
      self.create_rectangle(x1, y1, x2, y2, fill='blue', tags=frame_tag)
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

  def undo(self) -> None:
    """
    一手前に戻すメソッド
    """
    self.game.undo()
    self.__draw_othello_state(self.game)

if __name__ == '__main__':
  root = tk.Tk()
  app = OthelloApp(master=root)
  app.mainloop()

