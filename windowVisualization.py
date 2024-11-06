# Dependências 
import pygame
import model as conwayModel

# Constantes Globais
FPS = 60
DEAD, ALIVE = False, True #Estados de uma célula: vivo ou morto
BACKGROUND_COLOR = (32,32,32) #Cor de fundo da simulação
BORDER_COLOR = (0,0,0) #Cor da borda entre células
ALIVE_COLOR = (128,255,128) #Cor de uma célula viva
SELECTED_COLOR = (240,240,70) #Cor de uma célula selecionada*
DEAD_COLOR = (255,64,64) #Cor de uma célula morta

# Variáveis Globais
boardPaused = False
model = None #Instância do modelo mesa
board = None #Instância de Board
screen = None #Instância de Screen

# * Células selecionadas são células que tem algum estado entre vivo ou morto, mas na simulação aparecem de outra cor pois o usuário está prestes a inserir alguma figura especial que cobre essa célula

# Constantes de ação dos botões: Uma para cada figura
SUMMON_SQUARE = 1
SUMMON_BLINKER = 2
SUMMON_GLIDER = 3 
SUMMON_LWSS = 4
SUMMON_BEACON = 5
'''<FIGURAS>'''
SUMMON_FIGURA6 = 6
SUMMON_FIGURA7 = 7 
SUMMON_FIGURA8 = 8 
SUMMON_FIGURA9 = 9
SUMMON_FIGURA10 = 10
SUMMON_FIGURA11 = 11
SUMMON_FIGURA12 = 12 

#Constantes de ação dos botões: gerais
REVIVE_CELL = 13
KILL_CELL = 14
PAUSE_TIME = 15

#Tipos de colocação de figura
PREVIEW_FIGURE = False
ACTIVATE_FIGURE = True

# Tipos de botões
CONFIG_BUTTONS = range(13,16)
FIGURE_BUTTONS = range(1,13)
LIFE_BUTTONS = range(13,15)
CLICKABLE_BUTTONS = range(1,15)
PAUSE_BUTTON = 15

# Tipos de cursor
CURSOR_FREE = 0
CURSOR_AIM = 1
CURSOR_SELECTED = 2

# Imagens: Uma para cada botão
IMG_SQUARE = pygame.image.load("images/square.png")
IMG_BLINKER = pygame.image.load("images/blinker.png") 
IMG_GLIDER = pygame.image.load("images/glider.png") 
IMG_LWSS = pygame.image.load("images/lwss.png") 
IMG_BEACON = pygame.image.load("images/beacon.png")
'''<FIGURAS>'''
IMG_FIGURA6 = pygame.image.load("images/square.png")
IMG_FIGURA7 = pygame.image.load("images/square.png")
IMG_FIGURA8 = pygame.image.load("images/square.png") 
IMG_FIGURA9 = pygame.image.load("images/square.png")
IMG_FIGURA10 = pygame.image.load("images/square.png")
IMG_FIGURA11 = pygame.image.load("images/square.png")
IMG_FIGURA12 = pygame.image.load("images/square.png")

IMG_ALIVECELL = pygame.image.load("images/aliveCell.png")
IMG_DEADCELL = pygame.image.load("images/deadCell.png")
IMG_PAUSE = pygame.image.load("images/pauseTime.png")
IMG_BORDER = pygame.image.load("images/border.png")

# Classes
'''
Classe Tile -> A menor unidade do jogo da vida de conway
	_state: representa se a célula está viva ou morta
	selected: se o usuário está selecionando a célula no momento ou não
 
	state(): obtém o estado da célula (vivo/morto)
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

'''
Classe Board -> Possui um conjunto de tiles e uma instância de model, representa o tabuleiro do jogo
	rows: quantidade de linhas do tabuleiro
	cols: quantidade de colunas do tabuleiro
	tiles: matriz de tiles, representa as unidades gráficas correspondentes ao jogo da vida.
 
	boardDims(): retorna rows e cols, as dimensões do tabuleiro
	update(): atualiza as casas do tabuleiro, o parâmetro step indica se deve apenas tornar o tabuleiro gráfico atualizado em relação ao do modelo ou primeiro atualizar o modelo e depois atualizar o tabuleiro gráfico
