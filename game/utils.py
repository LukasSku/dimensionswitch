import random
import math
import pygame
import numpy as np
from typing import Tuple, Optional, Union, List, Dict, Any

def check_collision(rect1: pygame.Rect, rect2: pygame.Rect) -> str:
    """
    Verbesserte Kollisionserkennung, die auch die Kollisionsrichtung zurückgibt.
    
    Rückgabewerte:
    - "top": Kollision von oben
    - "bottom": Kollision von unten
    - "left": Kollision von links
    - "right": Kollision von rechts
    - "": Keine Kollision
    """
    if not rect1.colliderect(rect2):
        return ""
    
    # Bestimme die Überlappung in beiden Richtungen
    overlap_x = min(rect1.right, rect2.right) - max(rect1.left, rect2.left)
    overlap_y = min(rect1.bottom, rect2.bottom) - max(rect1.top, rect2.top)
    
    # Wenn die Überlappung in Y-Richtung größer ist, ist es eine horizontale Kollision
    if overlap_x >= overlap_y:
        # Bestimme vertikale Richtung
        if rect1.centery < rect2.centery:
            return "bottom"  # Kollision von oben
        else:
            return "top"     # Kollision von unten
    else:
        # Bestimme horizontale Richtung
        if rect1.centerx < rect2.centerx:
            return "right"   # Kollision von links
        else:
            return "left"    # Kollision von rechts

def generate_random_color(min_brightness: int = 100) -> Tuple[int, int, int]:
    """Generiert eine zufällige Farbe mit einer Mindesthelligkeit."""
    return (
        random.randint(min_brightness, 255),
        random.randint(min_brightness, 255),
        random.randint(min_brightness, 255)
    )

def draw_rounded_rect(surface: pygame.Surface, rect: Union[pygame.Rect, Tuple[int, int, int, int]], 
                     color: Tuple[int, int, int], radius: int = 10) -> None:
    """
    Zeichnet ein abgerundetes Rechteck auf die angegebene Oberfläche.
    Optimiert für weniger redundante Berechnungen.
    """
    if not isinstance(rect, pygame.Rect):
        rect = pygame.Rect(rect)
    
    # Rechtecke für horizontale und vertikale Teile
    h_rect = pygame.Rect(rect.x + radius, rect.y, rect.width - 2 * radius, rect.height)
    v_rect = pygame.Rect(rect.x, rect.y + radius, rect.width, rect.height - 2 * radius)
    
    # Kreismittelpunkte für die abgerundeten Ecken
    top_left = (rect.x + radius, rect.y + radius)
    top_right = (rect.x + rect.width - radius, rect.y + radius)
    bottom_left = (rect.x + radius, rect.y + rect.height - radius)
    bottom_right = (rect.x + rect.width - radius, rect.y + rect.height - radius)
    
    # Zeichnen in einem Durchgang
    pygame.draw.rect(surface, color, h_rect)
    pygame.draw.rect(surface, color, v_rect)
    
    # Zeichnen aller Ecken in einem Durchgang
    pygame.draw.circle(surface, color, top_left, radius)
    pygame.draw.circle(surface, color, top_right, radius)
    pygame.draw.circle(surface, color, bottom_left, radius)
    pygame.draw.circle(surface, color, bottom_right, radius)

