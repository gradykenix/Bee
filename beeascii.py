'''
A fan-made mod for ASCII Madness by Bee Jackson!
Open this file in the same directory as asciiMadness_v1.py and cmu_graphics.
Adds:
 - a few attacks
 - a bit of the Sans boss fight from Undertale
 - a few new powerups
 - some other things!
'''

import random
import math
import time
import os

#hide cursor
os.system("")
print("\x1b[?25l",end="\r")

#constants
WIDTH = 115
HEIGHT = 28

TEMPLATES = ['''  * 
,/ \\`
/###\\`
/###\\
  |''','''   ^
  /#\\
  /#\\
   |''']
ORNAMENTS = ['o','x','@','&','*',',','`']

colors = {"red": "\u001b[38;5;160m",
 "blue": "\u001b[38;5;20m",
 "white": "\u001b[38;5;15m",
 "yellow": "\u001b[38;5;220m",
 "green": "\u001b[38;5;34m"}

#get the file itself
f = open("asciiMadness_v1.py", "r")
beefile = f.read()
f.close()

#mod code
#for each attack mod, need to:
#  have a cursor class
#  have a spawnXAttack(app) function
#  put the above into spawnNewAttack DONE
#  move them in and out of the loadDesign list DONE

#bee avatar (non-optional because why not)

pos = beefile.index("checkHealthPackCollision(app)")
x = '''        if random.randint(1, 1000000) == 38:
            app.player.body = [[32, 46, 46, 44, 32], 
                        [42, 42, 38, 126, 126], 
                        [36, 64, 32, 46, 62], 
                        [96, 60, 126, 45, 62], 
                        [32, 124, 85, 32, 92], 
                        [47, 32, 42, 95, 46], 
                        [32, 32, 124, 124, 32]]
            spawnCodeBlock(app, "SURPRISE BEE JACKSON CAMEO :)")\n'''
beefile = beefile[:pos+30]+x+beefile[pos+30:]