'''

class Board:
	def __init__(self):
		global model
		self.rows, self.cols = model.dims()
		self.tiles = [[0]*self.cols for _ in range(self.rows)] #Inicia uma matriz
		for i in range(self.rows):
			for j in range(self.cols):
				self.tiles[i][j] = Tile() #Popula a matriz com tiles
  
	def boardDims(self):
		return [self.rows, self.cols]

	def update(self, step = True):
		global boardPaused, model
		if step and not boardPaused: #Atualizações de estado no modelo exigem o jogo despausado
			model.step()
		for i in range(self.rows):
			for j in range(self.cols): #O modelo considera em cell_layer.data[coluna][linha], mas na visualização, consideramos [linha][coluna], por isso é frequente o uso de [i][j] vs [j][i]
				if self.tiles[i][j].state() != model.cell_layer.data[j][i]:
					self.tiles[i][j].change()

'''
Classe Button -> Informações necessárias para representação de um botão na interface gráfica

'''

class Button:
	def __init__(self, act, slot, img):
		self.action = act
		self.slot = slot
		self.image = img
		self.selected = False
		self.updatePos()

	def updatePos(self):
		if self.action in FIGURE_BUTTONS:
			self.size = int(screen.actualHeight/7)
			slotRow = (self.slot-1)//2
			slotCol = (self.slot-1)%2
			self.x = screen.endX + int(0.4 * self.size) + slotCol * int(self.size * 1.2)
			self.y = screen.originY + slotRow * int(self.size * (1 + 1/6))
		elif self.action in CONFIG_BUTTONS:
			self.size = int(screen.actualHeight/12)
			slotCol = self.slot-13
			self.x = screen.originX + slotCol * int(self.size * 1.2)
			self.y = screen.originY - int(self.size * (1.2))

'''
Classe Screen: A classe que gerencia o display do tabuleiro e de todas as outras informações necessárias.
	board: instância da classe Board que representa o tabuleiro
	buttons: conjunto de instâncias da classe Button, representando os botões da interface
