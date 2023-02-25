import pygame
import random
import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math

cap = cv2.VideoCapture(0)
cap.set(3,800)
cap.set(4,600)
detector = HandDetector(maxHands=1)
classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")
pygame.mixer.init()
ex = 0
# Load your two music tracks
music1 = pygame.mixer.Sound("Steins Gate op full no vocal.wav")
music2 = pygame.mixer.Sound("152661__alexftw123__car-acceleration-inside-car.wav")

imgSize = 300

labels = ["A", "B", "C"]
#Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
dred = (200, 0, 0)
dgreen = (0, 200, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (240, 240, 60)
vico="a"
class Window:
    def __init__(self, w, h, caption, fps):
        pygame.init()
        self.gameDisplay = pygame.display.set_mode((w, h))
        self.width = w
        self.height = h
        self.clock = pygame.time.Clock()
        self.clock.tick(fps)
        pygame.display.set_caption(caption)

    def message(self, linesOfText, cx, ty, font=None, size=25, color=black):
        style = pygame.font.Font(font, size)
        i = 0
        for text in linesOfText:
            TextSurf = style.render(text, True, color)
            TextRec = TextSurf.get_rect()
            TextRec.center = (cx, ty + (i * size))
            self.gameDisplay.blit(TextSurf, TextRec)
            i += 1

    def close_win(self):
        record = open("data/HighScore.txt", "w")
        for i in scores:
            record.write(str(i)+"\n")
        record.close
        pygame.quit()
        quit()

    def button(self, linesOfText, x, y, w, h, i, a, font=None, size=25, color=black):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x+w and y < mouse[1] < y+h:
            c = a
            if click[0] == 1:
                return True
        else:
            c = i
        pygame.draw.rect(self.gameDisplay, c, (x, y, w, h))
        self.message(linesOfText, x + (w/2), y + (h/2), font, size, color)
        

#SPRITE BASE CLASS
class Sprite:
    def __init__(self, x, y, w, h, i=None):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        if i != None:
            self.i = pygame.image.load(i)

    def draw(self, screen):
        if self.i != None:
            screen.gameDisplay.blit(self.i, (self.x, self.y)) 

#CAR
class Car(Sprite):
    def __init__(self, x, y, w, h, i, ns):
        Sprite.__init__(self, x, y, w, h, i)
        self.noSpoiler = ns
        self.steerSpeed = 7
        ex=x
#OBSTACLE
goingCars = []
class Obstacle(Sprite):
    def __init__(self, x, y, w, h, s):
        Sprite.__init__(self, x, y, w, h)
        self.speed = s
        c1=random.randint(1, 9)
        self.i = pygame.image.load("Going Cars/"+"GC"+str(c1)+".png").convert_alpha()

    def draw(self, screen):
        screen.gameDisplay.blit(self.i, (self.x, self.y))

#START SCREEN
def start_screen(screen):
    screen.gameDisplay.blit(pygame.image.load(
        "fotor_2023-2-24_4_16_45.png"), (0, 0))
    music1_channel = music1.play(-1)
    music1_channel.set_volume(0.1)
    intro = True
    font = "freesansbold.ttf"
    start = False
    over = False
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                screen.close_win()

        
        
        start = screen.button(["GO!"], (screen.width / 3 - 50), (3 * screen.height / 4 - 25), 100, 50, dgreen, green, font=font, size=20)
        over = screen.button(["QUIT"], (2 * screen.width / 3 - 50), (3 * screen.height / 4 - 25), 100, 50, dred, red, font=font, size=20)
        
        if start == True:
            GameLoop(screen)
        if over == True:
            screen.close_win()

        pygame.display.update()

def spawn_obstacle():
    pass

def crashed_message(score, update):
    if update == 0:
        if score > scores[1]:
            update = 1
            scores[5] = scores[3]
            scores[4] = scores[2]
            scores[3] = scores[1]
            scores[2] = scores[0]
            scores[1] = score
            scores[0] = ""
        elif score > scores[3]:
            update = 2
            scores[5] = scores[3]
            scores[4] = scores[2]
            scores[3] = score
            scores[2] = ""
        elif score > scores[5]:
            update = 3
            scores[5] = score
            scores[4] = ""
        else:
            update = 0
    if update == 0:
        message = "TAB TO RESTART"
    else:
        message = "ENTER INITIALS"
    font = "freesansbold.ttf"


    screen.message([message], screen.width/2, (4*screen.height/5), font=font, size = 60, color=white)
    return update

#GAME LOOP
def GameLoop(screen):
    music2_channel = music2.play(-1)
    
    crashed = False
    font = "freesansbold.ttf"
    score = 0
    update = 0
    paused = False
    car = Car(screen.width * .4, screen.height *.7, 108, 155, "Group 1.png", 135)
    obstacle = Obstacle(random.randrange(62, screen.width - 123), -300, 88, 175, 4)
    background = [pygame.image.load("Road1.png"), pygame.image.load("Road1.png"), pygame.image.load("Road2.png"), pygame.image.load("Road2.png"), pygame.image.load("Road3.png"), pygame.image.load("Road3.png"), pygame.image.load("Road4.png"), pygame.image.load("Road4.png")]
    b = 0
    i=0
    vico="A"
    x, y, ex = 0, 0, screen.width * .4
    while True:
        #Events
        if i % 5 == 0:
            i=+ 1
            success, img = cap.read()
            imgOutput = img.copy()
            imgOutput = cv2.flip(imgOutput, 1)
            hands, img = detector.findHands(img)
            if hands:
                hand = hands[0]
                x, y, w, h = hand['bbox']
                if x < 0:
                    x = 0
                imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
                imgCrop = img[y:y + h , x :x + w ]

                imgCropShape = imgCrop.shape

                aspectRatio = h / w

                if aspectRatio > 1:
                    k = imgSize / h
                    wCal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                    imgResizeShape = imgResize.shape
                    wGap = math.ceil((imgSize - wCal) / 2)
                    imgWhite[:, wGap:wCal + wGap] = imgResize
                    prediction, index = classifier.getPrediction(imgWhite, draw=False)
                    screen.message([" " + str(labels[index])],screen.width/5 + 10, screen.height/20, color=blue)
                    print(labels[index])
                    vico=labels[index]
                else:
                    k = imgSize / w
                    hCal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                    imgResizeShape = imgResize.shape
                    hGap = math.ceil((imgSize - hCal) / 2)
                    imgWhite[hGap:hCal + hGap, :] = imgResize
                    prediction, index = classifier.getPrediction(imgWhite, draw=False)
                    screen.message([" " + str(labels[index])], screen.width/5 +10, screen.height/20, color=blue)
                    


                
            imgRGB = cv2.cvtColor(imgOutput, cv2.COLOR_BGR2RGB)
            imgRGB = np.rot90(imgRGB)
            frame = pygame.surfarray.make_surface(imgRGB).convert()
            frame = pygame.transform.flip(frame, True, False)
            cv2.waitKey(1)
        print(i)
        print("-"*20)
        print(x,ex,ex-x,vico)
        
        i =i+1
        for event in pygame.event.get():
            if crashed == True and update == 0:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LSHIFT:
                        GameLoop(screen)
                        return

            if crashed == True and update > 0:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LSHIFT:
                        GameLoop(screen)
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        scores[(update - 1)*2] = scores[(update - 1)*2][:-1]
                    elif event.key != pygame.K_LSHIFT and event.key != pygame.K_RSHIFT and len(scores[(update - 1)*2]) < 3:
                        if chr(event.key).isalpha() or chr(event.key).isdigit():
                            scores[(update - 1)*2] = scores[(update - 1)*2] + str(chr(event.key).upper())
                    

            if event.type == pygame.KEYDOWN and crashed == False:
                if event.key == pygame.K_SPACE:
                    paused = not paused
    
            if event.type == pygame.QUIT:
                screen.close_win()

        #Key Holds
        keys = pygame.key.get_pressed()
        if not crashed and not paused:
            if keys[pygame.K_LEFT] : 
                car.x += -car.steerSpeed
            if (x>ex and x!=0):
                car.x += -(car.steerSpeed+(x-ex)*0.7)
            if keys[pygame.K_RIGHT] :
                car.x += car.steerSpeed
            if (x<ex and x!=0):
                car.x += (car.steerSpeed+(ex-x)*0.7)
        #DRAW
        screen.gameDisplay.blit(background[b], (0, 0))
        if not crashed and not paused:
            b += 1
        if b == 8:
            b = 0

        obstacle.draw(screen)
        car.draw(screen)
        font = pygame.font.Font("abnes.ttf", 20)

# Render the score text
        score_text = font.render("Score: " + str(score), True, yellow)

        # Draw the score text on the screen
        screen.gameDisplay.blit(score_text, (screen.width/5 -80, screen.height/20))

        # Render the obstacle speed text
        speed_text = font.render("V | " + str(int(obstacle.speed)*11)+"  km/h  || "+ str(vico)+" ||", True,white)

        # Draw the obstacle speed text on the screen
        screen.gameDisplay.blit(speed_text, (screen.width/5 +260, screen.height/20))

        # Render the vico speed text
        

        #Adjust Scene
        if not crashed and not paused:
            obstacle.y += obstacle.speed
        
        if paused == True:
            screen.message(["PAUSE"], screen.width/2, screen.height/3, font=font, size = 115, color=dgreen)
        
        #things_dodged(score)
        if car.x <= 58 or car.x + car.width >= screen.width - 58:
            crashed = True
            update = crashed_message(score, update)
            music2_channel.stop()
        if obstacle.y > screen.height:
            obstacle.y = 0 - obstacle.height
            obstacle.x = random.randrange(62, screen.width - obstacle.width - 60)
            score += 2
            if vico=="A":
                obstacle.speed += 0.5#speed of obstacle
                music2_channel.set_volume(0.5)
            if vico=="B":
                obstacle.speed += 4
                music2_channel.set_volume(1)
            if vico=="C":
                obstacle.speed -= 3
                music2_channel.set_volume(0.5)
            car.steerSpeed += .009

        #Collision Detection With Obstacle
        if car.y + 7 < obstacle.y+obstacle.height and car.y + 109 > obstacle.y:
            if car.x + 30 > obstacle.x and car.x + 30 < obstacle.x + obstacle.width or car.x + car.width - 25 > obstacle.x and car.x + car.width - 25 < obstacle.x + obstacle.width:
                update = crashed_message(score, update)
                crashed = True
                music2_channel.stop()
        if car.y + 110 < obstacle.y+obstacle.height and car.y + car.noSpoiler > obstacle.y:
            if car.x > obstacle.x and car.x < obstacle.x + obstacle.width or car.x + car.width > obstacle.x and car.x + car.width < obstacle.x + obstacle.width:
                update = crashed_message(score, update)
                crashed = True     
                music2_channel.stop()   
        #UPDATE SCREEN
        ex = x
        
        pygame.display.update()


scores = []
with open("data/HighScore.txt","r") as f:
    for line in f:
        try:
            scores.append(int(line[:-1]))
        except ValueError:
            scores.append(line[:-1])
        

screen = Window(800, 600, "Readikai", 60)
start_screen(screen)



