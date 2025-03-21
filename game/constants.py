"""
Enthält Konstanten und Konfigurationsparameter für das gesamte Spiel.
"""
import pygame
import math

# Fenster und Spiel
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TARGET_FPS = 60
GAME_TITLE = "DimensionSwitch"

# Physik
GRAVITY = 0.5
TERMINAL_VELOCITY = 10
FRICTION = 0.85

# Spieler
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 5
PLAYER_JUMP_POWER = 15
PLAYER_MAX_HEALTH = 3
PLAYER_STARTING_LIVES = 3
PLAYER_INVINCIBLE_TIME = 1.5  # Sekunden
PLAYER_INVINCIBILITY_AFTER_HIT = 2.0  # Sekunden nach Treffer unverwundbar
DIMENSION_CHANGE_COOLDOWN = 1.0  # Sekunden

# Welt
PLATFORM_HEIGHT = 30
LEVEL_WIDTH = 3000
LEVEL_HEIGHT = 1000
CAMERA_SMOOTHING = 0.1
BACKGROUND_PARTICLES = 150

# Dimensionen
MAX_DIMENSIONS = 4
DIMENSION_TRANSITION_TIME = 0.5
DIMENSION_NORMAL = 1  # Normale Dimension
DIMENSION_MIRROR = 2  # Spiegeldimension
DIMENSION_TIME_SLOW = 3  # Zeitdehnungsdimension

# Gegner
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 40
ENEMY_SPEED = 2
ENEMY_DAMAGE = 1
ENEMY_RESPAWN_TIME = 5.0  # Sekunden

# Objekte
COLLECTIBLE_SIZE = 20
COLLECTIBLE_SCORE = 10
PORTAL_WIDTH = 60
PORTAL_HEIGHT = 100

# Spieler-Bewegungsparameter
PLAYER_JUMP_STRENGTH = -16.0  # Negative Werte für Aufwärtsbewegung
MAX_FALL_SPEED = 15.0  # Maximale Fallgeschwindigkeit

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

# Spieler-Farben
PLAYER_COLOR = (0, 128, 255)  # Blau

# Plattform-Farben
PLATFORM_COLOR = (100, 200, 100)  # Grün

# Gegner-Farben
ENEMY_COLOR = (255, 100, 100)  # Rot

# Powerup-Farben
POWERUP_COLOR = (200, 200, 50)  # Gelb
PORTAL_COLOR = (200, 100, 200)  # Violett
COLLECTIBLE_COLOR = (255, 215, 0)  # Gold

# UI-Farben
UI_BG_COLOR = (20, 20, 40)
UI_TEXT_COLOR = (220, 220, 220)
UI_ACCENT_COLOR = (100, 180, 255)
UI_BORDER_COLOR = (100, 100, 150)
UI_ELEMENT_COLOR = (50, 50, 70)
UI_ELEMENT_HOVER_COLOR = (70, 70, 100)

# HUD-Farben
HUD_BACKGROUND_COLOR = (20, 20, 40, 180)  # Dunkel mit Transparenz
HUD_HEALTH_COLOR = (220, 50, 50)  # Rot für Leben
HUD_ENERGY_COLOR = (50, 150, 250)  # Blau für Energie
HUD_TEXT_COLOR = (255, 255, 255)  # Weiß für Text
HUD_BG_COLOR = (0, 0, 0, 128)  # Halbtransparent
HUD_BORDER_COLOR = (80, 80, 80)
HUD_SCORE_COLOR = (255, 215, 0)  # Gold-Farbe für Punktzahl
HUD_WARNING_COLOR = (200, 200, 50)
HUD_DANGER_COLOR = (200, 50, 50)
HUD_DANGER_COLOR_BRIGHT = (255, 80, 80)  # Hellere Rot-Farbe für Blinken
HUD_DEBUG_COLOR = (100, 200, 255)
HUD_NOTIFICATION_COLOR = (30, 30, 50, 200)  # Dunkelblau mit Transparenz

# Menü-Farben
MENU_BG_COLOR = (10, 10, 30, 220)  # Leicht transparent
MENU_TITLE_COLOR = (200, 200, 255)  # Helles Blau
MENU_TEXT_COLOR = (200, 200, 200)  # Hellgrau
MENU_BUTTON_COLOR = (60, 60, 80)
MENU_BUTTON_HOVER_COLOR = (80, 80, 120)  # Helleres Blau
BUTTON_COLOR = (60, 60, 80)
BUTTON_HOVER_COLOR = (80, 80, 120)
BUTTON_BORDER_COLOR = (100, 120, 200)

# Farben für UI-Elemente
SLIDER_BACKGROUND_COLOR = (40, 40, 60)
SLIDER_FILL_COLOR = (80, 100, 180)
SLIDER_BORDER_COLOR = (100, 120, 200)
SLIDER_HANDLE_COLOR = (150, 170, 250)

# Input-Farben
INPUT_BG_COLOR = (40, 40, 60)
INPUT_ACTIVE_COLOR = (50, 50, 80)
INPUT_BORDER_COLOR = (100, 120, 200)

