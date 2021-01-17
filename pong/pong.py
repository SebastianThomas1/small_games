# Sebastian Thomas (coding at sebastianthomas dot de)

# randomization
from random import choice

# python gaming framework
from pygame import init as init_pygame, quit as quit_pygame, \
    get_init as pygame_is_active
from pygame.constants import QUIT, KEYDOWN, KEYUP, K_w, K_s, K_UP, K_DOWN
from pygame.display import set_mode as set_mode_of_screen, \
    flip as flip_screen, set_caption as set_caption_of_screen
from pygame.font import init as init_pygame_fonts, SysFont
from pygame.rect import Rect
from pygame.draw import circle as draw_circle, rect as draw_rect, \
    line as draw_line
from pygame.event import get as get_event
from pygame.math import Vector2
from pygame.time import Clock, wait


# constants
FRAMES_PER_SECOND = 120
RESTART_TIME = 1000

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WINDOW_COLOR = 0, 0, 0  # black

init_pygame_fonts()
FONT = SysFont('couriernewbold', 50, bold=False)
FONT_COLOR = 255, 255, 255  # white

SCORE1_LABEL_LEFT \
    = (WINDOW_WIDTH - 2*FONT.render('00', True, FONT_COLOR).get_width()) // 4
SCORE2_LABEL_LEFT \
    = (3*WINDOW_WIDTH - 2*FONT.render('00', True, FONT_COLOR).get_width()) // 4
SCORE_LABELS_TOP = 10
SCORE1_LABEL_POSITION = SCORE1_LABEL_LEFT, SCORE_LABELS_TOP
SCORE2_LABEL_POSITION = SCORE2_LABEL_LEFT, SCORE_LABELS_TOP
WINNER_LABEL = FONT.render('PLAYER 0 WON', True, FONT_COLOR)
WINNER_LABEL_POSITION = (WINDOW_WIDTH - WINNER_LABEL.get_width()) // 2, \
                        (WINDOW_HEIGHT - WINNER_LABEL.get_height()) // 2

NET_X = WINDOW_WIDTH // 2
NET_COLOR = 211, 211, 211

MIN_VELOCITY = 3
MAX_VELOCITY = 5

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE1_INITIAL_LEFT = 50  # x-coordinate of upper left corner
PADDLE2_INITIAL_LEFT = WINDOW_WIDTH - PADDLE_WIDTH - 50
PADDLES_INITIAL_TOP = (WINDOW_HEIGHT - PADDLE_HEIGHT) // 2
PADDLE_COLOR = 255, 40, 0  # red

BALL_INITIAL_CENTER = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
BALL_RADIUS = 15
BALL_VELOCITY_CHOICES = tuple(v for v in range(-MAX_VELOCITY, MAX_VELOCITY + 1)
                              if abs(v) >= MIN_VELOCITY)
BALL_COLOR = 255, 255, 0  # yellow


def draw_dashed_line(surface, color, start_pos, end_pos, width=1,
                     dash_length=10):
    origin = Vector2(start_pos)
    target = Vector2(end_pos)
    displacement = target - origin
    length = displacement.length()
    slope = displacement / length

    for index in range(0, int(length / dash_length), 2):
        start = origin + (slope * index * dash_length)
        end = origin + (slope * (index + 1) * dash_length)
        draw_line(surface, color, start, end, width)


