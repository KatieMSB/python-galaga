import sys
import pygame
import multiprocessing
from states.menu import Menu
from states.gameplay import Gameplay
from states.game_over import GameOver
from states.splash import Splash
from game import Game
import constants

def run_game():
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    states = {
        # "MENU": Menu(),
        # "SPLASH": Splash(),
        "GAMEPLAY": Gameplay(),
        "GAME_OVER": GameOver(),
    }

    game = Game(screen, states, "GAMEPLAY")
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn") 
    
    num_games = 20
    processes = []

    for _ in range(num_games):
        p = multiprocessing.Process(target=run_game)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
