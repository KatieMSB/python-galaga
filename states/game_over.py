import pygame
from .base_state import BaseState


class GameOver(BaseState):
    def __init__(self):
        super(GameOver, self).__init__()
        self.title = self.font.render("Game Over", True, pygame.Color("white"))
        self.title_rect = self.title.get_rect(center=self.screen_rect.center)
        self.instructions = self.font.render(
            "Press R to start again, or enter to go to the menu",
            True, pygame.Color("white"))
        instructions_center = (
            self.screen_rect.center[0], self.screen_rect.center[1] + 50)
        self.instructions_rect = self.instructions.get_rect(
            center=instructions_center)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN:
                self.next_state = "MENU"
                self.done = True
            elif event.key == pygame.K_r:
                self.next_state = "GAMEPLAY"
                self.done = True
            elif event.key == pygame.K_ESCAPE:
                self.quit = True

    def draw(self, surface, metrics):
        surface.fill(pygame.Color("black"))

        score_str = f'Score: {metrics[0]}'
        score = self.font.render(score_str, True, pygame.Color("white"))
        score_rectangle = score.get_rect(center=self.screen_rect.center)

        ttd_str = f'TTD: {metrics[1]} Seconds'
        ttd = self.font.render(ttd_str, True, pygame.Color("white"))
        ttd_center = (score_rectangle.center[0], score_rectangle.center[1] + 50)
        ttd_square = ttd.get_rect(
            center=ttd_center)
        
        enemies_str = f'Enemies Killed: {metrics[2]}'
        enemies = self.font.render(enemies_str, True, pygame.Color("white"))
        enemies_center = (ttd_square.center[0], ttd_square.center[1] + 50)
        enemies_square = enemies.get_rect(
            center=enemies_center)
        
        shots_str = f'Shots Shotted: {metrics[3]}'
        shots = self.font.render(shots_str, True, pygame.Color("white"))
        shots_center = (enemies_square.center[0], enemies_square.center[1] + 50)
        shots_square = shots.get_rect(
            center=shots_center)
        
        accuracy_str = f'Accuracy: {metrics[4]}%'
        accuracy = self.font.render(accuracy_str, True, pygame.Color("white"))
        accuracy_center = (shots_square.center[0], shots_square.center[1] + 50)
        accuraacy_square = accuracy.get_rect(
            center=accuracy_center)
        
        surface.blit(score, score_rectangle)
        surface.blit(ttd, ttd_square)
        surface.blit(enemies, enemies_square)
        surface.blit(shots, shots_square)
        surface.blit(accuracy, accuraacy_square)
