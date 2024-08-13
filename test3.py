import pygame
import sys
import cv2
from cvzone.HandTrackingModule import HandDetector
import random
from pygame import mixer

width = 1200
height = 600

# OpenCV setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Hand Detector
detector = HandDetector(maxHands=1, detectionCon=0.8)

# Initialize Pygame
pygame.init()

# Background sounds
mixer.music.load('music/background.mp3')
mixer.music.play(loops=-1)
closedHand_sound = mixer.Sound('music/slap.mp3')
catching_sound = mixer.Sound('music/catching_sound.wav')

# Define the screen
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Title and Icon
pygame.display.set_caption("Catch Ball")
icon = pygame.image.load('images/ball_32.png').convert_alpha()
pygame.display.set_icon(icon)
backgroundImg = pygame.image.load('images/TennisBack.png').convert()

# Define the index for closed fingers
indexes_for_closed_fingers = [8, 12, 16, 20]

def initialize_game():
    global score_value, currentTime, numberOfInsects
    global InsectImg, InsectX, InsectY, insect_rect, insectMoveX, insectMoveY
    global openHandImg, openHand_rect, closedHandImg, closedHand_rect
    global catch_insect_with_openHand

    # Initialize game variables
    score_value = 0
    currentTime = pygame.time.get_ticks()
    numberOfInsects = 10

    InsectImg = []
    InsectX = []
    InsectY = []
    insect_rect = []
    insectMoveX = []
    insectMoveY = []

    for i in range(numberOfInsects):
        InsectX.append(random.randint(0, width))
        InsectY.append(random.randint(0, height))
        InsectImg.append(pygame.image.load('images/ball_32.png').convert_alpha())
        insect_rect.append(InsectImg[i].get_rect(topleft=(InsectX[i], InsectY[i])))
        insectMoveX.append(10)
        insectMoveY.append(8)

    # Player
    x = width / 2 - 64
    y = height / 2 - 64
    openHandImg = pygame.image.load('images/openHand.png').convert_alpha()
    openHandImg = pygame.transform.scale(openHandImg, (128, 128))
    openHand_rect = openHandImg.get_rect(topleft=(x, y))

    closedHandImg = pygame.image.load('images/closedHand.png').convert_alpha()
    closedHandImg = pygame.transform.scale(closedHandImg, (128, 128))
    closedHand_rect = closedHandImg.get_rect(topleft=(x, y))

    catch_insect_with_openHand = False

initialize_game()

# Game Texts
font = pygame.font.Font('freesansbold.ttf', 32)
gameOver_font = pygame.font.Font('freesansbold.ttf', 100)
textX = 10
textY = 10

def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))

def show_timer():
    elapsed_time = (pygame.time.get_ticks() - currentTime) / 1000
    time_left = max(0, 10 - int(elapsed_time))
    timer = font.render("Time: " + str(time_left), True, (255, 0, 0) if time_left <= 2 else (255, 255, 255))
    screen.blit(timer, (1210, 10))
    if time_left == 0:
        gameOver = gameOver_font.render("Game Over!", True, (255, 0, 0))
        screen.blit(gameOver, (width / 2 - 300, height / 2 - 30))

restart_game = False
fingers = [0, 0, 0, 0]  # Initialize the fingers list

while True:
    screen.blit(backgroundImg, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()

    # OpenCV code
    success, frame = cap.read()
    hands, frame = detector.findHands(frame)

    if hands:
        lmList = hands[0]
        positionOfTheHand = lmList['lmList']
        openHand_rect.left = (positionOfTheHand[9][0] - 200) * 1.5
        openHand_rect.top = (positionOfTheHand[9][1] - 200) * 1.5
        closedHand_rect.left = (positionOfTheHand[9][0] - 200) * 1.5
        closedHand_rect.top = (positionOfTheHand[9][1] - 200) * 1.5

        hand_is_closed = 0
        for index in range(4):
            if positionOfTheHand[indexes_for_closed_fingers[index]][1] > positionOfTheHand[indexes_for_closed_fingers[index] - 2][1]:
                fingers[index] = 1
            else:
                fingers[index] = 0
            if fingers[0] * fingers[1] * fingers[2] * fingers[3]:
                if hand_is_closed and not catch_insect_with_openHand:
                    closedHand_sound.play()
                hand_is_closed = 0
                screen.blit(closedHandImg, closedHand_rect)
                for iteration in range(numberOfInsects):
                    if openHand_rect.colliderect(insect_rect[iteration]) and catch_insect_with_openHand:
                        score_value += 1
                        catching_sound.play()
                        catch_insect_with_openHand = False
                        insect_rect[iteration] = InsectImg[iteration].get_rect(topleft=(random.randint(0, width), random.randint(0, height)))
                catch_insect_with_openHand = False
            else:
                screen.blit(openHandImg, openHand_rect)
                hand_is_closed = 1
                for iterate in range(numberOfInsects):
                    if openHand_rect.colliderect(insect_rect[iterate]):
                        catch_insect_with_openHand = True

    # OpenCV Screen
    cv2.imshow("webcam", frame)

    # Game screen
    for i in range(numberOfInsects):
        insect_rect[i].right += insectMoveX[i]
        if insect_rect[i].right <= 16:
            insectMoveX[i] += 10
        elif insect_rect[i].right >= width:
            insectMoveX[i] -= 10

        insect_rect[i].top += insectMoveY[i]
        if insect_rect[i].top <= 0:
            insectMoveY[i] += 8
        elif insect_rect[i].top >= height - 32:
            insectMoveY[i] -= 8
        screen.blit(InsectImg[i], insect_rect[i])

    # Showing texts
    show_score(textX, textY)
    show_timer()

    # Check if time is up
    elapsed_time = (pygame.time.get_ticks() - currentTime) / 1000
    if elapsed_time >= 10:
        if not restart_game:
            pygame.time.wait(1000)  # Wait for 1 second before showing restart message
            screen.blit(gameOver_font.render("Press R to Restart", True, (255, 0, 0)), (width / 2 - 300, height / 2 - 30))
            pygame.display.update()
            restart_game = True
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                initialize_game()  # Restart the game
                restart_game = False

    # Display update
    pygame.display.update()
    clock.tick(60)
