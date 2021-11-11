import pygame


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('sprite/player.png')
        self.image = self.get_image(0, 0)
        self.image.set_colorkey([0, 0, 0])
        self.rect = self.image.get_rect()
        self.position = [x, y]
        self.speed = 2
        self.animation = 0.0
        self.images = {
            'down': self.get_image(0, 0),
            'left': self.get_image(0, 48),
            'right': self.get_image(0, 96),
            'up': self.get_image(0, 144)
        }
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 12)
        self.prev_pos = self.position.copy()

    def move_down(self): self.position[1] += self.speed

    def move_left(self): self.position[0] -= self.speed

    def move_right(self): self.position[0] += self.speed

    def move_up(self): self.position[1] -= self.speed

    def save_position(self): self.prev_pos = self.position.copy()

    def change_anim(self, name, state):


            if state == 'idle':
                self.image = self.images[name]
                self.image.set_colorkey([0, 0, 0])
            else:
                self.animation += 0.25
                if self.animation == 4.0:
                    self.animation = 0.0
                if self.animation.is_integer():
                    self.image = self.get_image(32 * self.animation, (name == 'down') * 0 + (name == 'left') * 48 + (name == 'right') * 96 + (name == 'up') * 144)
                    self.image.set_colorkey([0, 0, 0])

    def update(self):
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def move_back(self):
        self.position = self.prev_pos
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def get_image(self, x, y):
        image = pygame.Surface([32, 48])
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 48))
        return image
