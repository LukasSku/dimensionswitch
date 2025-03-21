"""
Enthält die HUD-Klasse für die Spieloberfläche, die Spielerinformationen anzeigt.
"""
import pygame
from game.constants import *
from typing import Dict, Any, Tuple, Optional, List
import math


class HUD:
    """Head-Up-Display für Spielinformationen während des Spiels."""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Schriftarten
        self.title_font = pygame.font.SysFont('Arial', 24)
        self.text_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Positionen und Größen
        # Mehr Platz zwischen Elementen für bessere Lesbarkeit
        self.health_bar_rect = pygame.Rect(50, 20, 180, 25)  # Weiter nach rechts verschoben
        self.score_rect = pygame.Rect(self.screen_width - 220, 20, 200, 25)
        self.dimension_indicator_rect = pygame.Rect(self.screen_width // 2 - 120, 20, 260, 30)  # Breiter für längeren Text
        # Zeit wird unter die Minimap platziert - die genaue Position wird später in Abhängigkeit der Minimap berechnet
        self.time_rect = pygame.Rect(0, 0, 130, 25)  # Diese Position wird später überschrieben
        
        # Zwischenspeicher für HUD-Textelemente
        self._cached_surfaces: Dict[str, Tuple[pygame.Surface, pygame.Rect]] = {}
        
        # Timer für blinkende Elemente und Animationen
        self.blink_timer = 0
        self.animation_timer = 0
        
        # Notification-System
        self.notifications: List[Tuple[str, float, float]] = []  # (text, remaining_time, opacity)
        self.notification_duration = 3.0  # Sekunden
        
        # Spritesheets für HUD-Elemente laden
        self.icon_sheet = self._create_icon_sheet()
        self.dimensions_icons = self._create_dimension_icons()
    
    def _create_icon_sheet(self) -> Dict[str, pygame.Surface]:
        """Erstellt ein Dictionary mit HUD-Icons."""
        icons = {}
        
        # Herz-Icon für Gesundheit
        heart_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(heart_surf, HUD_HEALTH_COLOR, 
                          [(10, 5), (7, 2), (3, 6), (3, 10), (10, 17), (17, 10), 
                           (17, 6), (13, 2), (10, 5)])
        icons["heart"] = heart_surf
        
        # Münz-Icon für Punkte
        coin_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(coin_surf, HUD_SCORE_COLOR, (8, 8), 7)
        pygame.draw.circle(coin_surf, (255, 223, 0), (8, 8), 5)
        icons["coin"] = coin_surf
        
        # Uhr-Icon für Zeit
        time_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(time_surf, (220, 220, 220), (8, 8), 7, 1)
        pygame.draw.line(time_surf, (220, 220, 220), (8, 8), (8, 4), 2)
        pygame.draw.line(time_surf, (220, 220, 220), (8, 8), (11, 10), 2)
        icons["time"] = time_surf
        
        return icons
    
    def _create_dimension_icons(self) -> Dict[int, pygame.Surface]:
        """Erstellt Icons für die verschiedenen Dimensionen."""
        dimensions = {}
        
        # Dimension 1: Normal (Blau)
        dim1 = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(dim1, DIMENSION_1_COLOR, (4, 4, 24, 24))
        dimensions[1] = dim1
        
        # Dimension 2: Gespiegelt (Rot)
        dim2 = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.polygon(dim2, DIMENSION_2_COLOR, 
                          [(4, 28), (16, 4), (28, 28)])
        dimensions[2] = dim2
        
        # Dimension 3: Zeit-Paradox (Grün)
        dim3 = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(dim3, DIMENSION_3_COLOR, (16, 16), 14)
        dimensions[3] = dim3
        
        # Dimension 4: Quantenüberlagert (Lila)
        dim4 = pygame.Surface((32, 32), pygame.SRCALPHA)
        for i in range(4):
            angle = i * 90
            x = 16 + 10 * math.cos(math.radians(angle))
            y = 16 + 10 * math.sin(math.radians(angle))
            pygame.draw.circle(dim4, DIMENSION_4_COLOR, (int(x), int(y)), 5)
        dimensions[4] = dim4
        
        return dimensions
    
    def update(self, dt: float) -> None:
        """Aktualisiert alle HUD-Elemente."""
        # Timer für Animationen aktualisieren
        self.animation_timer += dt
        self.blink_timer = (self.blink_timer + dt) % 1.0  # Blinken mit 1 Sekunde Periode
        
        # Benachrichtigungen aktualisieren
        updated_notifications = []
        for text, remaining_time, opacity in self.notifications:
            remaining_time -= dt
            if remaining_time > 0:
                # Fade-Out in den letzten 1s
                if remaining_time < 1.0:
                    opacity = remaining_time
                updated_notifications.append((text, remaining_time, opacity))
        
        self.notifications = updated_notifications
    
    def add_notification(self, text: str) -> None:
        """Fügt eine neue Benachrichtigung hinzu."""
        self.notifications.append((text, self.notification_duration, 1.0))
    
    def render(self, surface: pygame.Surface, 
               player_health: int, max_health: int, 
               score: int, current_dimension: int, 
               game_time: float, fps: int = 0,
               debug: bool = False) -> None:
        """Zeichnet das HUD mit aktuellen Spielinformationen."""
        # Gesundheitsleiste
        self._render_health_bar(surface, player_health, max_health)
        
        # Punktzahl
        self._render_score(surface, score)
        
        # Dimensions-Indikator
        self._render_dimension_indicator(surface, current_dimension)
        
        # Zeit
        self._render_time(surface, game_time)
        
        # Benachrichtigungen
        self._render_notifications(surface)
        
        # Debug-Informationen (wenn aktiviert)
        if debug:
            self._render_debug_info(surface, fps)
    
    def _render_health_bar(self, surface: pygame.Surface, current: int, maximum: int) -> None:
        """Zeichnet die Gesundheitsleiste des Spielers."""
        # Rahmen
        pygame.draw.rect(surface, HUD_BORDER_COLOR, self.health_bar_rect, 2)
        
        # Hintergrund
        bg_rect = pygame.Rect(self.health_bar_rect.x + 2, self.health_bar_rect.y + 2, 
                              self.health_bar_rect.width - 4, self.health_bar_rect.height - 4)
        pygame.draw.rect(surface, HUD_BG_COLOR, bg_rect)
        
        # Gesundheitsbalken
        if maximum > 0:  # Vermeide Division durch Null
            health_width = int((current / maximum) * (self.health_bar_rect.width - 4))
            health_rect = pygame.Rect(bg_rect.x, bg_rect.y, health_width, bg_rect.height)
            # Farbe basierend auf verbleibender Gesundheit
            if current / maximum > 0.6:
                color = HUD_HEALTH_COLOR
            elif current / maximum > 0.3:
                color = HUD_WARNING_COLOR
            else:
                color = HUD_DANGER_COLOR
                
                # Blinken bei niedriger Gesundheit
                if current / maximum <= 0.2 and self.blink_timer > 0.5:
                    color = HUD_DANGER_COLOR_BRIGHT
                    
            pygame.draw.rect(surface, color, health_rect)
        
        # Herz-Icon mit ausreichend Abstand
        heart_icon = self.icon_sheet["heart"]
        icon_x = self.health_bar_rect.x - 25  # Etwas näher an die Leiste
        icon_y = self.health_bar_rect.y + (self.health_bar_rect.height - heart_icon.get_height()) // 2
        surface.blit(heart_icon, (icon_x, icon_y))
        
        # Textanzeige mit besserem Kontrast
        health_text = f"{current}/{maximum}"
        text_surf = self.text_font.render(health_text, True, HUD_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(self.health_bar_rect.centerx, self.health_bar_rect.centery))
        surface.blit(text_surf, text_rect)
    
    def _render_score(self, surface: pygame.Surface, score: int) -> None:
        """Zeichnet die Punktzahl."""
        # Score-Hintergrund
        pygame.draw.rect(surface, HUD_BG_COLOR, self.score_rect)
        pygame.draw.rect(surface, HUD_BORDER_COLOR, self.score_rect, 2)
        
        # Score-Text
        score_text = f"Punkte: {score}"
        text_surf = self.text_font.render(score_text, True, HUD_SCORE_COLOR)
        text_rect = text_surf.get_rect(midright=(self.score_rect.right - 10, self.score_rect.centery))
        surface.blit(text_surf, text_rect)
        
        # Münz-Icon
        coin_icon = self.icon_sheet["coin"]
        coin_rect = coin_icon.get_rect(midright=(text_rect.left - 5, text_rect.centery))
        surface.blit(coin_icon, coin_rect)
    
    def _render_dimension_indicator(self, surface: pygame.Surface, dimension: int) -> None:
        """Zeichnet den Dimensionsindikator."""
        # Hintergrund
        pygame.draw.rect(surface, HUD_BG_COLOR, self.dimension_indicator_rect)
        pygame.draw.rect(surface, HUD_BORDER_COLOR, self.dimension_indicator_rect, 2)
        
        # Dimensionsname
        dimension_names = {
            1: "Normal",
            2: "Gespiegelt",
            3: "Zeit-Paradox",
            4: "Quantum"
        }
        
        dimension_colors = {
            1: DIMENSION_1_COLOR,
            2: DIMENSION_2_COLOR,
            3: DIMENSION_3_COLOR,
            4: DIMENSION_4_COLOR
        }
        
        current_name = dimension_names.get(dimension, "Unbekannt")
        current_color = dimension_colors.get(dimension, WHITE)
        
        try:
            # Dimensionsicon zuerst positionieren
            if dimension in self.dimensions_icons:
                icon = self.dimensions_icons[dimension]
                # Genug Abstand zum Text
                icon_x = self.dimension_indicator_rect.x + 10
                icon_y = self.dimension_indicator_rect.centery - icon.get_height() // 2
                icon_rect = pygame.Rect(icon_x, icon_y, icon.get_width(), icon.get_height())
                surface.blit(icon, icon_rect)
                
                # Dimensionstext mit ausreichend Abstand zum Icon
                dim_text = f"Dimension: {current_name}"
                text_surf = self.text_font.render(dim_text, True, current_color)
                text_x = icon_rect.right + 10
                text_y = self.dimension_indicator_rect.centery - text_surf.get_height() // 2
                surface.blit(text_surf, (text_x, text_y))
            else:
                # Falls kein Icon existiert, Text zentrieren
                dim_text = f"Dimension: {current_name}"
                text_surf = self.text_font.render(dim_text, True, current_color)
                text_rect = text_surf.get_rect(center=self.dimension_indicator_rect.center)
                surface.blit(text_surf, text_rect)
            
        except (KeyError, IndexError) as e:
            # Fehlerbehandlung - falls das Icon nicht existiert
            print(f"Fehler beim Rendern des Dimension-Icons für Dimension {dimension}: {e}")
            # Fallback: Nur Text anzeigen
            dim_text = f"Dimension: {current_name}"
            text_surf = self.text_font.render(dim_text, True, current_color)
            text_rect = text_surf.get_rect(center=self.dimension_indicator_rect.center)
            surface.blit(text_surf, text_rect)
    
    def _render_time(self, surface: pygame.Surface, game_time: float) -> None:
        """Zeichnet die Spielzeit."""
        # Zeit formatieren (MM:SS)
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Zeit-Text
        time_surf = self.text_font.render(time_str, True, WHITE)
        # Statt topright verwenden wir explizite Koordinaten
        time_rect = time_surf.get_rect()
        time_rect.topright = (self.time_rect.right, self.time_rect.y)
        surface.blit(time_surf, time_rect)
        
        # Zeit-Icon
        time_icon = self.icon_sheet["time"]
        icon_rect = time_icon.get_rect()
        icon_rect.midright = (time_rect.left - 5, time_rect.centery)
        surface.blit(time_icon, icon_rect)
    
    def _render_notifications(self, surface: pygame.Surface) -> None:
        """Zeichnet aktive Benachrichtigungen."""
        if not self.notifications:
            return
        
        # Positionierung und Größe der Benachrichtigungen
        notification_height = 30
        notification_spacing = 5
        notification_width = 300
        start_y = 100  # Höher angesetzt, um Überlappungen mit HUD zu vermeiden
        
        for i, (text, _, opacity) in enumerate(self.notifications):
            # Position berechnen
            notification_y = start_y + i * (notification_height + notification_spacing)
            notification_rect = pygame.Rect(
                self.screen_width // 2 - notification_width // 2,
                notification_y,
                notification_width,
                notification_height
            )
            
            # Hintergrund mit Transparenz
            bg_surface = pygame.Surface((notification_width, notification_height), pygame.SRCALPHA)
            bg_color = HUD_NOTIFICATION_COLOR[:3] + (int(HUD_NOTIFICATION_COLOR[3] * opacity),)
            pygame.draw.rect(bg_surface, bg_color, 
                             (0, 0, notification_width, notification_height), 0, 5)
            
            # Text
            text_surf = self.text_font.render(text, True, UI_TEXT_COLOR)
            text_rect = text_surf.get_rect(center=(notification_width // 2, notification_height // 2))
            
            # Alles auf die Oberfläche bringen
            bg_surface.blit(text_surf, text_rect)
            surface.blit(bg_surface, notification_rect)
    
    def _render_debug_info(self, surface: pygame.Surface, fps: int) -> None:
        """Zeichnet Debug-Informationen."""
        # FPS-Anzeige
        fps_text = f"FPS: {fps}"
        fps_surf = self.small_font.render(fps_text, True, HUD_DEBUG_COLOR)
        fps_rect = fps_surf.get_rect(bottomleft=(10, self.screen_height - 10))
        
        # Hintergrund für bessere Lesbarkeit
        bg_rect = fps_rect.inflate(10, 5)
        pygame.draw.rect(surface, (0, 0, 0, 150), bg_rect)
        
        surface.blit(fps_surf, fps_rect)


class MinimapWidget:
    """Zeigt eine kleine Karte der Spielwelt an."""
    def __init__(self, screen_width: int, screen_height: int, 
                minimap_size: Tuple[int, int] = (150, 100)):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width, self.height = minimap_size
        
        # Position in der rechten oberen Ecke
        self.rect = pygame.Rect(
            screen_width - self.width - 20,
            60,  # Position oben
            self.width, self.height
        )
        
        # Minimap-Oberfläche
        self.minimap_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.border_color = HUD_BORDER_COLOR
        self.background_color = (0, 0, 0, 150)  # Halbtransparent
    
    def render(self, surface: pygame.Surface, game_objects: List[Dict], player_pos: Tuple[float, float], 
              level_width: float, level_height: float, hud_time_rect: Optional[pygame.Rect] = None) -> None:
        """Zeichnet die Minimap mit Spielobjekten."""
        # Leere Minimap erstellen
        self.minimap_surface.fill(self.background_color)
        
        # Skalierungsfaktoren berechnen
        scale_x = self.width / level_width
        scale_y = self.height / level_height
        
        # Alle Objekte zeichnen
        for obj in game_objects:
            # Position und Größe berechnen
            minimap_x = int(obj['x'] * scale_x)
            minimap_y = int(obj['y'] * scale_y)
            minimap_width = max(2, int(obj['width'] * scale_x))
            minimap_height = max(2, int(obj['height'] * scale_y))
            
            # Verschiedene Objekttypen mit unterschiedlichen Farben darstellen
            if obj['type'] == 'platform':
                obj_color = (100, 100, 100)
            elif obj['type'] == 'enemy':
                obj_color = (200, 50, 50)
            elif obj['type'] == 'collectible':
                obj_color = (50, 200, 50)
            elif obj['type'] == 'portal':
                obj_color = (150, 50, 200)
            elif obj['type'] == 'powerup':
                obj_color = (200, 200, 50)
            else:
                obj_color = (150, 150, 150)
            
            # Objekt zeichnen
            pygame.draw.rect(self.minimap_surface, obj_color, 
                           (minimap_x, minimap_y, minimap_width, minimap_height))
        
        # Spieler zeichnen (als kleiner blauer Punkt)
        player_minimap_x = int(player_pos[0] * scale_x)
        player_minimap_y = int(player_pos[1] * scale_y)
        
        # Sicherstellen, dass die Koordinaten innerhalb der Minimap liegen
        player_minimap_x = max(3, min(self.width - 3, player_minimap_x))
        player_minimap_y = max(3, min(self.height - 3, player_minimap_y))
        
        pygame.draw.circle(self.minimap_surface, (0, 0, 255), 
                         (player_minimap_x, player_minimap_y), 3)
        
        # Rahmen zeichnen
        pygame.draw.rect(self.minimap_surface, self.border_color, 
                       (0, 0, self.width, self.height), 2)
        
        # Minimap auf den Bildschirm zeichnen
        surface.blit(self.minimap_surface, self.rect)
        
        # Position der Zeitanzeige unter der Minimap aktualisieren, falls übergeben
        if hud_time_rect is not None:
            # Zeitanzeige unter der Minimap positionieren
            hud_time_rect.x = self.rect.x + self.rect.width - hud_time_rect.width
            hud_time_rect.y = self.rect.y + self.rect.height + 10


class PowerupWidget:
    """Zeigt aktive Powerups und ihre verbleibende Zeit an."""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Position in der linken unteren Ecke
        self.x = 20
        self.y = screen_height - 80
        self.icon_size = 32
        self.spacing = 10
        
        # Schriftart
        self.font = pygame.font.SysFont('Arial', 12)
        
        # Icons für verschiedene Powerups
        self.powerup_icons = self._create_powerup_icons()
    
    def _create_powerup_icons(self) -> Dict[str, pygame.Surface]:
        """Erstellt Icons für die verschiedenen Powerups."""
        icons = {}
        
        # Doppelsprung
        double_jump_icon = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        pygame.draw.polygon(double_jump_icon, (100, 200, 255), 
                          [(16, 5), (5, 16), (27, 16)])
        pygame.draw.polygon(double_jump_icon, (50, 150, 255), 
                          [(16, 12), (5, 23), (27, 23)])
        icons["jump"] = double_jump_icon
        
        # Unverwundbarkeit
        invincibility_icon = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        pygame.draw.circle(invincibility_icon, (255, 215, 0), (16, 16), 12)
        pygame.draw.circle(invincibility_icon, (255, 150, 0), (16, 16), 8)
        icons["invincibility"] = invincibility_icon
        
        # Geschwindigkeit
        speed_icon = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        for i in range(3):
            pygame.draw.line(speed_icon, (50, 255, 50), 
                           (8 + i*5, 8), (18 + i*5, 24), 3)
        icons["speed"] = speed_icon
        
        # Gravitationsänderung
        gravity_icon = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        pygame.draw.circle(gravity_icon, (100, 200, 100), (16, 16), 12, 2)
        pygame.draw.line(gravity_icon, (100, 200, 100), (8, 20), (24, 12), 2)
        pygame.draw.polygon(gravity_icon, (100, 200, 100), 
                          [(22, 8), (26, 12), (22, 16)])
        icons["gravity"] = gravity_icon
        
        return icons
    
    def render(self, surface: pygame.Surface, active_powerups: Dict[str, bool]) -> None:
        """Zeichnet aktive Powerups und ihre verbleibende Zeit."""
        curr_x = self.x
        
        # Filtere aktive Powerups: Nur diejenigen behalten, die auch aktiv sind (True)
        active_powerup_types = [p for p, active in active_powerups.items() if active]
        
        for powerup_name in active_powerup_types:
            if powerup_name in self.powerup_icons:
                # Icon zeichnen
                icon = self.powerup_icons[powerup_name]
                surface.blit(icon, (curr_x, self.y))
                
                # Powerup-Name anzeigen
                name_map = {
                    "speed": "Geschwindigkeit",
                    "jump": "Sprungkraft",
                    "invincibility": "Unverwundbar",
                    "gravity": "Schwerkraft"
                }
                display_name = name_map.get(powerup_name, powerup_name)
                
                # Verbleibende Zeit (für Anzeige)
                name_surf = self.font.render(display_name, True, WHITE)
                
                # Stellen sicher, dass die Positionen Ganzzahlen sind
                name_rect = name_surf.get_rect(center=(
                    int(curr_x + self.icon_size // 2), 
                    int(self.y + self.icon_size + 10)
                ))
                
                surface.blit(name_surf, name_rect)
                
                # Position für das nächste Powerup
                curr_x += self.icon_size + self.spacing 