#cursor classes
pos = beefile.index("class arcCursor")
beefile = beefile[:pos]+'''
class flower(cursor):
  def __init__(self, app, cnx, cny, dx, dy, rot, angle):
    self.lifeSpan = 120*slowdownFactor
    self.cnx = cnx
    self.cny = cny
    self.dx = dx/slowdownFactor
    self.dy = dy/slowdownFactor
    self.rot = rot/slowdownFactor
    self.angle = angle
    self.cx = self.cnx + 10*math.cos(toRad(self.angle))
    self.cy = self.cny + 10*math.sin(toRad(self.angle))

  def updateAngle(self, app):
    self.angle += self.rot
  
  def move(self):
    self.cnx += self.dx
    self.cny += self.dy
    self.cx = self.cnx + 15*math.cos(toRad(self.angle))
    self.cy = self.cny + 15*math.sin(toRad(self.angle))

  def draw(self):
    drawRegularPolygon(self.cx, self.cy, 7, 3, fill="white", rotateAngle = self.angle-30)
    drawRect((3*self.cx+self.cnx)/4, (3*self.cy+self.cny)/4, 3, 15, fill="white", align = "center", rotateAngle = self.angle-270)

class barrage(cursor):
  def __init__(self, app, x, y, speed, colour):
    self.speed = speed/slowdownFactor
    self.cx = x
    self.cy = y
    self.colour = colour
    self.lifeSpan = 120*slowdownFactor
    self.isAlive = (self.colour == "red")

  def updateAngle(self, app):
    pass
    
  def move(self):
    self.cy += self.speed
    if self.lifeSpan <= 70 and 0 >= self.cy >= -550:
       self.cy += 650
       self.isAlive = True
    if self.cy >= 650:
       self.isAlive = False

  def draw(self):
    if self.isAlive:
        drawRegularPolygon(self.cx, self.cy, 7, 3, fill=self.colour, rotateAngle = 180)
        drawRect(self.cx, self.cy-1, 3, 15, fill=self.colour, align = "center", rotateAngle = 180)

class spray(cursor):
    def __init__(self, app, cx, cy, cnx, cny):
      self.cx = cx
      self.cy = cy
      self.cny = cny
      self.cnx = cnx
      self.dx = self.cnx-self.cx
      self.dy = self.cny-self.cy
      q = (self.dx**2 + self.dy**2)**0.5
      self.dx, self.dy = self.dx/q, self.dy/q
      self.dx, self.dy = self.dx*8/slowdownFactor, self.dy*8/slowdownFactor
      self.angle = getAngle(self.cx, self.cy, self.cnx, self.cny)
      self.isAlive = False
      self.lifeSpan = 320*slowdownFactor
      self.leftBound = app.terminalLeft+20
      self.rightBound = app.terminalLeft + app.terminalWidth-20
      self.topBound = app.terminalTop+20
      self.bottomBound = app.terminalTop + app.terminalHeight-20
    
    def updateAngle(self, app):
      pass
    
    def move(self):
      if (self.topBound <= self.cy <= self.bottomBound) and (self.leftBound <= self.cx <= self.rightBound):
        self.isAlive = True
      else:
        self.isAlive = False
      self.cx += self.dx
      self.cy += self.dy
    
    def draw(self):
      if self.isAlive:
        drawRegularPolygon(self.cx, self.cy, 7, 3, fill = 'white', rotateAngle = 90-self.angle)
        drawRect(self.cx-5*self.dx/14, self.cy-5*self.dy/14, 3, 15, fill = 'white', 
                 align = 'center', rotateAngle = 90-self.angle)
    
class bone:
    def __init__(self, app, cx, cy, height, riseTime, moveTime, speed, fallTime, wall):
        self.height = height
        self.speed = speed
        self.cx = cx
        self.cy = cy
        self.riseTime = riseTime
        self.moveTime = moveTime
        self.fallTime = fallTime
        self.wall = wall
        self.wallVal = app.playerBoundTop if wall == "ceiling" else app.playerBoundBottom
        self.endWall = app.playerBoundRight
        self.age = 0
        self.exposureHeight = self.cy + self.height - self.wallVal if wall == "floor" else self.wallVal - self.cy
    
    def move(self, app):
        if self.cx < self.endWall:
            if 0 <= self.age < self.riseTime:
                if self.wall == "ceiling":
                    self.cy += self.exposureHeight / self.riseTime
                    if self.cy + self.height > self.wallVal:
                        for i in range(int((self.cy + self.height - self.wallVal)//18) + 1):
                            app.cursors += [cursor(app, self.cx, self.cy + self.height - 18*i, 0, 0, 0, 0)]
                else:
                    self.cy -= self.exposureHeight / self.riseTime
                    if self.cy < self.wallVal:
                        for i in range(int((self.wallVal-self.cy)//18) + 1):
                            app.cursors += [cursor(app, self.cx, self.cy + 18*i, 0, 0, 0, 0)]

            elif self.riseTime <= self.age < self.riseTime + self.moveTime:
                self.cx += self.speed
                for i in range(int(self.height // 18) + 1):
                    if self.wall == "ceiling":
                        app.cursors += [cursor(app, self.cx, self.cy + self.height - 18*i, 0, 0, 0, 0)]
                    else:
                        app.cursors += [cursor(app, self.cx, self.cy + 18*i, 0, 0, 0, 0)]

            elif self.riseTime + self.moveTime <= self.age < self.riseTime + self.moveTime + self.fallTime:
                if self.wall == "ceiling":
                    self.cy -= self.exposureHeight / self.fallTime
                    if self.cy + self.height > self.wallVal:
                        for i in range(int((self.cy + self.height - self.wallVal)//18) + 1):
                            app.cursors += [cursor(app, self.cx, self.cy + self.height - 18*i, 0, 0, 0, 0)]
                else:
                    self.cy += self.exposureHeight / self.fallTime
                    if self.cy < self.wallVal:
                        for i in range(int((self.wallVal-self.cy)//18) + 1):
                            app.cursors += [cursor(app, self.cx, self.cy + 18*i, 0, 0, 0, 0)]
        self.age += 1

    def draw(self, app):
        pass        

class bidenCursor(cursor):
    def __init__(self, cx, cy, angle):
        self.cx = cx
        self.cy = cy
        self.lifeSpan = 2
        self.dx = math.cos(toRad(angle))
        self.dy = math.sin(toRad(angle))
        self.angle = angle
    
    def updateAngle(self, app):
        pass
    
    def move(self):
        self.cx += self.dx
        self.cy += self.dy
    
    def draw(self):
        drawRegularPolygon(self.cx, self.cy, 7, 3, fill = 'white', rotateAngle = 90-self.angle)
        drawRect(self.cx-5*self.dx/14, self.cy-5*self.dy/14, 3, 15, fill = 'white', 
                 align = 'center', rotateAngle = 90-self.angle)

class BIDEN_BLAST:
    def __init__(self, app, cx, cy, angle, width):
        self.speed = 5
        self.cx = cx
        self.cy = cy
        self.age = 0
        self.finalAngle = angle
        self.curAngle = 0
        self.bounds = [(app.playerBoundLeft, app.playerBoundRight), (app.playerBoundTop, app.playerBoundBottom)]
        self.width = width
    
    def move(self, app):
        if 0 <= self.age < 10:
            self.curAngle += self.finalAngle / 10
        elif 10 <= self.age < 30:
            dx, dy = 20*math.cos(toRad(self.finalAngle)), 20*math.sin(toRad(self.finalAngle))
            px, py = 12*dy/20, -12*dx/20
            x, y = self.cx+12*random.random(), self.cy+12*random.random()
            while not ((self.bounds[0][0] <= x <= self.bounds[0][1]) and (self.bounds[1][0] <= y <= self.bounds[1][1])):
                c = random.random()
                x, y = x + c*dx, y + c*dy
            while ((self.bounds[0][0] <= x <= self.bounds[0][1]) and (self.bounds[1][0] <= y <= self.bounds[1][1])):
                app.cursors += [bidenCursor(x+i*px, y+i*py, self.finalAngle) for i in range(-self.width//2, self.width//2 + 1)]
                x, y = x + dx, y + dy
            
    def draw(self):
        pass
                
    
    

'''+beefile[pos:]

