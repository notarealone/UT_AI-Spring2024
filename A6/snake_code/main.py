from utility import *
from cube import *
import pygame
import numpy as np
from tkinter import messagebox
from snake import Snake
import matplotlib.pyplot as plt
from tqdm import tqdm


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))

    snake_1 = Snake((255, 0, 0), (random.randint(1, ROWS-2), random.randint(1, ROWS-2)), SNAKE_1_Q_TABLE)
    snake_2 = Snake((255, 255, 0), (random.randint(1, ROWS-2), random.randint(1, ROWS-2)), SNAKE_2_Q_TABLE)
    snake_1.addCube()
    snake_2.addCube()

    snack = Cube(randomSnack(ROWS-1, snake_1), color=(0, 255, 0))

    clock = pygame.time.Clock()
    redrawWindow(snake_1, snake_2, snack, win)
    episodes = 100  # Number of episodes for training
    rewards = []  # List to store rewards for plotting

    for episode in tqdm(range(episodes), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        total_reward_1 = 0
        total_reward_2 = 0

        while True:
            #print(snake_1.epsilon)
            reward_1 = 0
            reward_2 = 0
            pygame.time.delay(1)
            clock.tick(50000)

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

            snake_1.update_q_table(state_1, action_1, new_state_1, reward_1)
            snake_2.update_q_table(state_2, action_2, new_state_2, reward_2)

            total_reward_1 += reward_1
            total_reward_2 += reward_2

            redrawWindow(snake_1, snake_2, snack, win)

            if (win_1_by2 or win_1_by1) or (win_2_by2 or win_2_by1):
                reset(snake_1, snake_2)
                break

        rewards.append((total_reward_1, total_reward_2))

    np.save(SNAKE_1_Q_TABLE, snake_1.q_table)
    np.save(SNAKE_2_Q_TABLE, snake_2.q_table)

    pygame.quit()
    print(snake_1.epsilon)
    # Plot the rewards
    rewards_1, rewards_2 = zip(*rewards)
    plt.plot(rewards_1, label="Snake 1")
    plt.plot(rewards_2, label="Snake 2")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.legend()
    plt.show()



if __name__ == "__main__":
    main()
