# Sebastian Thomas (coding at sebastianthomas dot de)

# randomization
from random import choice

# python gaming framework
from pygame import init as init_pygame, quit as quit_pygame
from pygame.constants import QUIT, KEYDOWN, K_LEFT, K_RIGHT
from pygame.display import set_mode as set_mode_of_screen, \
    flip as flip_screen, set_caption as set_caption_of_screen
from pygame.rect import Rect
from pygame.draw import circle as draw_circle, rect as draw_rect
from pygame.event import get as get_event
from pygame.time import Clock, wait


# constants
FRAMES_PER_SECOND = 120
RESTART_TIME = 1000

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 480
WINDOW_COLOR = 0, 0, 0  # black

MAX_VELOCITY = 2

PADDLE_TOP = 450  # y-coordinate of upper left corner
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_COLOR = 255, 40, 0  # red

BALL_RADIUS = 15
BALL_VELOCITY_CHOICES = tuple(v for v in range(-MAX_VELOCITY, MAX_VELOCITY + 1)
                              if v != 0)
BALL_COLOR = 255, 255, 0  # yellow


class PongSquash:
    """Class that implements a single player variant of the classical arcade
    game Pong by Atari."""

    class Paddle(Rect):
        """Internal paddle class for Pong."""

        def __init__(self, left, top=PADDLE_TOP, width=PADDLE_WIDTH,
                     height=PADDLE_HEIGHT, velocity=0, color=PADDLE_COLOR):
            """Initializes paddle."""
            super().__init__(left, top, width, height)
            self._velocity = velocity
            self._color = color

        @property
        def velocity(self):
            """Returns the velocity of this instance."""
            return self._velocity

        @velocity.setter
        def velocity(self, value):
            """Updates the velocity of this instance."""
            self._velocity = value

        @property
        def color(self):
            """Returns the color of this instance."""
            return self._color

    class Ball(Rect):
        """Internal ball class for Pong."""

        def __init__(self, center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2),
                     radius=BALL_RADIUS, velocity=(0, 0), color=BALL_COLOR):
            """Initializes ball."""
            # in pygame, circles are defined by their bounding rectangles
            super().__init__(center[0] - radius, center[1] - radius, 2*radius,
                             2*radius)
            self._velocity = velocity
            self._color = color

        @property
        def center_x(self):
            """Returns the x-coordinate of the center of this instance."""
            return self.left + self.radius

        @center_x.setter
        def center_x(self, value):
            """Updates the x-coordinate of the center of this instance."""
            self.left = value - self.radius

        @property
        def center_y(self):
            """Returns the y-coordinate of the center of this instance."""
            return self.top + self.radius

        @center_y.setter
        def center_y(self, value):
            """Updates the y-coordinate of the center of this instance."""
            self.left = value - self.radius

        @property
        def radius(self):
            """Returns the radius of this instance."""
            return self.width // 2

        @property
        def velocity(self):
            """Returns the velocity of this instance."""
            return self._velocity

        @velocity.setter
        def velocity(self, value):
            """Updates the velocity of this instance."""
            self._velocity = value

        @property
        def velocity_x(self):
            """Returns the x-coordinate of the velocity of this instance."""
            return self._velocity[0]

        @velocity_x.setter
        def velocity_x(self, value):
            """Updates the x-coordinate of the velocity of this instance."""
            self._velocity = value, self._velocity[1]

        @property
        def velocity_y(self):
            """Returns the y-coordinate of the velocity of this instance."""
            return self._velocity[1]

        @velocity_y.setter
        def velocity_y(self, value):
            """Updates the y-coordinate of the velocity of this instance."""
            self._velocity = self._velocity[0], value

        @property
        def color(self):
            """Returns the color of this instance."""
            return self._color

    def __init__(self):
        """Initializes single player variant of Pong game."""
        init_pygame()
        self._screen = set_mode_of_screen(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        set_caption_of_screen('1-Player Pong')

        self._paddle = self.Paddle((WINDOW_WIDTH - PADDLE_WIDTH) // 2)
        self._ball = self.Ball(velocity=(choice(BALL_VELOCITY_CHOICES),
                                         choice(BALL_VELOCITY_CHOICES)))
        self._n_lives = 3

    def _redraw_screen(self):
        """Redraws the screen."""
        # fill background with window color
        self._screen.fill(WINDOW_COLOR)

        # draw paddle and ball
        draw_rect(self._screen, self._paddle.color, self._paddle)
        draw_circle(self._screen, self._ball.color, self._ball.center,
                    self._ball.radius)

        # update whole screen
        flip_screen()

    def _handle_wall_collision(self):
        """Handles collisions of the paddle and of the ball with the walls
        at the left, right and top of the screen, as well as the reset after
        the ball leaves the bottom of the screen."""
        # collision of paddle with left wall
        if self._paddle.left < 0:
            self._paddle.left = 0
        # collision of paddle with right wall
        if self._paddle.right > WINDOW_WIDTH:
            self._paddle.right = WINDOW_WIDTH
        # collision of ball with left wall
        if self._ball.left < 0:
            self._ball.left = 0
            self._ball.velocity_x *= -1
        # collision of ball with right wall
        if self._ball.right > WINDOW_WIDTH:
            self._ball.right = WINDOW_WIDTH
            self._ball.velocity_x *= -1
        # collision of ball with top wall
        if self._ball.top < 0:
            self._ball.top = 0
            self._ball.velocity_y *= -1
        # ball leaves bottom
        if self._ball.top > WINDOW_HEIGHT:
            self._n_lives -= 1
            self._reset()

    def _handle_paddle_ball_collision(self):
        """Handles collisions of the ball with the paddle."""
        if self._paddle.colliderect(self._ball):
            self._ball.velocity_y *= -1
            if self._paddle.left <= self._ball.center_x <= self._paddle.right:
                self._ball.bottom = self._paddle.top

    def _move_paddle_and_ball(self):
        """Updates coordinates of the paddle and the ball to the values after
        one time step."""
        # update paddle
        self._paddle.left += self._paddle.velocity
        # update ball
        self._ball.left += self._ball.velocity_x
        self._ball.top += self._ball.velocity_y

    def _reset(self):
        """Resets the properties of the paddle and of the ball to their
        initial values, respectively, and redraws the screen."""
        # reset paddle
        self._paddle.left = (WINDOW_WIDTH - PADDLE_WIDTH) // 2
        self._paddle.velocity = 0
        # reset ball
        self._ball.center = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self._ball.velocity_x = choice(BALL_VELOCITY_CHOICES)
        self._ball.velocity_y = choice(BALL_VELOCITY_CHOICES)

        # redraw screen
        self._redraw_screen()

        # wait until game continues
        wait(RESTART_TIME)

    def run(self):
        """Runs the instance."""
        clock = Clock()

        while self._n_lives > 0:
            # check for events
            for event in get_event():
                # clicking quit button of window kills the game
                if event.type == QUIT:
                    quit_pygame()

                # clicking key board button to move paddle
                if event.type == KEYDOWN:
                    # button is left arrow key
                    if event.key == K_LEFT:
                        self._paddle.velocity = -MAX_VELOCITY
                    # button is right arrow key
                    elif event.key == K_RIGHT:
                        self._paddle.velocity = MAX_VELOCITY

            # redraw screen
            self._redraw_screen()

            # update coordinates of paddle and ball
            self._move_paddle_and_ball()

            # handle collisions of paddle with walls and of ball with
            # walls and paddle
            self._handle_wall_collision()
            self._handle_paddle_ball_collision()

            # set count of updates
            clock.tick(FRAMES_PER_SECOND)

        quit_pygame()


if __name__ == '__main__':
    PongSquash().run()
