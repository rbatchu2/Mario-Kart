from cmu_112_graphics import *
import sys
import cv2,math,random,time,pygame
import mediapipe as mp
print(f'sudo "{sys.executable}" -m pip install pillow')
print(f'sudo "{sys.executable}" -m pip install requests')
#CITATIONS: 
#Sprites: http://www.mariouniverse.com/sprites-snes-smk/
#Sound: https://www.youtube.com/watch?v=RqbHKbIyC5o&ab_channel=TotallyFun
#Home Page Screen: https://tcrf.net/Mario_Kart_Wii
#Character Screen: https://www.joe.ie/gaming/mario-kart-character-ranking-personality-test-658579
#Bullet Bill: https://mariokart.fandom.com/wiki/Bullet_Bill
#Shells and Lightening Bolt: https://www.mariowiki.com/

#modified code from https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
#Plays mario kart theme song 
class Sound(object):
    def __init__(self, path):
        self.path = path
        self.loops = 1
        pygame.mixer.music.load(path)

    def isPlaying(self):
        return bool(pygame.mixer.music.get_busy())

    def start(self, loops=1):
        self.loops = loops
        pygame.mixer.music.play(loops=loops)

    def stop(self):
        pygame.mixer.music.stop()

def rgbString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

def appStarted(app):
    loadImages(app)
    initializeStartVariables(app)
    app.mode = "titleScreen"

#Function loads and scales all images needed to start the game 
def loadImages(app):
    app.image =  app.loadImage("titleScreen.jpeg")
    app.luigi = app.loadImage("luigiSpriteSheet.jpg")
    app.luigi = app.loadImage("luigiSpriteSheet.jpg")
    app.itemBox = app.loadImage("itemBox.jpg")
    app.itemBox = app.scaleImage(app.itemBox,1/15)
    app.straightLuigi = app.scaleImage(app.luigi, 1/2)
    app.luigi = app.straightLuigi 
    app.lightningBolt = app.loadImage("lightningBolt.png")
    app.lightningBolt = app.scaleImage(app.lightningBolt,1/15)
    app.bulletBill = app.loadImage("bulletBill.png")
    app.bulletBill = app.scaleImage(app.bulletBill, 1/12)
    app.banana = app.loadImage("banana.png")
    app.banana = app.scaleImage(app.banana, 1/30)
    app.leftMario = app.loadImage("leftMario.jpg")
    app.leftMario = app.scaleImage(app.leftMario, 2/3)
    app.rightMario = app.loadImage("rightMario.jpg")
    app.rightMario = app.scaleImage(app.rightMario, 2/3)
    app.leftLuigi = app.loadImage("leftLuigi.jpg")
    app.leftLuigi = app.scaleImage(app.leftLuigi,2/3)
    app.rightLuigi = app.loadImage("rightLuigi.jpg")
    app.rightLuigi = app.scaleImage(app.rightLuigi,2/3)
    app.bigGreenShell = app.loadImage("greenShell.jpg")
    app.bigGreenShell = app.scaleImage(app.bigGreenShell,1/15)
    app.greenShell = app.scaleImage(app.bigGreenShell, 1/4)
    app.redShell = app.loadImage("redshell.jpg")
    app.redShell = app.scaleImage(app.redShell,1/10)
    app.smallRedShell = app.scaleImage(app.redShell,1/4)

