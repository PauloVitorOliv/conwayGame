import numpy as np
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import PropertyLayer
from scipy.signal import convolve2d

class GameOfLifeModel(Model):
	def __init__(self, rows=10, cols=10, mode="probabilistic", rounds=10):
		super().__init__()
		# Inicializa a camada de propriedades para os estados das células
		self.cell_layer = PropertyLayer("cells", rows, cols, False, dtype=bool)

		self.dead_layer = PropertyLayer("cells", rows, cols, 0, dtype=int)

		# Métricas e coletor de dados
		self.cells = rows * cols
		self.alive_count = 0
		self.alive_fraction = 0
		self.datacollector = DataCollector(
			model_reporters={"Cells alive": "alive_count",
							 "Fraction alive": "alive_fraction"}
		)
		self.datacollector.collect(self)
		
		# Dados adicionais
		self.iteration = 0
		self.rows = rows
		self.cols = cols
		self.vizInf = 2 #Sobrevive se quantidade de vizinho estiver em [vizInf, vizSup]
		self.vizSup = 3 
		self.vizRen = 3 #Quantidade de vizinhos para renascer
		self.mode = mode  # 'deterministic' or 'probabilistic'
		self.rounds = rounds  # Number of rounds to run

	def step(self):
		# Define um kernel para contar os vizinhos. O kernel tem 1s ao redor da célula central (que é 0).
		# Essa configuração nos permite contar os vizinhos vivos de cada célula ao aplicar a convolução.
		kernel = np.array([[1, 1, 1],
						   [1, 0, 1],
						   [1, 1, 1]])

		# Conta os vizinhos usando convolução.
		# convolve2d aplica o kernel a cada célula da grade, somando os valores dos vizinhos.
		# boundary="wrap" garante que a grade envolva as bordas, simulando uma superfície toroidal.
		neighbor_count = convolve2d(self.cell_layer.data, kernel, mode="same", boundary="wrap")
		has_infected_neighbor = convolve2d(self.dead_layer.data%2, kernel, mode="same", boundary="wrap")

		# Aplica as regras do Jogo da Vida:
		# 1. Uma célula viva com 2 ou 3 vizinhos vivos sobrevive, caso contrário, morre.
		# 2. Uma célula morta com exatamente 3 vizinhos vivos torna-se viva.
		# Essas regras são implementadas usando operações lógicas na grade.
		
		# Apply deterministic or probabilistic rules
		if self.mode == "probabilistic":
			# Probabilistic rules: probability of being alive is proportional to the number of live neighbors
			probabilities = neighbor_count / 8.0  # Normalize to get probabilities (max neighbors = 8)
			self.cell_layer.data = np.logical_and(
       			np.random.rand(self.rows, self.cols) < probabilities,
				self.dead_layer.data == 0
        	)
		else:
			# Deterministic rules (same as classic Game of Life)
			self.cell_layer.data = np.logical_and(
				# ter um end logico. com 
				np.logical_or(
					np.logical_and(self.cell_layer.data, np.logical_and((neighbor_count >= self.vizInf),(neighbor_count <= self.vizSup))),
					np.logical_and(~self.cell_layer.data, neighbor_count == self.vizRen)  # Regra para células mortas
				),
    			(self.dead_layer.data == 0)
			)
   
		# Regras de novos estados
		self.dead_layer.data = np.logical_and(self.dead_layer.data == 2, True)*1 + np.logical_and(
				self.cell_layer.data == False,
    			np.logical_or(
					self.dead_layer.data != 0, has_infected_neighbor != 0
				)
			)*1

		# Métricas
		self.alive_count = np.sum(self.cell_layer.data)
		self.alive_fraction = self.alive_count / self.cells
		self.datacollector.collect(self)
		
	def dims(self):
		return [self.rows, self.cols]
		
	def randomize(self,aliveFraction):
		self.alive_fraction = aliveFraction
		# Define aleatoriamente células como vivas
		self.cell_layer.data = np.random.choice([True, False], size=(self.rows, self.cols), p=[self.alive_fraction, 1 - self.alive_fraction])
		self.datacollector.collect(self)
  
	def updateRule(self, id, val):
		if id == 0:
			self.vizRen = val
		elif id == 1:
			self.vizInf = val
		else:
			self.vizSup = val