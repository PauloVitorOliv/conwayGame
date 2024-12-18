# Dependências de bibliotecas externas
import random
import pygame
import tkinter as tk
from PIL import Image, ImageTk
import numpy as NP

# Dependências no projeto
import model as conwayModel

# Constantes Globais
FPS = 60
DEAD, ALIVE = False, True #Estados de uma célula: vivo, morto e permanentemente morto
NONE, INFECTED, PERM_DEAD, SICK = 0, 1, 2, 3
BACKGROUND_COLOR = (32,32,32) #Cor de fundo da simulação
BORDER_COLOR = (0,0,0) #Cor da borda entre células
ALIVE_COLOR = (128,255,128) #Cor de uma célula viva
SELECTED_COLOR = (240,240,70) #Cor de uma célula selecionada*
DEAD_COLOR = (255,64,64) #Cor de uma célula morta
DEAD_PERMANENTE_COLOR = (56,11,11) #Cor de uma célula permanentemente morta
INFECTED_COLOR = (160,50,160) #Cor de uma célula infectada

# Variáveis Globais
boardPaused = False
model = None #Instância do modelo mesa
board = None #Instância de Board
screen = None #Instância de Screen
used_font = None #Fonte a ser usada
rotation_count = 0 #Quantas rotações a figura está da sua posição original
rounds = 0 #Quantos rounds faltam (apenas cassino)
maxRounds = 0 #Máximo de rounds (apenas cassino)
guess = 0 #Quantos % das células mortas serão infectadas (apenas cassino)
currentBet = 0 #Quanto você apostou na última jogada (apenas cassino)
prevPercentage = -1 #Usando enquanto calcula porcentagem (apenas cassino)

# * Células selecionadas são células que tem algum estado entre vivo ou morto, mas na simulação aparecem de outra cor pois o usuário está prestes a inserir alguma figura especial que cobre essa célula

# Constantes de ação dos botões: Uma para cada figura
SUMMON_SQUARE = 1
SUMMON_BLINKER = 2
SUMMON_GLIDER = 3 
SUMMON_LWSS = 4
SUMMON_BEACON = 5
SUMMON_EATER = 6
SUMMON_TOAD = 7 
SUMMON_BEEHIVE = 8 
SUMMON_TUB = 9
SUMMON_LEGS = 10
SUMMON_XPENTOMINO = 11
SUMMON_LONGHOOK = 12

#Constantes de ação dos botões: gerais
REVIVE_CELL = 13
KILL_CELL = 14
KILL_EVER = 15
SICK_CELL = 16
PAUSE_TIME = 17
GENERATE_BOARD = 18
CLEAR_BOARD = 19
ROTATION = 20

CHANGE_REVIVAL = 22
CHANGE_MIN_SURVIVAL = 23
CHANGE_MAX_SURVIVAL = 24

#Constantes de ação: cassino
CASSINO_PLAY = 90
CASSINO_RAISE = 91
CASSINO_LOWER = 92
CASSINO_GUESS = 95

CASSINO_MONEY = 1
CASSINO_BET = 0

#Tipos de colocação de figura
PREVIEW_FIGURE = False
ACTIVATE_FIGURE = True

# Tipos de botões
CONFIG_BUTTONS = range(13,22)
FIGURE_BUTTONS = range(1,13)
LIFE_BUTTONS = range(13,17)
CLICKABLE_BUTTONS = range(1,17)
NUMBER_BOXES = range(22,25)
GENERATE_BUTTON = range(18,21)
CASSINO_BUTTONS = range(90, 93)

# Tipos de cursor
CURSOR_FREE = 0
CURSOR_AIM = 1
CURSOR_SELECTED = 2

# Imagens: Uma para cada botão
IMG_SQUARE = pygame.image.load("images/gligun.png")
IMG_BLINKER = pygame.image.load("images/blinker.png") 
IMG_GLIDER = pygame.image.load("images/glider.png") 
IMG_LWSS = pygame.image.load("images/lwss.png") 
IMG_BEACON = pygame.image.load("images/beacon.png")
IMG_EATER = pygame.image.load("images/eater.png")
IMG_TOAD = pygame.image.load("images/toad.png")
IMG_BEEHIVE = pygame.image.load("images/beehive.png") 
IMG_TUB = pygame.image.load("images/tub.png")
IMG_LEGS = pygame.image.load("images/legs.png")
IMG_XPENTOMINO = pygame.image.load("images/xpentomino.png")
IMG_LONGHOOK = pygame.image.load("images/longhook.png")
IMG_DEADPERMANENTE = pygame.image.load("images/permadead.png")
IMG_ALIVECELL = pygame.image.load("images/aliveCell.png")
IMG_DEADCELL = pygame.image.load("images/deadCell.png")
IMG_PAUSE = pygame.image.load("images/pauseTime.png")
IMG_BORDER = pygame.image.load("images/border.png")
IMG_GENERATEBOARD = pygame.image.load("images/generateBoard.png")
IMG_CLEARBOARD = pygame.image.load("images/clearBoard.png")
IMG_SPEED = pygame.image.load("images/icon_speed.png")
IMG_ROTATION = pygame.image.load("images/rotation.png")
IMG_LOGO = pygame.image.load("images/logo.png")
IMG_PURPLE = pygame.image.load("images/sickcell.png")
IMG_RAISE = pygame.image.load("images/raise.png")
IMG_LOWER = pygame.image.load("images/lower.png")
IMG_BET = pygame.image.load("images/bet.png")

# Classes
'''
Classe Tile -> A menor unidade do jogo da vida de conway
	state: representa se a célula está viva ou morta
	selected: True se o usuário está com o mouse por cima da célula no momento

	change(): muda o estado da célula (na interface gráfica)
	live(): revive a célula (na interface gráfica)
	die(): mata a célula (na interface gráfica)
'''