#spawnXAttack
pos = beefile.index("def spawnPipAttack(app)")
beefile = beefile[:pos]+'''

def spawnSansAttack(app):
    global gravity
    if app.sansStep == 54:
        #get new bones
        for i in range(22):
            app.bones += [bone(app, app.playerBoundLeft + i*15, app.playerBoundBottom + 95, 95, 10, 30, 0, 10, "floor")]
    elif 55 <= app.sansStep < 105:
        new_bones = []
        app.cursors = []
        for bono in app.bones:
            bono.move(app)
            if bono.age < bono.riseTime + bono.moveTime + bono.fallTime:
                new_bones += [bono]
        app.bones = new_bones[:]
    if app.sansStep == 105:
        #get new bones
        for i in range(12):
            shft = 20*math.cos(toRad(i*200/6))
            app.bones += [bone(app, app.playerBoundLeft + i*15 - 200, app.playerBoundTop - 65, 45+shft, 10, 70, 10, 10, "ceiling")]
            app.bones += [bone(app, app.playerBoundLeft + i*15 - 200, app.playerBoundBottom + 95, 105-shft, 10, 70, 10, 10, "floor")]
    elif 116 <= app.sansStep < 206:
        new_bones = []
        app.cursors = []
        for bono in app.bones:
            bono.move(app)
            if bono.age < bono.riseTime + bono.moveTime + bono.fallTime:
                new_bones += [bono]
        app.bones = new_bones[:]
    elif app.sansStep == 206:
        bidenBlaster1 = BIDEN_BLAST(app, app.playerBoundLeft + 40, app.playerBoundTop - 40, 90, 3)
        bidenBlaster2 = BIDEN_BLAST(app, app.playerBoundLeft - 40, app.playerBoundTop + 30, 0, 3)
        bidenBlaster3 = BIDEN_BLAST(app, app.playerBoundRight + 40, app.playerBoundBottom - 40, 180, 3)
        bidenBlaster4 = BIDEN_BLAST(app, app.playerBoundRight - 40, app.playerBoundBottom + 40, 270, 3)
        app.BIDEN_BLASTERS = [bidenBlaster1, bidenBlaster2, bidenBlaster3, bidenBlaster4]
    elif 206 <= app.sansStep < 236:
        new_bbs = []
        for bb in app.BIDEN_BLASTERS:
            bb.move(app)
            bb.age += 1
            if bb.age < 30:
                new_bbs += [bb]
        app.BIDEN_BLASTERS = new_bbs[:]
    elif app.sansStep == 239:
        bidenBlaster1 = BIDEN_BLAST(app, app.playerBoundLeft - 40, app.playerBoundTop - 40, 45, 3)
        bidenBlaster2 = BIDEN_BLAST(app, app.playerBoundRight + 40, app.playerBoundTop - 40, 135, 3)
        app.BIDEN_BLASTERS = [bidenBlaster1, bidenBlaster2]
    elif 240 <= app.sansStep < 270:
        new_bbs = []
        for bb in app.BIDEN_BLASTERS:
            bb.move(app)
            bb.age += 1
            if bb.age < 30:
                new_bbs += [bb]
        app.BIDEN_BLASTERS = new_bbs[:]
    elif app.sansStep == 273:
        bidenBlaster1 = BIDEN_BLAST(app, app.playerBoundLeft + 40, app.playerBoundTop - 40, 90, 3)
        bidenBlaster2 = BIDEN_BLAST(app, app.playerBoundLeft - 40, app.playerBoundTop + 30, 0, 3)
        bidenBlaster3 = BIDEN_BLAST(app, app.playerBoundRight + 40, app.playerBoundBottom - 40, 180, 3)
        bidenBlaster4 = BIDEN_BLAST(app, app.playerBoundRight - 40, app.playerBoundBottom + 40, 270, 3)
        app.BIDEN_BLASTERS = [bidenBlaster1, bidenBlaster2, bidenBlaster3, bidenBlaster4]
    elif 274 <= app.sansStep < 304:
        new_bbs = []
        for bb in app.BIDEN_BLASTERS:
            bb.move(app)
            bb.age += 1
            if bb.age < 30:
                new_bbs += [bb]
        app.BIDEN_BLASTERS = new_bbs[:]
    elif app.sansStep == 307:
        bidenBlaster1 = BIDEN_BLAST(app, app.playerBoundLeft - 40, 0.5*app.playerBoundTop + 0.5*app.playerBoundBottom, 0, 7)
        bidenBlaster2 = BIDEN_BLAST(app, app.playerBoundRight + 40, 0.5*app.playerBoundTop + 0.5*app.playerBoundBottom, 180, 7)
        app.BIDEN_BLASTERS = [bidenBlaster1, bidenBlaster2]
    elif 308 <= app.sansStep < 338:
        new_bbs = []
        for bb in app.BIDEN_BLASTERS:
            bb.move(app)
            bb.age += 1
            if bb.age < 30:
                new_bbs += [bb]
        app.BIDEN_BLASTERS = new_bbs[:]
    elif app.sansStep >= 338:
        app.BIDEN_BLASTERS = []
        spawnPowerUp(app, random.choice(['purple', 'green', 'blue']))

def spawnTreeAttack(app):
    for i in range(20):
        cnx = random.randint(int(app.playerBoundLeft), int(app.playerBoundRight))
        cny = random.randint(0, 100)
        rot = random.random()
        speed = random.random()*15
        for x in range(5):
            newFlower = flower(app, cnx, cny, 0, speed, rot, (360/5)*x)
            app.cursors += [newFlower]

def spawnEraseAttack(app):
    x = random.randint(int(app.playerBoundLeft), int(app.playerBoundRight))
    warningShot = barrage(app, x, 0, 30, "red")
    app.cursors += [warningShot]
    for i in range(-2000, -100, 25):
        if i % 2:
            newEraser1 = barrage(app, x, i, 8, "white")
            app.cursors += [newEraser1]
        else:
            newEraser2 = barrage(app, x-15, i, 8, "white")
            newEraser3 = barrage(app, x+15, i, 8, "white")
            app.cursors += [newEraser2, newEraser3]
    x = random.randint(int(app.playerBoundLeft), int(app.playerBoundRight))
    warningShot = barrage(app, x, 0, 30, "red")
    app.cursors += [warningShot]
    for i in range(-2000, -100, 25):
        if i % 2:
            newEraser1 = barrage(app, x, i, 8, "white")
            app.cursors += [newEraser1]
        else:
            newEraser2 = barrage(app, x-15, i, 8, "white")
            newEraser3 = barrage(app, x+15, i, 8, "white")
            app.cursors += [newEraser2, newEraser3]

def spawnEchoAttack(app):
    x = random.randint(2, 5)
    if (x == 5):
        #central spray ordered
        n = 11
        r = 1
        for j in range(6):
          for i in range(1, n+1):
              theta = r/30 + 180 + i*180/(n+1)
              x, y = r*math.cos(toRad(theta)), r*math.sin(toRad(theta))
              r += 10
              newSpray = spray(app, 430+x, 100+y, 430, 100)
              app.cursors += [newSpray]

    elif (x == 4):
        #central spray random
        for i in range(75):
           newSpray = spray(app, random.randint(-130, 1030), random.randint(-400, 0), 430, 100)
           app.cursors += [newSpray]
    elif (x == 3):
        #left and right random
        for i in range(25):
           newSpray = spray(app, random.randint(-500, 30), random.randint(-400, 100), 30, 100)
           app.cursors += [newSpray]
        for i in range(25):
           newSpray = spray(app, random.randint(830, 1330), random.randint(-400, 100), 830, 100)
           app.cursors += [newSpray]
    elif (x == 2):
        #left and right ordered
        n = 5
        r = 1
        for j in range(3):
          for i in range(1, n+1):
              theta = r/30 + 180 + i*90/(n+1)
              x, y = r*math.cos(toRad(theta)), r*math.sin(toRad(theta))
              r += 30
              newSpray = spray(app, 30+x, 100+y, 30, 100)
              app.cursors += [newSpray]
        n = 5
        r = 1
        for j in range(6):
          for i in range(1, n+1):
              theta = r/30 + 270 + i*90/(n+1)
              x, y = r*math.cos(toRad(theta)), r*math.sin(toRad(theta))
              r += 30
              newSpray = spray(app, 830+x, 100+y, 830, 100)
              app.cursors += [newSpray]

def spawnCmdAttack(app):
    pass  
       
'''+beefile[pos:]
pos = beefile.index("currentCursor.draw()")
x = '''currentCursor.draw()
        if len(app.bones) != 0:
            for currentBone in app.bones:
                currentBone.draw(app)'''
