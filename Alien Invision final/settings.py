class Settings:
    """A class to store all settings for Alien Invasion."""

    def __init__(self):
        """Initialize the game's static settings."""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 775
        self.bg_color = (230, 230, 230)

        # Ship settings
        self.ship_speed = 12
        self.ship_limit = 3

        # Alien settings
        self.alien_speed = 10.0
        self.fleet_drop_speed = 10
        self.fleet_direction = 1

        # How quickly the game speed up
        self.speedup_scale = 1.1

        # How quickly the alien point values increase
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

        # Bullet settings
        self.bullet_speed = 12.0
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (248, 180, 0)
        self.bullets_allowed = 100

        # Camera settings
        self.wCam = 640
        self.hCam = 480


    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = 12
        self.bullet_speed = 12.0
        self.alien_speed = 10.0

        # Fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1

        # Scoring
        self.alien_points = 50

    
    def increase_speed(self):
        """Increase speed settings and alien point values."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)