class Tile:
	def __init__(self):
		self.state = DEAD
		self.selected = False
		self.condition = NONE

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
		self.tiles = [[0]*self.cols for _ in range(self.rows)] #Inicia uma matriz vazia
		for i in range(self.rows):
			for j in range(self.cols):
				self.tiles[i][j] = Tile() #Popula a matriz com tiles novos
  
	def boardDims(self):
		return [self.rows, self.cols]

	def update(self, step = True):
		global boardPaused, model, rounds, guess, currentBet, prevPercentage, maxRounds
		if step and not boardPaused: #Atualizações de estado no modelo exigem o jogo despausado
			model.step()
			if model.mode == "cassino" and rounds > 0:
				maxRounds -= 1
				newP = model.calcPercentage()*100
				if newP == prevPercentage:
					rounds -= 1
				prevPercentage = newP
				if rounds == 0 or maxRounds == 0:
					screen.cassinoTexts[CASSINO_MONEY].text = str(int(screen.cassinoTexts[CASSINO_MONEY].text) + int(currentBet*10*pow(0.7,abs(newP - guess))))
					prevPercentage = -1
					rounds = 0; maxRounds = 0
					
		for i in range(self.rows):
			for j in range(self.cols):
				if self.tiles[i][j].state != model.cell_layer.data[i][j]:
					self.tiles[i][j].state = 1 - self.tiles[i][j].state
				if self.tiles[i][j].condition != model.dead_layer.data[i][j]:
					self.tiles[i][j].condition = model.dead_layer.data[i][j]

'''
Classe Button -> Informações necessárias para representação de um botão na interface gráfica
	action: ID de ação que o botão faz, pode ser uma figura ou configuração
	slot: que posição o botão ocupará na tela, cada slot tem um significado:
		slots 1 à 12 -> botões de figura, alinhados alternadamente nas linhas 1 à 6 na parte à direita do tabuleiro
		slots 13+ -> botões de configuração, alinhados em fileira acima do tabuleiro
	image: imagem do botão
	selected: propriedade que mostra se o botão está no momento clicado ou não
	updatePos(): atualiza as dimensões e posições do botão para o estado atual da tela

'''

class Button:
	def __init__(self, act, slot, img):
		self.action = act
		self.slot = slot
		self.image = img
		self.selected = False
		self.updatePos()

	def updatePos(self):
		global screen
		if self.action in FIGURE_BUTTONS:
			self.size = int(screen.actualHeight/7)
			slotRow = (self.slot-1)//2
			slotCol = (self.slot-1)%2
			self.x = screen.endX + int(0.4 * self.size) + slotCol * int(self.size * 1.2)
			self.y = screen.originY + slotRow * int(self.size * (1 + 1/6))
		elif self.action in CONFIG_BUTTONS or self.action in CASSINO_BUTTONS:
			self.size = int(screen.actualHeight/12)
			slotCol = self.slot-13
			self.x = screen.originX + slotCol * int(self.size * 1.2)
			self.y = screen.originY - int(self.size * (1.2))


class Number_Box:
	def __init__(self, act, slot, start = 1, widthProp = 1):
		self.action = act
		self.altSlot = slot
		self.selected = False
		self.value = start
		self.rect = pygame.Rect(0,0,1,1)
		self.widthProp = widthProp
		self.updatePos()

	def updatePos(self):
		global screen
		self.size = int(screen.actualHeight/25)
		slotRow = (self.altSlot)%2
		slotCol = (self.altSlot-30)//2
		self.x = screen.originX + slotCol * int(self.size * 1.2) + int(screen.actualHeight/20)*18
		self.y = screen.originY - int(int(screen.actualHeight/12) * (1.2)) + slotRow * (int(screen.actualHeight/12) - self.size)
		self.epsx = int(self.size*0.3) #Epsilon de posicionamento do texto numérico
		self.epsy = int(self.size*0.1)
		self.rect = pygame.Rect(self.x, self.y, self.size*self.widthProp, self.size)

	def draw(self, surface):
		global used_font
		pygame.draw.rect(surface, (50,50,50) , self.rect)
		if self.selected:
			surface.blit(pygame.transform.scale(IMG_BORDER, (self.size, self.size)), (self.x, self.y))
		surface.blit(used_font.render(str(self.value),True,SELECTED_COLOR), (self.x + self.epsx, self.y + self.epsy))

class Floating_Text:
	def __init__(self, words, slot):
		self.text = words
		self.altSlot = slot
		self.x = 0
		self.y = 0

	def updatePos(self): #Mesmo sistema de posicionamento de Number_Box
		global screen
		self.size = int(screen.actualHeight/25)
		slotRow = (self.altSlot)%2
		slotCol = (self.altSlot-30)//2
		self.x = screen.originX + slotCol * int(self.size * 1.2) + int(screen.actualHeight/10)*5 #Espaçamento Adicional Fixo
		self.y = screen.originY - int(int(screen.actualHeight/12) * (1.2)) + slotRow * (int(screen.actualHeight/12) - self.size)
		self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
		self.epsx = int(self.size*0.3) #Epsilon de posicionamento do texto
		self.epsy = int(self.size*0.1)

	def draw(self, surface):
		surface.blit(used_font.render(self.text,True,SELECTED_COLOR), (self.x + self.epsx, self.y + self.epsy))

class Slider_Button:
	def __init__(self, progr=0.5):
		self.slider_value = 60
		self.dragging = False
		self.progress = progr
		self.slider_rect = pygame.Rect(300, 70, 300, 10)
		self.slider_thumb_rect = pygame.Rect(0, 75, 10, 20)
		self.updatePos()
		self.slider_thumb_rect.x = self.x_st

	def updatePos(self):
		global screen

		self.height_sr = int(screen.actualHeight/49)
		self.width_sr = self.height_sr*15
		self.x_sr = screen.originX
		self.y_sr = screen.endY + int(self.height_sr*(3))

		self.height_st = 3*self.height_sr
		self.width_st = self.height_sr
		self.x_st = screen.originX + self.progress*(self.width_sr - self.width_st)
		self.y_st = screen.endY + int(self.height_sr*(3)) - self.height_sr

		#atualização das variáveis
		self.slider_rect.height = self.height_sr
		self.slider_rect.width = self.width_sr
		self.slider_rect.x = self.x_sr
		self.slider_rect.y = self.y_sr
		self.slider_thumb_rect.height = self.height_st
		self.slider_thumb_rect.width = self.width_st
		self.slider_thumb_rect.x = self.x_st 
		self.slider_thumb_rect.y = self.y_st

	def updateThumb(self, MousePos = (0,0)):
		global screen

		if self.dragging:
			new_x = max(min(MousePos[0], self.slider_rect.right - self.slider_thumb_rect.width), self.slider_rect.left)
			self.progress = (new_x - self.x_sr)/(self.width_sr - self.width_st)
			self.x_st = screen.originX + self.progress*(self.width_sr - self.width_st)
			self.slider_thumb_rect.x = self.x_st

	def draw(self, surface):
		pygame.draw.rect(surface, (50,50,50) , self.slider_rect)
		pygame.draw.rect(surface, (0,0,255) , self.slider_thumb_rect)