beefile = beefile[:pos]+x+beefile[pos+20:]
#spawnNewAttack
pos = beefile.index("def spawnNewAttack")
attacks = "\n        elif string == 'tree':\n            spawnTreeAttack(app)"
attacks+= "\n        elif string == 'erase':\n            spawnEraseAttack(app)"
attacks+= "\n        elif string == 'echo':\n            spawnEchoAttack(app)"
attacks+= "\n        elif string == 'cmd':\n            spawnCmdAttack(app)"
attacks+= "\n        elif string == 'dir':\n            global flipped\n            flipped = True"
attacks+= "\n        elif string == 'mkdir':\n            global gravity\n            gravity = 5"
attacks+= "\n        elif string == 'sans':\n            global sans\n            sans = True"
beefile = beefile[:pos+92]+attacks+beefile[pos+92:]

#sans modification of onStep
pos = beefile.index("import random")
x = '''import random
sans = False'''
beefile = beefile[:pos]+x+beefile[pos+13:]
pos = beefile.index("managePowerUpsSpawning(app)")
x = '''managePowerUpsSpawning(app)
            if sans:
                spawnSansAttack(app)
                app.sansStep += 1'''
beefile = beefile[:pos]+x+beefile[pos+27:]
pos = beefile.index("app.points = 0")
x = '''app.points = 0
    app.sansStep = 0
    app.bones = []
    app.BIDEN_BLASTERS = []'''
beefile = beefile[:pos]+x+beefile[pos+14:]
pos = beefile.index("drawBorder(app)")
x = '''drawBorder(app)
        for bb in app.BIDEN_BLASTERS:
            drawRegularPolygon(bb.cx, bb.cy, 20, 3, fill="white", rotateAngle = bb.curAngle+90)\n'''
beefile = beefile[:pos]+x+beefile[pos+15:]

#now he struggles against the syrupy grasp of matter
pos = beefile.index("removeCodeBlocks(app)")
x = '''removeCodeBlocks(app)
        global gravity
        gravity = "mkdir" in [q.string for q in app.codeBlocks]\n'''
beefile = beefile[:pos]+x+beefile[pos+21:]
pos = beefile.index("import random")
x = '''import random
gravity = 0'''
beefile = beefile[:pos]+x+beefile[pos+13:]
pos = beefile.index("animateWalk(app)\n")
x = '''animateWalk(app)
        if gravity:
            app.player.cy += gravity
            while not spriteIsLegal(app):
                app.player.cy -= 1\n'''
beefile = beefile[:pos]+x+beefile[pos+17:]

#now he moonwalks
pos = beefile.index("if 'a' in keys:")
x = '''if 'a' in keys:
            app.sidePressed = True
            app.player.move(app, 0, 1 if flipped else -1)
        if 'd' in keys:
            app.sidePressed = True
            app.player.move(app, 0, -1 if flipped else 1)
        if 's' in keys:
            app.verticalPressed = True
            app.player.dy = -1 if flipped else 1
            app.player.move(app, app.player.dy, 0)
        if 'w' in keys:
            app.verticalPressed = True
            app.player.dy = 1 if flipped else -1
            app.player.move(app, app.player.dy, 0)'''
beefile = beefile[:pos]+x+beefile[pos+454:]
pos = beefile.index("import random")
x = '''import random
flipped = False'''
beefile = beefile[:pos]+x+beefile[pos+13:]
beefile.index("import random")
pos = beefile.index("removeCodeBlocks(app)")
x = '''removeCodeBlocks(app)
        global flipped
        flipped = "dir" in [q.string for q in app.codeBlocks]\n'''
beefile = beefile[:pos]+x+beefile[pos+21:]
#powerups: static modify revertBuff and addBuff

