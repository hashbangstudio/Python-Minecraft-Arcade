# Implementation of Inkspill in Minecraft using the Python API
# Adapts the original PyGame code from Al Sweigart to Minecraft display
# Keeps the same "Simplified BSD" license
#
# Original header comment :
#
# Ink Spill (a Flood It clone)
# http://inventwithpython.com/pygame
# By Al Sweigart al@inventwithpython.com
# Released under a "Simplified BSD" license

import sys
import random, copy
from time import sleep
from mcpi.vec3 import Vec3
from mcpi.block import WOOL, GLOWING_OBSIDIAN, GLASS, DIAMOND_BLOCK, TNT, AIR
from mcpi.minecraft import Minecraft
from blockData import COLOUR_NAME_TO_ID as woolCol

# There are different number of boxes, and
# life depending on the "board size" setting selected.

SMALLBOARDSIZE  = 6 # size is in boxes
MEDIUMBOARDSIZE = 17
LARGEBOARDSIZE  = 30

SMALLMAXLIFE  = 10 # number of turns
MEDIUMMAXLIFE = 30
LARGEMAXLIFE  = 64


EASY   = 0   # arbitrary but unique value
MEDIUM = 1   # arbitrary but unique value
HARD   = 2   # arbitrary but unique value

#The pause between each iteration of the game loop
POLL_TIME = 1.0/60.0

difficulty  = MEDIUM # game starts in "medium" mode
maxLife     = MEDIUMMAXLIFE
boardWidth  = MEDIUMBOARDSIZE
boardHeight = MEDIUMBOARDSIZE

# The first color in each scheme is the background color, the next six are the palette colors.
COLORSCHEMES = (
               (woolCol["red"], woolCol["lime"], woolCol["blue"], woolCol["yellow"], woolCol["orange"], woolCol["magenta"]),
               )

for i in range(len(COLORSCHEMES)):
    assert len(COLORSCHEMES[i]) == 6, 'Color scheme %s does not have exactly 6 colors.' % (i)

paletteColors =  COLORSCHEMES[0][:]

BOARD_OFFSET = (6, 0, 3)

LIFE_BAR_OFFSET = (3, 0, 3)

PALETTE_OFFSET = (6, 0 , 9)

boardBottomLeft = Vec3()
lifeBarPos = Vec3()

def main(mc):
    global maxLife, difficulty, boardWidth, boardHeight
    # save a checkpoint of the world to restore to
    mc.saveCheckpoint()

    #create an inkspill board
    mainBoard = generateRandomBoard(boardWidth, boardHeight, difficulty)
    life = maxLife
    lastPaletteClicked = None

    # make the world immutable so game board can't be destroyed
    mc.setting("world_immutable", True)
    
    # Draw the board in minecraft
    initialPlayerPos = mc.player.getTilePos()
    clearAreaForGame(initialPlayerPos, mc)
    createBoard(mainBoard, initialPlayerPos, mc)
    createLifeMeter(life, initialPlayerPos, mc)
    drawPalettes(initialPlayerPos, mc)

    resetGame = False
    while True: # main game loop
        sleep(POLL_TIME)
        paletteClicked = None

        hits = mc.events.pollBlockHits()
        if len(hits) > 0:
            #print hits
            #print hits[0]
            blockHit = mc.getBlockWithData(hits[0].pos.x, hits[0].pos.y, hits[0].pos.z )
            blockId = blockHit.id
            colour = blockHit.data
            # check if a palette block hit
            if blockId == WOOL.id:
                paletteClicked = colour
                #for colElement in woolCol.items():
                #    if colour == colElement[1]:
                #        print colElement[0] , "hit"

            if paletteClicked != None and paletteClicked != lastPaletteClicked:
                # a palette button was clicked that is different from the
                # last palette button clicked (this check prevents the player
                # from accidentally clicking the same palette twice)
                oldColour = mc.getBlockWithData(boardBottomLeft).data
                floodFill(mainBoard, oldColour, paletteClicked, 0, 0)

                lastPaletteClicked = paletteClicked
                life -= 1
                drawBoard(mainBoard, mc)
                drawLifeMeter(life, mc)
                
            if hasWon(mainBoard):
                print("have won!")
                #set blocks to success
                time.sleep(3)
                resetGame = True
            elif life == 0:
                drawLifeMeter(life, mc)
                print "have lost!"
                #set blocks to fail
                time.sleep(3)
                resetGame = True
        
        if resetGame:
            mainBoard = generateRandomBoard(boardWidth, boardHeight, difficulty)
            life = maxLife
            lastPaletteClicked = None
            # Draw the board in minecraft
            drawBoard(mainBoard, mc)
            drawLifeMeter(life, mc)
            resetGame = False

def hasWon(board):
    global boardWidth, boardHeight
    # if the entire board is the same color, player has won
    for x in range(boardWidth):
        for y in range(boardHeight):
            if board[x][y] != board[0][0]:
                return False # found a different color, player has not won
    return True


