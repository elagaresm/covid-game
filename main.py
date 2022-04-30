# Enmanuel Lagares
# 2018-7375

import pygame
import sys
import random
import math
from pygame import mixer
from pygame.constants import MOUSEBUTTONDOWN
import sqlite3
import atexit

con = sqlite3.connect('game.db')
atexit.register(con.close)
cur = con.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score INTEGER    
);''')

# initializing the pygame
pygame.init()

# creating the screen
screen = pygame.display.set_mode((800, 600))

click = False

# background
background = pygame.image.load('Images/Artboard 2.png')

# background sound
mixer.music.load('Sound FX/background.wav')
mixer.music.play(-1)

# title and icon
pygame.display.set_caption('Coronavirus Attack!')
# icon .png downloaded from https://www.flaticon.com
icon = pygame.image.load('Images/coronavirus.png')
pygame.display.set_icon(icon)


def main_menu():
    while True:
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))

        main_font = pygame.font.Font('Font/Righteous-Regular.ttf', 64)
        main_text = main_font.render('CORONAVIRUS ATTACK', True, (255, 0, 0))
        screen.blit(main_text, (45, 200))
        buttons_font = pygame.font.Font('Font/Righteous-Regular.ttf', 42)
        button1_text = buttons_font.render('START GAME', True, (255, 255, 255))
        button2_text = buttons_font.render('EXIT GAME', True, (255, 255, 255))

        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(250, 300, 285, 50)
        button_2 = pygame.Rect(272, 400, 230, 50)
        pygame.draw.rect(screen, (255, 0, 0), button_1)
        pygame.draw.rect(screen, (255, 0, 0), button_2)
        screen.blit(button1_text, (260, 300))
        screen.blit(button2_text, (280, 400))

        if button_1.collidepoint((mx, my)):
            if click:
                break
        if button_2.collidepoint((mx, my)):
            if click:
                pygame.quit()
                sys.exit()

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()


main_menu()


# player
player_img = pygame.image.load('Images/Asset 2.png')
# player position
playerX = 370
playerY = 480
# player x-axis movement variable
playerX_change = 0


# enemy
enemy_img = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemy_img.append(pygame.image.load('Images/coronavirus.png'))
    # enemy position
    enemyX.append(random.randint(0, 735))
    enemyY.append(random.randint(50, 150))
    # enemy x-axis movement variable
    enemyX_change.append(3)
    enemyY_change.append(40)


# bullet

# ready => {display: none}
# fire => The bullet is shown and currenlty moving
bullet_img = pygame.image.load('Images/drop.png')
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 10
bullet_state = 'ready'


# score
score = 0
font = pygame.font.Font('Font/Righteous-Regular.ttf', 32)

textX = 10
textY = 10

# game over text
over_font = pygame.font.Font('Font/Righteous-Regular.ttf', 64)


def show_score(x, y):
    score_value = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_value, (x, y))

def high_score():
    cur.execute('SELECT MAX(score) FROM scores')
    high_score_value = font.render(f'Highscore: {cur.fetchone()[0]}', True, (255, 255, 255))
    screen.blit(high_score_value, (10, 45))


def game_over_text():
    over_text = over_font.render('GAME OVER', True, (0, 0, 0))
    screen.blit(over_text, (200, 250))


def player(x, y):
    screen.blit(player_img, (x, y))


def enemy(x, y, i):
    screen.blit(enemy_img[i], (x, y))


def fire_bullet(x, y):
    global bullet_state
    bullet_state = 'fire'
    screen.blit(bullet_img, (x + 16, y + 10))


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((math.pow(enemyX - bulletX, 2)) +
                         (math.pow(enemyY - bulletY, 2)))

    return distance < 32


# game loop until `exit` is called
running = True
while running:

    # background color
    screen.fill((0, 0, 0))

    # background image
    screen.blit(background, (0, 0))

    # looking if `exit` is called
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # checking if key down was left or right
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -5
            if event.key == pygame.K_RIGHT:
                playerX_change = 5
            # space key down
            if event.key == pygame.K_SPACE:
                # wait until bullet gets to 0 px to shoot again
                if bullet_state == 'ready':
                    bullet_sound = mixer.Sound('Sound FX/laser.wav')
                    bullet_sound.play()
                    # getting the current x coordinate of the player
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)

        # checking if key up was left o right
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

    playerX += playerX_change

    # setting the movement limits
    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:
        playerX = 736

    for i in range(num_of_enemies):

        # game over
        if enemyY[i] > 440:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            game_over_text()
            cur.execute("INSERT INTO scores(score) VALUES (?)", (score,))
            con.commit()
            break

        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0:
            enemyX_change[i] = 3
            enemyY[i] += enemyY_change[i]
        elif enemyX[i] >= 736:
            enemyX_change[i] = -3
            enemyY[i] += enemyY_change[i]

        # collision
        collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
        if collision:
            explosion = mixer.Sound('Sound FX/explosion.wav')
            explosion.play()
            bulletY = 480
            bullet_state = 'ready'
            score += 1
            enemyX[i] = random.randint(0, 735)
            enemyY[i] = random.randint(50, 150)

        enemy(enemyX[i], enemyY[i], i)

    # bullet movement
    if bulletY <= 0:
        bulletY = 480
        bullet_state = 'ready'

    if bullet_state == 'fire':
        fire_bullet(bulletX, bulletY)
        bulletY -= bulletY_change

    player(playerX, playerY)
    show_score(textX, textY)
    high_score()
    # updating the screen in the loop
    pygame.display.update()
