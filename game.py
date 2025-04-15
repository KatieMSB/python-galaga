import sys
import pygame
import time
import constants
import math


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
        self.start_state = start_state
        self.state = self.states[self.state_name]
        self.sethighscore = False

    def reset(self):
        self.done = False
        self.start_time = time.time()
        self.death_time = time.time()
        self.sethighscore = False
        self.state_name = self.start_state
        self.state = self.states[self.state_name]
        self.state.startup()

    def event_loop(self):
        if self.state_name == "GAME_OVER" and not self.sethighscore:
            self.sethighscore = True
            self.death_time = round(time.time() - self.start_time)
            with open("highscores.txt","a") as f:
                f.write(str(self.states["GAMEPLAY"].score)+","+str(self.death_time)+"\n")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            else:
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
        ttd = round(time.time() - self.start_time)
        if shots > 0:
            accuracy =  round(((self.states["GAMEPLAY"].score // 120) / self.states["GAMEPLAY"].total_rocket_shot) * 100)
        metrics = [self.states["GAMEPLAY"].score, ttd, self.states["GAMEPLAY"].score // 120, shots, accuracy ]
        return metrics

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.state.draw(self.screen, self.final_metrics())

    def _get_reward(self):
        # Get total time alive
        time_elapsed = round(time.time() - self.start_time)

        # Calculate points earned for killing an enemy
        enemy_points = self.states["GAMEPLAY"].score // 120

        # Calculate time points
        time_points = math.floor(pow(10, 0.01 * time_elapsed)) - 1
        # time_points = math.sqrt(0.01 * time_elapsed)

        # Calculate rewards
        reward = enemy_points + time_points

        return reward

    def step(self, action):
        """
        Run one step of the game.
        Returns:
            - Reward (int)
            - Done (bool)
        """
        match action:
            case 1:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))

            case 2:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
            
            case 3:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))

            case _:
                None

        dt = self.clock.tick(self.fps)

        pygame.event.set_blocked(pygame.MOUSEMOTION)
        self.event_loop()
        self.update(dt)
        self.draw()
        pygame.display.update()
        
        reward = self._get_reward()
        done = self.done or self.state_name == "GAME_OVER"

        print(f"Action: {action} Reward: {reward}")

        return reward, done

    # def run(self):
    #     while not self.done:
    #         dt = self.clock.tick(self.fps)
    #         pygame.event.set_blocked(pygame.MOUSEMOTION)
    #         self.event_loop()
    #         self.update(dt)
    #         self.draw()
    #         pygame.display.update()