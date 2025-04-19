import sys
import pygame
import time
import constants
import math
import numpy as np


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
        self.near_misses = 0
        self.player = self.states["GAMEPLAY"].player
        self.time_off_center = time.time()

    def reset(self):
        self.done = False
        self.start_time = time.time()
        self.death_time = time.time()
        self.sethighscore = False
        self.state_name = self.start_state
        self.state = self.states[self.state_name]
        self.near_misses = 0
        self.state.startup()
        self.time_off_center = time.time()

    def event_loop(self):
        self.player = self.states["GAMEPLAY"].player

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

    def _get_near_misses(self):
        danger_zone = 50

        for i, rocket in enumerate(self.states["GAMEPLAY"].enemy_rockets):
            if abs(self.player.rect.centerx - rocket.rect.centerx) <= danger_zone and abs(self.player.rect.centery - rocket.rect.centery) <= danger_zone:
                self.near_misses += 1

        return self.near_misses

    def _get_reward(self):
        enemies_killed = self.states["GAMEPLAY"].score // 120
        shots_fired = self.states["GAMEPLAY"].total_rocket_shot * 5
        rockets_avoided = self.states["GAMEPLAY"].rockets_avoided * 5
        time_elapsed = round(time.time() - self.start_time)
        wave_count = self.states["GAMEPLAY"].wave_number
        center = constants.SCREEN_WIDTH // 2

        # Calculate Rocket Points
        rocket_points = shots_fired + rockets_avoided

        # Calculate points earned for killing an enemy
        enemy_points = math.floor(pow(10, 0.05 * enemies_killed)) + 19

        # Calculate time points
        time_points = math.floor(pow(10, 0.1 * time_elapsed)) - 1

        # Calculate near misses
        near_miss_points = self._get_near_misses() * 10

        # Calculate rewards
        reward = rocket_points + enemy_points + time_points - near_miss_points

        # Reward for reaching next wave
        reward += wave_count * 100       

        # Reward for aiming at enemies
        corner_time = 0
        if abs(self.player.rect.centerx - center) > 100:
            corner_time = round(time.time() - self.time_off_center)
            reward -= corner_time * 15
        else:
            self.time_off_center = time.time()

        print(f"Shots Fired: {shots_fired} Rockets Avoided: {rockets_avoided} Enemies: {enemy_points} Time: {time_points} Near Miss: {-1 * near_miss_points} Waves: {wave_count * 100} Corner: {corner_time}")

        return reward

    def get_info(self):
        return {"Score": self.states["GAMEPLAY"].score, "Time": round(time.time() - self.start_time)}

    def get_obs(self):
        # Convert data into a numpy array
        score = self.get_info()["Score"]
        time_elapsed = self.get_info()["Time"]
        player_data = np.array([self.player.rect.centerx, self.player.rect.centery])
        shots_data = np.full((2, 4), -1)
        enemies_data = np.full((26, 2), -1)
        rockets_data = np.full((26, 4), -1)

        for i, shot in enumerate(self.states["GAMEPLAY"].all_rockets):
            shots_data[i][0] = shot.rect.centerx
            shots_data[i][1] = shot.rect.centery
            shots_data[i][2] = shot.xSpeed
            shots_data[i][3] = shot.ySpeed

        for i, enemy in enumerate(self.states["GAMEPLAY"].all_enemies):
            enemies_data[i][0] = enemy.rect.centerx
            enemies_data[i][1] = enemy.rect.centery

        for i, rocket in enumerate(self.states["GAMEPLAY"].enemy_rockets):
            rockets_data[i][0] = rocket.rect.centerx
            rockets_data[i][1] = rocket.rect.centery
            rockets_data[i][2] = rocket.xSpeed
            rockets_data[i][3] = rocket.ySpeed
        
        observations = np.append([score], np.append([time_elapsed], np.append([player_data], np.append(shots_data, np.append(enemies_data, rockets_data))))).flatten()

        # print(f"Observations: {observations}")

        return observations

    def step(self, action):
        """
        Run one step of the game.
        Returns:
            - Reward (int)
            - Done (bool)
        """
        reward = self._get_reward()

        match action:
            case 1:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
                print(f"Action: LEFT Reward: {reward}")

            case 2:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
                print(f"Action: RIGHT Reward: {reward}")
            
            case 3:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                print(f"Action: SHOOT Reward: {reward}")

            case _:
                print(f"Action: NONE Reward: {reward}")
                None

        dt = self.clock.tick(self.fps)

        pygame.event.set_blocked(pygame.MOUSEMOTION)
        self.event_loop()
        self.update(dt)
        self.draw()
        pygame.display.update()
        
        done = self.done or self.state_name == "GAME_OVER"

        return reward, done

    # def run(self):
    #     while not self.done:
    #         dt = self.clock.tick(self.fps)
    #         pygame.event.set_blocked(pygame.MOUSEMOTION)
    #         self.event_loop()
    #         self.update(dt)
    #         self.draw()
    #         pygame.display.update()