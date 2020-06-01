import pygame,random,sys,os,time
from pygame.locals import *
import win32gui,win32api,win32con


from ai import Ai

def LoadImageWithSize(name,size):
    return pygame.transform.scale(pygame.image.load(os.path.join("imgs",name)).convert_alpha(), size)

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" %(0,0)

#game config
TILE_W = 30
GAP = 5
MINE_COUNT = 60
FPS = 30
TILE_H_NUMBER = 20
TILE_V_NUMBER = 20
WINDOW_W = (GAP+TILE_W)*TILE_H_NUMBER+80
WINDOW_H = (GAP+TILE_W)*TILE_V_NUMBER+160
AUTO = True
MINE_LEFT = MINE_COUNT

TILE_COLOR = (200,200,200)
NUM_COLOR = (0,0,0)
MARK_COLOR = (200,0,0)
COVER_COLOR = (120,120,120)
TILE_HIGHLIGHT_COLOR = (255,0,0)
BUTTON_BGCOLOR = (255,255,255)
BUTTON_TEXTCOLOR = (0,0,0)

windowXOffset =0
windowYOffset =0


#pygame init
pygame.init()
pygame.font.init()
WINDOW = pygame.display.set_mode((WINDOW_W,WINDOW_H))
pygame.display.set_caption("美丽的扫雷")
mouse_pos = (0,0)
WINDOW.fill((0,0,0))
NORMAL_FONT = pygame.font.SysFont(None,20)
BIG_FONT = pygame.font.Font("C:\Windows\Fonts\STXIHEI.TTF",30)
BIG_BIG_FONT = pygame.font.Font("C:\Windows\Fonts\STXIHEI.TTF",100)



#img things
FAIL_IMG = LoadImageWithSize("fail.png",(120,200))
WIN_IMG = LoadImageWithSize("win.png",(120,200))
ICON =LoadImageWithSize("mark.png",(30,30))
pygame.display.set_icon(ICON)


def main():
    global MINE_LEFT
    #initgame
    mines,nums,revealed,marked,ai = initGame()
    clock = pygame.time.Clock()
    
    # btns
    reset_btn, reset_rect = button('重来', BUTTON_TEXTCOLOR, BUTTON_BGCOLOR, 70, WINDOW_H-60)
    ai_btn, ai_rect = button('AI', BUTTON_TEXTCOLOR, BUTTON_BGCOLOR, WINDOW_W -60, WINDOW_H-60)

    while True:
        clock.tick(FPS)        
        mouse_left = False
        mouse_right = False
        for event in pygame.event.get(): 
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                quit()
                break
            elif event.type == MOUSEMOTION:
                mouse_pos = event.pos
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                #left click
                if(event.button==1):
                    mouse_left = True
                #right click
                elif(event.button==3):
                    mouse_right = True

        #black background
        WINDOW.fill((0,0,0))

        #draw
        drawTiles()
        drawNumbers(nums,mines,revealed)
        drawCovers(revealed,marked)
        drawMineLeft()
        tile_hover = getTileFromPixel(mouse_pos)
        WINDOW.blit(reset_btn,reset_rect)
        WINDOW.blit(ai_btn,ai_rect)


        #use ai if auto
        if(AUTO):
            next = ai.pickNext()
            x = next["position"]["x"]
            y = next["position"]["y"]
            if next["mine"]:
                cursorPX,cursorPY = getLeftTopOfTile(x,y)
                moveCursor(cursorPX+TILE_W/2,cursorPY+TILE_W/2)
                markMine(x,y,marked)    
            else:
                if(mines[x][y]):
                    gameOver(revealed,mines,marked)
                    mines,nums,revealed,marked,ai = initGame()
                    continue
                cursorPX,cursorPY = getLeftTopOfTile(x,y)
                moveCursor(cursorPX+TILE_W/2,cursorPY+TILE_W/2)
                revealNumbers(revealed,mines,x,y,nums)


        if tile_hover == None:
            # restart the game
            if reset_rect.collidepoint(mouse_pos[0],mouse_pos[1]):
                if mouse_left:
                    mines,nums,revealed,marked,ai = initGame()
            #get next step from ai algorithm
            elif ai_rect.collidepoint(mouse_pos[0],mouse_pos[1]):
                if mouse_left:
                    next = ai.pickNext()
                    x = next["position"]["x"]
                    y = next["position"]["y"]
                    if next["mine"]:
                        markMine(x,y,marked)
                    else:
                        if(mines[x][y]):
                            gameOver(revealed,mines,marked)
                            mines,nums,revealed,marked,ai = initGame()
                            continue
                        revealNumbers(revealed,mines,x,y,nums)
        #hover over tile
        else:
            if not revealed[tile_hover[0]][tile_hover[1]]:
                if marked[tile_hover[0]][tile_hover[1]] == False:
                    highlightTile(tile_hover[0],tile_hover[1])
                
                #right click: mark the tile as mine
                if mouse_right:
                    if marked[tile_hover[0]][tile_hover[1]] == True:
                        unMarkMine(tile_hover[0],tile_hover[1],marked)
                    else:
                        markMine(tile_hover[0],tile_hover[1],marked)
                # left click: reveal it
                if mouse_left:
                    if marked[tile_hover[0]][tile_hover[1]] == False:
                        if mines[tile_hover[0]][tile_hover[1]] == False:
                            revealed[tile_hover[0]][tile_hover[1]] = True
                            revealNumbers(revealed,mines,tile_hover[0],tile_hover[1],nums)
                        else:
                            showMines(nums,revealed,mines,marked)
                            time.sleep(3)
                            gameOver(revealed,mines,marked)
                            mines,nums,revealed,marked,ai = initGame()
        # check if win
        if win(revealed,mines):
            gameWin(revealed,mines,marked)
            mines,nums,revealed,marked,ai = initGame()


        pygame.display.update()


