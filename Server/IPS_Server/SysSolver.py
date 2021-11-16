from scipy.spatial import distance

import numpy as np
from sympy import symbols, nsolve
# from sympy.solvers.solveset import nonlinsolve
# import mpmath
# mpmath.mp.dps = 15

# from Beacon import Beacon

class SysSolver:
	"""docstring for SysSolver"""

	def __init__(self):
		super(SysSolver, self).__init__()
		self.x = symbols('x')
		self.y = symbols('y')

	def equations(self, paras):
		F = [None] * len(paras)
		for nequ in range(len(paras)):
			# f=(x-x_i)^2+(y-y_i)^2-d^2
			F[nequ] = (self.x-paras[nequ][0])**2+(self.y-paras[nequ][1])**2-paras[nequ][2]**2			
		return F
	
	def runSolver(self, sysMat):
		sysEqu = self.equations(paras=sysMat)
		res=nsolve(sysEqu, (self.x, self.y), (6,6), verify=False)
		return res