#revertBuff
pos = beefile.index("self.dashLength /= 2\n")
x = "        if buff == 'lightCoral':\n            self.shooting = False\n"
x+= "        global slowdownFactor\n"
x+= '''        if buff == 'mediumAquamarine':
            for currentCursor in app.cursors:
              currentCursor.lifeSpan /= slowdownFactor
              try:
                currentCursor.accelerationx *= slowdownFactor**2
                currentCursor.accelerationy *= slowdownFactor**2
              except AttributeError:
                pass
              try:
                currentCursor.dx *= slowdownFactor
                currentCursor.dy *= slowdownFactor
              except AttributeError:
                pass
              try:
                currentCursor.speed *= slowdownFactor
              except AttributeError:
                pass
            slowdownFactor = 1\n'''
x+= "        if buff == 'aqua':\n            self.invincible = False\n"
x+= "        if buff == 'white':\n            self.tripping = False\n"
beefile = beefile[:pos+21]+x+beefile[pos+21:]

#addBuff
pos = beefile.index("self.dashLength *= 2\n")
x = '''            if name == 'lightCoral':
                self.shooting = True
            global slowdownFactor
            if name == 'mediumAquamarine':
                slowdownFactor = 3
                for currentCursor in app.cursors:
                  currentCursor.lifeSpan *= slowdownFactor
                  try:
                    currentCursor.accelerationx /= slowdownFactor**2
                    currentCursor.accelerationy /= slowdownFactor**2
                  except AttributeError:
                    pass
                  try:
                    currentCursor.dx /= slowdownFactor
                    currentCursor.dy /= slowdownFactor
                  except AttributeError:
                    pass
                  try:
                    currentCursor.speed /= slowdownFactor
                  except AttributeError:
                    pass
            if name == 'aqua':
                self.invincible = True
            if name == 'white':
                self.tripping = True\n'''
beefile = beefile[:pos+21]+x+beefile[pos+21:]

#slowdown of time
def egg(codeString, suffix):
    global beefile
    pos = beefile.index(codeString)
    beefile = beefile[:pos]+codeString+suffix+beefile[pos+len(codeString):]

pos = beefile.index("import random")
beefile = beefile[:pos+14]+"slowdownFactor = 1\n"+beefile[pos+14:]
egg("app.player.decayBuffs(","app")
egg("def decayBuffs(self",", app")
egg("self.revertBuff(buff", ", app")
egg("def revertBuff(self, buff", ", app")
egg("self.speed = speed", "/slowdownFactor")
egg("self.lifeSpan = 120", "*slowdownFactor")
pos = beefile.index("self.lifeSpan = 120")
ipos= beefile[pos+1:].index("self.lifeSpan = 120")
beefile = beefile[:pos+1+ipos]+"self.lifeSpan = 120*slowdownFactor"+beefile[pos+ipos+20:]
pos = beefile.index("class cursor:")
ipos= beefile[pos:].index("self.dx = dx")
beefile = beefile[:pos+ipos]+"self.dx = dx/slowdownFactor"+beefile[pos+ipos+12:]
ipos= beefile[pos:].index("self.dy = dy")
beefile = beefile[:pos+ipos]+"self.dy = dy/slowdownFactor"+beefile[pos+ipos+12:]
egg("self.accelerationx = accelerationx", "/(slowdownFactor**2)")
egg("self.accelerationy = accelerationy", "/(slowdownFactor**2)")
pos = beefile.index("class zigZagCursor(cursor):")
ipos= beefile[pos:].index("self.dx = dx")
beefile = beefile[:pos+ipos]+"self.dx = dx/slowdownFactor"+beefile[pos+ipos+12:]
ipos= beefile[pos:].index("self.dy = dy")
beefile = beefile[:pos+ipos]+"self.dy = dy/slowdownFactor"+beefile[pos+ipos+12:]

#invincibility
pos = beefile.index("32)")
beefile = beefile[:pos+3]+" if not self.invincible else self.body[row][col]"+beefile[pos+3:]
pos = beefile.index("self.isDead = False\n")
beefile = beefile[:pos]+"self.invincible = False\n        "+beefile[pos:]

#give him a glock
pos = beefile.index("import random")
x = '''import random
reloadTime = 0'''
beefile = beefile[:pos]+x+beefile[pos+13:]
#ADD app.bullets
pos = beefile.index('self.typed = True')+19
x = '''
class bullet:
    def __init__(self, x, y, dx, dy):
        self.blink = True
        self.lifeSpan = 80
        self.cx = x
        self.cy = y
        self.dx = dx
        self.dy = dy
        self.radius = 4*(random.random()+0.5)
    
    def move(self):
        self.dx *= 0.98
        self.dy *= 0.98
        self.cx += self.dx
        self.cy += self.dy
        if self.lifeSpan < 40:
            self.blink = (self.lifeSpan % 4) < 2
    
    def draw(self):
        if self.blink:
            drawCircle(self.cx, self.cy, self.radius, fill="white")'''
beefile = beefile[:pos]+x+beefile[pos:]
pos = beefile.index("def checkPlayerAttackCollision(app):")
x = '''def checkPlayerAttackCollision(app):
    i = 0
    if not app.player.shooting:
      rows, cols = len(app.player.body), len(app.player.body[0])
      playerWidth, playerHeight = cols * app.cellSize, rows * app.cellSize
      while i < len(app.blockChars):
          char = app.blockChars[i]
          angle = getAngle(app.player.cx, app.player.cy, char.cx, char.cy)
          attackRadius = getEllipseRadius(playerWidth/2, playerHeight/2, angle)
          distanceFromPlayer = distance(char.cx, char.cy, 
                                        app.player.cx, app.player.cy)
          lesserBoundaryAngle = (app.player.attackAngle - 
                                          (app.sweepConeWidth+20))
          greaterBoundaryAngle = (app.player.attackAngle + 
                                          (app.sweepConeWidth +20))
          if (isInCounterClockWiseOrder(lesserBoundaryAngle, 
                                        angle, greaterBoundaryAngle) and 
                  distanceFromPlayer < attackRadius + app.attackOffset):
              app.blockChars.pop(i)
          else:
              i += 1
    else:
      while i < len(app.blockChars):
          char = app.blockChars[i]
          got_him = False
          for bt in app.player.bullets:
              if distance(char.cx, char.cy, bt.cx, bt.cy) < 3*bt.radius:
                app.blockChars.pop(i)
                got_him = True
                break
          if not got_him:
              i += 1'''
