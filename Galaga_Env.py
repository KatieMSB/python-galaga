import numpy as np
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from typing import Optional
import gymnasium as gym
from gymnasium import spaces, register
import constants
from states.gameplay import Gameplay
from states.game_over import GameOver
from game import Game

class GalagaEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb-array"], "render_fps": 60}

    def __init__(self, render_mode=None):
        self.render_mode = render_mode

        # Define the agent and target location; randomly chosen in `reset` and updated in `step`
        self._agent_location = np.array([constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT - 40], dtype=np.int32)

        # Observations are dictionaries with the agent's and the target's location.
        # Each location is encoded as an element of {0, ..., `size`-1}^2
        self.observation_space = spaces.Box(
            low = np.array([0, 0], dtype = np.float32),
            high = np.array([constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT], dtype = np.float32),
            dtype = np.float32
        )

        # We have 3 actions, corresponding to "right", "left", "shoot"
        self.action_space = gym.spaces.Discrete(4)

    def _init_game(self):
        pygame.init()
        
        if self.render_mode == "rgb-array":
            self.screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), flags=pygame.HIDDEN)
        else:
            self.screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()

        states = {
            "GAMEPLAY": Gameplay(False, self.render_mode),
            "GAME_OVER": GameOver()
        }

        self.game = Game(self.screen, states, "GAMEPLAY")
        self.game.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._init_game()
        obs = self._get_obs()
        info = {}
        return obs, info

    def _get_obs(self):
        # return pygame.surfarray.array3d(self.screen).swapaxes(0, 1)
        return self.game.get_obs()
    
    def _get_info(self):
        return self.game.get_info()

    def step(self, action):
        # Map the action (element of {0,1,2,3}) to the direction we walk in
        match action:
            case 1:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))

            case 2:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
            
            case 3:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))

            case _:
                None

        reward, done = self.game.step(action)
        obs = self._get_obs()
        truncated = False
        info = self._get_info()

        return obs, reward, done, truncated, info
    
    def render(self):
        if self.render_mode == "human":
            pygame.display.flip()
        elif self.render_mode == "rgb-array":
            return self._get_obs()
        
    def close(self):
        pygame.quit()

register (
    id = 'Galaga-v0',
    entry_point = GalagaEnv,
)