def highlightTile(x,y):
    lineWidth = 3
    left,top = getLeftTopOfTile(x,y)
    pygame.draw.rect(WINDOW,TILE_HIGHLIGHT_COLOR,(left,top,TILE_W,TILE_W))
    pygame.draw.rect(WINDOW,TILE_COLOR,(left+lineWidth,top+lineWidth,TILE_W-lineWidth*2,TILE_W-lineWidth*2))

def drawTiles():
    for x in range(TILE_H_NUMBER):
        for y in range(TILE_V_NUMBER):
            left,top = getLeftTopOfTile(x,y)
            pygame.draw.rect(WINDOW,TILE_COLOR,(left,top,TILE_W,TILE_W))

def getLeftTopOfTile(x,y):
    left = WINDOW_W/2 - (TILE_H_NUMBER/2*TILE_W+TILE_H_NUMBER/2*GAP)+(GAP+TILE_W)*x
    top = 50 + (GAP+TILE_W)*y
    return left,top

def drawNumbers(nums,mines,revealed):
    for x in range(TILE_H_NUMBER):
        for y in range(TILE_V_NUMBER):
            left,top = getLeftTopOfTile(x,y)
            if(mines[x][y] == False):
                if(nums[x][y]>0):
                    drawText(str(nums[x][y]),left+TILE_W/2,top+TILE_W/2,NORMAL_FONT,NUM_COLOR)
            else:
                if(revealed[x][y]):
                    drawText("BOOM",left+TILE_W/2,top+TILE_W/2,NORMAL_FONT,(255,0,0))
                
def drawText(text,x,y,font,color):
    text = font.render(text,True,color)
    rect = text.get_rect()
    rect.centerx = x
    rect.centery = y
    WINDOW.blit(text,rect)

def drawMineLeft():
    global MINE_LEFT
    left = BIG_FONT.render(str(MINE_LEFT),True,(255,255,255),(0,150,0))
    leftRect = left.get_rect()
    leftRect.centerx = WINDOW_W/2
    leftRect.centery = WINDOW_H - 60
    WINDOW.blit(left,leftRect)


def button(text,color,bgcolor,centerx,centery):
    btn = BIG_FONT.render(text, True, color, bgcolor)
    btnRect = btn.get_rect()
    btnRect.centerx = centerx
    btnRect.centery = centery
    return (btn, btnRect)

def drawCovers(revealed,marked):
    for x in range(len(revealed)):
        for y in range(len(revealed[x])):
            if(revealed[x][y] == False):
                left,top = getLeftTopOfTile(x,y)
                pygame.draw.rect(WINDOW,COVER_COLOR,(left,top,TILE_W,TILE_W))
                if(marked[x][y] == True):
                    rect = ICON.get_rect()
                    rect.centerx = left + TILE_W/2
                    rect.centery = top + TILE_W/2
                    WINDOW.blit(ICON,rect)

def getTileFromPixel(pos):
    for x in range(TILE_H_NUMBER):
        for y in range(TILE_V_NUMBER):
            left,top = getLeftTopOfTile(x,y)
            rect = pygame.Rect((left,top,TILE_W,TILE_W))
            if rect.collidepoint(pos[0],pos[1]):
                return x,y
    return None

def markMine(x,y,marked):
    global MINE_LEFT
    if(marked[x][y] == False):
        marked[x][y] = True
        MINE_LEFT -=1

def unMarkMine(x,y,marked):
    global MINE_LEFT
    if(marked[x][y] == True):
        marked[x][y] = False
        MINE_LEFT += 1
    


def revealNumbers(revealed,mines,x,y,numbers):

    revealed[x][y] = True



    if(numbers[x][y]!=0):
        return 0

    for x,y in getAdjacentTiles(x,y):
        if revealed[x][y]== False:
            revealNumbers(revealed,mines,x,y,numbers)

def getAdjacentTiles(x,y):

    # get box XY coordinates for all adjacent boxes to (box_x, box_y)
    x_w =TILE_H_NUMBER
    y_w = TILE_V_NUMBER

    adjacents = []
    if x!=0:
        adjacents.append([x-1,y])
        if y!= 0:
            adjacents.append([x-1,y-1])
        if y!= y_w-1:
            adjacents.append([x-1,y+1])
    if x!= x_w -1:
        adjacents.append([x+1,y])
        if y!= 0:
            adjacents.append([x+1,y-1])
        if y!= y_w-1:
            adjacents.append([x+1,y+1])           
    if y!= 0:
        adjacents.append([x,y-1])
    if y!= y_w-1:
        adjacents.append([x,y+1])

    return adjacents
    

