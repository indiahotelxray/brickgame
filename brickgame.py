#!/usr/bin/python3
import pyxel
import math
import random
import time

FPS = 60
RATE = 2
SPEED = 1./RATE

class BrickGame:
    def __init__(self):
        self.board = BrickBoard(x=200,y=150)
        pyxel.init(self.board.x,self.board.y,caption="Brick", fps=FPS)
        self.paddle = BrickPaddle(self.board, y=self.board.y - 10., width=2., length=30.,col=7)
        self.ball = BrickBall(self.board, self.paddle,
                self.board.x/2, self.board.y/2 + 20, size=4.,col=11,shadow=False)
        pyxel.run(self.update, self.draw)

    def update(self):
        self.board.update()
        self.paddle.update()
        self.ball.update()

    def draw(self):
        pyxel.cls(0)
        self.board.draw()
        self.paddle.draw()
        self.ball.draw()

class BrickBoard:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.bricks = BrickArray(self, self.x/2.,40,5,6,10,20,spacing=4)

    def moveball(self, bx, by, bvel, bsize):
        #handle collisions with walls
        xbounds = (bsize, self.x - bsize)
        ybounds = (bsize, self.y - bsize)
        xunlimited = bx + bvel[0]
        yunlimited = by + bvel[1]
        newx = min(max(xbounds[0],bx + bvel[0]),xbounds[1])
        newy = min(max(ybounds[0],by + bvel[1]),ybounds[1])
        xdiff = newx - xunlimited
        ydiff = newy - yunlimited
        hit = False
        if xdiff != 0:
            bvel[0] *= -1
            newx + xdiff
            hit = True
        if ydiff != 0:
            bvel[1] *= -1
            newy + ydiff
            hit = True
        return hit, newx, newy, bvel

    def update(self):
        self.bricks.update()

    def draw(self):
        self.bricks.draw()

class BrickPaddle:
    def __init__(self, board, y, width, length, col):
        self.board = board
        self.width = width
        self.length = length
        self.col = col
        self.x = self.board.x/2.
        self.y = y
        self.velocity = 0

    def moveball(self, bx, by, bvel, bsize):
        yunlimited = by + bvel[1]
        if by <= self.y and yunlimited > self.y:
            # check intersection
            xintersect = bx # div by zero case)
            if bvel[0] != 0:
                velslope = bvel[1]/bvel[0]
                xintersect = bx + math.floor(velslope*(self.y - by))
            # check and return new velocity 
            if (self.x - self.length/2.) <= xintersect <= (self.x + self.length/2.):
                hit = True
                newx = bx + bvel[0] 
                ydiff = yunlimited - (self.y - bsize)
                newy = self.y - ydiff
                newvel = [bvel[0]+(-self.velocity/4.), bvel[1]*-1]
                print("newvel: %f %f" % (newvel[0], newvel[1]))
                return (hit, newx, newy, newvel)
        return (False, bx, by, bvel)

    def update(self):
        prevx = self.x 
        self.x = pyxel.mouse_x
        self.velocity = prevx - self.x # TODO: this only modifies by ints?
    
    def draw(self):
        x1 = self.x - self.length/2.
        x2 = self.x + self.length/2.
        y1 = self.y
        y2 = self.y + self.width
        pyxel.rect(x1, y1, x2, y2, 7)

class BrickBall:
    def __init__(self, board, paddle, x, y, size, col, shadow=False, velvector=False):
        self.board = board
        self.paddle = paddle
        self.x = x
        self.y = y
        self.size = size
        self.col = col
        self.velocity = [0.*SPEED,1.*SPEED] # initial velocity
        self.shadow = shadow # draw shadow?
        self.velvector = velvector
    
    def update(self):
        paddlehit = False
        paddlehit, self.x, self.y, self.velocity = self.paddle.moveball(self.x, self.y, 
                self.velocity, self.size)
        brickhit = False
        for brick in self.board.bricks.bricks:
            brickhit, self.x, self.y, self.velocity = brick.moveball(self.x, self.y, 
                    self.velocity, self.size)
            if brickhit: break
        if not paddlehit and not brickhit:
            wallhit, self.x, self.y, self.velocity = self.board.moveball(self.x, self.y, 
                    self.velocity, self.size)
        

    def draw(self):
        pyxel.circ(self.x, self.y, self.size/2., col=self.col)
        if self.velvector:
            pyxel.line(self.x, self.y, self.x + self.velocity[0], self.y + self.velocity[1], 9)

