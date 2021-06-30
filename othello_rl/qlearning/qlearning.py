from logging import getLogger

logger = getLogger(__name__)

class QLearning:
  """
  Q-Learning用のクラス

  Attributes
  ----------
  alpha : float
    学習率α
  gamma : float
    割引率γ
  data : dict
    Q-Learningでの学習結果の保存用辞書
  init_value : float
    dataの初期値
  """
  def __init__(self, alpha: float, gamma: float, data: dict = {}, init_value: float = 0) -> None:
    self.alpha = alpha
    self.gamma = gamma

    self.data = data
    self.init_value = init_value

  def get(self, s: int, a: int) -> float:
    """
    dataから値の取得

    Parameters
    ----------
    s : int
      状態
    a : int
      行動

    Returns
    -------
    value : float
      Q値, Q(s, a)
    """
    return self.data.get((s, a), self.init_value)
    
  def __set(self, s: int, a: int, value: float) -> None:
    """
    dataへの値の代入

    Parameters
    ----------
    s : int
      状態
    a : int
      行動
    value : float
      代入するQ値, Q(s, a)
    """
    self.data[(s, a)] = value

  def update(self, s: int, a: int, r: float, q: float, *q_old: float) -> float:
    """
    Q値の更新

    Parameters
    ----------
    s : int
      状態
    a : int
      行動
    r : float
      報酬
    q : float
      Q(s_t+1, a)
    q_old : float
      Q(s, a)

    Returns
    ------
    q_new : float
      updateされたQ値
    """
    if len(q_old) == 0:
      q_old = self.get(s, a)
    else:
      q_old = q_old[0]
    #print('alpha:{}, q_old:{}, r:{}, gamma:{}, q:{}'.format(self.alpha, q_old, r, self.gamma, q))
    q_new = (1-self.alpha)*q_old+self.alpha*(r + self.gamma*q)

    self.__set(s, a, q_new)

    return q_new
