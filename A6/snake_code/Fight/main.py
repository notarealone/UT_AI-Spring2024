from utility import *
from cube import *
import pygame
import numpy as np
from tkinter import messagebox
from snake_1 import Snake as Snake_1
from snake_2 import Snake as Snake_2
import matplotlib.pyplot as plt
from tqdm import tqdm


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))

    snake_1 = Snake_1((255, 0, 0), (random.randint(1, ROWS-2), random.randint(1, ROWS-2)), SNAKE_1_Q_TABLE)
    snake_2 = Snake_2((255, 255, 0), (random.randint(1, ROWS-2), random.randint(1, ROWS-2)), SNAKE_2_Q_TABLE)
    snake_1.addCube()
    snake_2.addCube()

    snack = Cube(randomSnack(ROWS-1, snake_1), color=(0, 255, 0))

    clock = pygame.time.Clock()
    redrawWindow(snake_1, snake_2, snack, win)
    episodes = 500  # Number of episodes for training
    winners = {"snake_1": 0, "snake_2": 0}  # List to store rewards for plotting
    winners_com = []

    for episode in tqdm(range(episodes), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):

        while True:
            pygame.time.delay(1)
            clock.tick(1000)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    if messagebox.askokcancel("Quit", "Do you want to save the Q-tables?"):
                        save(snake_1, snake_2)
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    np.save(SNAKE_1_Q_TABLE, snake_1.q_table)
                    np.save(SNAKE_2_Q_TABLE, snake_2.q_table)
                    pygame.time.delay(1000)

            state_1, new_state_1, action_1 = snake_1.move(snack, snake_2)
            state_2, new_state_2, action_2 = snake_2.move(snack, snake_1)

            snack, reward_1, win_1_by1, win_2_by1 = snake_1.calc_reward(snack, snake_2)
            snack, reward_2, win_2_by2, win_1_by2 = snake_2.calc_reward(snack, snake_1)

            redrawWindow(snake_1, snake_2, snack, win)

            if win_1_by2 or win_1_by1:
                winners["snake_1"] += 1
            if win_2_by2 or win_2_by1:
                winners["snake_2"] += 1

            if win_1_by2 or win_1_by1 or win_2_by2 or win_2_by1:
                reset(snake_1, snake_2)
                break

        winners_com.append((winners['snake_1'], winners['snake_2']))

    pygame.quit()
    print(f"Snake_1 Score {winners['snake_1']}\nSnake_2 Score {winners['snake_2']}")
    # Plot the rewards
    winners_1, winners_2 = zip(*winners_com)
    plt.plot(winners_1, label="Snake 1")
    plt.plot(winners_2, label="Snake 2")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.legend()
    plt.show()



if __name__ == "__main__":
    main()