class BrickArray:
    """
    generates bricks as they fall
    """
    def __init__(self, board, x, y, nrow, ncol, brickheight,brickwidth, spacing=0):
        self.bricks = []
        arraywidth = brickwidth*ncol + spacing*(ncol-1)
        arrayheight = brickheight*nrow + spacing*(nrow-1)
        for i in range(nrow):
            y_row = y - arrayheight/2. + i*(brickheight+spacing) + brickheight/2.
            for j in range(ncol):
                x_col = x - arraywidth/2. + j*(brickwidth+spacing) + brickwidth/2.
                print("new brick at %d x %d" % (x_col, y_row))
                self.bricks.append(BrickBrick(board,x_col,y_row,brickheight,brickwidth,8))
    
    def update(self):
        for brick in self.bricks:
            brick.update()
            if brick.delete:
                self.bricks.remove(brick)
    def draw(self):
        for brick in self.bricks:
            brick.draw()

class BrickBrick:
    """
    represents individual brick
    """
    def __init__(self, board, x, y, height, width, col, shadow=True):
        self.board = board
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.col = col
        self.shadow = shadow
        self.delete = False

    def moveball(self, bx, by, bvel, bsize):
        # get brick dimensions
        x1 = self.x - self.width/2. - bsize
        x2 = self.x + self.width/2. + bsize
        y1 = self.y - self.height/2. - bsize
        y2 = self.y + self.height/2. + bsize
        xunlimited, yunlimited = bx + bvel[0], by + bvel[1]
        if not self.delete and x1 < xunlimited < x2 and y1 < yunlimited < y2:
            newy = yunlimited
            newx = xunlimited
            if by <= y1: # from top
                newy = by - (yunlimited - y1)
                bvel[1] *= -1
            elif by >= y2: # from bottom
                newy = by + (yunlimited - y2)
                bvel[1] *= -1
            elif bx <= x1: # from left
                newx = bx - (xunlimited - x1)
                bvel[0] *= -1
            elif bx >= x2: # from y
                newx = bx + (xunlimited - x2)
                bvel[0] *= -1
            self.delete = True
            return(True, xunlimited, newy, bvel) 
        else:
            return (False, bx, by, bvel)

    def draw(self):
        if not self.delete:
            x1 = self.x - self.width/2.
            x2 = self.x + self.width/2.
            y1 = self.y - self.height/2.
            y2 = self.y + self.height/2.
            if self.shadow:
                pyxel.rect(x1 + 1, y1 + 1, x2 + 1, y2 + 1, 5)
            pyxel.rect(x1, y1, x2, y2, self.col)

    def update(self):
        pass


BrickGame()


""" todo:
- fix velocities to floats
- bricks advance slowly, lose life when bricks reach bottom
- new bricks added randomly to top
- set background pattern(s) from buffer
- brick patterns in buffer
- score = 1pt per brick
- color bricks - multiplier for each additional one of same color hit in a row. first is 1pts, second is 2pts, 3rd is 3pts...
- introduce special bricks over time
double/triple hit brick
stealth brick - disappear after a few rows
flashlight brick - briefly reveal stealth bricks
ball spawn brick - creates second ball w yvel=1
hot brick - speed up ball in y dir
cold brick - slow ball in y dir
rachet brick - speed advance briefly
pause advance bricks
falling brick - drop when hit, need to catch w paddle or lose life
soft brick - don't bounce ball, just disappear
mystery brick - when hit convert to one of the above
extra life brick
paddle size +/- 5/10 temporarily
impossible brick - can't break, rare, lose life when it reaches bottom
gravity brick - causes ball to temporarily have acceleration towards bottom of screen


further todo: iterate through all objects to determine 
"""
