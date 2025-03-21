import pygame
import random
import math
from typing import List, Dict, Tuple, Optional, Set, Union, Any
from game.constants import *
from game.utils import draw_with_dimension_effect, draw_rounded_rect

class GameObject:
    """Basisklasse für alle Spielobjekte."""
    __slots__ = ('x', 'y', 'width', 'height')
    
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def get_rect(self) -> pygame.Rect:
        """Gibt das Rechteck des Objekts zurück."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, dt: float) -> None:
        """Aktualisiert den Zustand des Objekts."""
        pass
    
    def render(self, surface: pygame.Surface, current_dimension: int) -> None:
        """Rendert das Objekt auf die angegebene Oberfläche."""
        pass

class Platform(GameObject):
    __slots__ = ('color', 'dimension_visible')
    
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__(x, y, width, height)
        self.color = PLATFORM_COLOR
        self.dimension_visible = -1  # -1 bedeutet in allen Dimensionen sichtbar
        
    def render(self, surface: pygame.Surface, current_dimension: int) -> None:
        # Nur zeichnen, wenn in aktueller Dimension sichtbar
        if self.dimension_visible == -1 or self.dimension_visible == current_dimension:
            draw_with_dimension_effect(surface, self.get_rect(), self.color, current_dimension)
        
class Enemy(GameObject):
    __slots__ = ('color', 'patrol_left', 'patrol_right', 'speed', 'direction', 
                 'is_dead', 'animation_frame', 'frame_timer')
    
    def __init__(self, x: float, y: float, patrol_left: float, patrol_right: float):
        super().__init__(x, y, 40, 40)
        self.color = ENEMY_COLOR
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.speed = 2
        self.direction = 1  # 1 = rechts, -1 = links
        self.is_dead = False
        self.animation_frame = 0
        self.frame_timer = 0
        
    def update(self, dt: float, current_dimension: int) -> None:
        if self.is_dead:
            return
            
        # Zeitfaktor für konsistente Bewegung unabhängig von FPS
        time_factor = dt * 60
            
        self.x += self.speed * self.direction * time_factor / 60.0
        
        if self.x <= self.patrol_left:
            self.x = self.patrol_left
            self.direction = 1
        elif self.x + self.width >= self.patrol_right:
            self.x = self.patrol_right - self.width
            self.direction = -1
            
        self.frame_timer += time_factor / 60.0
        if self.frame_timer >= 10:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.frame_timer = 0
            
    def die(self) -> None:
        self.is_dead = True
        
    def render(self, surface: pygame.Surface, current_dimension: int) -> None:
        if self.is_dead:
            return
            
        enemy_rect = self.get_rect()
        draw_with_dimension_effect(surface, enemy_rect, self.color, current_dimension)
        
        # Augen
        eye_offset = 10 if self.direction > 0 else -10
        eye_x = self.x + 10 if self.direction < 0 else self.x + 30
        
        eye_color = WHITE if current_dimension == DIMENSION_NORMAL else \
                   (200, 200, 100) if current_dimension == DIMENSION_MIRROR else \
                   (150, 150, 200)
        
        # Koordinaten zu Ganzzahlen machen, um Fehler zu vermeiden
        eye_x_int = int(eye_x)
        eye_y_int = int(self.y + 15)
        
        # Stelle sicher, dass die Position als Tupel (int, int) übergeben wird
        pygame.draw.circle(surface, eye_color, (eye_x_int, eye_y_int), 8)
        pygame.draw.circle(surface, BLACK, (eye_x_int + eye_offset // 2, eye_y_int), 4)

class Collectible(GameObject):
    __slots__ = ('color', 'collected', 'animation_offset', 'animation_direction')
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 20, 20)
        self.color = COLLECTIBLE_COLOR
        self.collected = False
        self.animation_offset = 0
        self.animation_direction = 1
        
    def update(self, dt: float) -> None:
        if self.collected:
            return
            
        # Animationsgeschwindigkeit an delta time anpassen
        anim_speed = 0.2 * dt * 60 / 60.0
            
        self.animation_offset += anim_speed * self.animation_direction
        
        if self.animation_offset > 5:
            self.animation_direction = -1
        elif self.animation_offset < -5:
            self.animation_direction = 1
            
    def render(self, surface: pygame.Surface, current_dimension: int) -> None:
        if self.collected:
            return
            
        # Basis-Collectible zeichnen
        collectible_rect = pygame.Rect(
            self.x, 
            self.y + self.animation_offset, 
            self.width, 
            self.height
        )
        
        # Dimension-spezifische Farben
        if current_dimension == DIMENSION_NORMAL:
            color = self.color
        elif current_dimension == DIMENSION_MIRROR:
            color = (self.color[0], self.color[2], self.color[1])
        else:
            color = (self.color[2], self.color[0], self.color[1])
            
        # Center-Koordinaten als Tupel mit ganzen Zahlen (int, int)
        center_pos = (
            int(self.x + self.width // 2), 
            int(self.y + self.height // 2 + self.animation_offset)
        )
        pygame.draw.circle(
            surface, 
            color, 
            center_pos, 
            self.width // 2
        )
        
        # Glanz-Effekt
        highlight_pos = (
            int(self.x + self.width * 0.7),
            int(self.y + self.height * 0.3 + self.animation_offset)
        )
        pygame.draw.circle(surface, WHITE, highlight_pos, self.width // 6)

class Portal(GameObject):
    __slots__ = ('animation_frame', 'portal_color')
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 40, 60)
        self.animation_frame = 0
        self.portal_color = PORTAL_COLOR
        
    def update(self, dt: float) -> None:
        # Animation aktualisieren
        self.animation_frame = (self.animation_frame + dt * 5) % 360
        
    def render(self, surface: pygame.Surface, current_dimension: int) -> None:
        # Portal-Basis
        portal_rect = self.get_rect()
        
        # Dimension-spezifische Farben
        if current_dimension == DIMENSION_NORMAL:
            portal_base_color = self.portal_color
        elif current_dimension == DIMENSION_MIRROR:
            portal_base_color = (self.portal_color[0], 
                                self.portal_color[2], 
                                self.portal_color[1])
        else:
            portal_base_color = (self.portal_color[2], 
                                self.portal_color[0], 
                                self.portal_color[1])
        
        # Animierte Wellen
        num_waves = 8
        max_radius = max(self.width, self.height) // 2 + 5
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Portalbasis zeichnen
        pygame.draw.ellipse(surface, portal_base_color, portal_rect)
        
        # Wellenmuster zeichnen
        for i in range(num_waves):
            wave_offset = (self.animation_frame + i * 45) % 360
            wave_radius = int(max_radius * (0.5 + 0.5 * math.sin(math.radians(wave_offset))))
            
            # Farbe mit Dimension und Animation anpassen
            wave_intensity = 0.5 + 0.5 * math.sin(math.radians(wave_offset))
            wave_color = (
                min(255, int(portal_base_color[0] * wave_intensity + 50)),
                min(255, int(portal_base_color[1] * wave_intensity + 50)),
                min(255, int(portal_base_color[2] * wave_intensity + 50))
            )
            
            # Stelle sicher, dass das center-Argument ein Paar von Python-int-Werten ist
            center_pos = (int(center_x), int(center_y))
            
            try:
                pygame.draw.circle(
                    surface, 
                    wave_color, 
                    center_pos, 
                    wave_radius, 
                    2
                )
            except Exception:
                # Bei Fehler einfach überspringen
                pass

class Powerup(GameObject):
    __slots__ = ('powerup_type', 'duration', 'effect_strength', 'display_name', 
                 'description', 'color', 'animation_offset', 'animation_direction', 
                 'collected', 'dimension_visible')
    
    def __init__(self, x: float, y: float, powerup_type: str, dimension: int = -1):
        super().__init__(x, y, 30, 30)
        self.powerup_type = powerup_type
        self.collected = False
        self.animation_offset = 0
        self.animation_direction = 1
        self.dimension_visible = dimension  # -1 bedeutet in allen Dimensionen sichtbar
        
        # Eigenschaften basierend auf Typ setzen
        self.setup_properties()
    
    def setup_properties(self) -> None:
        """Setzt die spezifischen Eigenschaften basierend auf dem Powerup-Typ."""
        if self.powerup_type == "speed":
            self.duration = 10.0  # Sekunden
            self.effect_strength = 1.5  # Multiplikator
            self.display_name = "Geschwindigkeit"
            self.description = "Erhöht die Geschwindigkeit"
            self.color = (0, 200, 200)
        elif self.powerup_type == "jump":
            self.duration = 15.0
            self.effect_strength = 1.3
            self.display_name = "Sprungkraft"
            self.description = "Erhöht die Sprungkraft"
            self.color = (200, 100, 200)
        elif self.powerup_type == "invincibility":
            self.duration = 5.0
            self.effect_strength = 1.0
            self.display_name = "Unverwundbarkeit"
            self.description = "Macht unverwundbar"
            self.color = (255, 215, 0)
        elif self.powerup_type == "gravity":
            self.duration = 8.0
            self.effect_strength = 0.7
            self.display_name = "Schwerkraft"
            self.description = "Reduziert die Schwerkraft"
            self.color = (100, 200, 100)
        else:
            # Standardwerte für unbekannte Typen
            self.duration = 10.0
            self.effect_strength = 1.0
            self.display_name = "Unbekannt"
            self.description = "???"
            self.color = (150, 150, 150)
    
    def update(self, dt: float) -> None:
        if self.collected:
            return
            
        # Animation mit delta time aktualisieren
        anim_speed = 0.3 * dt * 60 / 60.0
        self.animation_offset += anim_speed * self.animation_direction
        
        if self.animation_offset > 5:
            self.animation_direction = -1
        elif self.animation_offset < -5:
            self.animation_direction = 1
    
    def render(self, surface: pygame.Surface, current_dimension: int) -> None:
        if self.collected:
            return
            
        # Basis-Form
        powerup_rect = pygame.Rect(
            self.x, 
            self.y + self.animation_offset, 
            self.width, 
            self.height
        )
        
        # Powerup-Typ-spezifische Formen zeichnen
        if self.powerup_type == "speed":
            # Pfeil nach oben
            pygame.draw.polygon(
                surface,
                self.color,
                [
                    (self.x + self.width // 2, self.y + self.animation_offset),
                    (self.x, self.y + self.height + self.animation_offset),
                    (self.x + self.width, self.y + self.height + self.animation_offset)
                ]
            )
        elif self.powerup_type == "jump":
            # Sprungfeder
            pygame.draw.rect(surface, self.color, powerup_rect)
            spring_base = pygame.Rect(
                self.x + 5, 
                self.y + self.height - 10 + self.animation_offset,
                self.width - 10, 
                10
            )
            pygame.draw.rect(surface, (100, 100, 100), spring_base)
        elif self.powerup_type == "invincibility":
            # Stern
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2 + self.animation_offset
            radius = self.width // 2
            points = []
            
            for i in range(5):
                # Äußere Punkte (Sternspitzen)
                angle_outer = math.pi / 2 + 2 * math.pi * i / 5
                x_outer = float(center_x + radius * math.cos(angle_outer))
                y_outer = float(center_y + radius * math.sin(angle_outer))
                points.append((int(x_outer), int(y_outer)))
                
                # Innere Punkte
                angle_inner = math.pi / 2 + 2 * math.pi * (i + 0.5) / 5
                x_inner = float(center_x + radius * 0.4 * math.cos(angle_inner))
                y_inner = float(center_y + radius * 0.4 * math.sin(angle_inner))
                points.append((int(x_inner), int(y_inner)))
                
            pygame.draw.polygon(surface, self.color, points)
        elif self.powerup_type == "gravity":
            # Schwerkraftsymbol (halbe Kugel mit Pfeilen)
            # Center-Koordinaten als Tupel mit ganzen Zahlen (int, int)
            center_pos = (
                int(self.x + self.width // 2), 
                int(self.y + self.height // 2 + self.animation_offset)
            )
            pygame.draw.circle(
                surface, 
                self.color, 
                center_pos, 
                self.width // 2
            )
            pygame.draw.rect(
                surface,
                BLACK,
                pygame.Rect(
                    self.x, 
                    self.y + self.height // 2 + self.animation_offset, 
                    self.width, 
                    self.height // 2
                )
            )
        else:
            # Generischer Powerup (Kreis)
            # Center-Koordinaten als Tupel mit ganzen Zahlen (int, int)
            center_pos = (
                int(self.x + self.width // 2), 
                int(self.y + self.height // 2 + self.animation_offset)
            )
            pygame.draw.circle(
                surface, 
                self.color, 
                center_pos, 
                self.width // 2
            )
            
        # Glanzeffekt für alle Powerups
        highlight_pos = (
            int(self.x + self.width * 0.7),
            int(self.y + self.height * 0.3 + self.animation_offset)
        )
        pygame.draw.circle(surface, WHITE, highlight_pos, self.width // 8) 