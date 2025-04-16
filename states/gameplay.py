import pygame
import random
import spritesheet
import constants
from starfield import StarField

from pygame.locals import (
    K_LEFT,
    K_RIGHT,
)

from simple_reflex_agent import SimpleReflexAgent
from .base_state import BaseState
from sprites.player import Player
from sprites.rocket import Rocket
from sprites.enemy import Enemy
from sprites.control_point import ControlPoint
from sprites.explosion import Explosion

from bezier.control_point_collection_factory import ControlPointCollectionFactory
from bezier.path_point_calculator import PathPointCalculator
from bezier.control_handler_mover import ControlHandlerMover
from bezier.path_point_selector import PathPointSelector
ADDENEMY = pygame.USEREVENT + 1
ENEMYSHOOTS = pygame.USEREVENT + 2
FREEZE = pygame.USEREVENT + 3

def read_scores():
    integer_list = []
    with open("highscores.txt", 'r') as file:
        for line in file:
            linestr = line.strip().split(",")
            integer_list.append(int(linestr[0]))
    integer_list.sort(reverse=True)
    return integer_list
class Gameplay(BaseState):
    def __init__(self, use_simple):
        super(Gameplay, self).__init__()
        pygame.time.set_timer(ADDENEMY, 450)
        pygame.time.set_timer(ENEMYSHOOTS, 1000)
        pygame.time.set_timer(FREEZE, 2000)

        self.rect = pygame.Rect((0, 0), (80, 80))
        self.next_state = "GAME_OVER"
        self.sprites = spritesheet.SpriteSheet(constants.SPRITE_SHEET)
        self.explosion_sprites = spritesheet.SpriteSheet(constants.SPRITE_SHEET_EXPLOSION)
        self.starfield = StarField()
        self.control_points1 = ControlPointCollectionFactory.create_collection1()
        self.control_points2 = ControlPointCollectionFactory.create_collection2()
        self.control_points3 = ControlPointCollectionFactory.create_collection3()
        self.control_points4 = ControlPointCollectionFactory.create_collection4()
        self.path_point_selector = PathPointSelector(self.control_points1)
        self.path_point_selector.create_path_point_mapping()
        self.mover = ControlHandlerMover(self.control_points1, self.path_point_selector)
        self.control_sprites = pygame.sprite.Group()
        self.add_control_points()
        self.use_simple = use_simple
        if use_simple:
            self.agent = SimpleReflexAgent(self.player, self.enemy_rockets, self.all_enemies)
        self.player = Player(self.sprites, self.use_simple)
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.wave_count = 0
        self.enemies = 0
        self.number_of_enemies = 13
        self.score = 0
        scores = read_scores()
        self.high_score = 0
        if len(scores):
            self.high_score = scores[0]
        self.freeze = False

        self.all_enemies = pygame.sprite.Group()
        self.all_rockets = pygame.sprite.Group()
        self.enemy_rockets = pygame.sprite.Group()
        self.shoot_sound = pygame.mixer.Sound("./assets/sounds/13 Fighter Shot1.mp3")
        self.kill_sound = pygame.mixer.Sound("./assets/sounds/kill.mp3")
        self.show_control = False
        self.mover.align_all()
        self.is_dead = False
        self.total_rocket_shot = 0
        self.rockets_avoided = 0

    def startup(self):
        pygame.mixer.music.load('./assets/sounds/02 Start Music.mp3')
        pygame.mixer.music.play()
        self.use_simple = False
        if self.use_simple:
            self.agent = SimpleReflexAgent(self.player, self.enemy_rockets, self.all_enemies)
        self.player = Player(self.sprites, self.use_simple)
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.wave_count = 0
        self.enemies = 0
        self.number_of_enemies = 10
        self.score = 0
        self.freeze = False
        self.total_rocket_shot = 0

        self.all_enemies = pygame.sprite.Group()
        self.all_rockets = pygame.sprite.Group()
        self.enemy_rockets = pygame.sprite.Group()
        self.shoot_sound = pygame.mixer.Sound("./assets/sounds/13 Fighter Shot1.mp3")
        self.kill_sound = pygame.mixer.Sound("./assets/sounds/kill.mp3")
        self.show_control = False
        self.mover.align_all()
        self.is_dead = False
        self.rockets_avoided = 0

    def add_control_points(self):
        for quartet_index in range(self.control_points1.number_of_quartets()):
            for point_index in range(4):
                quartet = self.control_points1.get_quartet(quartet_index)
                point = quartet.get_point(point_index)
                self.control_sprites.add(ControlPoint(
                    point.x, point.y, (255, 120, 120), quartet_index, point_index,
                    self.control_points1, self.mover))

    def get_event(self, event):
        if self.use_simple:
            if not (self.is_dead or len(self.all_rockets) == 2):
                self.total_rocket_shot += 1
                self.agent.shoot(shoot_fn=self.shoot_rocket)

            if (self.agent.check_boundary()):
                self.agent.move_player()
            else:
                self.agent.reset_player()
        else:
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_LEFT:
                        self.player.update({K_LEFT: True, K_RIGHT: False})

                    case pygame.K_RIGHT:
                        self.player.update({K_LEFT: False, K_RIGHT: True})
        
        for entity in self.all_sprites:
            entity.get_event(event)

        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == ADDENEMY:
            if self.enemies < self.number_of_enemies:
                self.add_enemy()
            elif len(self.all_enemies) == 0:
                self.enemies = 0
                self.wave_count += 1
                if self.wave_count > 2:
                    self.wave_count = 0
        if event.type == ENEMYSHOOTS:
            self.enemy_shoots()
        if event.type == FREEZE:
            if self.freeze:
                self.done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.control_points1.save_control_points()
                self.done = True
            if event.key == pygame.K_s:
                self.show_control = not self.show_control
            if event.key == pygame.K_SPACE:
                if len(self.all_rockets) < 2 and not self.is_dead:
                    self.total_rocket_shot += 1
                    self.shoot_rocket()

        # Get the number of rockets avoided
        for i, rocket in enumerate(self.enemy_rockets):
            if rocket.rect.top >= constants.SCREEN_HEIGHT:
                self.rockets_avoided += 1

    def add_enemy(self):
        self.enemies += 1
        if self.wave_count == 0:
            enemy1 = Enemy(self.sprites, self.control_points1, self.wave_count)
            enemy2 = Enemy(self.sprites, self.control_points2, self.wave_count)
        else:
            enemy1 = Enemy(self.sprites, self.control_points3, self.wave_count)
            enemy2 = Enemy(self.sprites, self.control_points4, self.wave_count)

        self.all_enemies.add(enemy1)
        self.all_sprites.add(enemy1)
        self.all_enemies.add(enemy2)
        self.all_sprites.add(enemy2)

    def shoot_rocket(self):
        rocket = Rocket(self.sprites, 0, -15)
        rocket.rect.centerx = self.player.rect.centerx
        self.all_rockets.add(rocket)
        self.all_sprites.add(rocket)
        self.shoot_sound.play()

    def enemy_shoots(self):
        nr_of_enemies = len(self.all_enemies)
        if nr_of_enemies > 0:
            enemy_index = random.randint(0, nr_of_enemies - 1)
            start_rocket = None
            for index, enemy in enumerate(self.all_enemies):
                if index == enemy_index:
                    start_rocket = enemy.rect.center

            if start_rocket[1] < 400:
                ySpeed = 7
                # get player position to calculate trajectory for rocket
                dx = self.player.rect.centerx - start_rocket[0]
                dy = self.player.rect.centery - start_rocket[1]

                number_of_steps = dy / ySpeed
                xSpeed = dx / number_of_steps

                rocket = Rocket(self.sprites, xSpeed, ySpeed)
                rocket.rect.centerx = start_rocket[0]
                rocket.rect.centery = start_rocket[1]

                # print(rocket, rocket.rect.centerx, rocket.rect.centery)

                self.enemy_rockets.add(rocket)
                self.all_sprites.add(rocket)

    def draw(self, screen, a):
        self.starfield.render(screen)
        pressed_keys = pygame.key.get_pressed()
        for entity in self.all_sprites:
            entity.update(pressed_keys)

        for entity in self.control_sprites:
            entity.update(pressed_keys)

        for entity in self.all_sprites:
            screen.blit(entity.get_surf(), entity.rect)

        if self.show_control:
            for entity in self.control_sprites:
                screen.blit(entity.get_surf(), entity.rect)

            self.drawPath(screen)
            self.draw_control_lines(screen)

        self.draw_score(screen)

        result = pygame.sprite.groupcollide(self.all_rockets, self.all_enemies, True, True)
        if result:
            for key in result:
                self.score += 120
                if self.score > self.high_score:
                    self.high_score = self.score
                self.all_sprites.add(Explosion(self.explosion_sprites, key.rect[0], key.rect[1]))
                self.kill_sound.play()

        result = pygame.sprite.spritecollideany(self.player, self.enemy_rockets)
        if result:
            self.all_sprites.add(Explosion(self.explosion_sprites, result.rect[0], result.rect[1]))
            self.all_sprites.add(Explosion(self.explosion_sprites, result.rect[0] - 30, result.rect[1] - 30))
            self.all_sprites.add(Explosion(self.explosion_sprites, result.rect[0] + 30, result.rect[1] + 30))
            self.all_sprites.add(Explosion(self.explosion_sprites, result.rect[0], result.rect[1] - 30))
            self.kill_sound.play()
            self.freeze = True
            self.player.kill()
            self.is_dead = True
            if self.score > self.high_score:
                self.high_score = self.score

    def drawPath(self, screen):
        calculator = PathPointCalculator()
        bezier_timer = 0
        previous_path_point = None
        while bezier_timer < self.control_points1.number_of_quartets():
            control_point_index = int(bezier_timer)
            path_point = calculator.calculate_path_point(
                self.control_points1.get_quartet(control_point_index), bezier_timer)
            if previous_path_point is None:
                previous_path_point = path_point

            pygame.draw.line(screen, (255, 255, 255), (previous_path_point.xpos,
                             previous_path_point.ypos), (path_point.xpos, path_point.ypos))
            previous_path_point = path_point
            bezier_timer += 0.005

    def draw_control_lines(self, screen):
        for pair in self.path_point_selector.get_control_point_pairs():
            pygame.draw.line(screen, (255, 255, 255), pair[0], pair[1])

    def draw_score(self, screen):
        score = self.font.render('SCORE', True, (255, 20, 20))
        screen.blit(score, (constants.SCREEN_WIDTH / 2 - 300 - score.get_rect().width / 2, 10))
        score = self.font.render(str(self.score), True, (255, 255, 255))
        screen.blit(score, (constants.SCREEN_WIDTH / 2 - 300 - score.get_rect().width / 2, 40))

        score = self.font.render('HIGH SCORE', True, (255, 20, 20))
        screen.blit(score, (constants.SCREEN_WIDTH / 2 - score.get_rect().width / 2, 10))
        score = self.font.render(str(self.high_score), True, (255, 255, 255))
        screen.blit(score, (constants.SCREEN_WIDTH / 2 - score.get_rect().width / 2, 40))
