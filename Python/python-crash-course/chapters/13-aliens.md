# Chapter 13 — Aliens!

> **Part II: Project — Alien Invasion (2/3)**

---

## 🎯 What This Chapter Covers

Creating the alien fleet, moving aliens, detecting collisions (bullets vs aliens, alien vs ship, alien vs bottom), and ending/restarting the game.

---

## 👾 The Alien Class

```python
# alien.py
import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    """A class to represent a single alien in the fleet."""

    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the alien image and set its rect attribute
        self.image = pygame.image.load('images/alien.bmp')
        self.rect = self.image.get_rect()

        # Start each new alien near the top left of the screen
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the alien's exact horizontal position
        self.x = float(self.rect.x)

    def update(self):
        """Move the alien to the right or left."""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x

    def check_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)
```

---

## 🏗️ Building the Fleet

```python
def _create_fleet(self):
    """Create the fleet of aliens."""
    # Create an alien and keep adding aliens until no room left
    alien = Alien(self)
    alien_width, alien_height = alien.rect.size

    current_x, current_y = alien_width, alien_height
    while current_y < (self.settings.screen_height - 3 * alien_height):
        while current_x < (self.settings.screen_width - 2 * alien_width):
            self._create_alien(current_x, current_y)
            current_x += 2 * alien_width
        # Finished a row; reset x, increment y
        current_x = alien_width
        current_y += 2 * alien_height

def _create_alien(self, x_position, y_position):
    """Create an alien and place it in the fleet."""
    new_alien = Alien(self)
    new_alien.x = x_position
    new_alien.rect.x = x_position
    new_alien.rect.y = y_position
    self.aliens.add(new_alien)
```

---

## 🔄 Fleet Movement

```python
# settings.py additions
self.fleet_direction = 1   # 1 = right, -1 = left
self.fleet_drop_speed = 10

def _update_aliens(self):
    """Check if the fleet is at an edge, then update positions."""
    self._check_fleet_edges()
    self.aliens.update()
    # Check for alien-ship collisions
    if pygame.sprite.spritecollideany(self.ship, self.aliens):
        self._ship_hit()
    # Check for aliens hitting the bottom
    self._check_aliens_bottom()

def _check_fleet_edges(self):
    """Respond if any aliens have reached an edge."""
    for alien in self.aliens.sprites():
        if alien.check_edges():
            self._change_fleet_direction()
            break

def _change_fleet_direction(self):
    """Drop the entire fleet and change the fleet's direction."""
    for alien in self.aliens.sprites():
        alien.rect.y += self.settings.fleet_drop_speed
    self.settings.fleet_direction *= -1
```

---

## 💥 Collision Detection

```python
def _update_bullets(self):
    """Update position of bullets and get rid of old bullets."""
    self.bullets.update()

    # Delete bullets that have gone off the top of the screen
    for bullet in self.bullets.copy():
        if bullet.rect.bottom <= 0:
            self.bullets.remove(bullet)

    self._check_bullet_alien_collisions()

def _check_bullet_alien_collisions(self):
    """Respond to bullet-alien collisions."""
    # Remove any bullets and aliens that have collided
    # groupcollide() returns a dict: bullet -> list of aliens hit
    collisions = pygame.sprite.groupcollide(
        self.bullets, self.aliens, True, True
    )
    if not self.aliens:
        # Destroy existing bullets and create new fleet
        self.bullets.empty()
        self._create_fleet()
        self.settings.increase_speed()

def _ship_hit(self):
    """Respond to the ship being hit by an alien."""
    if self.stats.ships_left > 0:
        self.stats.ships_left -= 1
        self.aliens.empty()
        self.bullets.empty()
        self._create_fleet()
        self.ship.center_ship()
        sleep(0.5)   # pause so player can register what happened
    else:
        self.stats.game_active = False
```

---

## 🔑 Key Takeaways

- `pygame.sprite.spritecollideany(sprite, group)` detects single sprite vs group collision
- `pygame.sprite.groupcollide(g1, g2, True, True)` detects group vs group, removes both
- `fleet_direction = 1` (right) or `-1` (left) — multiply speed by direction for movement
- `alien.check_edges()` returns True if the alien is at the screen boundary → drop and reverse
- When fleet is destroyed: `settings.increase_speed()` makes the next wave faster
- `sleep(0.5)` pauses after a ship hit — gives the player time to notice
- Game state tracked in `GameStats` class (`ships_left`, `game_active`, `score`)
