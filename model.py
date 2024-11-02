import numpy as np
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import PropertyLayer
from scipy.signal import convolve2d

# fmt: off
class GameOfLifeModel(Model):
    def __init__(self, width=10, height=10, alive_fraction=0.2):
        super().__init__()
        # Inicializa a camada de propriedades para os estados das células
        self.cell_layer = PropertyLayer("cells", width, height, False, dtype=bool)

        # Métricas e coletor de dados
        self.cells = width * height
        self.alive_count = 0
        self.alive_fraction = 0
        self.datacollector = DataCollector(
            model_reporters={"Cells alive": "alive_count",
                             "Fraction alive": "alive_fraction"}
        )
        self.datacollector.collect(self)
        
        # Aditional Data
        self.iteration = 0
        self.width = width
        self.height = height

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

        # Aplica as regras do Jogo da Vida:
        # 1. Uma célula viva com 2 ou 3 vizinhos vivos sobrevive, caso contrário, morre.
        # 2. Uma célula morta com exatamente 3 vizinhos vivos torna-se viva.
        # Essas regras são implementadas usando operações lógicas na grade.
        self.cell_layer.data = np.logical_or(
            np.logical_and(self.cell_layer.data, np.logical_or(neighbor_count == 2, neighbor_count == 3)),
            # Regra para células vivas
            np.logical_and(~self.cell_layer.data, neighbor_count == 3)  # Regra para células mortas
        )

        # Métricas
        self.alive_count = np.sum(self.cell_layer.data)
        self.alive_fraction = self.alive_count / self.cells
        self.datacollector.collect(self)

    def exportData(self):
        return self.cell_layer.data
    
    def dims(self):
        return [self.height, self.width]
    
    def randomize(self,aliveFraction):
        self.alive_fraction = aliveFraction
        # Define aleatoriamente células como vivas
        self.cell_layer.data = np.random.choice([True, False], size=(self.width, self.height), p=[self.alive_fraction, 1 - self.alive_fraction])