class Pong:
    """Class that implements the classical arcade game Pong by Atari."""

    class Paddle(Rect):
        """Internal paddle class for Pong."""

        def __init__(self, left, top, width=PADDLE_WIDTH,
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

        def __init__(self, center=BALL_INITIAL_CENTER, radius=BALL_RADIUS,
                     velocity=(0, 0), color=BALL_COLOR):
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
        """Initializes Pong game."""
        init_pygame()
        self._screen = set_mode_of_screen(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        set_caption_of_screen('Pong')

        self._paddle1 = self.Paddle(PADDLE1_INITIAL_LEFT, PADDLES_INITIAL_TOP)
        self._paddle2 = self.Paddle(PADDLE2_INITIAL_LEFT, PADDLES_INITIAL_TOP)
        self._ball = self.Ball(velocity=(choice(BALL_VELOCITY_CHOICES),
                                         choice(BALL_VELOCITY_CHOICES)))

        self._score1 = 0
        self._score2 = 0

        self._is_active = True

    @property
    def _label1(self):
        return FONT.render('{:2d}'.format(self._score1), True, FONT_COLOR)

    @property
    def _label2(self):
        return FONT.render('{:2d}'.format(self._score2), True, FONT_COLOR)

    def _redraw_screen(self):
        """Redraws the screen."""
        # fill background with window color
        self._screen.fill(WINDOW_COLOR)

        # draw labels
        self._screen.blit(self._label1, SCORE1_LABEL_POSITION)
        self._screen.blit(self._label2, SCORE2_LABEL_POSITION)

        # draw net
        draw_dashed_line(self._screen, NET_COLOR, (NET_X, 0),
                         (NET_X, WINDOW_HEIGHT))

        # draw paddles and ball
        draw_rect(self._screen, self._paddle1.color, self._paddle1)
        draw_rect(self._screen, self._paddle2.color, self._paddle2)
        draw_circle(self._screen, self._ball.color, self._ball.center,
                    self._ball.radius)

        # update whole screen
        flip_screen()

    def _move_paddles_and_ball(self):
        """Updates coordinates of the paddles and of the ball to the values
        after one time step."""
        # update paddles
        self._paddle1.top += self._paddle1.velocity
        self._paddle2.top += self._paddle2.velocity
        # update ball
        self._ball.left += self._ball.velocity_x
        self._ball.top += self._ball.velocity_y

    def _handle_wall_collision(self):
        """Handles collisions of the paddles and of the ball with the walls
        at the top and bottom of the screen, as well as the reset after the
        ball leaves the left or the right of the screen."""
        # collision of paddle1 with top wall
        if self._paddle1.top < 0:
            self._paddle1.top = 0
        # collision of paddle2 with top wall
        if self._paddle2.top < 0:
            self._paddle2.top = 0
        # collision of paddle1 with bottom wall
        if self._paddle1.bottom > WINDOW_HEIGHT:
            self._paddle1.bottom = WINDOW_HEIGHT
        # collision of paddle2 with bottom wall
        if self._paddle2.bottom > WINDOW_HEIGHT:
            self._paddle2.bottom = WINDOW_HEIGHT
        # collision of ball with top wall
        if self._ball.top < 0:
            self._ball.top = 0
            self._ball.velocity_y *= -1
        # collision of ball with bottom wall
        if self._ball.bottom > WINDOW_HEIGHT:
            self._ball.bottom = WINDOW_HEIGHT
            self._ball.velocity_y *= -1
        # ball leaves left
        if self._ball.right < 0:
            self._score2 += 1
            if self._score2 < 11:
                self._reset()
            else:
                self._is_active = False
        # ball leaves right
        if self._ball.left > WINDOW_WIDTH:
            self._score1 += 1
            if self._score1 < 11:
                self._reset()
            else:
                self._is_active = False

    def _handle_paddles_ball_collision(self):
        """Handles collisions of the ball with the paddles."""
        if self._paddle1.colliderect(self._ball):
            self._ball.velocity_x *= -1
            if self._paddle1.top <= self._ball.center_y \
                    <= self._paddle1.bottom:
                self._ball.left = self._paddle1.right
        if self._paddle2.colliderect(self._ball):
            self._ball.velocity_x *= -1
            if self._paddle2.top <= self._ball.center_y \
                    <= self._paddle2.bottom:
                self._ball.right = self._paddle2.left

    def _reset(self):
        """Resets the properties of the paddle and of the ball to their
        initial values, respectively, and redraws the screen."""
        # reset paddles
        self._paddle1.velocity = 0
        self._paddle2.velocity = 0
        # reset ball
        self._ball.center = BALL_INITIAL_CENTER
        self._ball.velocity_x = choice(BALL_VELOCITY_CHOICES)
        self._ball.velocity_y = choice(BALL_VELOCITY_CHOICES)

        # redraw screen
        self._redraw_screen()

        # wait until game continues
        wait(RESTART_TIME)

    def _draw_game_over_screen(self):
        """Draws the game over screen."""
        # fill background with window color
        self._screen.fill(WINDOW_COLOR)

        # draw labels
        self._screen.blit(self._label1, SCORE1_LABEL_POSITION)
        self._screen.blit(self._label2, SCORE2_LABEL_POSITION)

        # draw game over label
        winner = '1' if self._score1 > self._score2 else '2'
        winner_label = FONT.render('PLAYER {} WON'.format(winner), True,
                                   FONT_COLOR)
        self._screen.blit(winner_label, WINNER_LABEL_POSITION)

        # draw paddles
        draw_rect(self._screen, self._paddle1.color, self._paddle1)
        draw_rect(self._screen, self._paddle2.color, self._paddle2)

        # update whole screen
        flip_screen()

    def run(self):
        """Runs the instance."""
        clock = Clock()

        while self._is_active:
            # redraw screen
            self._redraw_screen()

            # check for events
            for event in get_event():
                # clicking quit button of window kills the game
                if event.type == QUIT:
                    quit_pygame()

                # clicking key board button to move paddle
                if event.type == KEYDOWN:
                    # button is key W
                    if event.key == K_w:
                        self._paddle1.velocity = -MAX_VELOCITY
                    # button is key S
                    elif event.key == K_s:
                        self._paddle1.velocity = MAX_VELOCITY
                    # button is up arrow key
                    if event.key == K_UP:
                        self._paddle2.velocity = -MAX_VELOCITY
                    # button is down arrow key
                    elif event.key == K_DOWN:
                        self._paddle2.velocity = MAX_VELOCITY
                if event.type == KEYUP:
                    # button is key W or key S
                    if event.key == K_w or event.key == K_s:
                        self._paddle1.velocity = 0
                    # button is up arrow key or down arrow key
                    if event.key == K_UP or event.key == K_DOWN:
                        self._paddle2.velocity = 0

            # update coordinates of paddles and ball
            self._move_paddles_and_ball()

            # handle collisions of paddles with walls and of ball with
            # walls and paddles
            self._handle_wall_collision()
            self._handle_paddles_ball_collision()

            # set count of updates
            clock.tick(FRAMES_PER_SECOND)

        self._draw_game_over_screen()

        while pygame_is_active():
            # check for events
            for event in get_event():
                # clicking quit button of window kills the game
                if event.type == QUIT:
                    quit_pygame()


if __name__ == '__main__':
    Pong().run()