#Intitalizes all start variables 
def initializeStartVariables(app):
    app.startGame = False 
    app.cx,app.cy = 700,600 
    app.leftCornerX, app.leftCornerY = 800,app.height//4
    app.opponentCx, app.opponentCy = 615,600
    app.redShellCx, app.redShellCy = app.cx, app.cy - 50
    app.bananaCx, app.bananaCy = 0,0
    app.greenShellCx, app.greenShellCy = 0,0 
    app.itemBoxCx,app.itemBoxCy = 0,0
    app.opponentEnd = False 
    app.spawnABox = True 
    app.currentItem = "green shell"
    app.usePowerUp = False 
    app.redShellHeight = app.smallRedShell.size[1]
    app.hit = False 
    app.spawnABanana = True 
    pygame.mixer.init()
    app.sound = Sound("marioKartSong.mp3")
    app.sound.start(loops=-1)
    app.drawRedShell = False 
    app.delay = False
    app.keyBoard = False
    app.timerDelay = 50 
    app.amp,app.freq = 200,100
    app.startTimePlayer, app.startTimeOpponent = time.time(), time.time()
    app.endTimePlayer, app.endTimeOpponent = 0,0 
    app.counter = 1 
    app.drawOpponent = True
    app.fullOpponentEnd = True 
    app.start = 0
    app.opponentPowerUp = True 
    app.opponentItem = None 
    app.opponentShellCx,app.opponentShellCy = app.opponentCx,app.opponentCy+60 

#Draws the choose your control screen
def chooseYourControlScreen_redrawAll(app,canvas):
    canvas.create_rectangle(0,0,1280,720,fill = "black")
    canvas.create_text(640,50,text = "Choose your control", 
                       font="Times 40 bold", fill = "white")
    canvas.create_rectangle(100,100,500,620, fill = "red")
    canvas.create_rectangle(780,100,1180,620, fill = "red")
    canvas.create_text(300,360,text = "Keyboard", fill = "white", 
                       font = "Times 35 bold")
    canvas.create_text(980,360,text = "Using your hand!", fill = "white", 
                       font = "Times 35 bold")

#Based on user mouse press, determines whether user chose keyboard control 
#or hand detection control 
def chooseYourControlScreen_mousePressed(app,event): 
    x = event.x 
    y = event.y
    if(100 <= x <= 500 and 100 <= y <= 620):
        app.keyBoard = True 
        app.mode = "raceScreen"
    elif(780 <= x <= 1180 and 100 <= y <= 620):
        app.keyBoard = False 
        app.mode = "raceScreen"

#modified code from https://www.analyticsvidhya.com/blog/2021/07/building-a-hand-tracking-system-using-opencv/
def cameraControl(app):
    if(not app.keyBoard):
        app.cy -= 4
        cap = cv2.VideoCapture(0)
        mpHands = mp.solutions.hands
        hands = mpHands.Hands(static_image_mode=False,
                            max_num_hands=2,
                            min_detection_confidence=0.5,
                            min_tracking_confidence=0.5)
        mpDraw = mp.solutions.drawing_utils
        pTime = 0
        cTime = 0
        app.frame = cv2.resize(app.frame, (200,200)) 
        imgRGB = cv2.cvtColor(app.frame, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        landMarkList = []
        success, img = cap.read()
        if results.multi_hand_landmarks == None:
            app.image = app.mario
            app.usePowerUp = True  
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    landMarkList.append(lm)
                    h, w, c = img.shape
                    cx, cy = int(lm.x *w), int(lm.y*h)
                    if id ==0:
                        cv2.circle(img, (cx,cy), 3, (255,0,255), cv2.FILLED)
                    mpDraw.draw_landmarks(img, handLms,
                                           mpHands.HAND_CONNECTIONS)
            for element in str(landMarkList[8]).splitlines():
                if(element.startswith("x:")):
                    x = element[3:]
                    xPointEight = float(x)
            for element in str(landMarkList[5]).splitlines():
                if(element.startswith("x:")):
                    x = element[3:]
                    xPointFive = float(x)
            for element in str(landMarkList[9]).splitlines():
                if(element.startswith("x:")):
                    x = element[3:]
                    xPointNine = float(x)
            for element in str(landMarkList[12]).splitlines():
                if(element.startswith("x:")):
                    x = element[3:]
                    xPointTwelve = float(x)
            if(xPointEight > xPointFive and xPointTwelve > xPointNine):
                app.cx -= 5
                app.image = app.leftMario
            elif(xPointFive > xPointEight and xPointTwelve < xPointNine):
                app.cx += 5
                app.image = app.rightMario
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img,str(int(fps)), (10,70),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)