'''
Classe Screen -> A classe que gerencia o display do tabuleiro e de todas as outras informações necessárias
	buttons: conjunto de instâncias da classe Button, representando os botões da interface
 
	Variáveis usadas para calcular posicionamento:
		scaling: multiplicador usado de tamanho para os itens, varia de acordo com o tamanho da tela
		originX, originY, endX, endY: Posições-chave para posicionamento de itens na tela
		width, height: dimensões da tela
		expectedWidth, expectedHeight: dimensões esperadas do tabuleiro na tela se fosse ele estivesse em aspect ratio ideal, usado para calcular posições
		actualWidth, actualHeight: dimensões atuais do tabuleiro

	update(): atualiza posições de tudo presente na tela dadas as novas largura e altura da tela
	addButton(): adiciona um novo botão à lista buttons
'''

class Screen:
	def __init__(self, width, height):
		self.buttons = []
		self.sliders = []
		self.numberBoxes = []
		self.floatingTexts = []
		self.cassinoBoxes = []
		self.cassinoTexts = []
		self.cassinoButtons = []
		self.update(width,height)

	def size(self):
		return [self.width, self.height]

	def update(self, width, height):
		global board, used_font
		self.width = width
		self.height = height
  
		#Atualização das variáveis de posicionamento: manipuladas com constantes pensadas para a tela ficar visualmente boa apesar do aspect ratio alterar de acordo com o tamanho da janela e do tabuleiro
		self.scaling = int(min((width * (12/16))/board.cols , (height * (7/9)/board.rows)))
		self.expectedWidth = width*(12/16)
		self.expectedHeight = height*(7/9)

		self.actualWidth = self.scaling*board.cols
		self.actualHeight = self.scaling*board.rows
		used_font = pygame.font.Font(None, int(self.actualHeight/20))
  
		self.originX = int(width/16 + (self.expectedWidth-self.actualWidth)/2)
		self.originY = int(height/9 + (self.expectedHeight-self.actualHeight)/2)
  
		self.endX = self.originX + self.actualWidth
		self.endY = self.originY + self.actualHeight

		for bt in self.buttons:
			bt.updatePos()

		for sl in self.sliders:
			sl.updatePos()

		for nb in self.numberBoxes:
			nb.updatePos()
   
		for ft in self.floatingTexts:
			ft.updatePos()
   
		if model.mode == "cassino":
			for bt in self.cassinoButtons:
				bt.updatePos()

			for ft in self.cassinoTexts:
				ft.updatePos()
    
			for cb in self.cassinoBoxes:
				cb.updatePos()
  
	def addButton(self, newButton):
		self.buttons.append(newButton)

	def addSlider(self, newSlider):
		self.sliders.append(newSlider)

	def addNumberBox(self, newNumberBox):
		self.numberBoxes.append(newNumberBox)
  
	def addFloatingText(self, newFloatingText):
		self.floatingTexts.append(newFloatingText)
  
	def addCassinoButton(self, newButton):
		self.cassinoButtons.append(newButton)
  
	def addCassinoBox(self, newBox):
		self.cassinoBoxes.append(newBox)
  
	def addCassinoText(self, newText):
		self.cassinoTexts.append(newText)

# Funções

def waitToBet(qtSteps):
	while(qtSteps > 0):
		board.update(True)
		qtSteps -= 1

def cassinoBet():
	global model, board, screen, currentBet, guess, rounds, maxRounds
	moneyBet = int(screen.cassinoTexts[CASSINO_BET].text)
	myMoney = int(screen.cassinoTexts[CASSINO_MONEY].text)
	if myMoney < moneyBet:
		return
	myMoney -= moneyBet
	screen.cassinoTexts[CASSINO_BET].text = str(max(min(myMoney,moneyBet),1))
	screen.cassinoTexts[CASSINO_MONEY].text = str(myMoney)
 
	#Agora você apostou $moneyBet reais. Vamos ver o que aconteceu:
	guess = screen.cassinoBoxes[0].value
	currentBet = moneyBet

	lim = NP.random.randint(5,7)
	model.updateRule(2,lim)

	launchEventOnce(GENERATE_BOARD)
	waitToBet(60)
	rounds = 5
	maxRounds = board.boardDims()[0]*3 + 40
 
	li = NP.random.randint(0,board.boardDims()[0])
	co = NP.random.randint(0,board.boardDims()[1])
	paintTile(li,co,SICK_CELL)
	