beefile = beefile[:pos]+x+beefile[pos+1042:]
pos = beefile.index("def animateAttack(self, app):")
x = '''def animateAttack(self, app):
        if not self.shooting:
            sweepConeWidth = app.sweepConeWidth
            if app.attackCounter == 0:
                self.startAngle = self.attackAngle-(sweepConeWidth/2) + 10
                self.sweepAngle = sweepConeWidth
            elif 4 > app.attackCounter >= 3:
                self.startAngle = self.attackAngle-(sweepConeWidth/2)
                self.sweepAngle = sweepConeWidth/1.9
            elif 6 > app.attackCounter >= 4:
                self.startAngle = self.attackAngle-(sweepConeWidth/2)
                self.sweepAngle = sweepConeWidth/2.7
            app.attackCounter += 1
            if app.attackCounter >= 6:
                self.isAttacking = False
                app.attackCounter = 0
        else:
            if self.reloadTime == 18:
                gunx = self.cx + 20*math.cos(toRad(360-self.attackAngle))
                guny = self.cy + 20*math.sin(toRad(360-self.attackAngle))
                kx, ky = 2*gunx - self.cx, 2*guny - self.cy
                for i in range(random.randint(5, 8)):
                    bx = kx + random.randint(-6, 6)
                    by = ky + random.randint(-6, 6)
                    newBullet = bullet(bx, by, 15*math.cos(toRad(180-getAngle(bx, by, gunx, guny))), 15*math.sin(toRad(180-getAngle(bx, by, gunx, guny))))
                    self.bullets.append(newBullet)
            bulletsNew = []
            for bt in self.bullets:
                bt.move()
                bt.lifeSpan -= 1
                if bt.lifeSpan > 0:
                    bulletsNew += [bt]
            self.bullets = bulletsNew[:]
            if not len(self.bullets):
                self.isAttacking = False
                         
'''
beefile = beefile[:pos]+x+beefile[pos+673:]
pos = beefile.index("def drawAttack(self, app):")
x = '''def drawAttack(self, app):
        if not self.shooting:
            rows, cols = len(app.player.body), len(app.player.body[0])
            playerWidth, playerHeight = cols * app.cellSize, rows * app.cellSize
            offset = app.attackOffset 
            attackHeight = playerHeight + offset
            attackWidth = playerWidth + offset
            if app.attackCounter > 0:
                drawArc(self.cx, self.cy, attackWidth, attackHeight, 
                        self.startAngle, self.sweepAngle, fill = 'white')
                drawOval(self.cx, self.cy, playerWidth + 35, playerHeight + 35)
        else:
            for bullet in self.bullets:
                bullet.draw()'''
beefile = beefile[:pos]+x+beefile[pos+539:]

pos = beefile.index("self.attackAngle = 0\n")
x = '''self.attackAngle = 0
        self.bullets = []
        self.reloadTime = 0
        self.shooting = False'''
beefile = beefile[:pos]+x+beefile[pos+21:]

pos = beefile.index("removeCodeBlocks(app)\n")
x = '''removeCodeBlocks(app)
        app.player.reloadTime -= 1\n'''
beefile = beefile[:pos]+x+beefile[pos+22:]

pos = beefile.index("def attack(self, mouseX, mouseY):")
x = '''def attack(self, mouseX, mouseY):
        self.reloadTime = 18
        self.attackAngle = getAngle(self.cx, self.cy, mouseX, mouseY)
        self.isAttacking = True'''
beefile = beefile[:pos]+x+beefile[pos+33:]

#checkPlayerAttackCollision, animateAttack, attack class, app.player.bullets, reloadTime, app.player.shooting
#mod switches in loadDesign
def flowers(tf):
    global beefile
    if tf:
        pos = beefile.index("'codeBlocks':")
        ipos= beefile[pos:].index("]")
        beefile = beefile[:pos+ipos]+", 'tree'"+beefile[pos+ipos:]
    else:
        pos = beefile.index(", 'tree'")
        beefile = beefile[:pos]+beefile[pos+8:]

def beams(tf):
    global beefile
    if tf:
        pos = beefile.index("'codeBlocks':")
        ipos= beefile[pos:].index("]")
        beefile = beefile[:pos+ipos]+", 'erase'"+beefile[pos+ipos:]
    else:
        pos = beefile.index(", 'erase'")
        beefile = beefile[:pos]+beefile[pos+9:]

def bursts(tf):
    global beefile
    if tf:
        pos = beefile.index("'codeBlocks':")
        ipos= beefile[pos:].index("]")
        beefile = beefile[:pos+ipos]+", 'echo'"+beefile[pos+ipos:]
    else:
        pos = beefile.index(", 'echo'")
        beefile = beefile[:pos]+beefile[pos+8:]

def blur(tf):
    global beefile
    print("This one's still under construction!")
    '''
    if tf:
        pos = beefile.index("'codeBlocks':")
        ipos= beefile[pos:].index("]")
        beefile = beefile[:pos+ipos]+", 'cmd'"+beefile[pos+ipos:]
    else:
        pos = beefile.index(", 'cmd'")
        beefile = beefile[:pos]+beefile[pos+7:]'''

