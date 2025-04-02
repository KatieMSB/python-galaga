import pygame
import random
from pygame.locals import (
    K_LEFT,
    K_RIGHT,
)

class SimpleReflexAgent:
    def __init__(self, player, rockets, enemies, danger_zone=150):
        self.player = player
        self.rockets = rockets
        self.enemies = enemies
        self.danger_zone = danger_zone
        self.danger_up = False
        self.danger_down = False
        self.danger_left = False
        self.danger_right = False

    def get_event(self, event):
        pass

    def check_boundary(self):
        print(len(self.rockets))

        for rocket in self.rockets:
            distance_x = rocket.rect.centerx - self.player.rect.centerx
            distance_y = rocket.rect.centery - self.player.rect.centery

            if abs(distance_x) < self.danger_zone and abs(distance_y) < self.danger_zone:
                self.danger_left = distance_x < 0
                self.danger_right = distance_x > 0
                self.danger_up = abs(distance_x) < self.danger_zone // 2
                return True
        return False

    def move_player(self):
        if self.danger_up:
            print("DANGER UP")
            if self.danger_left:
                self.player.update({K_LEFT: False, K_RIGHT: True})
            self.player.update({K_LEFT: True, K_RIGHT: False})
        if self.danger_left:
            print("DANGER LEFT")
            self.player.update({K_LEFT: False, K_RIGHT: True})
        if self.danger_right:
            print("DANGER RIGHT")
            self.player.update({K_LEFT: True, K_RIGHT: False})

    def reset_player(self):
        print(self.enemies)
        # reset to center of screen
        width, _ = pygame.display.get_surface().get_size()
        center = width / 2
        if len(self.enemies):
            count = 0
            # pick the first enemy
            # for enemy in self.enemies:
            #     center = enemy.rect.x
            #     break
            # pick the last enemy
            # for enemy in self.enemies:
            #     if count == len(self.enemies) - 1:
            #         center = enemy.rect.x
            #     count += 1
            # pick a random enemy
            random_int = random.randint(0, len(self.enemies) - 1)
            for enemy in self.enemies:
                if count == random_int:
                    center = enemy.rect.x
                count += 1
        if self.player.rect.x > center:
            self.player.update({K_LEFT: True, K_RIGHT: False})
        if self.player.rect.x < center:
            self.player.update({K_LEFT: False, K_RIGHT: True})
        