# Toggle-Farben
TOGGLE_BACKGROUND_COLOR = (40, 40, 60)
TOGGLE_ACTIVE_COLOR = (80, 120, 200)
TOGGLE_HANDLE_COLOR = (200, 200, 220)

# Nützliche Funktionen
def get_angle_to_target(x1, y1, x2, y2):
    """Berechnet den Winkel zwischen zwei Punkten in Radiant."""
    dx = x2 - x1
    dy = y2 - y1
    return math.atan2(dy, dx)

def get_distance(x1, y1, x2, y2):
    """Berechnet die Entfernung zwischen zwei Punkten."""
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)

def clamp(value, min_value, max_value):
    """Begrenzt einen Wert auf einen Bereich."""
    return max(min_value, min(value, max_value))

def lerp(start, end, t):
    """Lineare Interpolation zwischen zwei Werten."""
    return start + t * (end - start)

# Powerups
POWERUP_DURATION = 10.0  # Sekunden
POWERUP_SIZE = 30
POWERUP_DOUBLE_JUMP_DURATION = 15.0  # Sekunden
POWERUP_SPEED_BOOST_DURATION = 12.0  # Sekunden
POWERUP_INVINCIBILITY_DURATION = 8.0  # Sekunden
DOUBLE_JUMP_HEIGHT = 10
SPEED_BOOST_FACTOR = 1.5
INVINCIBILITY_DURATION = 5.0  # Sekunden

# Powerup-Farben
DOUBLE_JUMP_COLOR = (50, 150, 255)  # Blau für Doppelsprung
SPEED_BOOST_COLOR = (255, 200, 0)   # Gelb für Geschwindigkeit
INVINCIBILITY_COLOR = (255, 50, 50)  # Rot für Unverwundbarkeit
EXTRA_LIFE_COLOR = (50, 255, 50)    # Grün für Extra-Leben

# Speicherort für Spielstände und Einstellungen
SAVE_DIRECTORY = "./saves/"
SETTINGS_FILE = "settings.json"
HIGHSCORE_FILE = "highscores.json"

# Standard-Tastenbelegung
DEFAULT_CONTROLS = {
    "move_left": pygame.K_LEFT,
    "move_right": pygame.K_RIGHT,
    "jump": pygame.K_SPACE,
    "dimension_change": pygame.K_d,
    "pause": pygame.K_ESCAPE
}

# Standard-Einstellungen
DEFAULT_SETTINGS = {
    "music_volume": 0.7,
    "sfx_volume": 0.8,
    "fullscreen": False,
    "particles_enabled": True,
    "show_minimap": True,
    "difficulty": 1  # 0=Leicht, 1=Normal, 2=Schwer
}

# Dimensions-Farben
DIMENSION_1_COLOR = (50, 100, 200)    # Blau - Normal
DIMENSION_2_COLOR = (200, 50, 50)     # Rot - Gespiegelt
DIMENSION_3_COLOR = (50, 180, 50)     # Grün - Zeit-Paradox
DIMENSION_4_COLOR = (180, 50, 180)    # Lila - Quantum

# Partikel-Farben
PARTICLE_COLORS = [
    (255, 255, 255),    # Weiß
    (255, 255, 200),    # Hellgelb
    (200, 200, 255),    # Hellblau
    (255, 200, 200),    # Hellrot
    (200, 255, 200)     # Hellgrün
]

# Explosions-Farben
EXPLOSION_COLORS = [
    (255, 255, 0),      # Gelb
    (255, 165, 0),      # Orange
    (255, 69, 0),       # Orangerot
    (139, 0, 0),        # Dunkelrot
    (50, 50, 50)        # Dunkelgrau (Rauch)
]

# Audio-Kategorien
SOUND_CATEGORIES = {
    "player": ["jump", "land", "hurt", "die", "powerup", "dimension_change", "step"],
    "world": ["collect", "portal", "explosion", "platform"],
    "enemy": ["hit", "spawn", "die"],
    "ui": ["click", "hover", "pause", "unpause", "level_complete"]
}

# Musik-Typen
MUSIC_TYPES = ["menu", "dimension_1", "dimension_2", "dimension_3", "dimension_4", "boss", "game_over"]

# Animations-Zeiten
ANIMATION_RATES = {
    "player_idle": 0.2,
    "player_run": 0.1,
    "player_jump": 0.2,
    "player_fall": 0.2,
    "player_hurt": 0.1,
    "enemy_move": 0.15,
    "collectible_hover": 0.1,
    "portal_active": 0.05
}

# Level-Generierung
LEVEL_CONFIGS = {
    "tutorial": {
        "platforms": 10,
        "enemies": 5,
        "collectibles": 15
    },
    "easy": {
        "platforms": 15,
        "enemies": 10,
        "collectibles": 20
    },
    "medium": {
        "platforms": 20,
        "enemies": 15,
        "collectibles": 25
    },
    "hard": {
        "platforms": 25,
        "enemies": 20,
        "collectibles": 30
    }
} 