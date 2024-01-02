import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE WARS")

BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


class SHIP:
    def __init__(self, x, y, speed = 5, health = 100, COOLDOWN = 10):
        self.x = x
        self.y = y
        self.speed = speed
        self.health = health
        self.ship_img = YELLOW_SPACE_SHIP
        self.ship_laser = YELLOW_LASER
        self.lasers = []
        self.COOLDOWN = COOLDOWN
        self.cooldown_counter = 0
        self.width = self.ship_img.get_width()
        self.height = self.ship_img.get_height()
        self.mask = pygame.mask.from_surface(self.ship_img)
    def draw(self, WIN):
        WIN.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(WIN)
    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.ship_laser)
            self.lasers.append(laser)
            self.cooldown_counter = self.COOLDOWN
    def reload(self):
        self.cooldown_counter = self.cooldown_counter - 1 if self.cooldown_counter > 0 else 0
    def move_lasers(self, enemies): 
        for laser in self.lasers[:]:
            laser.y -= laser.speed
            for enemy in enemies:
                if laser.is_collision(enemy):
                    self.lasers.remove(laser)
                    enemies.remove(enemy)
                    break
                elif laser.is_off_screen():
                    self.lasers.remove(laser)
                    break
class ENEMY(SHIP):
    COLOR_MAP = {
                    "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
                    "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                    "red" : (RED_SPACE_SHIP, RED_LASER)
                }
    def __init__(self, x, y, color, speed = 2, health = 100):
        super().__init__(x, y, speed, health)
        self.ship_img = self.COLOR_MAP[color][0]
        self.ship_laser = self.COLOR_MAP[color][1]
        self.COOLDOWN = 80
        self.mask = pygame.mask.from_surface(self.ship_img)
    def move(self):
        self.y += self.speed
    def shoot(self):
        if self.y >= 0 and self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.ship_laser)
            self.lasers.append(laser)
            self.cooldown_counter = self.COOLDOWN
    def move_lasers(self, player):
        for laser in self.lasers:
            laser.y += laser.speed
            if laser.is_collision(player):
                player.health -= 10
                self.lasers.remove(laser)
                break
            elif laser.is_off_screen():
                self.lasers.remove(laser)
                break

class Laser:
    def __init__(self, x, y, img, speed = 5):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        self.speed = speed
    def draw(self, WIN):
        WIN.blit(self.img, (self.x, self.y))        
    def is_off_screen(self):
        return (self.y < 0 or self.y > HEIGHT)
    def is_collision(self, ship):
        offset_x = self.x - ship.x + 15
        offset_y = self.y - ship.y
        return True if self.mask.overlap(ship.mask, (offset_x, offset_y)) != None else False
def main():
    run = True
    FPS = 60
    main_font = pygame.font.SysFont("comicsans", 20)
    secondary_font = pygame.font.SysFont("comicsans", 50)
    ship = SHIP(300, 650, 5)
    clock = pygame.time.Clock()
    enemies = []
    wave_length = 0
    countdown = 360
    def redraw_window():
        WIN.blit(BG, (0,0))
        health_label = main_font.render(f"{ship.health}", 1, (0, 0, 255))
        WIN.blit(health_label, (WIDTH - health_label.get_width() - 10, 10))
        # level_label = main_font.render(f"{lives}", 1, (255, 0, 0))
        # WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        for enemy in enemies:
            enemy.draw(WIN)
        ship.draw(WIN)
        pygame.display.update()
    def game_over():
        game_over_label = main_font.render("GAME OVER", 1, (0, 0, 255))
        WIN.blit(game_over_label, (WIDTH/2 - game_over_label.get_width()/2, HEIGHT/2))
    while countdown > 0:
        clock.tick(FPS)
        if run:
            redraw_window()        
            if(len(enemies) == 0):
                wave_length = wave_length + 1 if wave_length + 1 <= 10 else 10
                for _ in range(wave_length):
                    new_enemy = ENEMY(random.randrange(50, WIDTH - 50), random.randrange(-1500, -100), random.choice(["blue", "green", "red"]))
                    enemies.append(new_enemy)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                ship.y = ship.y + ship.speed if ship.y + ship.speed + ship.height <= HEIGHT else HEIGHT - ship.height
            if keys[pygame.K_UP]:
                ship.y = ship.y - ship.speed if ship.y - ship.speed >= 0 else 0
            if keys[pygame.K_LEFT]:
                ship.x = ship.x - ship.speed if ship.x - ship.speed >= 0 else 0
            if keys[pygame.K_RIGHT]:
                ship.x = ship.x + ship.speed if ship.x + ship.width + ship.speed <= WIDTH else WIDTH - ship.width 
            if keys[pygame.K_SPACE]:
                ship.shoot()
            for enemy in enemies: 
                enemy.reload()
                enemy.move()
                enemy.shoot()
                enemy.move_lasers(ship)
                if enemy.y + enemy.height >= HEIGHT:
                    enemies.remove(enemy)
            ship.reload()
            ship.move_lasers(enemies)
        else:
            game_over()
        if ship.health <= 0:
            run = False
            print(ship.health)
            countdown -= 1   
    pygame.quit()
    
main()