def topsyturvy(tf):
    global beefile
    if tf:
        pos = beefile.index("'codeBlocks':")
        ipos= beefile[pos:].index("]")
        beefile = beefile[:pos+ipos]+", 'dir'"+beefile[pos+ipos:]
    else:
        pos = beefile.index(", 'dir'")
        beefile = beefile[:pos]+beefile[pos+7:]

def gravity(tf):
    global beefile
    if tf:
        pos = beefile.index("'codeBlocks':")
        ipos= beefile[pos:].index("]")
        beefile = beefile[:pos+ipos]+", 'mkdir'"+beefile[pos+ipos:]
    else:
        pos = beefile.index(", 'mkdir'")
        beefile = beefile[:pos]+beefile[pos+9:]

#mod switches in managePowerUpsSpawning
def shotgun(tf):
    global beefile
    if tf:
        pos = beefile.index("color = random.choice")
        ipos = beefile[pos:].index("]")
        beefile = beefile[:pos+ipos]+", 'lightCoral'"+beefile[pos+ipos:]
    else:
        pos = beefile.index(", 'lightCoral'")
        beefile = beefile[:pos]+beefile[pos+14:]
  
def timeslow(tf):
    global beefile
    if tf:
        pos = beefile.index("color = random.choice")
        ipos = beefile[pos:].index("]")
        beefile = beefile[:pos+ipos]+", 'mediumAquamarine'"+beefile[pos+ipos:]
    else:
        pos = beefile.index(", 'mediumAquamarine'")
        beefile = beefile[:pos]+beefile[pos+20:]

def invincible(tf):
    global beefile
    if tf:
        pos = beefile.index("color = random.choice")
        ipos = beefile[pos:].index("]")
        beefile = beefile[:pos+ipos]+", 'aqua'"+beefile[pos+ipos:]
    else:
        pos = beefile.index(", 'aqua'")
        beefile = beefile[:pos]+beefile[pos+8:]

def lsd(tf):
    global beefile
    print("This one's still under construction!")
    '''
    if tf:
        pos = beefile.index("color = random.choice")
        ipos = beefile[pos:].index("]")
        beefile = beefile[:pos+ipos]+", 'white'"+beefile[pos+ipos:]
    else:
        pos = beefile.index(", 'white'")
        beefile = beefile[:pos]+beefile[pos+9:]'''

def coolguy(tf):
    global beefile
    if tf:
        pos = beefile.index("'player': ")
        x = ''''player': [[32, 32, 95, 95, 32], 
                        [32, 95, 61, 61, 95], 
                        [32, 32, 124, 81, 62], 
                        [32, 32, 47, 32, 96], 
                        [32, 60, 42, 59, 92], 
                        [95, 45, 42, 95, 46], 
                        [32, 32, 124, 124, 32]]'''
        beefile = beefile[:pos]+x+beefile[pos+317:]
    else:
        pos = beefile.index("'player': ")
        x = ''''player': [[32, 32, 95, 95, 32], 
                        [32, 95, 61, 61, 95], 
                        [32, 32, 124, 46, 62], 
                        [32, 32, 47, 32, 96], 
                        [32, 60, 42, 59, 92], 
                        [95, 45, 42, 95, 46], 
                        [32, 32, 124, 124, 32]]'''
        beefile = beefile[:pos]+x+beefile[pos+317:]

def noEXIT(tf):
    global beefile
    if tf:
        pos = beefile.index("'codeBlocks':")
        ipos = beefile[pos:].index(", 'EXIT'")
        beefile = beefile[:pos+ipos]+beefile[pos+ipos+8:]
    else:
        pos = beefile.index("'codeBlocks':")
        ipos= beefile[pos:].index("]")
        beefile = beefile[:pos+ipos]+", 'EXIT'"+beefile[pos+ipos:]

def undertale(tf):
    global beefile
    if tf:
        pos = beefile.index("app.playerBoundLeft")
        x = '''app.playerBoundLeft = app.terminalLeft + 5*app.terminalWidth/15 + 40
    app.playerBoundTop = app.terminalTop + 5*app.terminalHeight/15 + 20
    app.playerBoundRight = app.playerBoundLeft + 200
    app.playerBoundBottom = app.playerBoundTop + 200\n'''
        beefile = beefile[:pos]+x+beefile[pos+365:]
        pos = beefile.index("'codeBlocks':")
        apos = beefile[pos:].index('[')+1
        bpos = beefile[pos:].index(']')
        beefile = beefile[:pos+apos]+'"sans"'+beefile[pos+bpos:]
        pos = beefile.index("def spawnCodeBlock")
        x = '''def spawnCodeBlock(app, string):
    cx = 440
    cy = 250
    app.codeBlocks += [codeBlock(app, cx, cy, string)]'''
        beefile = beefile[:pos]+x+beefile[pos+327:]
        pos = beefile.index("'player':")
        x = ''''player': [[66]]'''
        beefile = beefile[:pos]+x+beefile[pos+317:]
    else:
        pos = beefile.index("app.playerBoundLeft")
        x = '''app.playerBoundLeft = app.terminalLeft + app.terminalWidth/15
    app.playerBoundTop = app.terminalTop + app.terminalHeight/15
    app.playerBoundRight = (app.terminalLeft + app.terminalWidth 
                            - app.terminalWidth/15)
    app.playerBoundBottom = (app.terminalTop + app.terminalHeight 
                             - app.terminalHeight/15)'''
        beefile = beefile[:pos]+x+beefile[pos+247:]
        pos = beefile.index('def spawnCodeBlock')
        x = '''def spawnCodeBlock(app, string):
    cx = random.randint(rounded(app.playerBoundLeft + 10), 
                        rounded(app.playerBoundRight - 10))
    cy = random.randint(rounded(app.playerBoundTop + 10), 
                        rounded(app.playerBoundBottom - 10))
    app.codeBlocks += [codeBlock(app, cx, cy, string)]'''
        beefile = beefile[:pos]+x+beefile[pos+113:]
        pos = beefile.index("'player':")
        x = ''''player': [[32, 32, 95, 95, 32], 
                        [32, 95, 61, 61, 95], 
                        [32, 32, 124, 46, 62], 
                        [32, 32, 47, 32, 96], 
                        [32, 60, 42, 59, 92], 
                        [95, 45, 42, 95, 46], 
                        [32, 32, 124, 124, 32]]'''
        beefile = beefile[:pos]+x+beefile[pos+16:]
        
