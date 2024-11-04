# Dependências 
import pygame
import model

# Constantes Globais
TESTE = 358318
FPS = 60
DEAD, ALIVE = False, True #Estados de uma célula: vivo ou morto
BACKGROUND_COLOR = (32,32,32) #Cor de fundo da simulação
BORDER_COLOR = (0,0,0) #Cor da borda entre células
ALIVE_COLOR = (128,255,128) #Cor de uma célula viva
SELECTED_COLOR = (240,240,70) #Cor de uma célula selecionada*
DEAD_COLOR = (255,64,64) #Cor de uma célula morta

# * Células selecionadas são células que tem algum estado entre vivo ou morto, mas na simulação aparecem de outra cor pois o usuário está prestes a inserir alguma figura especial que cobre essa célula

# Constantes de Ação dos Botões: Uma para cada figura
SUMMON_SQUARE = 1
'''<FIGURAS>'''
SUMMON_FIGURA2 = 2
SUMMON_FIGURA3 = 3 
SUMMON_FIGURA4 = 4 
SUMMON_FIGURA5 = 5 
SUMMON_FIGURA6 = 6 
SUMMON_FIGURA7 = 7 
SUMMON_FIGURA8 = 8 
SUMMON_FIGURA9 = 9
SUMMON_FIGURA10 = 10
SUMMON_FIGURA11 = 11
SUMMON_FIGURA12 = 12 

# Imagens: Uma para cada figura
IMG_SQUARE = pygame.image.load("images/square.png")
'''<FIGURAS>'''
IMG_FIGURA2 = pygame.image.load("images/square.png")
IMG_FIGURA3 = pygame.image.load("images/square.png") 
IMG_FIGURA4 = pygame.image.load("images/square.png") 
IMG_FIGURA5 = pygame.image.load("images/square.png") 
IMG_FIGURA6 = pygame.image.load("images/square.png") 
IMG_FIGURA7 = pygame.image.load("images/square.png")
IMG_FIGURA8 = pygame.image.load("images/square.png") 
IMG_FIGURA9 = pygame.image.load("images/square.png")
IMG_FIGURA10 = pygame.image.load("images/square.png")
IMG_FIGURA11 = pygame.image.load("images/square.png")
IMG_FIGURA12 = pygame.image.load("images/square.png")

# Classes
'''
Classe Tile -> A menor unidade do jogo da vida de conway
	state: representa se a célula está viva ou morta
	selected: se o usuário está selecionando a célula no momento ou não
 
	state(): obtém o estado da célula
	change(): muda o estado da célula (na interface gráfica)
	live(): revive a célula (na interface gráfica)
	die(): mata a célula (na interface gráfica)
'''

class Tile:
	def __init__(self):
		self._state = DEAD
		self.selected = False

	def __repr__(self):
		return f"{self._state}"

	def state(self):
		return self._state

	def change(self):
		self._state = 1 - self._state

	def live(self):
		self._state = ALIVE

	def die(self):
		self._state = DEAD

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

	def update(self, step = True):
		if step:
			self.game.step()
		for i in range(self.rows):
			for j in range(self.cols): #O modelo considera em cell_layer.data[coluna][linha], mas na visualização, consideramos [linha][coluna], por isso [i][j] vs [j][i]
				if self.tiles[i][j].state() != self.game.cell_layer.data[j][i]:
					self.tiles[i][j].change()
	 
class Screen:
	def __init__(self, board:Board, width, height):
		self.board = board
		self.buttons = []
		self.update(width,height)

	def size(self):
		return [self.width, self.height]

	def update(self, width, height):
		self.width = width
		self.height = height
		self.scaling = int(min((width * (12/16))/self.board.cols , (height * (7/9)/self.board.rows)))

		self.expectedWidth = width*(12/16)
		self.expectedHeight = height*(7/9)
		self.expectedOriginX = int(width/16)
		self.expectedOriginY = int(height/9)
  
		self.actualWidth = self.scaling*self.board.cols
		self.actualHeight = self.scaling*self.board.rows
		self.originX = int(width/16 + (self.expectedWidth-self.actualWidth)/2)
		self.originY = int(height/9 + (self.expectedHeight-self.actualHeight)/2)
		self.endX = self.originX + self.actualWidth
		self.endY = self.originY + self.actualHeight

		for bt in self.buttons:
			bt.updatePos(self)

	def updateBoard(self, newBoard):
		self.board = newBoard
		self.update(self.width,self.height)
  
	def addButton(self, newButton):
		self.buttons.append(newButton)

class Button:
	def __init__(self, screen:Screen, act, slot, img):
		self.action = act
		self.slot = slot
		self.image = img
		self.updatePos(screen)

	def updatePos(self, screen:Screen):
		self.size = int(screen.actualHeight/7)
		slotRow = (self.slot-1) // 2
		slotCol = (self.slot-1)%2
		self.x = screen.endX + int(0.4 * self.size) + slotCol * int(self.size * 1.2)
		self.y = screen.originY + slotRow * int(self.size * (1 + 1/6))