def generateRandomBoard(width, height, difficulty=MEDIUM):
    # Creates a board data structure with random colors for each box.
    board = []
    for x in range(width):
        column = []
        for y in range(height):
            column.append(paletteColors[random.randint(0, len(paletteColors) - 1)])
        board.append(column)

    # Make board easier by setting some boxes to same color as a neighbor.

    # Determine how many boxes to change.
    if difficulty == EASY:
        boxesToChange = 10
    elif difficulty == MEDIUM:
        boxesToChange = 20
    else:
        boxesToChange = 0

    # Change neighbor's colors:
    for i in range(boxesToChange):
        # Randomly choose a box whose color to copy
        x = random.randint(1, width-2)
        y = random.randint(1, height-2)

        # Randomly choose neighbors to change.
        direction = random.randint(0, 3)
        if direction == 0: # change left and up neighbor
            board[x-1][y] == board[x][y]
            board[x][y-1] == board[x][y]
        elif direction == 1: # change right and down neighbor
            board[x+1][y] == board[x][y]
            board[x][y+1] == board[x][y]
        elif direction == 2: # change right and up neighbor
            board[x][y-1] == board[x][y]
            board[x+1][y] == board[x][y]
        else: # change left and down neighbor
            board[x][y+1] == board[x][y]
            board[x-1][y] == board[x][y]
    return board



def createBoard(board,playerPos, mc):
    global boardBottomLeft

    boardBottomLeft = copy.deepcopy(playerPos)
    boardBottomLeft.x += BOARD_OFFSET[0]
    boardBottomLeft.y += BOARD_OFFSET[1]
    boardBottomLeft.z += BOARD_OFFSET[2]

    drawBoard(board, mc)

def drawBoard(board, mc):
    global boardBottomLeft, boardWidth, boardHeight
    for x in range(boardWidth):
        for y in range(boardHeight):
            #print x,y,board[x][y]
            colourId = board[x][y]
            mc.setBlock(boardBottomLeft.x + x, boardBottomLeft.y + y, boardBottomLeft.z, WOOL.withData(colourId))


def drawPalettes(initialPlayerPos, mc):
    # Draws the six color palettes at the bottom of the playArea.
    palettePosition = copy.deepcopy(initialPlayerPos)
    palettePosition.x += PALETTE_OFFSET[0]
    palettePosition.y += PALETTE_OFFSET[1]
    palettePosition.z += PALETTE_OFFSET[2]
    xShift = 0
    for colour in paletteColors:
        mc.setBlock(palettePosition.x + xShift, palettePosition.y, palettePosition.z, WOOL.withData(colour))
        xShift += 1

def clearAreaForGame(initialPlayerPos, mc):
    global maxLife, boardHeight, boardWidth
    # Draws the six color palettes at the bottom of the playArea.
    playerPosition = copy.deepcopy(initialPlayerPos)
    lifeBarPos = Vec3(  playerPosition.x + LIFE_BAR_OFFSET[0], 
                        playerPosition.y + LIFE_BAR_OFFSET[1], 
                        playerPosition.z + LIFE_BAR_OFFSET[2])
                    
    palettePosition = Vec3( playerPosition.x + PALETTE_OFFSET[0],
                            playerPosition.y + PALETTE_OFFSET[1],
                            playerPosition.z + PALETTE_OFFSET[2])
                            
    boardBottomLeft = Vec3( playerPosition.x + BOARD_OFFSET[0],
                            playerPosition.y + BOARD_OFFSET[1],
                            playerPosition.z + BOARD_OFFSET[2])
    
    mc.setBlocks(lifeBarPos.x - 2, lifeBarPos.y - 2, lifeBarPos.z -2,
                 boardBottomLeft.x + boardWidth + 2, lifeBarPos.y + maxLife + 2, palettePosition.z + 2,
                 AIR)
        

def createLifeMeter(currentLife, position, mc):
    global lifeBarPos
    lifeBarPos = copy.deepcopy(position)
    lifeBarPos.x += LIFE_BAR_OFFSET[0]
    lifeBarPos.y += LIFE_BAR_OFFSET[1]
    lifeBarPos.z += LIFE_BAR_OFFSET[2]
    drawLifeMeter(currentLife, mc)


def drawLifeMeter(currentLife, mc):
    global lifeBarPos, maxLife
    lifeBoxSize = maxLife

    for i in range(maxLife):    
        y = lifeBarPos.y + i
        if currentLife >=  i: # draw a 'red' box
            mc.setBlock(lifeBarPos.x, y, lifeBarPos.z, GLOWING_OBSIDIAN)
        else: # draw a 'clear' box
            mc.setBlock(lifeBarPos.x, y, lifeBarPos.z, GLASS)


def floodFill(board, oldColor, newColor, x, y):
    # This is the flood fill algorithm.
    if oldColor == newColor or board[x][y] != oldColor:
        return

    board[x][y] = newColor # change the color of the current box

    # Make the recursive call for any neighboring boxes:
    if x > 0:
        floodFill(board, oldColor, newColor, x - 1, y) # on box to the left
    if x < boardWidth - 1:
        floodFill(board, oldColor, newColor, x + 1, y) # on box to the right
    if y > 0:
        floodFill(board, oldColor, newColor, x, y - 1) # on box to up
    if y < boardHeight - 1:
        floodFill(board, oldColor, newColor, x, y + 1) # on box to down


if __name__ == '__main__':
    try:
        mc = Minecraft.create()
        main(mc)
    except KeyboardInterrupt:
        # make the world mutable to return to how was
        mc.setting("world_immutable", False)
        # Restore the world to the state it was in before the game
        mc.restoreCheckpoint()
        sys.exit()
    finally:
        # make the world mutable to return to how was
        mc.setting("world_immutable", False)
        # Restore the world to the state it was in before the game
        mc.restoreCheckpoint()
        sys.exit()
    
    
    
