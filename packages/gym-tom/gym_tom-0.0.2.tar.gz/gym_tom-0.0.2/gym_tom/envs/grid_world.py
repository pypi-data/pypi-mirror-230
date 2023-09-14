# Virtual display
import numpy as np
import pygame
from gym import spaces
import gym

class GridWorldB(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 4}

    def __init__(self, render_mode=None, size=np.array([5, 1])):
        self.size = size
        self.window_size = np.array([500, 100])

        self.observation_space = spaces.Dict({
            "agent": spaces.Discrete(1),
            "target": spaces.Discrete(1),
        })

        self.action_space = spaces.Discrete(2)

        self._action_to_direction = {
            0: np.array([0]),
            1: np.array([1]),
        }

        self._action_to_direction = {
            0: np.array([1, 0]),
            1: np.array([-1, 0]),
        }

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.pix_square_size = self.window_size / self.size

        if render_mode == "human":
            pygame.init()

    def _get_obs(self):
        return {"agent": self._agent_location, "target": self._target_location}

    def _get_info(self):
        return {"distance": np.linalg.norm(self._agent_location - self._target_location, ord=1)}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self._agent_location = np.array([2, 0])
        self._target_location = np.array([4, 0])
        self._obstacle_location = np.array([0, 0])

        observation = self._get_obs()
        info = self._get_info()

        self._render_frame()

        return observation, info

    def step(self, action):
        direction = self._action_to_direction[action]

        self._agent_location = np.clip(
            self._agent_location + direction, 0, self.size - 1
        )

        terminated = np.array_equal(self._agent_location, self._target_location)
        reward = 1 if terminated else 0
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, info

    def render(self):
        if self.render_mode == "human":
            return self._render_frame()

    def _render_frame(self):
        # First we draw the target
        pygame.init()
        pygame.display.init()

        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode(self.window_size)

        canvas = pygame.Surface(self.window_size)
        canvas.fill((255, 255, 255))

        pygame.display.flip()

        position = self.pix_square_size * self._target_location
        pygame.draw.rect(
            canvas,
            (255, 0, 0),
            pygame.Rect(position[0], position[1], self.pix_square_size[0], self.pix_square_size[1]),
        )

        obstacle = self.pix_square_size * self._obstacle_location
        pygame.draw.rect(
            canvas,
            (0, 255, 0),
            pygame.Rect(obstacle[0], obstacle[1], self.pix_square_size[0], self.pix_square_size[1]),
        )

        pygame.draw.circle(
            canvas,
            (0, 0, 255), [(self._agent_location[0] + 0.5) * self.pix_square_size[0],
                          (self._agent_location[1] + 0.5) * self.pix_square_size[1]],
            self.pix_square_size[0] / 3,
        )

        # draw lines
        for x in range(self.size[0] + 1):
            pygame.draw.line(canvas, (0, 0, 0),
                             [self.pix_square_size[0] * x, 0],
                             [self.pix_square_size[0] * x, self.window_size[1]],
                             width=5,
                             )

        for x in range(self.size[1] + 1):
            pygame.draw.line(canvas, (0, 0, 0),
                             [0, self.pix_square_size[1] * x],
                             [self.window_size[0], self.pix_square_size[1] * x],
                             width=5,
                             )

        # Copying our drawings from `canvas` to the visible window
        self.window.blit(canvas, canvas.get_rect())
        pygame.event.pump()
        pygame.display.update()

        # Ensure that human-rendering occurs at the predefined frame rate.
        # Adding a delay to keep the frame rate stable.
        self.clock.tick(self.metadata["render_fps"])