#implement choices
mods = ['n/a','flowers','beams','bursts','blur','topsyturvy','gravity','shotgun',
        'timeslow','invincible','lsd','coolguy','noEXIT','undertale']
toggle = dict([(i, False) for i in mods])
menu = '''/---------------------\\
|                     |
|  Select your mods!  |
|                     |
|  MOUSE ATTACKS      |
|   1 ) flowers       |
|   2 ) beams         |
|   3 ) bursts        |
|  NON-MOUSE ATTACKS  |
|   4 ) [---]         |
|   5 ) topsyturvy    |
|   6 ) gravity       |
|  POWERUPS           |
|   7 ) shotgun       |
|   8 ) timeslow      |
|   9 ) invincible    |
|   10 ) [---]        |
|  MISC               |
|   11 ) coolguy      |
|   12 ) no EXIT      |
|   13 ) undertale    |
|                     |
|  ALL DONE: press 0  |
|                     |
\\---------------------/'''

class Matrix:
    def __init__(self, width, height):
        self.grid = [[(' ', 'white') for i in range(width)] for i in range(height)]
        self.w = width
        self.h = height
    def insert(self, row, col, char, color):
        self.grid[row][col] = (char, color)
    def empty_col_check(self, col):
        for i in range(self.h):
            if self.grid[i][col][0] != ' ':
                return False
        return True
    def empty_row_check(self, row):
        for i in range(self.w):
            if self.grid[row][i][0] != ' ':
                return False
        return True
    def prune(self):
        while self.empty_row_check(0):
            self.h -= 1
            self.grid = self.grid[1:]
        while self.empty_row_check(self.h - 1):
            self.h -= 1
            self.grid = self.grid[:-1]
        while self.empty_col_check(0):
            self.w -= 1
            self.grid = [i[1:] for i in self.grid]
        while self.empty_col_check(self.w - 1):
            self.w -= 1
            self.grid = [i[:-1] for i in self.grid]
    def insertInto(self, other, row, col):
        for r in range(self.h):
            for c in range(self.w):
                try:
                    other.insert(r+row, c+col, self.grid[r][c][0], self.grid[r][c][1])
                except IndexError:
                    pass
    def display(self):
        print("\u001b[0;0H",end="")
        for row in self.grid:
            print("\u001b[2K", end="")
            for char, color in row:
                print(colors[color]+char,end="")
            print("|")

class Tree:
    def __init__(self):
        template = random.choice(TEMPLATES)
        self.grid = Matrix(len(template), len(template))
        for pos in range(len(template)):
            if template[pos] == '\n':
                continue
            if template[pos] == '#':
                template = template[:pos]+random.choice(ORNAMENTS+[' ']*10)+template[pos+1:]
                row = template[:pos].count('\n')
                column = template[:pos][::-1].index('\n')
                self.grid.insert(row, column, template[pos], 'red')
            else:
                row = template[:pos].count('\n')
                column = template[:pos][::-1].index('\n') if '\n' in template[:pos] else pos
                self.grid.insert(row, column, template[pos], 'green')
        self.grid.prune()
        for r in range(self.grid.h):
            for c in range(self.grid.w):
                if self.grid.grid[r][c][0] in ['`',',']:
                    self.grid.grid[r][c] = (self.grid.grid[r][c][0], random.choice(['yellow', 'blue']))

    def timestep(self):
        for r in range(self.grid.h):
            for c in range(self.grid.w):
                if self.grid.grid[r][c][0] in ['`',',']:
                    self.grid.grid[r][c] = (self.grid.grid[r][c][0], random.choice(['yellow', 'blue']))

MENU = Matrix(len(menu), len(menu))
for r in range(len(menu.split('\n'))):
    for c in range(len('|                     |')):
        MENU.insert(r, c, menu.split('\n')[r][c], 'white')

forest = []
for i in range(60):
    cx, cy = random.randint(0, WIDTH-7), random.randint(0, HEIGHT-7)
    forest += [(cx, cy, Tree())]

while True:
    screen = Matrix(WIDTH, HEIGHT)
    for cx, cy, tree in forest:
        tree.timestep()
        tree.grid.insertInto(screen, cy, cx)
    MENU.prune()
    MENU.insertInto(screen, 1, 13)
    screen.display()
    '''x = input('Response : ')
    try:
        x = int(x)
        if not (0 <= x <= 13):
            raise ValueError
    except ValueError:
        print('Invalid input! Only numbers 0-13 are allowed.')
        continue
    if (x == 0):
        break
    if toggle[mods[x]]:
        #mod is already active
        exec(mods[x]+'(False)')
    else:
        exec(mods[x]+'(True)')
    toggle[mods[x]] = not toggle[mods[x]]'''
    time.sleep(0.2)

#run the new file
exec(beefile)
