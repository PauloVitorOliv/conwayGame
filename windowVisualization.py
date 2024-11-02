# Dependências 
import pygame
import model

# Constantes Globais
FPS = 30
DEAD, ALIVE = False, True
BACKGROUND_COLOR = (32,32,32)
BORDER_COLOR = (0,0,0)
ALIVE_COLOR = (128,255,128)
DEAD_COLOR = (255,64,64)

# Classes

class Tile:
	def __init__(self, size = 1):
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
	def __init__(self, game:model.GameOfLifeModel):
		self.game = game
		self.rows, self.cols = game.dims()
		self.tiles = [[0]*self.cols for _ in range(self.rows)]
		for i in range(self.rows):
			for j in range(self.cols):
				self.tiles[i][j] = Tile()
  
	def boardDims(self):
		return [self.rows, self.cols]

	def update(self):
		self.game.step()
		for i in range(self.rows):
			for j in range(self.cols): #O modelo considera em cell_layer.data[coluna][linha], na visualização, o contrário
				if self.tiles[i][j].state() != self.game.cell_layer.data[j][i]:
					self.tiles[i][j].change()
     
class Screen:
	def __init__(self, board:Board, width, height):
		self.board = board
		self.width = width
		self.height = height
		self.scaling = int(min((width * (12/16))/board.cols , (height * (7/9)/board.rows)))

		expectedWidth = width*(12/16); expectedHeight = height*(7/9)
		actualWidth = self.scaling*board.cols; actualHeight = self.scaling*board.rows

		self.originX = int(width/16 + (expectedWidth-actualWidth)/2); self.originY = int(height/9 + (expectedHeight-actualHeight)/2)
		self.endX = int(13*width/16); self.endY = int(8*height/9)

	def size(self):
		return [self.width, self.height]

	def update(self, width, height):
		self.__init__(self.board,width,height)

	def updateBoard(self, newBoard):
		self.__init__(newBoard,self.width,self.height)

def drawCurrentGame(board:Board, screen:Screen, surface):
	gridSize = board.boardDims()
	tileSize = screen.scaling
	tileBorder = screen.scaling/16
 
	for i in range(gridSize[0]):
		for j in range(gridSize[1]):
			xPos = j*screen.scaling + screen.originX
			yPos = i*screen.scaling + screen.originY

			if board.tiles[i][j].state() == ALIVE:
				pygame.draw.rect(surface,BORDER_COLOR,(xPos,yPos,screen.scaling,screen.scaling))
				pygame.draw.rect(surface,ALIVE_COLOR,(xPos+tileBorder,yPos+tileBorder,tileSize-tileBorder,tileSize-tileBorder))
			else:
				pygame.draw.rect(surface,BORDER_COLOR,(xPos,yPos,tileSize,tileSize))
				pygame.draw.rect(surface,DEAD_COLOR,(xPos+tileBorder,yPos+tileBorder,tileSize-tileBorder,tileSize-tileBorder))

def runGame(board:Board, screen:Screen):
	pygame.init()
	gameRunning = True; updateCounter = FPS; microTime = 0
 
	pySurface = pygame.display.set_mode(screen.size(),pygame.RESIZABLE)
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
			elif event.type == pygame.VIDEORESIZE:
				screen.update(event.w,event.h)

		pySurface.fill(BACKGROUND_COLOR)
		drawCurrentGame(board, screen, pySurface)
		pygame.display.update()
    
	pygame.quit()

# Tabuleiro de Exemplo:
myModel = model.GameOfLifeModel(width=25,height=20)
myBoard = Board(myModel)
myScreen = Screen(myBoard,1280,720)
runGame(myBoard,myScreen)