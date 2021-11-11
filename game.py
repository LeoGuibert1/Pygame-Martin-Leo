import pygame
import pytmx
import pyscroll
from guerrier import Guerrier, HealthBar
from player import Player
from pygame import mixer


class Game:
    def __init__(self):
        #dimensions de l'écran
        self.screen_width = 1600
        self.screen_height = 840

        self.screen_center = (self.screen_width/2, self.screen_height/2)

        #création des fps
        self.fps = 60
   
        #création de l'écran de jeu
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Jeu de rôle")

        self.end = pygame.image.load('img\Background\end.png')   

        #création de la map avec pytmx et pyscroll
        tmx_data = pytmx.util_pygame.load_pygame('map/nsi.tmx')
        map_data = pyscroll.data.TiledMapData(tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 2.2

        #création de l'apparition du joueur (player), du combattant (Rain), et de l'ennemi en combat (Veritas)
        player_pos = tmx_data.get_object_by_name("spawn")
        self.player = Player(player_pos.x, player_pos.y)
        self.rain = Guerrier(770, 500, 'Rain', 500, 500, 250, 0, 1)                                                                                                                                      
        self.veritas = Guerrier(300, 480, 'Veritas', 100, 100, 150, 0, 2)

        #création de la barre de vie en combat
        self.rain_health_bar = HealthBar(920, 270, self.rain.hp, self.rain.max_hp)
        self.veritas_health_bar = HealthBar(505, 270, self.veritas.hp, self.veritas.max_hp)

        #création des différentes collisions (murs et ennemis)
        self.walls = []
        self.ennemis = []
        self.ennemis1 = []
        self.ennemis2 = []
        self.ennemis3 = []
        for obj in tmx_data.objects:
            if obj.type == 'niska':
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            if obj.type == 'ennemis':
                self.ennemis.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            if obj.type == 'ennemis1':
                self.ennemis1.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            if obj.type == 'ennemis2':
                self.ennemis2.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            if obj.type == 'ennemis3':
                self.ennemis3.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            
        #ici on range tous les sprites dans un groupe afin de pouvoir les mettre à jour en même temps
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=3)
        self.group.add(self.player)
        self.dir = 'down'


        #chargement des images de victoire et de défaite
        self.victory_image = pygame.image.load('img/Icons/victory.png').convert_alpha()
        self.defeat_image = pygame.image.load('img/Icons/defeat.png').convert_alpha()

        #chargement des images des ennemis
        self.ennemis_img = pygame.image.load('sprite/veritas.png').convert_alpha()

        #création des variables de combat
        self.current_fighter = 1
        self.action_cooldown = 0
        self.action_wait_time = 200
        self.game_over = 0 #1: gagné, -1: perdu
        self.game = 0 #0: hors-combat, #1: en combat

        #temps après la fin du combat
        self.end_cooldown = 300
        self.end_count = 0

        #création de la police d'écriture
        self.font = pygame.font.SysFont('Times New Roman', 26)
        
        #création des couleurs
        self.red = (255,0,0)
        self.green = (0,255,0)

        #image du background
        self.background_image = pygame.image.load('img/Background/background.png').convert_alpha()

   
    #fonction pour créer du texte
    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))


            

    #fonction pour dessiner le background 
    def draw_bg(self):
        self.screen.blit(self.background_image, (0, 0))
        #montre les stats de Rain 
        self.draw_text(f'{self.rain.name}, HP: {self.rain.hp}, Niveau: {self.rain.niveau}', self.font, self.red, 920, 240)
        #Montre les stats de Veritas
        self.draw_text(f'{self.veritas.name}, HP: {self.veritas.hp}, Niveau: {self.veritas.niveau}', self.font, self.red, 500, 240)
        
   

    def handle_input(self):
        #range toutes les touches enfoncées
        pressed = pygame.key.get_pressed()
        self.dir_key_pressed = 0

        #création des touches directionnelles 
        if pressed[pygame.K_DOWN]:
            self.player.move_down()
            self.dir_key_pressed += 1
            self.dir = 'down'
            self.state = 'move'
        if pressed[pygame.K_LEFT]:
            self.player.move_left()
            self.dir_key_pressed += 1
            self.dir = 'left'
            self.state = 'move'
        if pressed[pygame.K_RIGHT]:
            self.player.move_right()
            self.dir_key_pressed += 1
            self.dir = 'right'
            self.state = 'move'
        if pressed[pygame.K_UP]:
            if pressed[pygame.K_RIGHT]:
                self.dir = 'right'
            elif pressed[pygame.K_LEFT]:
                self.dir = 'left'
            else:
                self.dir = 'up'
                self.state = 'move'

            self.player.move_up()
            self.dir_key_pressed += 1

        if self.dir_key_pressed >= 2:
            self.player.speed = 1.4
        else:
            self.player.speed = 2

    def end_screen(self):
        self.screen.blit(self.end, (0, 0))
        self.font = pygame.font.SysFont('Times New Roman', 150)
        self.draw_text("FIN", self.font, (255,255,255), 700, 320)
        self.font = pygame.font.SysFont('Times New Roman', 80)
        self.draw_text("gg wp", self.font, (255,255,255), 700, 450)
        
        


    def update(self):
        #rafraichissement des sprites
        self.group.update()
        #verification des collisions 
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()
            if sprite.feet.collidelist(self.ennemis) > -1:
                self.game = 1
            if sprite.feet.collidelist(self.ennemis1) > -1:    
                if self.game == 0:            
                    self.veritas.alive = True
                    self.veritas.max_hp = 350
                    self.veritas.hp = 350
                    self.veritas.niveau = 3
                    self.veritas_health_bar.max_hp = 350
                    self.veritas.strength = 150
                    self.current_fighter = 1
                    self.action_cooldown = 0
                    self.end_count = 0
                    self.game_over = 0
                    self.game = 1
              

            
            if sprite.feet.collidelist(self.ennemis2) > -1:
                if self.game == 0:            
                    self.veritas.alive = True
                    self.veritas.max_hp = 400
                    self.veritas.hp = 400
                    self.veritas.niveau = 4
                    self.veritas.strength = 170
                    self.veritas_health_bar.max_hp = 400
                    self.current_fighter = 1
                    self.action_cooldown = 0
                    self.end_count = 0
                    self.game_over = 0
                    self.game = 1
            if sprite.feet.collidelist(self.ennemis3) > -1:
                if self.game == 0:            
                    self.veritas.alive = True
                    self.veritas.max_hp = 450
                    self.veritas.hp = 450
                    self.veritas.niveau = 5
                    self.veritas.strength = 190
                    self.veritas_health_bar.max_hp = 450
                    self.current_fighter = 1
                    self.action_cooldown = 0.
                    self.end_count = 0
                    self.game_over = 0
                    self.game = 1

    def run(self):
        clock = pygame.time.Clock()

        running = True
        
        #boucle du jeu qui tourne à 60 tours par seconde (60 fps)
        while running:
            if self.game == 3:
                self.end_screen()
                self.end_count += 1                 
                if self.end_count > self.end_cooldown:
                    pygame.quit()
                        

            if self.game == 0:
                
                self.player.save_position()
                self.state = 'idle'
                self.handle_input()
                if self.state == 'idle':
                    self.player.animation = 0.0
                self.player.change_anim(self.dir, self.state)
                self.update()
                self.group.center(self.player.rect.center)
                self.group.draw(self.screen)
        

            if self.game == 1:
                pygame.mixer.music.set_volume(0.1)
                if pygame.mixer.music.get_busy() == False and self.game_over != -1 and self.game_over != 1:
                    
                    pygame.mixer.music.load('music/combat.mp3')
                    pygame.mixer.music.play(0, start=76.0)
                

                    
                #dessiner background
                self.draw_bg()

                #dessiner guerrier (Rain)
                self.rain.update()
                self.rain.draw(self.screen)

                #dessiner ennemi (Veritas)
                self.veritas.update()
                self.veritas.draw(self.screen)

                #dessiner la barre de vie des deux combattants
                self.rain_health_bar.draw(self.screen, self.rain.hp)
                self.veritas_health_bar.draw(self.screen, self.veritas.hp)

                

                if self.game_over == 0:
                   
                    #action joueur (Rain)
                    if self.rain.alive:
                        if self.current_fighter == 1:
                            self.action_cooldown += 1
                            if self.action_cooldown >= self.action_wait_time:
                                self.rain.attack(self.veritas)
                                self.current_fighter += 1
                                self.action_cooldown = 0
                    else:
                        self.game_over = -1
                        pygame.mixer.music.stop()
                        

                    #action ennemi (Veritas)
                    if self.veritas.alive:
                        if self.current_fighter == 2:
                            self.action_cooldown += 1
                            if self.action_cooldown >= self.action_wait_time:
                                self.veritas.attack(self.rain)
                                self.current_fighter -= 1
                                self.action_cooldown = 0
                    else:
                        self.game_over = 1
                        pygame.mixer.music.stop()
                        
            
                        
                #check si le jeu est fini
                if self.game_over != 0:
                    if self.game_over == 1:
                        self.screen.blit(self.victory_image, (647, 160))
                        self.end_count += 1           
                        if pygame.mixer.music.get_busy() == False:
                            pygame.mixer.music.load('music/victoire.mp3')
                            pygame.mixer.music.play(0)
                        if self.end_count > self.end_cooldown:
                            self.game = 0
                            for sprite in self.group.sprites():
                                    
                                if sprite.feet.collidelist(self.ennemis) > -1:
                                    self.ennemis = []
                                    self.rain.monterExperience(5)
                                if sprite.feet.collidelist(self.ennemis1) > -1:                                    
                                    self.ennemis1 = []
                                    self.rain.monterExperience(7)
                                if sprite.feet.collidelist(self.ennemis2) > -1:
                                    self.ennemis2 = []
                                    self.rain.monterExperience(9)
                                if sprite.feet.collidelist(self.ennemis3) > -1:
                                    self.ennemis3 = []
                                    self.end_count = 0
                                    self.game = 3
                                    

                            
                            
                            
                            pygame.mixer.music.stop()
                            
                        
                    if self.game_over == -1:
                        self.screen.blit(self.defeat_image, (660, 160))
                        self.end_count += 1
                        if pygame.mixer.music.get_busy() == False:
                            
                            pygame.mixer.music.load('music/defaite.mp3')
                            pygame.mixer.music.play(0)
                        if self.end_count > self.end_cooldown:
                            pygame.quit()
                        
                
        

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 

            
            clock.tick(self.fps)
            pygame.display.update()
        pygame.quit()
