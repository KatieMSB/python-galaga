import sys
import pygame
import time
import constants


class Game(object):
    def __init__(self, screen, states, start_state):
        self.done = False
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.fps = constants.FPS
        self.states = states
        self.start_time = time.time()
        self.death_time = time.time()
        self.state_name = start_state
        self.state = self.states[self.state_name]
        self.sethighscore = False


    def event_loop(self):
        if self.state_name == "GAME_OVER" and not self.sethighscore:
            self.sethighscore = True
            self.death_time = round(time.time() - self.start_time)
            with open("highscores.txt","a") as f:
                f.write(str(self.states["GAMEPLAY"].score)+","+str(self.death_time)+"\n")
        
        for event in pygame.event.get():
            self.state.get_event(event)

    def flip_state(self):
        next_state = self.state.next_state
        self.state.done = False
        self.state_name = next_state
        self.state = self.states[self.state_name]
        self.state.startup()

    def update(self, dt):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(dt)

    def final_metrics(self):
        accuracy = 0
        shots = self.states["GAMEPLAY"].total_rocket_shot
        if shots > 0:
            accuracy =  round(((self.states["GAMEPLAY"].score // 120) / self.states["GAMEPLAY"].total_rocket_shot) * 100)
        metrics = [self.states["GAMEPLAY"].score, self.death_time, self.states["GAMEPLAY"].score // 120, shots, accuracy ]
        return metrics

    def draw(self):
        self.screen.fill((0, 0, 0))
        print("draw", self.state_name)
        self.state.draw(self.screen, self.final_metrics())

    def run(self):
        while not self.done:
            dt = self.clock.tick(self.fps)
            pygame.event.set_blocked(pygame.MOUSEMOTION)
            self.event_loop()
            self.update(dt)
            self.draw()
            pygame.display.update()