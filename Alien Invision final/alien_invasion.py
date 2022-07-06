import sys
import pygame
from time import sleep
import cv2
import numpy as np
import HandTrackingModule as htm

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import Game_stats
from button import Button
from scoreboard import Scoreboard



class Alien_Invasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.screen = pygame.display.set_mode(
            [1280,720])
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption('Alien Invasion')

        # Set ship
        self.ship = Ship(self)
        self.can_fire = 0

        # Hand detector settings
        self.detector = htm.handDetector(maxHands=1)

        # set camera settings
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.settings.screen_width)
        self.cap.set(4, self.settings.screen_height)

        # Creat an instanc to store game statistics
        self.stats = Game_stats(self)

        # Create an instance to store game statistics, and creat a scoreboard.
        self.sb = Scoreboard(self)

        # Set the background color.
        self.bg_color = (230, 230, 230)
        self._create_fleet()

        # make the Play button.
        self.play_button = Button(self, "Play")


    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            self._update_screen()
            if self.stats.game_active:
                self.ship.update(self.lmList)
                self._update_bullets()
                self._update_alien()


    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


            # Use key down to for exit
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            # Use mouse to click on Play buttom
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)


    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:

            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ship()

            # Get ride of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)


    def _check_keydown_events(self, event):
        if event.key == pygame.K_q:
            sys.exit()


    def _fire_bullet(self):
        """Creat a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        success, frame = self.cap.read()
        frame = self.detector.findHands(frame)
        self.lmList = self.detector.findPosition(frame, draw = False)
        if len(self.lmList) != 0:
            if self.lmList[8][2] > self.lmList[6][2]:
                if self.can_fire == 0:
                    self._fire_bullet()
                    self.can_fire = 1
            else:
                self.can_fire = 0

        # Fix cv2 with pygame to display webcam in background
        if self.stats.level < 3:
            frame = np.fliplr(frame)
        frame = np.rot90(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        surf = pygame.surfarray.make_surface(frame)
        pygame.display.update
        self.screen.blit(surf, (0,0))

        # show ship and aliens in screen
        self.ship.blitme()
        self.aliens.draw(self.screen)

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()


        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        pygame.display.flip()
        


    def _update_bullets(self):
        """Update position of bullets and get ride of old bullets"""
        # Update bullets positions.
        self.bullets.update()

        # get ride of bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()



    def _create_fleet(self):
        """Creat the fleets of aliens."""
        # create an alien and find the number of aliens in a row
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        availbale_space_x = self.settings.screen_width - (4 * alien_width)
        number_aliens_x = availbale_space_x // (2 * alien_width)

        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (4 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            # Create first row of aliens.
            for alien_number in range (number_aliens_x):
                # Create an alien and place it in the row.
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _update_alien(self):
        """
        check if the fleet is at the edge,
            then update the positions of all aliens in the fleet.
        """
        self._check_fleet_edge()
        self.aliens.update()

        # Look for alien and ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Lookfor aliens hitting the bottom of the screen.
        self._check_aliens_bottom()



    def _check_fleet_edge(self):
        """Respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_directions()
                break


    def _change_fleet_directions(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        # Check for any bullets that have hit aliens
        #  If so, get ride of the bullet and the alien
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level
            self.stats.level += 1
            self.sb.prep_level()


    def _ship_hit(self):
        """respond to the ship being hit by an alien."""
        if self.stats.ship_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ship_left -= 1
            self.sb.prep_ship()

            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

        # Pause.
        sleep(0.5)


    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Track this the same as if the ship got hit
                self._ship_hit()
                break




if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = Alien_Invasion()
    ai.run_game()
