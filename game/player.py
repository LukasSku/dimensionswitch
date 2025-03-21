import pygame
import math
import time
from typing import Dict, List, Tuple, Set, Any, Optional, Union
from game.constants import *
from game.utils import check_collision
from game.game_objects import GameObject, Platform, Portal, Collectible, Enemy

class Player:
    """Repräsentiert den Spieler-Charakter mit Bewegungs- und Kollisionslogik."""
    
    __slots__ = ('x', 'y', 'width', 'height', 'velocity_x', 'velocity_y', 
                'on_ground', 'is_dead', 'level_completed', 'collected_item',
                'jump_count', 'max_jumps', 'direction', 'animation_frame', 
                'frame_timer', 'last_x', 'step_distance', 'lives', 'score',
                'active_powerups', 'powerup_timers', 'invincible_timer', 
                'animation_state', 'collision_rects', 'last_safe_position',
                'last_portal_time')
    
    def __init__(self, x: float, y: float):
        """Initialisiert den Spieler an der gegebenen Position."""
        self.reset(x, y)
        
    def reset(self, x: float, y: float) -> None:
        """Setzt den Spieler auf die Startposition und alle Werte zurück."""
        # Position und Größe
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        
        # Bewegung
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.on_ground = False
        
        # Spielzustand
        self.is_dead = False
        self.level_completed = False
        self.collected_item = False
        
        # Springen
        self.jump_count = 0
        self.max_jumps = 2  # Doppelsprung als Standard
        
        # Animation
        self.direction = 1  # 1 = rechts, -1 = links
        self.animation_frame = 0
        self.frame_timer = 0
        self.animation_state = "idle"  # "idle", "run", "jump", "fall"
        
        # Für Schrittgeräusche
        self.last_x = x
        self.step_distance = 0.0
        
        # Leben und Punkte
        self.lives = PLAYER_STARTING_LIVES
        self.score = 0
        
        # Powerups
        self.active_powerups: Dict[str, bool] = {}
        self.powerup_timers: Dict[str, float] = {}
        self.invincible_timer = 0.0  # Nach Treffer kurz unverwundbar
        
        # Vorberechnete Kollisionsrechtecke für präzisere Kollisionserkennung
        self.collision_rects = {
            "top": pygame.Rect(x + 5, y, self.width - 10, 5),
            "bottom": pygame.Rect(x + 5, y + self.height - 5, self.width - 10, 5),
            "left": pygame.Rect(x, y + 5, 5, self.height - 10),
            "right": pygame.Rect(x + self.width - 5, y + 5, 5, self.height - 10)
        }
        
        # Letzte sichere Position (für Fallback bei Kollisionsproblemen)
        self.last_safe_position = (x, y)
        
        # Portal-Cooldown
        self.last_portal_time = time.time()
        
    def move_left(self) -> None:
        """Bewegt den Spieler nach links."""
        # Geschwindigkeit durch Powerups anpassen
        speed_multiplier = self.get_powerup_effect("speed", 1.0)
        self.velocity_x = -PLAYER_SPEED * speed_multiplier
        self.direction = -1
        self.animation_state = "run"
        
    def move_right(self) -> None:
        """Bewegt den Spieler nach rechts."""
        # Geschwindigkeit durch Powerups anpassen
        speed_multiplier = self.get_powerup_effect("speed", 1.0)
        self.velocity_x = PLAYER_SPEED * speed_multiplier
        self.direction = 1
        self.animation_state = "run"
        
    def stop_horizontal_movement(self) -> None:
        """Stoppt die horizontale Bewegung."""
        self.velocity_x = 0
        if self.on_ground:
            self.animation_state = "idle"
        
    def jump(self) -> bool:
        """Führt einen Sprung aus, wenn möglich."""
        if self.jump_count < self.max_jumps:
            # Sprungkraft durch Powerups anpassen
            jump_multiplier = self.get_powerup_effect("jump", 1.0)
            
            # Reduzierte Sprungkraft beim zweiten Sprung
            jump_strength = PLAYER_JUMP_STRENGTH
            if self.jump_count > 0:
                jump_strength *= 0.8
                
            self.velocity_y = jump_strength * jump_multiplier
            self.jump_count += 1
            self.on_ground = False
            self.animation_state = "jump"
            return True
        return False
    
    def get_rect(self) -> pygame.Rect:
        """Gibt das Rechteck des Spielers zurück."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def add_powerup(self, powerup_type: str, duration: float) -> None:
        """Fügt ein Powerup hinzu und setzt dessen Timer."""
        self.active_powerups[powerup_type] = True
        
        # Bei existierendem Powerup Timer verlängern statt überschreiben
        if powerup_type in self.powerup_timers:
            self.powerup_timers[powerup_type] += duration
        else:
            self.powerup_timers[powerup_type] = duration
            
        # Spezielle Powerup-Effekte anwenden
        if powerup_type == "jump":
            self.max_jumps = 3  # Dreifachsprung mit Sprung-Powerup
    
    def get_powerup_effect(self, powerup_type: str, default_value: float = 1.0) -> float:
        """Gibt den Effekt-Multiplikator für ein bestimmtes Powerup zurück."""
        if powerup_type not in self.active_powerups or not self.active_powerups[powerup_type]:
            return default_value
            
        # Powerup-spezifische Effekte
        if powerup_type == "speed":
            return 1.5  # 50% schneller
        elif powerup_type == "jump":
            return 1.3  # 30% höhere Sprünge
        elif powerup_type == "gravity":
            return 0.7  # 30% weniger Schwerkraft
        
        return default_value
    
    def update_powerups(self, dt: float) -> None:
        """Aktualisiert die Timer für alle aktiven Powerups."""
        expired_powerups = []
        
        for powerup_type, time_remaining in self.powerup_timers.items():
            # Timer reduzieren
            self.powerup_timers[powerup_type] -= dt
            
            # Abgelaufene Powerups markieren
            if self.powerup_timers[powerup_type] <= 0:
                expired_powerups.append(powerup_type)
        
        # Abgelaufene Powerups entfernen
        for powerup_type in expired_powerups:
            self.active_powerups[powerup_type] = False
            del self.powerup_timers[powerup_type]
            
            # Spezielle Powerup-Effekte zurücksetzen
            if powerup_type == "jump":
                self.max_jumps = 2  # Zurück zu Doppelsprung
                
        # Unverwundbarkeits-Timer aktualisieren
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
    
    def _update_animation(self, dt: float) -> None:
        """Aktualisiert den Animationszustand des Spielers."""
        self.frame_timer += dt
        
        # Animationsgeschwindigkeit basierend auf Bewegungszustand
        anim_speed = 0.1  # Basisgeschwindigkeit
        
        if self.animation_state == "run":
            anim_speed = 0.07
        elif self.animation_state == "jump" or self.animation_state == "fall":
            anim_speed = 0.15
            
        # Nächster Frame, wenn Timer abgelaufen
        if self.frame_timer >= anim_speed:
            self.animation_frame = (self.animation_frame + 1) % 4  # 4 Frames pro Animation
            self.frame_timer = 0
            
    def _update_collision_rects(self) -> None:
        """Aktualisiert die Kollisionsrechtecke basierend auf der aktuellen Position."""
        self.collision_rects["top"].x = self.x + 5
        self.collision_rects["top"].y = self.y
        
        self.collision_rects["bottom"].x = self.x + 5
        self.collision_rects["bottom"].y = self.y + self.height - 5
        
        self.collision_rects["left"].x = self.x
        self.collision_rects["left"].y = self.y + 5
        
        self.collision_rects["right"].x = self.x + self.width - 5
        self.collision_rects["right"].y = self.y + 5
            
    def update(self, dt: float, platforms: List[Platform], portals: List[Portal], 
              collectibles: List[Collectible], enemies: List[Enemy], current_dimension: int = 1) -> Dict[str, Any]:
        """Aktualisiert den Spielerzustand und prüft Kollisionen."""
        # Event-Dictionary für Rückgabe
        events = {}
        
        # Keine Updates, wenn tot
        if self.is_dead:
            return events
            
        # Sichere Position speichern (für Fallback)
        if self.on_ground:
            self.last_safe_position = (self.x, self.y)
            
        # Bewegung anhand Delta-Zeit aktualisieren
        # Powerup-Effekte berücksichtigen
        gravity_multiplier = self.get_powerup_effect("gravity", 1.0)
        
        # Schwerkraft anwenden
        self.velocity_y += GRAVITY * gravity_multiplier * dt
        
        # Maximum-Fallgeschwindigkeit begrenzen
        max_fall_speed = MAX_FALL_SPEED * gravity_multiplier
        self.velocity_y = min(self.velocity_y, max_fall_speed)
        
        # Position aktualisieren
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Spielbegrenzungen einhalten
        self.x = max(0, min(self.x, LEVEL_WIDTH - self.width))
        
        # Animationszustand aktualisieren
        self._update_animation(dt)
        
        # Kollisionsrechtecke aktualisieren
        self._update_collision_rects()
        
        # Kollisionen prüfen - aktuelle Dimension übergeben
        self.check_platform_collisions(platforms, current_dimension)
        
        # Audio-Events (Schritte) erkennen
        step_threshold = 40  # Pixel Bewegung für ein Schrittgeräusch
        if self.on_ground and abs(self.x - self.last_x) > 0:
            self.step_distance += abs(self.x - self.last_x)
            if self.step_distance >= step_threshold:
                events["step"] = True
                self.step_distance = 0
        
        self.last_x = self.x
        
        # Powerups aktualisieren
        self.update_powerups(dt)
        
        # Animationszustand basierend auf Bewegung aktualisieren
        if not self.on_ground:
            if self.velocity_y < 0:
                self.animation_state = "jump"
            else:
                self.animation_state = "fall"
        elif self.velocity_x == 0:
            self.animation_state = "idle"
        else:
            self.animation_state = "run"
            
        # Kollisionen mit anderen Objekten prüfen
        # Portal-Kollision mit verbesserter Logik
        if self._check_portal_collision(portals):
            print("[DEBUG] Portal-Kollision erkannt! Level abgeschlossen.")
            # Sicherstellen, dass wir ein eindeutiges Ereignis mit Verzögerung auslösen
            events["level_complete"] = True
            self.level_completed = True
            
            # Kurze Verzögerung, um sicherzustellen, dass das Level vollständig geladen wird
            time.sleep(0.3)
            
        if self.check_collectible_collisions(collectibles):
            events["collect"] = True
            self.collected_item = True
            
        enemy_hit = self.check_enemy_collisions(enemies)
        if enemy_hit == "player_death":
            if not self.is_invincible() and not self.active_powerups.get("invincibility", False):
                self.lives -= 1
                self.is_dead = self.lives <= 0
                events["player_death"] = True
                
                # Kurze Unverwundbarkeit nach Treffer
                if not self.is_dead:
                    self.invincible_timer = PLAYER_INVINCIBILITY_AFTER_HIT
        elif enemy_hit == "enemy_death":
            events["enemy_death"] = True
            
        # Tod durch Fallen aus der Welt
        if self.y > LEVEL_HEIGHT:
            self.lives -= 1
            self.is_dead = self.lives <= 0
            events["player_death"] = True
            
        return events
    
    def is_invincible(self) -> bool:
        """Gibt zurück, ob der Spieler aktuell unverwundbar ist."""
        return self.invincible_timer > 0 or self.active_powerups.get("invincibility", False)
        
    def check_platform_collisions(self, platforms: List[Platform], current_dimension: int) -> None:
        """Prüft und behandelt Kollisionen mit Plattformen."""
        self.on_ground = False
        
        player_rect = self.get_rect()
        
        # Erweitere den bottom_rect für bessere Kollisionserkennung
        bottom_rect = pygame.Rect(
            self.x + 2,
            self.y + self.height - 6,
            self.width - 4,
            10  # Größerer Bereich für Kollisionserkennung
        )
        
        for platform in platforms:
            # Nur Kollisionen mit Plattformen überprüfen, die in der aktuellen Dimension sichtbar sind
            if not (platform.dimension_visible == -1 or platform.dimension_visible == current_dimension):
                continue
                
            platform_rect = platform.get_rect()
            
            # Performante Vorprüfung
            if not player_rect.colliderect(platform_rect):
                continue
            
            # Kollisionsrichtung bestimmen mit verbesserter Boden-Erkennung
            if bottom_rect.colliderect(platform_rect) and self.velocity_y >= 0:
                # Der Spieler ist auf der Plattform gelandet
                self.y = platform_rect.y - self.height
                self.velocity_y = 0
                self.on_ground = True
                self.jump_count = 0  # Sprünge zurücksetzen
                continue
                
            # Präzisere Kollisionsprüfung mit der check_collision Funktion
            collision_side = check_collision(player_rect, platform_rect)
            
            if collision_side == "bottom":
                # Auf dem Boden gelandet - sollte durch die verbesserte Prüfung oben bereits abgedeckt sein
                self.y = platform_rect.y - self.height
                self.velocity_y = 0
                self.on_ground = True
                self.jump_count = 0  # Sprünge zurücksetzen
                
            elif collision_side == "top":
                # Kopf an Plattform gestoßen
                self.y = platform_rect.y + platform_rect.height
                self.velocity_y = 0
                
            elif collision_side == "left":
                # Linke Seite kollidiert
                self.x = platform_rect.x - self.width + 1  # +1 um Hängenbleiben zu vermeiden
                self.velocity_x = 0
                
            elif collision_side == "right":
                # Rechte Seite kollidiert
                self.x = platform_rect.x + platform_rect.width - 1  # -1 um Hängenbleiben zu vermeiden
                self.velocity_x = 0
    
    def _check_portal_collision(self, portals: List[Portal]) -> bool:
        """
        Verbesserte Portalprüfung mit Cooldown und Robustheit.
        Verhindert mehrfache Portal-Kollisionen.
        """
        player_rect = self.get_rect()
        current_time = time.time()
        
        # Nur prüfen, wenn Cooldown abgelaufen ist
        if current_time - self.last_portal_time < 1.0:
            return False
            
        for portal in portals:
            portal_rect = portal.get_rect()
            # Prüfen, ob der Mittelpunkt des Spielers im Portal ist (robustere Kollisionserkennung)
            player_center_x = self.x + self.width / 2
            player_center_y = self.y + self.height / 2
            
            if (portal_rect.collidepoint(player_center_x, player_center_y) or
                player_rect.colliderect(portal_rect)):
                # Portal-Cooldown aktualisieren
                self.last_portal_time = current_time
                print(f"[DEBUG] Portal bei ({portal.x}, {portal.y}) betreten")
                return True
                
        return False
    
    def check_collectible_collisions(self, collectibles: List[Collectible]) -> bool:
        """Prüft Kollisionen mit Sammelobjekten und markiert diese als gesammelt."""
        player_rect = self.get_rect()
        collected = False
        
        for collectible in collectibles:
            if not collectible.collected and player_rect.colliderect(collectible.get_rect()):
                collectible.collected = True
                collected = True
                
        return collected
    
    def check_enemy_collisions(self, enemies: List[Enemy]) -> Optional[str]:
        """
        Prüft Kollisionen mit Gegnern.
        Rückgabewerte:
        - "player_death": Spieler wurde vom Gegner getroffen
        - "enemy_death": Spieler hat Gegner besiegt
        - None: Keine Kollision
        """
        player_rect = self.get_rect()
        bottom_rect = self.collision_rects["bottom"]
        
        for enemy in enemies:
            if enemy.is_dead:
                continue
                
            enemy_rect = enemy.get_rect()
            
            if player_rect.colliderect(enemy_rect):
                # Wenn der Spieler von oben auf den Gegner springt
                if bottom_rect.colliderect(enemy_rect) and self.velocity_y > 0:
                    enemy.die()
                    self.velocity_y = PLAYER_JUMP_STRENGTH * 0.7  # Abprallen
                    return "enemy_death"
                # Sonst trifft der Gegner den Spieler (außer bei Unverwundbarkeit)
                elif not self.is_invincible():
                    return "player_death"
                    
        return None
    
    def render(self, surface: pygame.Surface) -> None:
        """Rendert den Spieler auf die angegebene Oberfläche."""
        # Farbe basierend auf aktivem Powerup anpassen
        player_color = PLAYER_COLOR
        
        # Farbänderung für Powerups
        if self.active_powerups.get("speed", False):
            player_color = (0, 200, 255)  # Blau-Türkis für Geschwindigkeit
        elif self.active_powerups.get("jump", False):
            player_color = (200, 100, 255)  # Violett für Sprungkraft
        elif self.active_powerups.get("invincibility", False):
            player_color = (255, 215, 0)  # Gold für Unverwundbarkeit
        elif self.active_powerups.get("gravity", False):
            player_color = (100, 255, 100)  # Grün für Schwerkraft
            
        # Blinken bei temporärer Unverwundbarkeit nach Treffer
        if self.invincible_timer > 0 and math.floor(self.invincible_timer * 10) % 2 == 0:
            player_color = (255, 255, 255)  # Weiß für Blinken
            
        # Körper
        pygame.draw.rect(surface, player_color, self.get_rect())
        
        # Augen
        eye_offset = 10 if self.direction > 0 else -10
        eye_x = self.x + 10 if self.direction < 0 else self.x + 30
        
        # Stelle sicher, dass die Position als Tupel (int, int) übergeben wird
        eye_pos = (int(eye_x), int(self.y + 20))
        eye_pupil_pos = (int(eye_x + eye_offset // 3), int(self.y + 20))
        pygame.draw.circle(surface, WHITE, eye_pos, 8)
        pygame.draw.circle(surface, BLACK, eye_pupil_pos, 4)
        
        # Beine/Animation basierend auf Bewegungszustand
        if self.animation_state == "run":
            leg_offset = 5 if self.animation_frame % 2 == 0 else -5
            pygame.draw.rect(surface, player_color, 
                           (self.x + 10, self.y + self.height - 20, 
                            10, 20 + leg_offset))
            pygame.draw.rect(surface, player_color, 
                           (self.x + self.width - 20, self.y + self.height - 20, 
                            10, 20 - leg_offset))
        elif self.animation_state == "jump":
            # Beinhaltung beim Springen
            pygame.draw.rect(surface, player_color, 
                           (self.x + 5, self.y + self.height - 15, 
                            15, 15))
            pygame.draw.rect(surface, player_color, 
                           (self.x + self.width - 20, self.y + self.height - 15, 
                            15, 15))
        else:
            # Normale Beine
            pygame.draw.rect(surface, player_color, 
                           (self.x + 10, self.y + self.height - 20, 
                            10, 20))
            pygame.draw.rect(surface, player_color, 
                           (self.x + self.width - 20, self.y + self.height - 20, 
                            10, 20))
            
    def get_status(self) -> Dict[str, Any]:
        """Gibt ein Dictionary mit dem aktuellen Spielerstatus zurück."""
        return {
            "position": (self.x, self.y),
            "velocity": (self.velocity_x, self.velocity_y),
            "on_ground": self.on_ground,
            "jumps": self.jump_count,
            "lives": self.lives,
            "active_powerups": list(filter(lambda x: self.active_powerups.get(x, False), self.active_powerups.keys())),
            "is_dead": self.is_dead,
            "invincible": self.is_invincible()
        } 