'''

class Screen:
	def __init__(self, width, height):
		self.buttons = []
		self.update(width,height)

	def size(self):
		return [self.width, self.height]

	def update(self, width, height):
		global board
		self.width = width
		self.height = height
		self.scaling = int(min((width * (12/16))/board.cols , (height * (7/9)/board.rows)))

		self.expectedWidth = width*(12/16)
		self.expectedHeight = height*(7/9)
		self.expectedOriginX = int(width/16)
		self.expectedOriginY = int(height/9)
  
		self.actualWidth = self.scaling*board.cols
		self.actualHeight = self.scaling*board.rows
		self.originX = int(width/16 + (self.expectedWidth-self.actualWidth)/2)
		self.originY = int(height/9 + (self.expectedHeight-self.actualHeight)/2)
		self.endX = self.originX + self.actualWidth
		self.endY = self.originY + self.actualHeight

		for bt in self.buttons:
			bt.updatePos(self)

	def updateBoard(self, newBoard):
		global board
		board = newBoard
		self.update(self.width,self.height)
  
	def addButton(self, newButton):
		self.buttons.append(newButton)

# Funções
def drawCurrentGame(surface):
	global board, screen

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
		if bt.selected:
			surface.blit(pygame.transform.scale(IMG_BORDER, (bt.size, bt.size)), (bt.x, bt.y))

def launchEventOnce(type):
	global boardPaused, screen
	if type == PAUSE_TIME:
		boardPaused = not boardPaused
		screen.buttons[PAUSE_TIME-1].selected = boardPaused

def paintTile(i,j,type):
	global board, model
	i %= board.rows; j %= board.cols
	if type == REVIVE_CELL:
		board.tiles[i][j].live()
		model.cell_layer.data[j][i] = True
	elif type == KILL_CELL:
		board.tiles[i][j].die()
		model.cell_layer.data[j][i] = False

def setTileStates(i,j,type,setmode):
	global model, board
	tilist = []
	if type in LIFE_BUTTONS:
		tilist += [[i,j]]
	elif type == SUMMON_SQUARE:
		tilist += [[i,j],[(i+1)%board.rows,j],[i,(j+1)%board.cols],[(i+1)%board.rows,(j+1)%board.cols]]
	elif type == SUMMON_BLINKER:
		tilist +=[[i,j], [(i+1)%board.rows, j], [(i+2)%board.rows, j]]
	elif type == SUMMON_GLIDER:
		tilist +=[[i,j], [(i+1)%board.rows, (j+1)%board.cols], [(i+1)%board.rows, (j+2)%board.cols], [(i), (j+2)%board.cols], [(i-1)%board.rows, (j+2)%board.cols]]
	elif type == SUMMON_LWSS:
		tilist += [[i,j], [(i+2)%board.rows, j], [(i+2)%board.rows, (j+3)%board.cols], [(i-1)%board.rows, (j+1)%board.cols], [(i-1)%board.rows, (j+2)%board.cols], [(i-1)%board.rows, (j+3)%board.cols], [(i-1)%board.rows, (j+4)%board.cols], [(i), (j+4)%board.cols], [(i+1)%board.rows, (j+4)%board.cols]]
	elif type == SUMMON_BEACON:
		tilist += [[i,j],[(i+1)%board.rows,j],[i,(j+1)%board.cols],[(i+1)%board.rows,(j+1)%board.cols], [(i+2)%board.rows,(j+2)%board.cols],[(i+3)%board.rows,(j+2)%board.cols],[(i+2)%board.rows,(j+3)%board.cols],[(i+3)%board.rows,(j+3)%board.cols]]
	'''<FIGURAS>'''
	#Adicione elif para cada nova figura. tilist é a lista das coordenadas dos pontos afetados, sendo [i,j] o canto	superior esquerdo. Lembre-se de tomar coordenadas diferentes de [i,j] com o módulo, igual usado acima
 
	if setmode == False:
		for tile in tilist:
			board.tiles[tile[0]][tile[1]].selected = True
	else:
		for tile in tilist:
			board.tiles[tile[0]][tile[1]].selected = False
			board.tiles[tile[0]][tile[1]].live()
			model.cell_layer.data[tile[1]][tile[0]] = True

def runGame():
	global screen
	pygame.init()
	gameRunning = True; updateCounter = 1; microTime = updateCounter
 
	#Variáveis do cursor
	grabbed = False; grabType = 999; cursorPaintMode = 0
 
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
		cursorType = CURSOR_SELECTED if grabbed else CURSOR_FREE

		if cursorType == 0:
			for bt in screen.buttons:
				if bt.x <= mousePos[0] <= bt.x + bt.size and bt.y <= mousePos[1] <= bt.y + bt.size:
					cursorType = CURSOR_AIM
					break

		if cursorType == CURSOR_FREE:
			pygame.mouse.set_cursor(*pygame.cursors.arrow)
		elif cursorType == CURSOR_AIM:
			pygame.mouse.set_cursor(*pygame.cursors.broken_x)
		else:
			pygame.mouse.set_cursor(*pygame.cursors.tri_left)

		tileRow = int((mousePos[1] - screen.originY)/screen.scaling + 1)-1
		tileCol = int((mousePos[0] - screen.originX + 1)/screen.scaling + 1)-1 #Adição e subtração do -1 para evitar int(-0.9) = int(0.9), pela natureza da aproximação do python
		validTile = (tileRow < board.rows and tileCol < board.cols and tileRow >= 0 and tileCol >= 0)

		if validTile and grabbed:
			setTileStates(tileRow,tileCol,grabType,PREVIEW_FIGURE)

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
    
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
				for bt in screen.buttons:
					if bt.x <= mousePos[0] <= bt.x + bt.size and bt.y <= mousePos[1] <= bt.y + bt.size:
						if bt.action < PAUSE_TIME:
							if grabbed and grabType == bt.action:
								grabbed = False
								screen.buttons[grabType-1].selected = False
							else:
								if grabType in CLICKABLE_BUTTONS:
									screen.buttons[grabType-1].selected = False
								grabbed = True
								grabType = bt.action
								screen.buttons[grabType-1].selected = True
							break
						else:
							launchEventOnce(bt.action)
				if validTile and grabbed:
					if grabType in FIGURE_BUTTONS:
						setTileStates(tileRow,tileCol,grabType,ACTIVATE_FIGURE)
					elif grabType in LIFE_BUTTONS:
						cursorPaintMode = grabType
      
			elif event.type == pygame.MOUSEBUTTONUP:
				if grabType in LIFE_BUTTONS:
					cursorPaintMode = 0
     
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_p:
					launchEventOnce(PAUSE_TIME)
     
				elif event.key == pygame.K_ESCAPE:
					grabbed = False
					if grabType < PAUSE_TIME:
						screen.buttons[grabType-1].selected = False
      
				elif event.key == pygame.K_1:
					if grabbed and grabType == REVIVE_CELL:
						grabbed = False
						screen.buttons[grabType-1].selected = False
					else:
						if grabType < PAUSE_TIME:
							screen.buttons[grabType-1].selected = False
						grabbed = True
						grabType = REVIVE_CELL
						screen.buttons[grabType-1].selected = True
      
				elif event.key == pygame.K_2:
					if grabbed and grabType == KILL_CELL:
						grabbed = False
						screen.buttons[grabType-1].selected = False
					else:
						if grabType < PAUSE_TIME:
							screen.buttons[grabType-1].selected = False
						grabbed = True
						grabType = KILL_CELL
						screen.buttons[grabType-1].selected = True

		#Modo de pintura: ativação de células
		if validTile and cursorPaintMode in LIFE_BUTTONS:
			paintTile(tileRow,tileCol,grabType)

		pySurface.fill(BACKGROUND_COLOR)
		drawCurrentGame(pySurface)
		pygame.display.update()
	pygame.quit()

def generateConwayGame(isRandom = False):
	# Tabuleiro de Exemplo:
	global model, board, screen
	model = conwayModel.GameOfLifeModel(width=60,height=35)
	if isRandom:
		model.randomize(0.50)

	#Botões de Tabuleiro
	board = Board()
	screen = Screen(1280,720)

	#Botões de Figuras
	screen.addButton(Button(SUMMON_SQUARE,1,IMG_SQUARE))
	screen.addButton(Button(SUMMON_BLINKER,2,IMG_BLINKER))
	screen.addButton(Button(SUMMON_GLIDER,3,IMG_GLIDER))
	screen.addButton(Button(SUMMON_LWSS,4,IMG_LWSS))
	screen.addButton(Button(SUMMON_BEACON,5,IMG_BEACON))
	'''<FIGURAS>'''
	#Troque os nomes e códigos de ação de cada figura nova adicionada. Não altere o slot
	screen.addButton(Button(SUMMON_SQUARE,6,IMG_SQUARE))
	screen.addButton(Button(SUMMON_SQUARE,7,IMG_SQUARE))
	screen.addButton(Button(SUMMON_SQUARE,8,IMG_SQUARE))
	screen.addButton(Button(SUMMON_SQUARE,9,IMG_SQUARE))
	screen.addButton(Button(SUMMON_SQUARE,10,IMG_SQUARE))
	screen.addButton(Button(SUMMON_SQUARE,11,IMG_SQUARE))
	screen.addButton(Button(SUMMON_SQUARE,12,IMG_SQUARE))
 
	#Botões de matar e reviver células
	screen.addButton(Button(REVIVE_CELL,13,IMG_ALIVECELL))
	screen.addButton(Button(KILL_CELL,14,IMG_DEADCELL))
	screen.addButton(Button(PAUSE_TIME,15,IMG_PAUSE))

	runGame()

generateConwayGame(isRandom=False)