def drawCurrentGame(surface): #Desenha o estado atual da simulação na tela
	global board, screen, model

	#Define variáveis relevantes: tamanho de um tile e borda dele
	gridSize = board.boardDims()
	tileSize = screen.scaling
	tileBorder = screen.scaling/16
	if tileSize < 2:
		tileBorder = 0 #Se for pequeno demais, sem borda

	for i in range(gridSize[0]):
		for j in range(gridSize[1]):
			#Para cada tile, define a posição, cor e tamanho dele e desenha retângulos correspondentes a ele e sua borda
			xPos = j*screen.scaling + screen.originX
			yPos = i*screen.scaling + screen.originY
   
			if board.tiles[i][j].selected == True:
				board.tiles[i][j].selected = False
				pygame.draw.rect(surface,BORDER_COLOR,(xPos,yPos,screen.scaling,screen.scaling))
				pygame.draw.rect(surface,SELECTED_COLOR,(xPos+tileBorder,yPos+tileBorder,tileSize-tileBorder,tileSize-tileBorder))
			elif board.tiles[i][j].condition == PERM_DEAD:
				# Se a célula está permanentemente morta, desenha ela de preto
				pygame.draw.rect(surface, BORDER_COLOR, (xPos, yPos, screen.scaling, screen.scaling))
				pygame.draw.rect(surface, DEAD_PERMANENTE_COLOR, (xPos + tileBorder, yPos + tileBorder, tileSize - tileBorder, tileSize - tileBorder))  # Preto
			elif board.tiles[i][j].state == ALIVE:
				pygame.draw.rect(surface,BORDER_COLOR,(xPos,yPos,screen.scaling,screen.scaling))
				pygame.draw.rect(surface,ALIVE_COLOR,(xPos+tileBorder,yPos+tileBorder,tileSize-tileBorder,tileSize-tileBorder))
			elif board.tiles[i][j].condition == DEAD:
				pygame.draw.rect(surface,BORDER_COLOR,(xPos,yPos,tileSize,tileSize))
				pygame.draw.rect(surface,DEAD_COLOR,(xPos+tileBorder,yPos+tileBorder,tileSize-tileBorder,tileSize-tileBorder))
			else:
				pygame.draw.rect(surface,BORDER_COLOR,(xPos,yPos,tileSize,tileSize))
				pygame.draw.rect(surface,INFECTED_COLOR,(xPos+tileBorder,yPos+tileBorder,tileSize-tileBorder,tileSize-tileBorder))

	#Coloca na tela as imagens dos botões na posição correspondente
	for bt in screen.buttons:
		if bt.action != PAUSE_TIME and model.mode == "cassino":
			continue
		surface.blit(pygame.transform.scale(bt.image, (bt.size, bt.size)), (bt.x, bt.y))
		if bt.selected:
			surface.blit(pygame.transform.scale(IMG_BORDER, (bt.size, bt.size)), (bt.x, bt.y))

	coordx=screen.originX + screen.sliders[0].width_sr
	coordy=screen.endY + int(2*screen.sliders[0].height_sr)
	surface.blit(pygame.transform.scale(IMG_SPEED, (int(3*screen.sliders[0].height_sr), int(3*screen.sliders[0].height_sr))), (coordx, coordy))

	for sl in screen.sliders:
		sl.draw(surface)

	for nb in screen.numberBoxes:
		nb.draw(surface)
  
	for ft in screen.floatingTexts:
		ft.draw(surface)
  
	if model.mode == "cassino":
		for bt in screen.cassinoButtons:
			surface.blit(pygame.transform.scale(bt.image, (bt.size, bt.size)), (bt.x, bt.y))
     
		for ft in screen.cassinoTexts:
			ft.draw(surface)

		for cb in screen.cassinoBoxes:
			cb.draw(surface)

