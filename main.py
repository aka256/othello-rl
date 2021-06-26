from logging import basicConfig, getLogger, DEBUG, ERROR, INFO
import tkinter as tk
from othello_rl.app import OthelloApp

logger = getLogger(__name__)

def main():
  root = tk.Tk()
  app = OthelloApp(master=root)
  app.mainloop()

if __name__ == '__main__':
  basicConfig(level=DEBUG)
  
  main()