def raceScreen_cameraFired(app):
    cameraControl(app)

def raceScreenTwo_cameraFired(app):
    cameraControl(app)

#Starts the game if user presses a 
def titleScreen_keyPressed(app,event):
    if(event.key == "a"):
        app.mode = "characterChooseMode"
        app.image = app.loadImage("characters.jpg")

#Draws the title screen 
def titleScreen_redrawAll(app, canvas):
    canvas.create_image(640, 360, image=ImageTk.PhotoImage(app.image))

#Player chooses character based on the mouse press 
def characterChooseMode_mousePressed(app,event):
    row = 0 
    characters = [["Mario", "Luigi", "Peach", "Toad"], 
                 ["Yoshi", "Donkey Kong", "Wario", "Bowser"]]
    if(136<event.y<360):
        row = 0 
    else: row = 1 
    col = (event.x - 240)//200
    if(0<=col<4):
        characterSelected = characters[row][col]
        app.mode = "chooseYourControlScreen"
        if(characterSelected == "Mario"):
            app.mario = app.loadImage("marioSpriteSheet.jpg")
            app.mario = app.scaleImage(app.mario,1/2)
            app.image = app.loadImage("marioSpriteSheet.jpg")
        elif(characterSelected == "Luigi"):
            app.image = app.loadImage("luigiSpriteSheet.jpg")
        app.image = app.scaleImage(app.image, 1/2)

#Draws out the character choose mode 
def characterChooseMode_redrawAll(app,canvas):
    canvas.create_rectangle(0,0,1280,720, fill = "black")
    canvas.create_text(app.width/2, 30, text = "Choose Your Character Below",
                       fill = "white", font = "Times 35 bold")
    canvas.create_image(640, 360, image=ImageTk.PhotoImage(app.image))
    
