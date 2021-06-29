from othello_rl.othello.positional_evaluation import PositionalEvaluation4x4v1, PositionalEvaluation8x8v2, PositionalEvaluation8x8v1
import os
import functools
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from logging import getLogger
from typing import Union, Optional
from othello_rl.othello.agent import Agent, PlayerAgent, QLearningAgent, RandomAgent, MinMaxAgent
from othello_rl.othello.features import Featuresv1, Featuresv2
from othello_rl.othello.board import OthelloBoard, OthelloBoard4x4, OthelloBoard8x8
from othello_rl.file import parse_ql_json

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
  AGENT_KEY = {'Player': PlayerAgent, 'Random': RandomAgent, 'MinMax': MinMaxAgent, 'Q-Learning': QLearningAgent}
  POSEVAL_KEY = {'8x8 v1': PositionalEvaluation8x8v1, '8x8 v2': PositionalEvaluation8x8v2, '4x4 v1': PositionalEvaluation4x4v1}
  FEATURES_KEY = {'v1': Featuresv1, 'v2': Featuresv2}

  def __init__(self, master: Optional[tk.Tk] = None) -> None:
    """
    コンストラクタ

    Parameters
    ----------
    master : tk.Tk or None, default None
      tkのトップレベルのwidget
    """
    # 親クラスのコンストラクタを実行
    super().__init__(master, width=self.width, height=self.height, background='lightgray')
    self.pack(fill='both')

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
    othello_frame = ttk.Frame(self, width=600, height=600)
    othello_frame.grid(row=0, column=0, rowspan=3, columnspan=3, sticky=tk.W+tk.E+tk.N+tk.S)
    self.othello_main = OthelloBoardGUI(othello_frame, 0, 0, 600, 8)
    self.othello_main.start_new_game(PlayerAgent(), PlayerAgent())

    # details
    detail_main_frame = ttk.Frame(self, padding=[10, 5 , 5, 10], relief=tk.GROOVE)
    detail_main_frame.grid(row=0, column=3, sticky=tk.W+tk.E+tk.N+tk.S)

    ttk.Label(detail_main_frame, text='Board size').grid(row=0, column=0)
    self.board_size_spinbox = ttk.Spinbox(detail_main_frame, values=(4,8))
    self.board_size_spinbox.grid(row=0, column=1, pady=10)
    self.board_size_spinbox.set(8)

    agent1_frame = ttk.LabelFrame(detail_main_frame, text='Agent1')
    agent1_frame.grid(row=1, column=0, columnspan=2, pady=10)
    agent1_label = ttk.Label(agent1_frame, text='Agent Type')
    agent1_label.grid(row=0, column=0)
    self.agent1_combobox = ttk.Combobox(agent1_frame, value=list(self.AGENT_KEY.keys()), state='readonly')
    self.agent1_combobox.grid(row=0, column=1, pady=5)
    self.agent1_combobox.current(0)

    option1_labelframe = ttk.Labelframe(agent1_frame, text='Option')
    option1_labelframe.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
    ttk.Label(option1_labelframe, text='Deepth').grid(row=0, column=0, pady=5)
    self.option1_minmax_deepth_spinbox = ttk.Spinbox(option1_labelframe,values=list(range(10)))
    self.option1_minmax_deepth_spinbox.grid(row=0, column=1, columnspan=2, pady=5)
    self.option1_minmax_deepth_spinbox.set(3)

    ttk.Label(option1_labelframe, text='Positional Evaluation').grid(row=1, column=0, pady=5)
    self.option1_minmax_poseval_combobox = ttk.Combobox(option1_labelframe, value=list(self.POSEVAL_KEY.keys()), state='readonly')
    self.option1_minmax_poseval_combobox.grid(row=1, column=1, columnspan=2, pady=5)
    self.option1_minmax_poseval_combobox.current(0)

    ttk.Label(option1_labelframe, text='Features').grid(row=2, column=0, pady=5)
    self.option1_ql_features_combobox = ttk.Combobox(option1_labelframe, value=list(self.FEATURES_KEY.keys()), state='readonly')
    self.option1_ql_features_combobox.grid(row=2, column=1, columnspan=2, pady=5)
    self.option1_ql_features_combobox.current(0)

    ttk.Label(option1_labelframe, text='Data path').grid(row=3, column=0, pady=5)
    self.option1_ql_data_path_entry_val = tk.StringVar()
    self.option1_ql_data_path_entry = ttk.Entry(option1_labelframe, textvariable=self.option1_ql_data_path_entry_val)
    self.option1_ql_data_path_entry.grid(row=3, column=1, pady=5)
    ttk.Button(option1_labelframe, text='Reference', command=functools.partial(self.__file_select, 0)).grid(row=3, column=2)

    ttk.Label(option1_labelframe, text='Initial value').grid(row=4, column=0, pady=5)
    self.option1_ql_init_val_spinbox = ttk.Spinbox(option1_labelframe)
    self.option1_ql_init_val_spinbox.grid(row=4, column=1, columnspan=2, pady=5)
    self.option1_ql_init_val_spinbox.set(0.0)

    agent2_frame = ttk.LabelFrame(detail_main_frame, text='Agent2')
    agent2_frame.grid(row=2, column=0, columnspan=2, pady=10)
    agent2_label = ttk.Label(agent2_frame, text='Agent Type')
    agent2_label.grid(row=2, column=0)
    self.agent2_combobox = ttk.Combobox(agent2_frame, value=list(self.AGENT_KEY.keys()), state='readonly')
    self.agent2_combobox.grid(row=2, column=1, pady=5)
    self.agent2_combobox.current(0)

    option2_labelframe = ttk.Labelframe(agent2_frame, text='Option')
    option2_labelframe.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
    ttk.Label(option2_labelframe, text='Deepth').grid(row=0, column=0, pady=5)
    self.option2_minmax_deepth_spinbox = ttk.Spinbox(option2_labelframe,values=list(range(10)))
    self.option2_minmax_deepth_spinbox.grid(row=0, column=1, columnspan=2, pady=5)
    self.option2_minmax_deepth_spinbox.set(3)

    ttk.Label(option2_labelframe, text='Positional Evaluation').grid(row=1, column=0, pady=5)
    self.option2_minmax_poseval_combobox = ttk.Combobox(option2_labelframe, value=list(self.POSEVAL_KEY.keys()), state='readonly')
    self.option2_minmax_poseval_combobox.grid(row=1, column=1, columnspan=2, pady=5)
    self.option2_minmax_poseval_combobox.current(0)

    ttk.Label(option2_labelframe, text='Features').grid(row=2, column=0, pady=5)
    self.option2_ql_features_combobox = ttk.Combobox(option2_labelframe, value=list(self.FEATURES_KEY.keys()), state='readonly')
    self.option2_ql_features_combobox.grid(row=2, column=1, columnspan=2, pady=5)
    self.option2_ql_features_combobox.current(0)

    ttk.Label(option2_labelframe, text='Data path').grid(row=3, column=0, pady=5)
    self.option2_ql_data_path_entry_val = tk.StringVar()
    self.option2_ql_data_path_entry = ttk.Entry(option2_labelframe, textvariable=self.option2_ql_data_path_entry_val)
    self.option2_ql_data_path_entry.grid(row=3, column=1, pady=5)
    ttk.Button(option2_labelframe, text='Reference', command=functools.partial(self.__file_select, 1)).grid(row=3, column=2)

    ttk.Label(option2_labelframe, text='Initial value').grid(row=4, column=0, pady=5)
    self.option2_ql_init_val_spinbox = ttk.Spinbox(option2_labelframe)
    self.option2_ql_init_val_spinbox.grid(row=4, column=1, columnspan=2, pady=5)
    self.option2_ql_init_val_spinbox.set(0.0)

    agent_button = ttk.Button(detail_main_frame, text='New game', command=self.__push_agent_button)
    agent_button.grid(row=3, column=0, columnspan=2, pady=5)
    

    #state_frame = ttk.Frame(self, )
    #state_frame.grid(row=1, column=3, rowspan=2, sticky=tk.W+tk.E+tk.N+tk.S)

  def __on_new_game(self, event: Optional[tk.Event] = None) -> None:
    """
    メニューのNew gameをクリックしたときに呼び出されるメソッド

    Parameters
    ----------
    event : tk.Event or None, default None
      イベントのプロパティ
    """
    self.othello_main.start_new_game(PlayerAgent(), MinMaxAgent(3, PositionalEvaluation8x8v1()))

  def __on_undo(self, event: Optional[tk.Event] = None) -> None:
    """
    メニューのUndoをクリックしたときに呼び出されるメソッド

    Parameters
    ----------
    event : tk.Event or None, default None
      イベントのプロパティ
    """
    self.othello_main.undo()

  def __file_select(self, entry_idx: int) -> None:
    """
    
    """
    file_types = [('JSON', '*.json')]
    entry_list = [self.option1_ql_data_path_entry_val, self.option2_ql_data_path_entry_val]
    file_path = filedialog.askopenfilename(filetypes=file_types, initialdir=os.path.abspath(os.path.dirname(__file__)))
    entry_list[entry_idx].set(file_path)

  def __push_agent_button(self) -> None:
    """
    
    """
    agent1 = self.AGENT_KEY[self.agent1_combobox.get()]
    agent2 = self.AGENT_KEY[self.agent2_combobox.get()]
    board_size = int(self.board_size_spinbox.get())

    if agent1 == MinMaxAgent:
      deepth = int(self.option1_minmax_deepth_spinbox.get())
      poseval = self.POSEVAL_KEY[self.option1_minmax_poseval_combobox.get()]()
      agent1 = agent1(deepth, poseval)
    elif agent1 == QLearningAgent:
      features = self.FEATURES_KEY[self.option1_ql_features_combobox.get()]()
      data = parse_ql_json(self.option1_ql_data_path_entry_val, 1)
      init_val = float(self.option1_ql_init_val_spinbox.get())
      agent1 = agent1(features, data, init_val)
    else:
      agent1 = agent1()

    if agent2 == MinMaxAgent:
      deepth = int(self.option2_minmax_deepth_spinbox.get())
      poseval = self.POSEVAL_KEY[self.option2_minmax_poseval_combobox.get()]()
      agent2 = agent2(deepth, poseval)
    elif agent2 == QLearningAgent:
      features = self.FEATURES_KEY[self.option2_ql_features_combobox.get()]()
      data = parse_ql_json(self.option2_ql_data_path_entry_val, 1)
      init_val = float(self.option2_ql_init_val_spinbox.get())
      agent2 = agent2(features, data, init_val)
    else:
      agent2 = agent2()

    self.othello_main.start_new_game(agent1, agent2, board_size)


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
  board_size : int
    オセロのサイズ, 4 or 8
  game : othello.board.OthelloBoard
    OthelloBoardを管理する変数
  agent1 : othello.agent.Agent
    agent1
  agent2 : othello.agent.Agent
    agent2
  """

  def __init__(self, parent: tk.Frame, place_x: int, place_y: int, board_width: int, board_size: int = 8) -> None:
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
    board_size : int, default 8
      オセロのサイズ
    """
    self.board_width = board_width
    self.line_width = board_width//150
    self.frame_width = board_width//12
    self.enable_click_board = False
    self.board_size = board_size

    # メインとなるキャンバス
    super().__init__(parent, highlightthickness=0, background='green')
    self.place(x=place_x, y=place_y, width=self.board_width, height=self.board_width)

    # キャンバスに左クリックをバインド(オセロ盤内なら全ての場所でクリックイベントを取得する)
    self.bind('<1>', self.__click_board)

    # オセロ盤の線
    for i in range(self.board_size+1):
      self.create_line(0, (self.board_width-self.line_width)/self.board_size*i+self.line_width/2, self.board_width, (self.board_width-self.line_width)/self.board_size*i+self.line_width/2, width=self.line_width, fill='black')
      self.create_line((self.board_width-self.line_width)/self.board_size*i+self.line_width/2, 0, (self.board_width-self.line_width)/self.board_size*i+self.line_width/2, self.board_width, width=self.line_width, fill='black')
    

  def start_new_game(self, agent1: Agent, agent2: Agent, board_size: int = 8, first_player_num: int = 0) -> None:
    """
    新しくゲームを始めるメソッド

    Parameters
    ----------
    agent1 : othello.agent.Agent
      agent1
    agent2 : othello.agent.Agent
      agent2
    first_player_num : int, dafault 0
      最初のプレイヤー
    """
    self.agent1 = agent1
    self.agent2 = agent2
    self.board_size = board_size

    if self.board_size == 4:  
      self.game = OthelloBoard4x4(first_player_num)
    elif self.board_size == 8:
      self.game = OthelloBoard8x8(first_player_num)
    self.__draw_othello_state(self.game)

    self.__step()

  def __step(self):
    if hasattr(self, 'game'):
      if self.game.now_turn == 0:
        if type(self.agent1) is PlayerAgent:
          self.enable_click_board = True
        else:
          result = self.agent1.step(self.game)
      else:
        if type(self.agent2) is PlayerAgent:
          self.enable_click_board = True
        else:
          result = self.agent2.step(self.game)
      
      if not self.enable_click_board and result:
        next = self.game.get_next_state()
        #logger.debug('Next State: {}'.format(next))
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
    for i in range(self.board_size):
      if event.x-self.board_width/self.board_size/2*(2*i+1)-self.frame_width/2 <= x <= event.x-self.board_width/self.board_size/2*(2*i+1)+self.frame_width/2:
        x = i
      if event.y-self.board_width/self.board_size/2*(2*i+1)-self.frame_width/2 <= y <= event.y-self.board_width/self.board_size/2*(2*i+1)+self.frame_width/2:
        y = i
    
    logger.debug('x: {}, y: {}'.format(x, y))

    if x != -1 and y != -1:
      if self.game.now_turn == 0:
        result = self.agent1.step(self.game, x, y)
      else:
        result = self.agent2.step(self.game, x, y)
      
      if result:
        next = self.game.get_next_state()
        #logger.debug('Next State: {}'.format(next))
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
    x1 = self.board_width/self.board_size*x + self.board_width/self.board_size/2 - self.frame_width/2
    y1 = self.board_width/self.board_size*y + self.board_width/self.board_size/2 - self.frame_width/2
    x2 = self.board_width/self.board_size*x + self.board_width/self.board_size/2 + self.frame_width/2
    y2 = self.board_width/self.board_size*y + self.board_width/self.board_size/2 + self.frame_width/2

    self.delete(frame_tag)
    if state == 1:
      self.create_oval(x1, y1, x2, y2, fill='black', tags=frame_tag)
    elif state == 2:
      self.create_oval(x1, y1, x2, y2, fill='white', tags=frame_tag)
    elif state == 3:
      self.create_rectangle(x1, y1, x2, y2, fill='blue', tags=frame_tag)
    else:
      pass

  def __draw_othello_state(self, othello_board: OthelloBoard, _show_candidate: bool = True) -> None:
    """
    othello_boardの現在の状態を表示するメソッド

    Parameters
    ----------
    othello_board : othello.board.OthelloBoard
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

