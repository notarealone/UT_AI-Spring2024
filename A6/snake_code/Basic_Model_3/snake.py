from cube import Cube
from constants import *
from utility import *
import random
import numpy as np


class Snake:
    body = []
    turns = {}

    def __init__(self, color, pos, file_name=None):
        # pos is given as coordinates on the grid ex (1,5)
        self.color = color
        self.head = Cube(pos, color=color)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1
        try:
            self.q_table = np.load(file_name)
        except:
            self.q_table = np.zeros((8, 16, 4))  # Initialize Q-table
            #  (snack direction, danger possibility, action)

        self.lr = 0.05
        self.discount_factor = 1
        self.epsilon = 0.9
        self.epsilon_decay = 0.9997  # Epsilon decay for further runs
        self.min_epsilon = 0.01

    def get_optimal_policy(self, state):
        return np.argmax(self.q_table[state[0], state[1]])  # Get optimal policy

    def make_action(self, state):
        chance = random.random()
        if chance < self.epsilon:
            action = random.randint(0, 3)
        else:
            action = self.get_optimal_policy(state)
        return action

    def update_q_table(self, state, action, next_state, reward):
        self.q_table[state[0], state[1], action] = (1-self.lr)*self.q_table[state[0], state[1], action] + self.lr*(reward + self.discount_factor*np.max(self.q_table[next_state[0], next_state[1]]))

    def snack_relative_location(self, snack):
        if self.head.pos[0] == snack.pos[0]:
            if self.head.pos[1] > snack.pos[1]:
                return 0
            else:
                return 1
        if self.head.pos[0] > snack.pos[0]:
            if self.head.pos[1] < snack.pos[1]:
                return 2
            elif self.head.pos[1] == snack.pos[1]:
                return 3
            else:
                return 4
        else:
            if self.head.pos[1] < snack.pos[1]:
                return 5
            elif self.head.pos[1] == snack.pos[1]:
                return 6
            else:
                return 7

    def observe_obstacles(self, other_snake):
        obstacles = 0  # Initialize the obstacles variable to store the 4-bit representation
        head_x, head_y = self.head.pos

        # Check left
        if head_x == 1 or (head_x - 1, head_y) in [cube.pos for cube in self.body] or (head_x - 1, head_y) in [cube.pos for cube in other_snake.body]:
            obstacles += 8  # Set the first bit (2^3)

        # Check right
        if head_x == ROWS - 2 or (head_x + 1, head_y) in [cube.pos for cube in self.body] or (head_x + 1, head_y) in [cube.pos for cube in other_snake.body]:
            obstacles += 4  # Set the second bit (2^2)

        # Check up
        if head_y == 1 or (head_x, head_y - 1) in [cube.pos for cube in self.body] or (head_x, head_y - 1) in [cube.pos for cube in other_snake.body]:
            obstacles += 2  # Set the third bit (2^1)

        # Check down
        if head_y == ROWS - 2 or (head_x, head_y + 1) in [cube.pos for cube in self.body] or (head_x, head_y + 1) in [cube.pos for cube in other_snake.body]:
            obstacles += 1  # Set the fourth bit (2^0)

        return obstacles

    # def observe_obstacles(self, other_snake):
    #     obstacles = 0
    #     head_x, head_y = self.head.pos
    #
    #     # Define the relative positions in the 3x3 grid around the head
    #     directions = [
    #         (-1, -1), (0, -1), (1, -1),  # Top-left, top, top-right
    #         (-1, 0), (1, 0),  # Left,     center, right
    #         (-1, 1), (0, 1), (1, 1)  # Bottom-left, bottom, bottom-right
    #     ]
    #
    #     for idx, (dx, dy) in enumerate(directions):
    #         x, y = head_x + dx, head_y + dy
    #
    #         # Check if the cell is a wall
    #         if x < 0 or x >= ROWS or y < 0 or y >= ROWS:
    #             obstacles |= (1 << idx)
    #         # Check if the cell is part of this snake's body
    #         elif (x, y) in [cube.pos for cube in self.body]:
    #             obstacles |= (1 << idx)
    #         # Check if the cell is part of the other snake's body
    #         elif (x, y) in [cube.pos for cube in other_snake.body]:
    #             obstacles |= (1 << idx)
    #
    #     return obstacles

    def create_state(self, snack, other_snake):
        state = [
            self.snack_relative_location(snack),
            self.observe_obstacles(other_snake)
        ]
        return state

    def move(self, snack, other_snake):
        state = self.create_state(snack, other_snake)
        action = self.make_action(state)

        if action == 0: # Left
            self.dirnx = -1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 1: # Right
            self.dirnx = 1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 2: # Up
            self.dirny = -1
            self.dirnx = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 3: # Down
            self.dirny = 1
            self.dirnx = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                c.move(c.dirnx, c.dirny)

        new_state = self.create_state(snack, other_snake)
        return state, new_state, action

    def check_out_of_board(self):
        headPos = self.head.pos
        if headPos[0] >= ROWS - 1 or headPos[0] < 1 or headPos[1] >= ROWS - 1 or headPos[1] < 1:
            self.reset((random.randint(1, ROWS-2), random.randint(1, ROWS-2)))
            return True
        return False

    def calc_reward(self, snack, other_snake):
        reward = 0
        win_self, win_other = False, False
        
        if self.check_out_of_board():
            reward = -100  # Punish the snake for getting out of the board
            win_other = True
            #reset(self, other_snake)

        if self.head.pos == snack.pos:
            self.addCube()
            snack = Cube(randomSnack(ROWS, self), color=(0, 255, 0))
            reward = 40  # Reward the snake for eating

        if self.head.pos in list(map(lambda z: z.pos, self.body[1:])):
            reward = -100  # Punish the snake for hitting itself
            win_other = True
            #reset(self, other_snake)

        if self.head.pos in list(map(lambda z: z.pos, other_snake.body)):
            
            if self.head.pos != other_snake.head.pos:
                reward = -100  # Punish the snake for hitting the other snake
                win_other = True
            else:
                if len(self.body) > len(other_snake.body):
                    reward = 5  # Reward the snake for hitting the head of the other snake and being longer
                    win_self = True
                elif len(self.body) == len(other_snake.body):
                    reward = 0  # No winner
                else:
                    reward = -100  # Punish the snake for hitting the head of the other snake and being shorter
                    win_other = True
                    
            #reset(self, other_snake)
            
        return snack, reward, win_self, win_other
    
    def reset(self, pos):
        self.head = Cube(pos, color=self.color)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1
        self.epsilon = self.epsilon_decay*self.epsilon if self.epsilon > self.min_epsilon else self.min_epsilon


    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(Cube((tail.pos[0] - 1, tail.pos[1]), color=self.color))
        elif dx == -1 and dy == 0:
            self.body.append(Cube((tail.pos[0] + 1, tail.pos[1]), color=self.color))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] - 1), color=self.color))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] + 1), color=self.color))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)

    def save_q_table(self, file_name):
        np.save(file_name, self.q_table)
        