#Randomly spawns a banana on the track 
def spawnBanana(app):
    cy = random.randint(app.height//4,720)
    leftBoundSlope = (app.height-app.height//4)/(700)
    leftBound  = int((app.height-cy)/leftBoundSlope)
    rightBoundSlope = (app.height-app.height//4)/(1280-900)
    rightBound = int(app.width - ((app.height - cy)/rightBoundSlope))
    cx = random.randint(leftBound+50,rightBound-50)
    cy = random.randint(app.height//4,720)
    return (cx,cy)

#Makes sure the shells don't travel off the track 
def checkShellBounds(app,cx,cy):
    leftBoundSlope = (app.height-app.height//4)/(700)
    leftBound  = int((app.height-cy)/leftBoundSlope) + 50
    rightBoundSlope = (app.height-app.height//4)/(1280-900)
    rightBound = int(app.width - ((app.height - cy)/rightBoundSlope)) - 50
    if(cx < leftBound):
        return "right"
    elif(cx > rightBound):
        return "left"
    
#Draws a banana 
def drawBanana(cx,cy,app,canvas):
    canvas.create_image(cx,cy,image = ImageTk.PhotoImage(app.banana))

#The AI (Luigi) moves randomly 
#Establish bounds so the AI and player don't phase through each other 
#Checks for collisons as well 
def move_AIOpponent(app):
    oppenentAIheight, oppenentAIwidth = app.luigi.size
    playerHeight, playerWidth = app.image.size  
    totalSpaceOccupiedAIX = (app.opponentCx - oppenentAIwidth/2, 
                             app.opponentCx + oppenentAIwidth/2)
    totalSpaceOccupiedPlayerX = (app.cx - playerHeight/2, 
                                app.cx + playerHeight/2)
    if(abs(totalSpaceOccupiedPlayerX[0] - totalSpaceOccupiedAIX[0])<100 and 
       abs(app.cy - app.opponentCy) < 90):
        app.opponentCx = app.cx - playerWidth
    dy = random.randint(1,2) + app.counter 
    dx = random.randint(-1,2) 
    distanceX = (app.opponentCx - app.redShellCx)**2 
    distanceY = (app.opponentCy - app.redShellCy)**2
    distanceShell = math.sqrt(distanceX + distanceY)
    if(distanceShell < 80 and app.opponentCx < app.redShellCx):
        dx = -100
    if(abs(app.bananaCx - app.opponentCx) < 20):
        dx = 10
    if(dx < 0):
        app.luigi = app.leftLuigi 
    elif(dx > 0): 
        app.luigi = app.rightLuigi 
    else:
        app.luigi = app.straightLuigi 
    app.opponentCy -= dy 
    app.opponentCx += dx 

#Checks if player hits a banana 
def playerHitBanana(app):
    playerHeight, playerWidth = app.image.size 
    if(app.cy - playerHeight - app.bananaCy < 5 and app.cx - playerWidth -
       app.bananaCx < 5):
        return True 
    return False 

#Checks if the opponent hits a banana 
def opponentHitBanana(app):
    opponentHeight,opponentWidth = app.luigi.size
    if(app.opponentCy + opponentHeight - app.bananaCy < 5 and
       app.opponentCx - opponentWidth - app.bananaCx < 5):
        return True 
    return False 

#Checks for various different collisions 
def checkForCollisons(app):
    oppenentAIheight, oppenentAIwidth = app.luigi.size
    playerHeight, playerWidth = app.image.size 
    itemBoxHeight, itemBoxWidth = app.itemBox.size 
    totalSpaceOccupiedAIX = (app.opponentCx - oppenentAIwidth/2, 
                             app.opponentCx + oppenentAIwidth/2)
    totalSpaceOccupiedPlayerX = (app.cx - playerHeight/2, 
                                app.cx + playerHeight/2)
    if(abs(totalSpaceOccupiedPlayerX[0] - totalSpaceOccupiedAIX[0])<100 and 
       abs(app.cy - app.opponentCy) < 90):
        app.cx = app.opponentCx + oppenentAIwidth
    leftBoundSlope = (app.height-app.height//4)/(700)
    leftBound  = (app.height-app.cy)/leftBoundSlope
    rightBoundSlope = (app.height-app.height//4)/(1280-900)
    rightBound = app.width - ((app.height - app.cy)/rightBoundSlope)
    leftBoundOpponent = (app.height - app.opponentCy)/leftBoundSlope
    rightBoundOpponent=app.width-(app.height - app.opponentCy)/rightBoundSlope
    if(app.cx <= leftBound + playerWidth): 
        app.cx = leftBound + playerWidth 
    if(app.cx >= rightBound - playerWidth):
        app.cx = rightBound - playerWidth
    if(app.opponentCx <= leftBoundOpponent + oppenentAIwidth):
        app.opponentCx = leftBoundOpponent + oppenentAIwidth
    if(app.opponentCx >= rightBoundOpponent - oppenentAIwidth):
        app.opponentCx = rightBoundOpponent - oppenentAIwidth
    if(app.cy - app.itemBoxCy < itemBoxHeight-10 and
        app.cx - app.itemBoxCx < 70):
        app.itemBoxCx, app.itemBoxCy = spawnItemBox(app)
        app.currentItem = getMysteryItem(app)
    elif(app.opponentCy - app.itemBoxCy - 10 < itemBoxHeight and  
       app.opponentCx - app.itemBoxCx < 70):
        app.itemBoxCx, app.itemBoxCy = spawnItemBox(app)
        app.opponentItem = getMysteryItem(app)
    if(app.opponentCy - app.redShellCy < app.redShellHeight and 
       app.opponentCx - app.redShellCx < 50 and app.usePowerUp):
       app.hit = True 

#Checks if the shell hits opponent     
def checkIfShellHitsOpponent(app):
    distance = math.sqrt((app.redShellCx-app.opponentCx)**2 +
                          (app.redShellCy-app.opponentCy)**2)
    if(distance < 50):
        return True 
    distanceTwo = math.sqrt((app.greenShellCx-app.opponentCx)**2 +
                          (app.greenShellCy-app.opponentCy)**2)
    if(distanceTwo < 50):
        return True 
    return False 

def checkIfShellHitPlayer(app):
    if(app.opponentShellCx != None):
        distance = math.sqrt((app.opponentShellCx-app.cx)**2 +
                          (app.opponentShellCy-app.cy)**2)
        if(distance < 50):
            return True 
    return False 

#Activates the lightning bolt power up 
def lightningBoltPowerUp(app):
    if(app.currentItem == "lightning bolt" and app.usePowerUp):
        app.luigi = app.scaleImage(app.luigi,1/2)
        app.usePowerUp = False 

#Activates the rocket power up 
def rocketPowerUp(app):
    if(app.currentItem == "rocket" and app.usePowerUp): 
        app.image = app.bulletBill
        app.cy -= 15

#Checks if the player reached the end of the track. Sets position and time 
def checkForEnd(app):
    opponentAIheight, opponentAIwidth = app.luigi.size
    playerHeight, playerWidth = app.image.size 
    if(app.opponentCy - opponentAIheight < app.height//4): 
        app.opponentEnd = True 
    if(app.cy - playerHeight < app.height//4):
        app.image = app.mario 
        app.cy = 600
        app.counter += 1 
        app.opponentCx,app.opponentCy = 400,720-(app.opponentCy % app.height)
        print(app.opponentCy)

#Chooses a random mystery item from the four options 
def getMysteryItem(app):
    mysteryBox = ["banana", "rocket", "red shell", "green shell"]
    item = mysteryBox[random.randint(0,3)]
    return "red shell"

#Spawns item box in random x and y positions 
def spawnItemBox(app):
    cyItemBox = random.randint(app.height//4+50,app.cy)
    leftBoundSlope = (app.height-app.height//4)/(700)
    leftBound  = int((app.height-cyItemBox)/leftBoundSlope)
    rightBoundSlope = (app.height-app.height//4)/(1280-900)
    rightBound = int(app.width - ((app.height - cyItemBox)/rightBoundSlope))
    cxItemBox = random.randint(leftBound,rightBound)
    return (cxItemBox,cyItemBox)

def raceScreen_timerFired(app):
    if(app.counter == 3 and app.opponentCy - 100 < app.height//4 
       and app.fullOpponentEnd):
        app.endTimeOpponent = time.time()  
        app.fullOpponentEnd = not app.fullOpponentEnd  
    if(app.counter == 3 and app.cy  -  100 < app.height//4):
        app.endTimePlayer = time.time() 
        if(app.fullOpponentEnd):
            dt = app.endTimePlayer - app.startTimePlayer
            app.fullOpponentEnd = random.randint(10,20)/10
            app.fullOpponentEnd *= (app.opponentCy-app.height/4)
            app.fullOpponentEnd = dt + app.fullOpponentEnd
        app.mode = "leaderBoard"
    app.leftCornerY += 100 * (app.counter)
    if(not app.delay):
        move_AIOpponent(app)
    elif(app.delay):
        if(app.cy < app.opponentCy):
            app.delay = not app.delay
    checkForCollisons(app)
    checkForEnd(app)
    lightningBoltPowerUp(app)
    rocketPowerUp(app)
    app.start = (app.start + 100) % 60 
    if(app.cy < 300):
        raceScreenTwoBounds(app)
    if(not app.usePowerUp):
        app.redShellCx = app.cx
        app.redShellCy = app.cy - 50
        app.greenShellCx = app.cx 
        app.greenShellCy = app.cy - 50 
    if(playerHitBanana(app)):
        app.spawnABanana = True
        app.fullMarioSprite = app.loadImage("fullMarioSpriteSheet.png")
        app.fullMarioSprite = app.scaleImage(app.fullMarioSprite, 1/2)
        app.cy += 80
    if(opponentHitBanana(app)):
        app.spawnABanana = True
        app.opponentCy += 80
    if(app.spawnABox):
        app.itemBoxCx, app.itemBoxCy = spawnItemBox(app)
        app.spawnABox = False 
    shellMethods(app)

def shellMethods(app):
    if(app.currentItem == "red shell" and app.usePowerUp and 
      checkShellBounds(app,app.redShellCx,app.redShellCy) == None):
        xDistance = (app.opponentCx - app.cx)
        yDistance = (app.opponentCy - app.cy-40)
        dx = xDistance/10
        dy = yDistance/10
        app.redShellCx += dx 
        app.redShellCy += dy
    elif(app.opponentItem == "red shell" and app.opponentPowerUp):
        xDistance = (app.cx - app.opponentCx)
        yDistance = (app.cy - app.opponentCy)
        dx = xDistance/3
        dy = yDistance/3
        app.opponentShellCx += dx 
        app.opponentShellCy += dy 
    if(app.spawnABanana):
        app.bananaCx, app.bananaCy = spawnBanana(app)
        app.spawnABanana = False 
    if(app.currentItem == "green shell" and app.usePowerUp and 
       checkShellBounds(app,app.greenShellCx,app.greenShellCy) == None):
        xDistance = app.opponentCx - app.cx 
        yDistance = app.opponentCy - app.cy - 40 
        dx = xDistance/10
        dy = yDistance/10
        app.greenShellCx += dx 
        app.greenShellCy += dy 
    if(checkIfShellHitsOpponent(app)):
        app.delay = True
        app.drawRedShell = False
    elif(checkIfShellHitPlayer(app)):
        app.drawRedShell = False 
    if(checkShellBounds(app,app.greenShellCx,app.greenShellCy) == "right"):
        app.greenShellCx += 10
        app.greenShellCy -= 5
    elif(checkShellBounds(app,app.greenShellCx,app.greenShellCy) == "left"):
        app.greenShellCx -= 10
        app.greenShellCy -= 5
    if(checkShellBounds(app,app.redShellCx,app.redShellCy) == "right"):
        app.redShellCx += 10
        app.redShellCy -= 5
    elif(checkShellBounds(app,app.redShellCx,app.redShellCy) == "left"):
        app.redShellCx -= 10
        app.redShellCy -= 5

#Draws the main race screen with item boxs, bananas, players, and opponent 
def raceScreen_redrawAll(app,canvas):
    skyBlue = rgbString(135,206,235)
    highwayYellow = rgbString(247,181,0)
    dy = 1.5*(app.height - app.cy - 120.5)
    drawRandomCurvedTrack(app,canvas)
    endX = getFirstPointX(app)
    canvas.create_image(app.cx,app.cy,image=ImageTk.PhotoImage(app.image))
    canvas.create_polygon(0,app.height,endX,app.height//4+dy,endX+700,
                        app.height//4+dy,app.width,app.height, fill = "gray")
    canvas.create_image(app.cx,app.cy,image=ImageTk.PhotoImage(app.image))
    for i in range(1,10):
        leftCornerX = ((app.leftCornerX - i) % app.width) - 100
        leftCornerY = ((app.leftCornerY + 60*i)%(app.height)+app.height//4+dy)
        canvas.create_polygon(leftCornerX, leftCornerY, leftCornerX+20,
                             leftCornerY+3, leftCornerX+20, leftCornerY+30,
                             leftCornerX,leftCornerY+30, fill = highwayYellow)
    canvas.create_rectangle(0,0,app.width, app.height//4, fill = skyBlue)
    canvas.create_image(app.cx,app.cy,image=ImageTk.PhotoImage(app.image))  
    if(not app.opponentEnd):             
        canvas.create_image(app.opponentCx, app.opponentCy, 
                        image = ImageTk.PhotoImage(app.luigi))
    canvas.create_image(app.itemBoxCx,app.itemBoxCy,
                       image = ImageTk.PhotoImage(app.itemBox))
    drawPowerUps(app,canvas)
    if(not app.keyBoard):
        app.drawCamera(canvas)

def drawPowerUps(app,canvas):
    posOfPowerUpX = app.width - 110 
    if(app.currentItem == "red shell"):
        posOfPowerUpX = app.width - 80 
        canvas.create_image(posOfPowerUpX,70,
                            image = ImageTk.PhotoImage(app.redShell))
    elif(app.currentItem == "rocket"):
        canvas.create_image(posOfPowerUpX,70,
                            image = ImageTk.PhotoImage(app.bulletBill))
    elif(app.currentItem == "lightning bolt"):
        canvas.create_image(posOfPowerUpX,70,
                            image = ImageTk.PhotoImage(app.lightningBolt))
    elif(app.currentItem == "green shell"):
        canvas.create_image(posOfPowerUpX,70,
                            image = ImageTk.PhotoImage(app.bigGreenShell))
    if(app.usePowerUp and app.currentItem == "red shell" and 
       app.redShellCy > app.height/4):
        canvas.create_image(app.redShellCx, app.redShellCy, 
                        image = ImageTk.PhotoImage(app.smallRedShell))
    if(app.opponentPowerUp and app.opponentItem == "red shell" and 
       app.opponentShellCy > app.height/4):
        canvas.create_image(app.opponentShellCx, app.opponentShellCy, 
                        image = ImageTk.PhotoImage(app.smallRedShell))
    if(app.usePowerUp and app.currentItem == "green shell" 
      and app.greenShellCy > app.height//4):
        canvas.create_image(app.greenShellCx,app.greenShellCy, 
                            image = ImageTk.PhotoImage(app.greenShell))
    if(app.bananaCx, app.bananaCy != None,None):
        drawBanana(app.bananaCx, app.bananaCy, app,canvas)

#Establishes the keyboard control for the user 
def raceScreen_keyPressed(app,event):
    if(app.keyBoard):
        if(event.key == "Up"):
            app.cy -= 2 
            app.image = app.mario 
        elif(event.key == "Right"):
            app.cx += 10 
            app.image = app.rightMario
        elif(event.key == "Left"):
            app.cx -= 10
            app.image = app.leftMario 
        elif(event.key == "r"):
            app.usePowerUp = True 
    if(event.key == "q"):
        appStarted(app)
    elif(event.key == "o"):
        app.mode == "leaderBoard"
    elif(event.key == "k"):
        app.cy -= 60

#Picks a random value for amplitude 
#and frequency of the inverse sin track 
def getRandomCurvedTrack():
    amplitude = random.randint(150,200)
    frequency = random.randint(50,70)
    return amplitude,frequency

#Finds the x cooridinate of where the inverse sin curve 
#and straight trackmeet up 
def getFirstPointX(app):
    i = app.height - 84 
    x = app.amp*(math.sin(i/app.freq)) + 300 
    return x 

#Draws a random curved track based on the sin function. 
def drawRandomCurvedTrack(app,canvas):
    highwayYellow = rgbString(247,181,0)
    grassGreen = rgbString(126,200,80)
    skyBlue = rgbString(135,206,235)
    canvas.create_rectangle(0,0,1280,720,fill = grassGreen)
    for i in range(1,720):
        oldY = app.amp*math.sin((i-1)/app.freq) + 300
        y = app.amp*math.sin(i/app.freq) + 300
        y1 = app.amp*math.sin((i-1)/app.freq) + 1000
        y2 = app.amp*math.sin(i/app.freq) + 1000
        x = -i + 1.5*(app.height - app.cy)
        canvas.create_line(oldY,x-1,y,x,y1,x-1,y2,x,fill = "gray") 
    for i in range(app.start,720,100):
        leftCornerX = app.amp*math.sin(i/app.freq) + 650
        leftCornerY = -i + 1.5*(app.height - app.cy)
        canvas.create_polygon(leftCornerX, leftCornerY, leftCornerX+20,
                             leftCornerY-5, leftCornerX+20, leftCornerY-30,
                             leftCornerX,leftCornerY-30, fill = highwayYellow) 
    canvas.create_rectangle(0,0,app.width, app.height//6, fill = skyBlue)

#Given the difference in times of player and opponent, 
#sets the player vertical position 
def getPosOfOpponent(app):
    cy = 720
    timeDif = 10**7*(app.playerTimer - app.opponentTimer)
    dy = 8
    cy = cy - dy*timeDif 
    return cy 

#Makes sure that the player and opponent do not go off the track 
def raceScreenTwoBounds(app):
    leftBound = app.amp*math.sin(app.cy/app.freq) + 300
    rightBound = app.amp*math.sin(app.cy/app.freq) + 1000
    leftBoundOpponent = app.amp*math.sin(app.opponentCy/app.freq) + 300
    rightBoundOpponent = app.amp*math.sin(app.opponentCy/app.freq) + 1000
    if(app.cx - 70 < leftBound):
        app.cx = leftBound + 70
    elif(app.cx + 70 > rightBound):
        app.cx = rightBound - 70
    if(app.opponentCx - 70 < leftBoundOpponent):
        app.cx = leftBoundOpponent + 70
    elif(app.opponentCx + 70 > rightBoundOpponent):
        app.cx = rightBoundOpponent - 70
    oppenentAIheight, oppenentAIwidth = app.luigi.size
    playerHeight, playerWidth = app.image.size 
    totalSpaceOccupiedAIX = (app.opponentCx - oppenentAIwidth/2, 
                             app.opponentCx + oppenentAIwidth/2)
    totalSpaceOccupiedPlayerX = (app.cx - playerHeight/2, 
                                app.cx + playerHeight/2)
    if(abs(totalSpaceOccupiedPlayerX[0] - totalSpaceOccupiedAIX[0])<100 and 
       abs(app.cy - app.opponentCy) < 90):
        app.cx = app.opponentCx + oppenentAIwidth

#Draws the leaderboard with the elasped time it took for the player 
#and opponent to finish the race 
def leaderBoard_redrawAll(app,canvas):
    canvas.create_rectangle(1280,720,0,0,fill = "black")
    canvas.create_text(640,70,text = "LEADERBOARD", font = "Avenir 40 bold", 
                       fill = "white")
    canvas.create_rectangle(100,150,1180,300, fill = "red")
    canvas.create_rectangle(100,400,1180,550, fill = "red")
    canvas.create_rectangle(100,600,1180,700, fill = "red")  
    timeElaspedPlayer = (app.endTimePlayer - app.startTimePlayer)
    timeElaspedOpponent = (app.endTimeOpponent - app.startTimeOpponent)
    if(timeElaspedPlayer <= timeElaspedOpponent): 
        playerY = 225
        opponentY = 475
    elif(timeElaspedPlayer > timeElaspedOpponent):
        opponentY = 225
        playerY = 475 
    canvas.create_text(300,playerY,text = "Mario", font = "Avenir 30",
                           fill = "white")
    canvas.create_text(900,playerY,text = f'{int(timeElaspedPlayer)} seconds', 
                           font = "Avenir 30", fill = "white")
    canvas.create_text(300,opponentY, text = "Luigi", font = "Avenir 30", 
                           fill = "white")
    canvas.create_text(900,opponentY,text=f'{int(timeElaspedOpponent)} seconds', 
                           font = "Avenir 30", fill = "white")  
    canvas.create_text(640,650, text = "Play Again!", fill = "white", 
                       font = "Avenir 30 bold")

#Checks if the player pressed "Play Again", if so, it restarts the game 
def leaderBoard_mousePressed(app,event):
    x = event.x 
    y = event.y 
    if(100 < x < 1180 and 600 < y < 700):
        appStarted(app)

runApp(width=1280, height=720)