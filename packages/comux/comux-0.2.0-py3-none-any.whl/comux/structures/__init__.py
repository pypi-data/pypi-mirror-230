from collections import deque as __q
from threading import Event as Event


class LimitedQueue(__q):
  __E: Event

  def __init__(self, maxlen: int | None = None):
    super().__init__([], maxlen=maxlen)
    self.__E = Event()

  def append(self, element) -> None:
    super().append(element)
    self.__E.set()
    return element

  def pop(self, timeout: float | None = None):
    if not self.__E.wait(timeout):
      return None
    try:
      element = super().pop()
      if self.__len__() == 0:
        self.__E.clear()
      return element
    except:
      self.__E.clear()
      return None

  def popleft(self, timeout: float | None = None):
    if not self.__E.wait(timeout):
      return None
    try:
      return super().popleft()
    except:
      self.__E.clear()
      return None


class LimitedDict(dict):
  def __init__(self, maxlen: int | None = None, **kwargs) -> None:
    self.maxlen = maxlen
    return super().__init__(**kwargs)

  def update(self, __m, **kwargs):
    if self.maxlen is not None and len(self) >= self.maxlen:
      self.pop(min([key for key in self.keys() if isinstance(key, int)]))
    # TODO check include
    return super().update(__m, **kwargs)