# Funções
def drawCurrentGame(board:Board, screen:Screen, surface):
	gridSize = board.boardDims()
	tileSize = screen.scaling
	tileBorder = screen.scaling/16
	if tileSize < 2:
		tileBorder = 0

	for i in range(gridSize[0]):
		for j in range(gridSize[1]):
			xPos = j*screen.scaling + screen.originX
			yPos = i*screen.scaling + screen.originY
			
			if board.tiles[i][j].selected == True:
				board.tiles[i][j].selected = False
				pygame.draw.rect(surface,BORDER_COLOR,(xPos,yPos,screen.scaling,screen.scaling))
				pygame.draw.rect(surface,SELECTED_COLOR,(xPos+tileBorder,yPos+tileBorder,tileSize-tileBorder,tileSize-tileBorder))
			elif board.tiles[i][j].state() == ALIVE:
				pygame.draw.rect(surface,BORDER_COLOR,(xPos,yPos,screen.scaling,screen.scaling))
				pygame.draw.rect(surface,ALIVE_COLOR,(xPos+tileBorder,yPos+tileBorder,tileSize-tileBorder,tileSize-tileBorder))
			else:
				pygame.draw.rect(surface,BORDER_COLOR,(xPos,yPos,tileSize,tileSize))
				pygame.draw.rect(surface,DEAD_COLOR,(xPos+tileBorder,yPos+tileBorder,tileSize-tileBorder,tileSize-tileBorder))

	for bt in screen.buttons:
		surface.blit(pygame.transform.scale(bt.image, (bt.size, bt.size)), (bt.x, bt.y))
  
def setTileStates(board:Board,i,j,type,setmode):
	tilist = []
	if type == SUMMON_SQUARE:
		tilist += [[i,j],[(i+1)%board.rows,j],[i,(j+1)%board.cols],[(i+1)%board.rows,(j+1)%board.cols]]
	'''<FIGURAS>'''
	#Adicione elif para cada nova figura. tilist é a lista das coordenadas dos pontos afetados, sendo [i,j] o canto superior esquerdo. Lembre-se de tomar coordenadas diferentes de [i,j] com o módulo, igual usado acima
	
	if setmode == False:
		for tile in tilist:
			board.tiles[tile[0]][tile[1]].selected = True
	else:
		for tile in tilist:
			board.tiles[tile[0]][tile[1]].selected = False
			board.tiles[tile[0]][tile[1]].live()
			board.game.cell_layer.data[tile[1]][tile[0]] = True

def runGame(board:Board, screen:Screen):
	pygame.init()
	gameRunning = True; updateCounter = 1; microTime = updateCounter
	grabbed = False; grabType = 0
 
	pySurface = pygame.display.set_mode(screen.size(),pygame.RESIZABLE)
	timer = pygame.time.Clock()
	
	board.update(False)
	while(gameRunning):
		timer.tick(FPS)
		microTime -= 1
		if microTime <= 0:
			microTime = updateCounter
			board.update()

		mousePos = pygame.mouse.get_pos()
		cursorType = 2 if grabbed else 0

		if cursorType == 0:
			for bt in screen.buttons:
				if bt.x <= mousePos[0] <= bt.x + bt.size and bt.y <= mousePos[1] <= bt.y + bt.size:
					cursorType = 1
					break

		if cursorType == 0:
			pygame.mouse.set_cursor(*pygame.cursors.arrow)
		elif cursorType == 1:
			pygame.mouse.set_cursor(*pygame.cursors.broken_x)
		else:
			pygame.mouse.set_cursor(*pygame.cursors.tri_left)

		tileRow = int((mousePos[1] - screen.originY)/screen.scaling)
		tileCol = int((mousePos[0] - screen.originX)/screen.scaling)
		validTile = (tileRow < board.rows and tileCol < board.cols and tileRow >= 0 and tileCol >= 0)

		if validTile and grabbed:
			setTileStates(board,tileRow,tileCol,grabType,False)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				gameRunning = False
			elif event.type == pygame.VIDEORESIZE:
				screen.update(event.w,event.h)
			elif event.type == pygame.WINDOWMAXIMIZED:
				w, h = pygame.display.get_window_size()
				screen.update(w,h)
			elif event.type == pygame.WINDOWMINIMIZED:
				w, h = pygame.display.get_window_size()
				screen.update(w,h)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				for bt in screen.buttons:
					if bt.x <= mousePos[0] <= bt.x + bt.size and bt.y <= mousePos[1] <= bt.y + bt.size:
						if grabbed:
							grabbed = False
							break
						else:
							grabbed = True
							grabType = bt.action
							break
				if validTile and grabbed:
					setTileStates(board,tileRow,tileCol,grabType,True)
					grabbed = False

		pySurface.fill(BACKGROUND_COLOR)
		drawCurrentGame(board, screen, pySurface)
		pygame.display.update()
	pygame.quit()

def generateConwayGame(isRandom = True):
	# Tabuleiro de Exemplo:
	myModel = model.GameOfLifeModel(width=120,height=70)
	if isRandom:
		myModel.randomize(0.50)

	myBoard = Board(myModel)
	myScreen = Screen(myBoard,1280,720)

	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,1,IMG_SQUARE))
	'''<FIGURAS>'''
	#Troque os nomes e códigos de ação de cada figura nova adicionada. Não altere o slot
	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,2,IMG_SQUARE))
	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,3,IMG_SQUARE))
	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,4,IMG_SQUARE))
	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,5,IMG_SQUARE))
	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,6,IMG_SQUARE))
	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,7,IMG_SQUARE))
	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,8,IMG_SQUARE))
	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,9,IMG_SQUARE))
	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,10,IMG_SQUARE))
	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,11,IMG_SQUARE))
	myScreen.addButton(Button(myScreen,SUMMON_SQUARE,12,IMG_SQUARE))

	runGame(myBoard,myScreen)

generateConwayGame()