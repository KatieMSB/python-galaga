import sys
import pygame
import constants


class Game(object):
    def __init__(self, screen, states, start_state):
        self.done = False
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.fps = constants.FPS
        self.states = states
        self.state_name = start_state
        self.state = self.states[self.state_name]
        self.sethighscore = False


    def event_loop(self):
        if self.state_name == "GAME_OVER" and not self.sethighscore:
            self.sethighscore = True
            with open("highscores.txt","a") as f:
                f.write(str(self.states["GAMEPLAY"].score)+","+str(self.clock.get_time())+"\n")
        
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

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.state.draw(self.screen)

    def run(self):
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pygame.display.update()