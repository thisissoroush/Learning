# Chapter 14 — Scoring

> **Part II: Project — Alien Invasion (3/3)**

---

## 🎯 What This Chapter Covers

Score display, high score, ship lives display, level progression, and Play button to start/restart the game.

---

## 🎯 The Scoreboard

```python
# scoreboard.py
import pygame.font
from pygame.sprite import Group
from ship import Ship

class Scoreboard:
    """A class to report scoring information."""

    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        # Font settings for scoring information
        self.text_color = (30, 30, 30)
        self.font = pygame.font.SysFont(None, 48)

        # Prepare the initial score images
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

    def prep_score(self):
        """Turn the score into a rendered image."""
        rounded_score = round(self.stats.score, -1)
        score_str = f"{rounded_score:,}"
        self.score_image = self.font.render(
            score_str, True, self.text_color, self.settings.bg_color
        )
        # Display the score at the top right of the screen
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def check_high_score(self):
        """Check to see if there's a new high score."""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def prep_ships(self):
        """Show how many ships are left."""
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_game)
            ship.rect.x = 10 + ship_number * ship.rect.width
            ship.rect.y = 10
            self.ships.add(ship)

    def show_score(self):
        """Draw scores, level, and ships to the screen."""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)
```

---

## 🔢 Scoring Points

```python
# settings.py
def __init__(self):
    ...
    self.alien_points = 50     # base points per alien
    self.score_scale = 1.5     # multiplier per level

def increase_speed(self):
    """Increase speed settings and alien point values."""
    self.ship_speed *= self.speedup_scale
    self.bullet_speed *= self.speedup_scale
    self.alien_speed *= self.speedup_scale
    self.alien_points = int(self.alien_points * self.score_scale)

# In _check_bullet_alien_collisions()
collisions = pygame.sprite.groupcollide(
    self.bullets, self.aliens, True, True
)
if collisions:
    for aliens in collisions.values():
        self.stats.score += self.settings.alien_points * len(aliens)
    self.sb.prep_score()
    self.sb.check_high_score()
```

---

## ▶️ Play Button

```python
# button.py
import pygame.font

class Button:
    """A class to build buttons for the game."""

    def __init__(self, ai_game, msg):
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # Button dimensions and properties
        self.width, self.height = 200, 50
        self.button_color = (0, 135, 0)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 48)

        # Build the button's rect and center it
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        self._prep_msg(msg)

    def _prep_msg(self, msg):
        """Turn msg into a rendered image and center it on the button."""
        self.msg_image = self.font.render(msg, True,
            self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)

# Handle Play button click
def _check_play_button(self, mouse_pos):
    """Start a new game when the player clicks Play."""
    button_clicked = self.play_button.rect.collidepoint(mouse_pos)
    if button_clicked and not self.stats.game_active:
        self.settings.initialize_dynamic_settings()
        self._start_game()

def _start_game(self):
    self.stats.reset_stats()
    self.sb.prep_score()
    self.sb.prep_level()
    self.sb.prep_ships()
    self.stats.game_active = True
    self.aliens.empty()
    self.bullets.empty()
    self._create_fleet()
    self.ship.center_ship()
    pygame.mouse.set_visible(False)    # hide cursor during gameplay
```

---

## 🔑 Key Takeaways

- `pygame.font.render(text, antialias, color, bg_color)` turns text into a surface
- `f"{score:,}"` formats numbers with commas (1000 → 1,000)
- `round(score, -1)` rounds to nearest 10 — avoid showing false precision
- Ship lives displayed as actual ship images in a `Group`
- High score persists during the session (reset when app closes, unless saved to file)
- `pygame.mouse.set_visible(False)` during play; restore to `True` on game over
- `rect.collidepoint(mouse_pos)` detects if a click landed on a button rect