#Função para executar um evento que ocorre de forma imediata, por exemplo, pausar o jogo
def launchEventOnce(type):
	global boardPaused, screen, board, model
	if type == PAUSE_TIME:
		boardPaused = not boardPaused
		screen.buttons[PAUSE_TIME-1].selected = boardPaused
	elif type == GENERATE_BOARD:
		r, c = board.boardDims()
		newModel = conwayModel.GameOfLifeModel(rows=r,cols=c)
		newModel.randomize(random.betavariate(7,7)) #Distribuição beta probabilística pois tabuleiros muito próximos de 0% ou 100% de células ativas não são muito interessantes
		model.cell_layer = newModel.cell_layer
		model.dead_layer = newModel.dead_layer
		board.update(False)
	elif type == CLEAR_BOARD:
		r, c = board.boardDims()
		newModel = conwayModel.GameOfLifeModel(rows=r,cols=c)
		model.cell_layer = newModel.cell_layer
		model.dead_layer = newModel.dead_layer
		board.update(False)
	elif type == ROTATION:
		global rotation_count
		rotation_count += 1
	elif type == CASSINO_RAISE:
		currMoney = int(screen.cassinoTexts[CASSINO_MONEY].text)
		currBet = int(screen.cassinoTexts[CASSINO_BET].text)
		if(currMoney > currBet):
			currBet = max(min(2*currBet, currMoney),1)
			screen.cassinoTexts[CASSINO_BET].text = str(currBet)
	elif type == CASSINO_LOWER:
		currMoney = int(screen.cassinoTexts[CASSINO_MONEY].text)
		currBet = int(screen.cassinoTexts[CASSINO_BET].text)
		if(currBet > 1):
			currBet = max(currBet//2, 1)
			screen.cassinoTexts[CASSINO_BET].text = str(currBet)
	elif type == CASSINO_PLAY:
		cassinoBet()

#Pinta o quadrado de posição i,j, matando ou revivendo a célula, de acordo com a ocasião necessária
def paintTile(i,j,type):
	global board, model
	i %= board.rows; j %= board.cols

	if type == REVIVE_CELL:
		board.tiles[i][j].state = ALIVE
		model.cell_layer.set_cell((i,j),True)
		model.dead_layer.set_cell((i, j), NONE)
		board.tiles[i][j].condition = NONE
	elif type == KILL_CELL:
		board.tiles[i][j].state = DEAD
		model.cell_layer.set_cell((i,j),False)
		model.dead_layer.set_cell((i, j), NONE)
		board.tiles[i][j].condition = NONE
	elif type == KILL_EVER:
		# Marca a célula como permanentemete morta
		board.tiles[i][j].state = DEAD
		board.tiles[i][j].condition = PERM_DEAD
		model.cell_layer.set_cell((i,j),False)
		model.dead_layer.set_cell((i, j), PERM_DEAD)
	elif type == SICK_CELL:
		board.tiles[i][j].state = DEAD
		board.tiles[i][j].condition = SICK
		model.cell_layer.set_cell((i,j),False)
		model.dead_layer.set_cell((i, j), SICK)

def rotate(lista, rotation):
	translation = [lista[0][0], lista[0][1]]
	for i in lista: # Translação da figura para a origem
		i[0] -= translation[0]
		i[1] -= translation[1]

	for i in lista: # Rotação em torno da origem
		if rotation % 4 == 0:
			break
		if rotation % 4 == 1:
			i[0], i[1] = -i[1], i[0]

		if rotation % 4 == 2:
			i[0], i[1] = -i[0], -i[1]

		if rotation % 4 == 3:
			i[0], i[1] = i[1], -i[0]

	for i in lista: # Desfaz o translação
		i[0] += translation[0]
		i[1] += translation[1]

	return lista

def modulo_board(lista):
	for i in lista:
		i[0], i[1] = i[0] % board.rows, i[1] % board.cols
	return lista

#Pinta uma figura existente na tela, ou prevê sua posição caso ainda não tenha sido ativado o evento
def setTileStates(i,j,type,setmode):
	global model, board
	tilist = [] #Guarda as posições da figura
	if type in LIFE_BUTTONS:
		live_list = [[i,j]]
	elif type == SUMMON_SQUARE:
		live_list = [[i,j], [(i-1) , (j-1)], [i, (j-1)], [(i+1) , (j-1)], [(i-2) , (j-2)], [(i+2) , (j-2)], [i, (j-3)], [(i-3) , (j-4)], [(i+3) , (j-4)], [(i-3) , (j-5)], [(i+3) , (j-5)], [(i-2) , (j-6)], [(i+2) , (j-6)], [(i-1) , (j-7)], [i, (j-7)], [(i+1) , (j-7)], [(i-1) , (j-16)], [i, (j-16)], [(i-1) , (j-17)], [i, (j-17)], [(i-3) , (j+3)], [(i-2) , (j+3)], [(i-1) , (j+3)], [(i-3) , (j+4)], [(i-2) , (j+4)], [(i-1) , (j+4)], [(i-4) , (j+5)], [i, (j+5)], [(i-5) , (j+7)], [(i-4) , (j+7)], [i, (j+7)], [(i+1) , (j+7)], [(i-3) , (j+17)], [(i-2) , (j+17)], [(i-3) , (j+18)], [(i-2) , (j+18)]]
	elif type == SUMMON_BLINKER:
		live_list = [[i,j], [(i+1), j], [(i+2), j]]
	elif type == SUMMON_GLIDER:
		live_list = [[i,j], [(i+1), (j+1)], [(i+1), (j+2)], [(i), (j+2)], [(i-1), (j+2)]]
	elif type == SUMMON_LWSS:
		live_list = [[i,j], [(i+2), j], [(i+2), (j+3)], [(i-1), (j+1)], [(i-1), (j+2)], [(i-1), (j+3)], [(i-1), (j+4)], [(i), (j+4)], [(i+1), (j+4)]]
	elif type == SUMMON_BEACON:
		live_list = [[i,j],[(i+1),j],[i,(j+1)],[(i+1),(j+1)], [(i+2),(j+2)],[(i+3),(j+2)],[(i+2),(j+3)],[(i+3),(j+3)]]
	elif type == SUMMON_EATER:
		live_list = [[i,j],[i,(j+1)],[(i-1),j],[(i-2),(j+1)],[(i-2),(j+2)],[(i-2),(j+3)],[(i-3),(j+3)]]
	elif type == SUMMON_TOAD:
		live_list = [[i,j],[(i+1),j],[(i+2),(j+1)],[(i-1),(j+2)],[i,(j+3)],[(i+1),(j+3)]]
	elif type == SUMMON_BEEHIVE:
		live_list = [[i,j],[(i+1),(j+1)],[(i+1),(j+2)],[(i-1),(j+1)],[(i-1),(j+2)],[i,(j+3)]]
	elif type == SUMMON_TUB:
		live_list = [[i,j],[(i+1),(j+1)],[(i-1),(j+1)],[i,(j+2)]]
	elif type == SUMMON_LEGS:
		live_list = [[i, j], [(i+1) , j], [(i+1) , (j-1)],[(i+1) , (j-2)],[i, (j-3)],[(i-1) , (j-3)],[(i-2) , (j-3)],[(i-2) , (j-2)]]
	elif type == SUMMON_XPENTOMINO:
		live_list = [[i, j], [i, (j+1)], [i, (j+2)],[(i-1) , (j+1)],[(i+1) , (j+1)]]
	elif type == SUMMON_LONGHOOK:
		live_list = [[i, j], [i, (j+1)], [(i+1) , (j+1)],[(i+2) , j],[(i+2) , (j-1)],[(i+2) , (j-2)],[(i+2) , (j-3)],[(i+1) , (j-3)]]
	
	tilist += modulo_board(rotate(live_list, rotation_count))

	'''<FIGURAS>'''
	#Adicione elif para cada nova figura. tilist é a lista das coordenadas dos pontos afetados, sendo [i,j] o canto	superior esquerdo. Lembre-se de tomar coordenadas diferentes de [i,j] com o módulo, igual usado acima
 
	if setmode == False: #Se for apenas previsão de posições
		for tile in tilist:
			board.tiles[tile[0]][tile[1]].selected = True
	else: #Se for para ativar a figura de fato
		for tile in tilist:
			board.tiles[tile[0]][tile[1]].selected = False
			board.tiles[tile[0]][tile[1]].state = ALIVE
			board.tiles[tile[0]][tile[1]].condition = NONE
			model.cell_layer.set_cell((tile[0],tile[1]),True)
			model.dead_layer.set_cell((tile[0], tile[1]), NONE)
   

def runGame():
	global screen, board, used_font, model
	gameRunning = True; updateCounter = 1; microTime = updateCounter
 
	#Variáveis do cursor
	grabbed = False; grabType = 999; cursorPaintMode = 0
 
	#Superfície da tela
	used_font = pygame.font.Font(None, 32)
	pySurface = pygame.display.set_mode(screen.size(),pygame.RESIZABLE)
	timer = pygame.time.Clock()

	board.update(False)
	screen.update(screen.width, screen.height)

	min_update_counter = 0.1
	max_update_counter = 30

	pySurface = pygame.display.set_mode(screen.size(), pygame.RESIZABLE)
	timer = pygame.time.Clock()

	while(gameRunning):
     
		#Controle de tempo: execução esperada a quantia "FPS" de frames por segundo, onde microTime é um contador de ticks que ocorrem em intervalos de tempo de acordo com a execução esperada.
		#updateCounter é o número de ticks necessários para uma atualização no tabuleiro, pode ser controlado
		timer.tick(FPS)
		for sl in screen.sliders:
			if sl:
				updateCounter = int(min_update_counter + (max_update_counter - min_update_counter) * (1 - sl.progress))

		microTime -= 1
		if microTime <= 0:
			microTime = updateCounter
			board.update(True)

		#Controle de cursor
		mousePos = pygame.mouse.get_pos()
		cursorType = CURSOR_SELECTED if grabbed else CURSOR_FREE
		if cursorType == 0:
			for bt in screen.buttons: #Se estiver passando o mouse em um botão, altera o cursor
				if bt.action != PAUSE_TIME and model.mode == "cassino":
					continue
				if bt.x <= mousePos[0] <= bt.x + bt.size and bt.y <= mousePos[1] <= bt.y + bt.size:
					cursorType = CURSOR_AIM
					break
			if model.mode == "cassino":
				for bt in screen.cassinoButtons:
					if bt.x <= mousePos[0] <= bt.x + bt.size and bt.y <= mousePos[1] <= bt.y + bt.size:
						cursorType = CURSOR_AIM
						break
				

		#Ativamente define o cursor correto
		if cursorType == CURSOR_FREE: 
			pygame.mouse.set_cursor(*pygame.cursors.arrow)
		elif cursorType == CURSOR_AIM:
			pygame.mouse.set_cursor(*pygame.cursors.broken_x)
		else:
			pygame.mouse.set_cursor(*pygame.cursors.tri_left)

		#Posição do tile em que o mouse está em cima, pode não ser válido, mas se for, é atestado em validTile
		tileRow = int((mousePos[1] - screen.originY)/screen.scaling + 1)-1
		tileCol = int((mousePos[0] - screen.originX + 1)/screen.scaling + 1)-1 #Adição e subtração do -1 para evitar int(-0.9) = int(0.9), pela natureza da aproximação int do python
		validTile = (tileRow < board.rows and tileCol < board.cols and tileRow >= 0 and tileCol >= 0)

		if validTile and grabbed and (grabType in CLICKABLE_BUTTONS): #Se estiver clicado em uma figura, tenta prever ela na posição atual
			setTileStates(tileRow,tileCol,grabType,PREVIEW_FIGURE)

		for event in pygame.event.get(): #Gerenciamento dos eventos pygame
			if event.type == pygame.QUIT:
				gameRunning = False
    
			#Eventos de tela: atualiza os objetos caso a tela altere de tamanho
			elif event.type == pygame.VIDEORESIZE:
				screen.update(event.w,event.h)
    
			elif event.type == pygame.WINDOWMAXIMIZED:
				w, h = pygame.display.get_window_size()
				screen.update(w,h)
    
			elif event.type == pygame.WINDOWMINIMIZED:
				w, h = pygame.display.get_window_size()
				screen.update(w,h)
			
			#Cliques esquerdos do mouse em botões ou em tiles
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
				#Verifica se o botão deslizando está sendo acionado e atualiza seu estado
				for sl in screen.sliders:
					if sl.slider_thumb_rect.collidepoint(event.pos): 
						sl.dragging = True
					else:
						sl.dragging = False

				for bt in screen.buttons:
					if bt.action != PAUSE_TIME and model.mode == "cassino":
						continue
					#Verifica se clicou em um botão para ativar o evento correspondente
					if bt.x <= mousePos[0] <= bt.x + bt.size and bt.y <= mousePos[1] <= bt.y + bt.size:
						if bt.action in CLICKABLE_BUTTONS: #Botões clicáveis: marcáveis com select
							if grabbed and grabType == bt.action: #Apenas clique para desativação
								grabbed = False
								screen.buttons[grabType-1].selected = False
							else: #Clique para ativação ou mudança de botão selecionado
								if grabType in CLICKABLE_BUTTONS:
									screen.buttons[grabType-1].selected = False
								elif grabType in NUMBER_BOXES:
									screen.numberBoxes[grabType-22].selected = False
								grabbed = True
								grabType = bt.action
								screen.buttons[grabType-1].selected = True
							break
						else: #Botões de ativação imediata, como pause
							launchEventOnce(bt.action)
       
				if model.mode == "cassino":
					global rounds
					for bt in screen.cassinoButtons:
						if bt.x <= mousePos[0] <= bt.x + bt.size and bt.y <= mousePos[1] <= bt.y + bt.size and rounds == 0:
							launchEventOnce(bt.action)

				#Se foi clicado com um botão ativado, ou coloca uma figura, ou altera o paintMode, que segue ativado até soltar o botão
				if validTile and grabbed:
					if grabType in FIGURE_BUTTONS:
						setTileStates(tileRow,tileCol,grabType,ACTIVATE_FIGURE)
					elif grabType in LIFE_BUTTONS:
						cursorPaintMode = grabType
      
				#Verifica se foi clicado em um NumberBox
				for nb in screen.numberBoxes:
					if nb.rect.collidepoint(event.pos):
						if grabbed and grabType == nb.action:
							grabbed = False
							nb.selected = False
						elif not grabbed:
							grabbed = True
							grabType = nb.action
							nb.selected = True
						elif grabbed and grabType != nb.action:
							if grabType in NUMBER_BOXES:
								screen.numberBoxes[grabType-22].selected = False
							elif grabType in CLICKABLE_BUTTONS:
								screen.buttons[grabType-1].selected = False
							grabbed = True
							grabType = nb.action
							nb.selected = True
						
      
			#Soltar o botão, desativa o paintmode se ativado
			elif event.type == pygame.MOUSEBUTTONUP:
				if grabbed and grabType in LIFE_BUTTONS:
					cursorPaintMode = 0
				for sl in screen.sliders:
					sl.dragging = False
     
			elif event.type == pygame.KEYDOWN: #Pressionamento de teclas
				if event.key == pygame.K_p: #P = Pausar
					launchEventOnce(PAUSE_TIME)
				if model.mode == "cassino":
					if event.key >= pygame.K_0 and event.key <= pygame.K_9:
						actualKey = event.key - pygame.K_0
						if screen.cassinoBoxes[0].value*10 + actualKey <= 100:
							screen.cassinoBoxes[0].value = screen.cassinoBoxes[0].value*10 + actualKey
							screen.cassinoBoxes[0].txt = used_font.render(str(screen.cassinoBoxes[0].value),True,SELECTED_COLOR)
					elif event.key == pygame.K_BACKSPACE:
						screen.cassinoBoxes[0].value //= 10
						screen.cassinoBoxes[0].txt = used_font.render(str(screen.cassinoBoxes[0].value),True,SELECTED_COLOR)
					continue
 
				if event.key >= pygame.K_0 and event.key <= pygame.K_8 and grabbed and grabType in NUMBER_BOXES:
					screen.numberBoxes[grabType-CHANGE_REVIVAL].value = (event.key - pygame.K_0)
					screen.numberBoxes[grabType-CHANGE_REVIVAL].txt = used_font.render(str(event.key - pygame.K_0),True,SELECTED_COLOR)
					model.updateRule(grabType-CHANGE_REVIVAL,(event.key - pygame.K_0))
     
				elif event.key == pygame.K_ESCAPE: #Esc = Cancelar botão que está ativo
					grabbed = False
					if grabType in CLICKABLE_BUTTONS:
						screen.buttons[grabType-1].selected = False
					elif grabType in NUMBER_BOXES:
						screen.numberBoxes[grabType-CHANGE_REVIVAL].selected = False
      
				elif event.key == pygame.K_1: #1 = selecionar "Reviver células"
					if grabbed and grabType == REVIVE_CELL:
						grabbed = False
						screen.buttons[grabType-1].selected = False
					elif not grabbed or (grabType not in NUMBER_BOXES):
						if grabType in CLICKABLE_BUTTONS:
							screen.buttons[grabType-1].selected = False
						elif grabType in NUMBER_BOXES:
							screen.numberBoxes[grabType-CHANGE_REVIVAL].selected = False
						grabbed = True
						grabType = REVIVE_CELL
						screen.buttons[grabType-1].selected = True
      
				elif event.key == pygame.K_2: #2 = selecionar "Matar células"
					if grabbed and grabType == KILL_CELL:
						grabbed = False
						screen.buttons[grabType-1].selected = False
					elif not grabbed or (grabType not in NUMBER_BOXES):
						if grabType in CLICKABLE_BUTTONS:
							screen.buttons[grabType-1].selected = False
						elif grabType in NUMBER_BOXES:
							screen.numberBoxes[grabType-CHANGE_REVIVAL].selected = False
						grabbed = True
						grabType = KILL_CELL
						screen.buttons[grabType-1].selected = True
				elif event.key == pygame.K_3: # 3 = selecionar "Matar células permanentemente
					if grabbed and grabType == KILL_EVER:
						grabbed = False
						screen.buttons[grabType-1].selected = False
					elif not grabbed or (grabType not in NUMBER_BOXES):
						if grabType in CLICKABLE_BUTTONS:
							screen.buttons[grabType-1].selected = False
						elif grabType in NUMBER_BOXES:
							screen.numberBoxes[grabType-CHANGE_REVIVAL].selected = False
						grabbed = True
						grabType = KILL_EVER
						screen.buttons[grabType-1].selected = True
				elif event.key == pygame.K_4: # 4 = selecionar Contaminar celulas
					if grabbed and grabType == SICK_CELL:
						grabbed = False
						screen.buttons[grabType-1].selected = False
					elif not grabbed or (grabType not in NUMBER_BOXES):
						if grabType in CLICKABLE_BUTTONS:
							screen.buttons[grabType-1].selected = False
						elif grabType in NUMBER_BOXES:
							screen.numberBoxes[grabType-CHANGE_REVIVAL].selected = False
						grabbed = True
						grabType = SICK_CELL
						screen.buttons[grabType-1].selected = True

				elif event.key == pygame.K_5:  # 5 = botão configurado tabuleiro aleatorio
					launchEventOnce(GENERATE_BOARD)
				elif event.key == pygame.K_6:  # 6 = botão de limpar tabuleiro
					launchEventOnce(CLEAR_BOARD)
				if event.key == pygame.K_r: #r = Rotacionar
					launchEventOnce(ROTATION)
						

		#Modo de pintura: ativação/desativação de células individuais
		if validTile and cursorPaintMode in LIFE_BUTTONS:
			paintTile(tileRow,tileCol,grabType)	

		#Update do Slider
		for sl in screen.sliders:
			sl.updateThumb(mousePos)

		#Update da tela
		pySurface.fill(BACKGROUND_COLOR)
		drawCurrentGame(pySurface)
		pygame.display.update()

	pygame.quit()

def generateConwayGame(isRandom = False, modo= "deterministic", linhas=45, colunas=80 ):
	#Tabuleiro inicial
	global model, board, screen
	pygame.init()
	model = conwayModel.GameOfLifeModel(rows=linhas,cols=colunas, mode= modo)
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
	screen.addButton(Button(SUMMON_EATER,6,IMG_EATER))
	screen.addButton(Button(SUMMON_TOAD,7,IMG_TOAD))
	screen.addButton(Button(SUMMON_BEEHIVE,8,IMG_BEEHIVE))
	screen.addButton(Button(SUMMON_TUB,9,IMG_TUB))
	screen.addButton(Button(SUMMON_LEGS,10,IMG_LEGS))
	screen.addButton(Button(SUMMON_XPENTOMINO,11,IMG_XPENTOMINO))
	screen.addButton(Button(SUMMON_LONGHOOK,12,IMG_LONGHOOK))
 
	#Botões de matar e reviver células
	screen.addButton(Button(REVIVE_CELL,13,IMG_ALIVECELL))
	screen.addButton(Button(KILL_CELL,14,IMG_DEADCELL))
	screen.addButton(Button(KILL_EVER,15,IMG_DEADPERMANENTE))
	screen.addButton(Button(SICK_CELL, 16, IMG_PURPLE))
	screen.addButton(Button(PAUSE_TIME,17,IMG_PAUSE))
	screen.addButton(Button(GENERATE_BOARD,18,IMG_GENERATEBOARD))
	screen.addButton(Button(CLEAR_BOARD,19,IMG_CLEARBOARD))
	screen.addButton(Button(ROTATION,20,IMG_ROTATION))
	
	#Caixas numéricas de alterar regras e textos
	if model.mode == "deterministic":
		screen.addFloatingText(Floating_Text("Renascimentos:",66))
		screen.addFloatingText(Floating_Text("Permanências:  ≥       ≤    ",63))
		screen.addNumberBox(Number_Box(CHANGE_REVIVAL,62,3))
		screen.addNumberBox(Number_Box(CHANGE_MIN_SURVIVAL,59,2))
		screen.addNumberBox(Number_Box(CHANGE_MAX_SURVIVAL,63,3))
  
	#Utilidades do cassino
	if model.mode == "cassino":
		screen.addCassinoText(Floating_Text("1",72))
		screen.addCassinoText(Floating_Text("1024",73))
		screen.addCassinoText(Floating_Text(" Apostando:   R$",60))
		screen.addCassinoText(Floating_Text("Saldo:   R$",65))
		screen.addCassinoButton(Button(CASSINO_PLAY,13,IMG_BET))
		screen.addCassinoButton(Button(CASSINO_RAISE,14,IMG_RAISE))
		screen.addCassinoButton(Button(CASSINO_LOWER,15,IMG_LOWER))
		screen.addCassinoText(Floating_Text("  Estimativa (Digite):",30))
		screen.addCassinoBox(Number_Box(CASSINO_GUESS,15,50,2))
		screen.addCassinoText(Floating_Text("  %",35))
		screen.addSlider(Slider_Button(progr=1))
	else:
		screen.addSlider(Slider_Button())
	runGame()

def criar_tela_inicial():
	janela = tk.Tk()
	janela.title("Jogo da Vida - Tela Inicial")
	janela.geometry("1280x720")
	janela.resizable(False, False)

	# Adicionando um canvas para a imagem de fundo
	canvas = tk.Canvas(janela, width=1280, height=720)
	canvas.pack(fill="both", expand=True)

	# Carregando a imagem de fundo
	imagem_fundo = Image.open("images/logo.png")
	imagem_fundo = imagem_fundo.resize((1280, 720), Image.Resampling.LANCZOS)
	fundo = ImageTk.PhotoImage(imagem_fundo)

	# Exibindo a imagem no canvas
	canvas.create_image(0, 0, image=fundo, anchor="nw")

	# Adicionando widgets diretamente sobre o canvas
	titulo = tk.Label(janela, text="Bem-vindo ao Jogo da Vida", font=("Fixedsys", 22, "bold"), bg="#FFFFFF")
	titulo.place(x=640 - 431/2, y=25)

	tipo_jogo_var = tk.StringVar(value="deterministic")

	tipo_jogo_frame = tk.Frame(janela, bg="#FFFFFF")
	tipo_jogo_frame.place(x=640 + 110 + (326-259), y=110)

	tk.Label(tipo_jogo_frame, text="Opção de Jogo:", font=("Fixedsys", 19), bg = "#FFFFFF").pack(anchor="w")

	rb_prob = tk.Radiobutton(tipo_jogo_frame, text="Probabilístico", variable=tipo_jogo_var, value="probabilistic", font=("Fixedsys", 19), bg="#FFFFFF")
	rb_deter = tk.Radiobutton(tipo_jogo_frame, text="Determinístico", variable=tipo_jogo_var, value="deterministic", font=("Fixedsys", 19), bg="#FFFFFF")
	rb_cass = tk.Radiobutton(tipo_jogo_frame, text="Cassino", variable=tipo_jogo_var,
	value="cassino", font=("Fixedsys", 19), bg="#FFFFFF")
	rb_prob.pack(anchor="w")
	rb_deter.pack(anchor="w")
	rb_cass.pack(anchor="w")

	tamanho_tabuleiro_var = tk.StringVar(value="Medio")

	tabuleiro_frame = tk.Frame(janela, bg="#FFFFFF")
	tabuleiro_frame.place(x=640 - 326 - 110, y=110)

	tk.Label(tabuleiro_frame, text="Opções de Tabuleiro:", font=("Fixedsys", 19), bg="#FFFFFF").pack(anchor="w")

	rb_pequeno = tk.Radiobutton(tabuleiro_frame, text="Pequeno", variable=tamanho_tabuleiro_var, value="Pequeno", font=("Fixedsys", 19), bg="#FFFFFF")
	rb_medio = tk.Radiobutton(tabuleiro_frame, text="Médio", variable=tamanho_tabuleiro_var, value="Medio", font=("Fixedsys", 19), bg="#FFFFFF")
	rb_grande = tk.Radiobutton(tabuleiro_frame, text="Grande", variable=tamanho_tabuleiro_var, value="Grande", font=("Fixedsys", 19), bg="#FFFFFF")
	rb_pequeno.pack(anchor="w")
	rb_medio.pack(anchor="w")
	rb_grande.pack(anchor="w")
	
	def iniciar_jogo():
		# Obtém as opções selecionadas
		tipo_jogo = tipo_jogo_var.get()
		tamanho_tabuleiro = tamanho_tabuleiro_var.get()

		# Exibe no console (substitua por chamada à lógica do jogo)
		print(f"Jogo iniciado com opção: {tipo_jogo}, Tabuleiro: {tamanho_tabuleiro}")
		linha, coluna=  0,0
		if tamanho_tabuleiro == "Medio":
			linha= 36
			coluna= 60
		elif tamanho_tabuleiro == "Grande":
			linha= 60
			coluna=100
		else:
			linha=24
			coluna=40

		generateConwayGame(isRandom = False, modo = tipo_jogo, linhas=linha,  colunas=coluna)
  
	btn_iniciar = tk.Button(janela, text="Iniciar Jogo", font=("Fixedsys", 20), bg="green", fg="white", command=iniciar_jogo)
	btn_iniciar.place(x=640 - 216/2, y=310)
  
	# Mantém a imagem de fundo no escopo para evitar garbage collection
	canvas.image = fundo
	janela.mainloop()

# Chamar a função para exibir a janela inicial
criar_tela_inicial()

