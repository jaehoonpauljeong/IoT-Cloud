import collections
from itertools import islice

class MovingAverage():
   #self.rssiHisFil[-1]
   def __init__(self, alpha):
         self.alpha = alpha
         self.prior = -1  #beacon.py에서 prior arg로 받을 때
   
   def applyFilter(self, rssiList):
      newrssiList = list(collections.deque(rssiList))

      if self.prior != -1:   #처음이 아닐 때
         newrssiList[-3:].sort()
         self.prior = self.prior * (1- self.alpha) + newrssiList[-1] * self.alpha

      else: #처음일 때
         self.prior = newrssiList[-1]

      return self.prior 