def showMines(nums,revealed,mines,marked):
    for x in range(TILE_H_NUMBER):
        for y in range(TILE_V_NUMBER):
            if(mines[x][y] == True):
                revealed[x][y] = True
                drawTiles()
                drawNumbers(nums,mines,revealed)
                drawCovers(revealed,marked)
                pygame.display.update()
                

def gameOver(revealed,mines,marked):
    clock = pygame.time.Clock()
    fps = 2
    # for i in range(6):
    #     WINDOW.fill((0,0,0))
    #     if(i%2==0):
    #         rotated_img = pygame.transform.rotate(WIN_IMG,30)
    #     else:
    #         rotated_img = pygame.transform.rotate(WIN_IMG,-30)
    #     WINDOW.blit(rotated_img,(WINDOW_W/2,WINDOW_H-rotated_img.get_size()[1]))
    #     drawText("下次一定!!!",WINDOW_W/2,WINDOW_H/2,BIG_BIG_FONT,(255,255,255))
    #     pygame.display.update()
    #     clock.tick(fps)
    print("die")
        

                

def gameWin(revealed,mines,marked):
    clock = pygame.time.Clock()
    fps = 2
    # for i in range(6):
    #     WINDOW.fill((0,0,0))
    #     if(i%2==0):
    #         rotated_img = pygame.transform.rotate(FAIL_IMG,30)
    #     else:
    #         rotated_img = pygame.transform.rotate(FAIL_IMG,-30)

    #     WINDOW.blit(rotated_img,(WINDOW_W/2,WINDOW_H-rotated_img.get_size()[1]))
    #     drawText("这次一定",WINDOW_W/2,WINDOW_H/2,BIG_BIG_FONT,(255,255,255))
    #     pygame.display.update()
    #     clock.tick(fps)
    pass

def initGame():
    global MINE_LEFT
    mines = initMines()
    numbers = initNumbers(mines)
    marked = initMarked()
    revealed = initRevealed()
    ai = Ai(mines,revealed,marked,numbers,TILE_H_NUMBER,TILE_V_NUMBER,MINE_COUNT)
    MINE_LEFT = MINE_COUNT
    return mines,numbers,revealed,marked,ai
    
def initMarked():
    marks = []
    for x in range(TILE_H_NUMBER):
        marks.append([])    
        for y in range(TILE_V_NUMBER):
            marks[x].append(False)
    return marks   

def initRevealed():
    revealed = []
    for x in range(TILE_H_NUMBER):
        revealed.append([])
        for y in range(TILE_V_NUMBER):
            revealed[x].append(False)

    return revealed

def initMines():
    mines = []
    for x in range(TILE_H_NUMBER):
        mines.append([])    
        for y in range(TILE_V_NUMBER):
            mines[x].append(False)
    count = 0
    while count < MINE_COUNT:
        x = random.randint(0,TILE_H_NUMBER-1)
        y = random.randint(0,TILE_V_NUMBER-1)
        if(mines[x][y]==False):
            mines[x][y] = True
            count+=1
        else:
            continue
 
    return mines

def initNumbers(mines):
    numbers = []

    for x in range(TILE_H_NUMBER):
        numbers.append([])
        for y in range(TILE_V_NUMBER):
            if(mines[x][y]!=True):
                numbers[x].append(getNumbersOfTile(x,y,mines))
            else:
                numbers[x].append(-1)

    return numbers


def getNumbersOfTile(x,y,mines):
    checkPosition = []
    if x != 0:
        checkPosition.append([x-1,y])
        if y != 0:
            checkPosition.append([x-1,y-1])
        if y != TILE_V_NUMBER-1:
            checkPosition.append([x-1,y+1])
    if x != TILE_H_NUMBER-1: 
        checkPosition.append([x+1,y])
        if y != 0:
            checkPosition.append([x+1,y-1])
        if y != TILE_V_NUMBER-1:
            checkPosition.append([x+1,y+1])
    if y != 0:
        checkPosition.append([x,y-1])
    if y != TILE_V_NUMBER-1:
        checkPosition.append([x,y+1])

    output = 0

    for position in checkPosition:
        if(mines[position[0]][position[1]]==True):
            output += 1

    return output


def win(revealed,mines):
    revealedNum = 0
    for x in range(TILE_H_NUMBER):
        for y in range(TILE_V_NUMBER):
            if(revealed[x][y]==True):
                revealedNum+=1

    if(revealedNum == (TILE_H_NUMBER* TILE_V_NUMBER -MINE_COUNT)):
        return True
    else:
        return False

def moveCursor(x,y):
    global windowXOffset
    global windowYOffset
    win32api.SetCursorPos((int(x+windowXOffset),int(y+windowYOffset)))


if __name__ == '__main__':
    main()


