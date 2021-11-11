import pygame
import os, os.path
import random




class Guerrier():
    def __init__(self, x, y, name, hp, max_hp, strength, xp, niveau):
        super().__init__()
        self.name = name
        self.xp = xp
        self.niveau = niveau
        self.hp = hp
        self.max_hp = max_hp
        self.strength = strength
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 #0:idle, #1:attack, #2:dead #3:attack_limit
        self.update_time = pygame.time.get_ticks() 
        #load idle images
        count = os.listdir(f'img/{self.name}/Idle')
        temps_list = []
        for i in range(len(count)):
            img = pygame.image.load(f'img/{self.name}/Idle/tile00{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temps_list.append(img)
        self.animation_list.append(temps_list)

        #load attack images
        count = os.listdir(f'img/{self.name}/Attack')
        temps_list = []
        for i in range(len(count)):
            img = pygame.image.load(f'img/{self.name}/Attack/tile00{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temps_list.append(img)
        self.animation_list.append(temps_list)

        #load dead images
        count = os.listdir(f'img/{self.name}/Dead')
        temps_list = []
        for i in range(len(count)):
            img = pygame.image.load(f'img/{self.name}/Dead/tile00{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temps_list.append(img)
        self.animation_list.append(temps_list)

        #load attack_limit images
        count = os.listdir(f'img/{self.name}/Attack_limit')
        temps_list = []
        for i in range(len(count)):
            img = pygame.image.load(f'img/{self.name}/Attack_limit/tile00{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temps_list.append(img)
        self.animation_list.append(temps_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    def update(self):
        animation_cooldown = 100
        #update image
        self.image = self.animation_list[self.action][self.frame_index]

        #verifie le cooldown pour mettre la nouvelle image
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 2 and self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else: 
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
    
    def monterExperience(self, xp):
        self.xp = self.xp + xp
        if self.xp >= 10:
            self.xp = 0 
            self.niveau = self.niveau + 1

    def death(self):
        #death animation
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    
    def attack (self, target):
        #deal damage to enemy
        rand = random.randint(0, 5)
        if rand > 1:
            attaque = random.randint(-5, 5)
            damage = (self.strength + attaque) + (self.niveau*1.5)
            target.hp -= damage
        else:
            attaque = random.randint(50, 100)
            damage = self.strength + attaque
            target.hp -= damage
        #check si il est mort ou pas
        
        if rand >= 2:
            #variables pour animation attaque
            self.action = 1
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
        else:
            self.action = 3
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()





class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        super().__init__()
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, surf, hp):
        #update with new health
        self.hp = hp
        ratio = self.hp / self.max_hp
        #caculate new bar
        pygame.draw.rect(surf, (255,0,0), (self.x, self.y, 150, 20))
        pygame.draw.rect(surf, (0,255,0), (self.x, self.y, 150 * ratio, 20))