def draw_with_dimension_effect(surface: pygame.Surface, rect: pygame.Rect, 
                               normal_color: Tuple[int, int, int], dimension: int) -> None:
    """
    Zeichnet ein Objekt mit dimensionsspezifischen Effekten.
    Optimiert für weniger bedingte Anweisungen.
    """
    from game.constants import DIMENSION_NORMAL, DIMENSION_MIRROR, DIMENSION_TIME_SLOW
    
    # Dimensionsabhängige Farbanpassung (als Lookup statt bedingter Anweisungen)
    if dimension == DIMENSION_NORMAL:
        color = normal_color
    elif dimension == DIMENSION_MIRROR:
        # Invertierte Farbe für Spiegeldimension
        color = tuple(255 - c for c in normal_color)
    elif dimension == DIMENSION_TIME_SLOW:
        # Abgedunkelte, aber blaustichige Farbe für Zeitdimension
        color = (normal_color[0] // 2, normal_color[1] // 2, normal_color[2])
    else:
        # Fallback
        color = normal_color
    
    # Rechteck zeichnen
    try:
        pygame.draw.rect(surface, color, rect)
        
        # Dimension-spezifische Effekte
        if dimension == DIMENSION_TIME_SLOW:
            try:
                # Zeiteffekt-Partikel (pre-allokiert für bessere Performance)
                particle_positions = np.random.randint(
                    low=[rect.x, rect.y],
                    high=[rect.x + rect.width, rect.y + rect.height],
                    size=(3, 2)
                )
                
                # Alle Partikel in einem Batch zeichnen
                for pos in particle_positions:
                    try:
                        # Stelle sicher, dass die NumPy-Array-Werte zu Python-primitiven int konvertiert werden
                        # Doppelte Konvertierung, um NumPy-Typen zu vermeiden
                        x = int(float(pos[0]))
                        y = int(float(pos[1]))
                        
                        # Explizite Tupel-Erstellung mit Python-int-Werten
                        center_pos = (x, y)
                        pygame.draw.circle(surface, (200, 200, 255), center_pos, 2)
                    except Exception:
                        # Ignoriere Fehler für einzelne Partikel
                        continue
            except Exception:
                # Ignoriere komplette Partikel-Fehler, um das Spiel nicht zu unterbrechen
                pass
    except Exception:
        # Fehlerbehandlung für den Fall, dass das Rechteck nicht gezeichnet werden kann
        pass

def lerp(start: float, end: float, amount: float) -> float:
    """
    Lineare Interpolation zwischen zwei Werten.
    """
    return start + amount * (end - start)

def perlin_noise(x: float, y: float, seed: int = 0) -> float:
    """
    Vereinfachte Perlin-Noise-Funktion für Terraingeneration und andere Effekte.
    Gibt einen Wert zwischen 0 und 1 zurück.
    """
    # Seed verwenden
    random.seed(seed)
    
    # Gitterpunkte bestimmen
    x0 = math.floor(x)
    y0 = math.floor(y)
    x1 = x0 + 1
    y1 = y0 + 1
    
    # Interpolationsgewichte
    sx = x - x0
    sy = y - y0
    
    # Gradientenvektoren an den Gitterpunkten
    n00 = random.random()
    n10 = random.random()
    n01 = random.random()
    n11 = random.random()
    
    # Interpolieren
    ix0 = lerp(n00, n10, sx)
    ix1 = lerp(n01, n11, sx)
    value = lerp(ix0, ix1, sy)
    
    # Seed zurücksetzen, um nicht andere Zufallsgeneratoren zu beeinflussen
    random.seed()
    
    return value

def load_spritesheet(filename: str, tile_width: int, tile_height: int) -> List[pygame.Surface]:
    """
    Lädt ein Spritesheet und teilt es in einzelne Sprites auf.
    """
    spritesheet = pygame.image.load(filename)
    sheet_width, sheet_height = spritesheet.get_size()
    
    sprites = []
    for y in range(0, sheet_height, tile_height):
        for x in range(0, sheet_width, tile_width):
            rect = pygame.Rect(x, y, tile_width, tile_height)
            sprite = pygame.Surface(rect.size, pygame.SRCALPHA)
            sprite.blit(spritesheet, (0, 0), rect)
            sprites.append(sprite)
            
    return sprites

def create_shadow(surface: pygame.Surface, alpha: int = 128, offset: Tuple[int, int] = (5, 5)) -> pygame.Surface:
    """
    Erstellt einen Schatten für die gegebene Oberfläche.
    """
    shadow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 0))
    
    # Nicht-transparente Bereiche des Originals ermitteln
    for y in range(surface.get_height()):
        for x in range(surface.get_width()):
            color = surface.get_at((x, y))
            if color.a > 0:
                shadow.set_at((x, y), (0, 0, 0, alpha))
    
    # Oberfläche mit Schatten erstellen
    result = pygame.Surface((surface.get_width() + abs(offset[0]), 
                              surface.get_height() + abs(offset[1])), 
                             pygame.SRCALPHA)
    
    # Schatten an versetzter Position zeichnen
    shadow_x = max(0, offset[0])
    shadow_y = max(0, offset[1])
    result.blit(shadow, (shadow_x, shadow_y))
    
    # Original über den Schatten zeichnen
    orig_x = max(0, -offset[0])
    orig_y = max(0, -offset[1])
    result.blit(surface, (orig_x, orig_y))
    
    return result 