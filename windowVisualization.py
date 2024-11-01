# Dependências 
import pygame
import model

# Constantes Globais
FPS = 60
DEAD, ALIVE = False, True
BACKGROUND_COLOR = (255,255,255)
BORDER_COLOR = (0,0,0)
ALIVE_COLOR = (128,255,128)
DEAD_COLOR = (255,64,64)

# Classes

class Tile:
	def __init__(self, size = 20):
		self._size = size
		self._border = size/16
		self._state = DEAD

	def __len__(self):
		return self._size

	def __repr__(self):
		return f"{self._state}"

	def state(self):
		return self._state

	def change(self):
		self._state = 1 - self._state
  
	def border(self):
		return self._border

class Board:
	def __init__(self, tiling:Tile, game:model.GameOfLifeModel):
		self.game = game
		self.rows, self.cols = game.dims()
		self.tiles = [[0]*self.cols for _ in range(self.rows)]
		for i in range(self.rows):
			for j in range(self.cols):
				self.tiles[i][j] = Tile(len(tiling))
  
	def boardDims(self):
		return [self.rows, self.cols]

	def pixelDims(self):
		return [self.rows * len(self.tiles[0][0]), self.cols * len(self.tiles[0][0])]

	def update(self):
		self.game.step()
		for i in range(self.rows):
			for j in range(self.cols):
				if self.tiles[i][j].state() != self.game.cell_layer.data[i][j]:
					self.tiles[i][j].change()

def drawCurrentGame(board:Board, display):
	gridSize = board.boardDims()
	tileSize = len(board.tiles[0][0])
	tileBorder = board.tiles[0][0].border()
	for i in range(gridSize[0]):
		for j in range(gridSize[1]):
			if board.tiles[i][j].state() == ALIVE:
				pygame.draw.rect(display,BORDER_COLOR,(i*tileSize,j*tileSize,tileSize,tileSize))
				pygame.draw.rect(display,ALIVE_COLOR,(i*tileSize+tileBorder,j*tileSize+tileBorder,tileSize-tileBorder,tileSize-tileBorder))
			else:
				pygame.draw.rect(display,BORDER_COLOR,(i*tileSize,j*tileSize,tileSize,tileSize))
				pygame.draw.rect(display,DEAD_COLOR,(i*tileSize+tileBorder,j*tileSize+tileBorder,tileSize-tileBorder,tileSize-tileBorder))

def runGame(board:Board):
	pygame.init()
	gameRunning = True; updateCounter = 60; microTime = 0

	screenSize = board.pixelDims()
	screenSize[0] += len(board.tiles[0][0])/16
	display = pygame.display.set_mode(board.pixelDims())
	timer = pygame.time.Clock()

	while(gameRunning):
		timer.tick(FPS)
		microTime -= 1
		if microTime <= 0:
			microTime = updateCounter
			board.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				gameRunning = False

		display.fill(BACKGROUND_COLOR)
		drawCurrentGame(board, display)
		pygame.display.update()
    
	pygame.quit()

# Tabuleiro de Exemplo: runGame(Board(Tile(size=24),model.GameOfLifeModel(width=40,height=25)))