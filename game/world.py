import pygame
import random
import numpy as np
from typing import List, Dict, Tuple, Optional, Set, Union, Any
from game.constants import *
from game.game_objects import GameObject, Platform, Portal, Collectible, Enemy, Powerup

class World:
    """Verwaltet alle Spielobjekte, Partikel und die Kamera in der Spielwelt."""
    
    def __init__(self):
        # Spielobjekte
        self.platforms: List[Platform] = []
        self.portals: List[Portal] = []
        self.collectibles: List[Collectible] = []
        self.enemies: List[Enemy] = []
        self.powerups: List[Powerup] = []
        
        # Partikel
        self.background_particles: List[Dict[str, Any]] = []
        self.foreground_particles: np.ndarray = np.zeros((0, 7))  # x, y, größe, vx, vy, lebensdauer, farbe_index
        
        # Partikel-Cache für Wiederverwendung (Object Pooling)
        self.particle_pool_size = 300
        self.particle_pool: np.ndarray = np.zeros((self.particle_pool_size, 7))
        self.active_particles = 0
        
        # Kamera-Position und Ziel für sanftes Scrollen
        self.camera_x: float = 0.0
        self.camera_y: float = 0.0
        self.camera_target_x: float = 0.0
        self.camera_target_y: float = 0.0
        
        # Begrenzungen der Welt
        self.world_width: int = SCREEN_WIDTH
        self.world_height: int = SCREEN_HEIGHT
        
        # Farb-Lookup-Tabelle für Partikel (vermeidet viele kleine Dictionaries)
        self.particle_colors: List[Tuple[int, int, int, int]] = [
            (150, 150, 255, 100),  # Normale Dimension
            (255, 200, 150, 150),  # Spiegel-Dimension
            (100, 255, 200, 120),  # Zeit-Dimension
            (200, 150, 255, 130)   # Quanten-Dimension
        ]
        
        # Vorinitialisierte Arrays für bessere Performance
        self._init_particles()
        
    def _init_particles(self) -> None:
        """Initialisiert Hintergrund- und Vordergrundpartikel für visuelle Effekte."""
        # Hintergrundpartikel (Sterne/Umgebungspartikel)
        self.background_particles.clear()
        for _ in range(100):
            particle = {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.2, 1.0),
                'depth': random.uniform(0.5, 1.0),  # Tiefenwert für Parallax-Effekt
                'color': (
                    random.randint(180, 255),
                    random.randint(180, 255),
                    random.randint(200, 255)
                )
            }
            self.background_particles.append(particle)
            
        # Numpy-Arrays für optimierte Partikelverwaltung vorbereiten
        self.particle_positions = np.zeros((len(self.background_particles), 2), dtype=np.float32)
        self.particle_velocities = np.zeros((len(self.background_particles), 2), dtype=np.float32)
        self.particle_depths = np.zeros(len(self.background_particles), dtype=np.float32)
        self.particle_sizes = np.zeros(len(self.background_particles), dtype=np.float32)
        
        # Arrays mit Initialdaten füllen
        for i, particle in enumerate(self.background_particles):
            self.particle_positions[i] = [particle['x'], particle['y']]
            self.particle_velocities[i] = [0, particle['speed']]
            self.particle_depths[i] = particle['depth']
            self.particle_sizes[i] = particle['size']
        
        # Vordergrundpartikel-Pool vorbereiten (Object Pooling)
        self.foreground_particles = np.zeros((self.particle_pool_size, 7), dtype=np.float32)
        # Struktur: x, y, größe, vx, vy, lebensdauer, farbe_index
    
    def generate_level(self, level_number: int) -> None:
        """Generiert ein Level basierend auf der Levelnummer."""
        # Bestehende Objekte löschen
        self._clear_level()
        
        # Debug-Info
        print(f"[DEBUG] Generiere Level {level_number}...")
        
        # Level basierend auf der Nummer auswählen
        if level_number == 0:
            self._generate_tutorial_level()
        elif level_number == 1:
            self._generate_mirror_level()
        elif level_number == 2:
            self._generate_time_warp_level()
        else:
            # Höhere Level werden zufällig generiert
            self._generate_random_level(level_number)
            
        # Debug-Info zur Validierung
        self._debug_level_objects()
        
    def _debug_level_objects(self) -> None:
        """Gibt Debug-Informationen zu allen Levelobjekten aus."""
        print(f"[DEBUG] Level enthält:")
        print(f"  - Plattformen: {len(self.platforms)}")
        print(f"  - Gegner: {len(self.enemies)}")
        print(f"  - Sammelobjekte: {len(self.collectibles)}")
        print(f"  - Portale: {len(self.portals)}")
        print(f"  - Powerups: {len(self.powerups)}")
        
        # Plattformenpositionen
        if len(self.platforms) > 0:
            print("  - Plattform-Positionen:")
            for i, platform in enumerate(self.platforms):
                print(f"    {i+1}: ({platform.x}, {platform.y}), Größe: {platform.width}x{platform.height}")
                
        # Portalpositionen
        if len(self.portals) > 0:
            print("  - Portal-Positionen:")
            for i, portal in enumerate(self.portals):
                print(f"    {i+1}: ({portal.x}, {portal.y})")
            
    def _generate_tutorial_level(self) -> None:
        """Generiert das Tutorial-Level mit einfachen Hinweisen für neue Spieler."""
        # Plattformen
        self.platforms.append(Platform(300, 550, 200, 20))
        self.platforms.append(Platform(600, 450, 200, 20))
        self.platforms.append(Platform(300, 350, 200, 20))
        self.platforms.append(Platform(600, 250, 200, 20))
        
        # Sammelobjekte
        self.collectibles.append(Collectible(350, 520))
        self.collectibles.append(Collectible(650, 220))
        
        # Portal
        self.portals.append(Portal(750, 190))
        
    def _generate_mirror_level(self) -> None:
        """Generiert das Spiegel-Dimensions-Level mit Plattformen, die nur in der Spiegeldimension sichtbar sind."""
        # Plattformen (spiegeln sich in anderer Dimension)
        self.platforms.append(Platform(200, 600, 150, 20))
        self.platforms.append(Platform(400, 500, 150, 20))
        self.platforms.append(Platform(600, 400, 150, 20))
        self.platforms.append(Platform(800, 300, 150, 20))
        self.platforms.append(Platform(1000, 200, 150, 20))
        
        # Dimensionsabhängige Plattformen
        mirror_platform1 = Platform(300, 450, 100, 20)
        mirror_platform1.dimension_visible = DIMENSION_MIRROR
        self.platforms.append(mirror_platform1)
        
        mirror_platform2 = Platform(700, 250, 100, 20)
        mirror_platform2.dimension_visible = DIMENSION_MIRROR
        self.platforms.append(mirror_platform2)
        
        # Sammelobjekte
        self.collectibles.append(Collectible(250, 570))
        self.collectibles.append(Collectible(450, 470))
        self.collectibles.append(Collectible(650, 370))
        self.collectibles.append(Collectible(850, 270))
        
        # Gegner
        self.enemies.append(Enemy(450, 470, 400, 600))
        self.enemies.append(Enemy(850, 270, 800, 950))
        
        # Portal
        self.portals.append(Portal(1080, 140))
        
    def _generate_time_warp_level(self) -> None:
        """Generiert das Zeitdehnungs-Level mit einzigartigen Zeiteffekten."""
        print("[DEBUG] Generiere Zeit-Level (Level 2)...")
        
        # Aktive Partikel zurücksetzen (für saubere Umgebung)
        self.active_particles = 0
        
        # Sichere Boden-Plattform (immer oben in der Liste)
        floor = Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
        self.platforms.clear()  # Vorhandene löschen, falls vorhanden
        self.platforms.append(floor)
        
        # Start- und Ende-Plattformen (essentiell)
        self.platforms.append(Platform(100, 500, 200, 20))  # Startplattform
        self.platforms.append(Platform(500, 500, 200, 20))  # Mittlere Plattform
        
        # Dritte Plattform (war problematisch)
        self.platforms.append(Platform(790, 410, 180, 20))
        print("[DEBUG] Dritte Plattform erstellt: (790, 410)")
        
        # Backup-Plattformen für bessere Spielbarkeit
        self.platforms.append(Platform(750, 450, 150, 20))
        self.platforms.append(Platform(850, 370, 150, 20))
        
        # Zusätzliche Plattformen für das obere Level
        self.platforms.append(Platform(700, 250, 180, 20))
        self.platforms.append(Platform(400, 350, 150, 20))
        self.platforms.append(Platform(200, 400, 150, 20))
        
        # Verifizierbarer Status nach Plattform-Erstellung
        print(f"[DEBUG] Zeit-Level hat {len(self.platforms)} Plattformen erstellt")
        
        # Zeitabhängige Plattformen
        time_platform1 = Platform(500, 300, 150, 20)
        time_platform1.dimension_visible = DIMENSION_TIME_SLOW
        self.platforms.append(time_platform1)
        
        time_platform2 = Platform(300, 200, 150, 20)
        time_platform2.dimension_visible = DIMENSION_TIME_SLOW
        self.platforms.append(time_platform2)
        
        # Gegner
        fast_enemy = Enemy(550, 470, 500, 700)
        fast_enemy.speed = 5
        self.enemies.append(fast_enemy)
        
        second_enemy = Enemy(750, 380, 700, 900)
        second_enemy.speed = 4
        self.enemies.append(second_enemy)
        
        # Sammelobjekte
        self.collectibles.append(Collectible(250, 570))
        self.collectibles.append(Collectible(550, 470))
        self.collectibles.append(Collectible(850, 370))
        self.collectibles.append(Collectible(550, 270))
        self.collectibles.append(Collectible(350, 170))
        
        # Portal zum nächsten Level
        portal = Portal(900, 340)
        self.portals.append(portal)
        print(f"[DEBUG] Portal erstellt bei (900, 340)")
        
        # Powerup für zusätzlichen Anreiz
        self.powerups.append(Powerup(300, 370, "gravity"))
        
        # Final-Prüfung
        print(f"[DEBUG] Zeit-Level vollständig generiert. Plattformen: {len(self.platforms)}")
        print(f"[DEBUG] Erste Plattform bei ({self.platforms[0].x}, {self.platforms[0].y})")
        print(f"[DEBUG] Anzahl Portale: {len(self.portals)}")
        
    def _generate_random_level(self, level_number: int) -> None:
        """Generiert ein zufälliges Level basierend auf der Levelnummer für höhere Schwierigkeit."""
        platform_count = 5 + level_number
        enemy_count = level_number
        collectible_count = 3 + level_number
        
        # Breiter und höher für höhere Level
        level_width = SCREEN_WIDTH + level_number * 100
        level_height = SCREEN_HEIGHT
        
        # Zufällige Plattformen
        for _ in range(platform_count):
            x = random.randint(100, level_width - 200)
            y = random.randint(150, level_height - 100)
            width = random.randint(100, 250)
            height = 20
            
            platform = Platform(x, y, width, height)
            
            # Einige Plattformen sind nur in bestimmten Dimensionen sichtbar
            if random.random() < 0.3:
                platform.dimension_visible = random.choice([
                    DIMENSION_NORMAL, 
                    DIMENSION_MIRROR, 
                    DIMENSION_TIME_SLOW
                ])
                
            self.platforms.append(platform)
            
        # Plattformen sortieren nach y-Position (höchste zuerst)
        self.platforms.sort(key=lambda p: p.y)
            
        # Zufällige Gegner
        for _ in range(enemy_count):
            if len(self.platforms) > 1:
                platform = random.choice(self.platforms[1:])  # Den Boden ausschließen
                x = platform.x + random.randint(20, platform.width - 40)
                y = platform.y - 40
                patrol_left = max(platform.x - 50, 0)
                patrol_right = min(platform.x + platform.width + 50, level_width)
                
                enemy = Enemy(x, y, patrol_left, patrol_right)
                self.enemies.append(enemy)
            
        # Zufällige Sammelobjekte
        for _ in range(collectible_count):
            if len(self.platforms) > 1:
                platform = random.choice(self.platforms[1:])  # Den Boden ausschließen
                x = platform.x + random.randint(10, platform.width - 20)
                y = platform.y - 30
                
                collectible = Collectible(x, y)
                self.collectibles.append(collectible)
            
        # Portal an einer hohen Position
        if len(self.platforms) > 1:
            highest_platform = self.platforms[1]  # Zweit höchste Plattform (nach Sortierung)
            portal_x = highest_platform.x + highest_platform.width - 30
            portal_y = highest_platform.y - 60
            
            self.portals.append(Portal(portal_x, portal_y))
    
    def update(self, dt: float, player_x: float, player_y: float, current_dimension: int) -> None:
        """Aktualisiert die Welt und ihre Objekte basierend auf der verstrichenen Zeit."""
        # Kamera-Position aktualisieren
        self.camera_target_x = player_x - SCREEN_WIDTH // 2
        self.camera_target_y = player_y - SCREEN_HEIGHT // 2
        
        # Kamera in den Weltgrenzen halten
        self.camera_target_x = max(0, min(self.camera_target_x, self.world_width - SCREEN_WIDTH))
        self.camera_target_y = max(0, min(self.camera_target_y, self.world_height - SCREEN_HEIGHT))
        
        # Sanfte Kamerabewegung
        camera_smoothing = 0.1 * dt * 60
        self.camera_x += (self.camera_target_x - self.camera_x) * camera_smoothing
        self.camera_y += (self.camera_target_y - self.camera_y) * camera_smoothing
        
        # Hintergrundpartikel mit Numpy aktualisieren (vektorisierte Operation)
        # Tiefenwerte für die Parallaxe anwenden
        parallax_factor = self.particle_depths * 0.5
        
        # Partikel horizontal bewegen (mit Kamera)
        camera_delta_x = self.camera_target_x - self.camera_x
        # Explizit Überläufe vermeiden durch Typ-Konvertierung und Begrenzung
        try:
            # Sichere Berechnung mit Werten in einer vernünftigen Größenordnung
            safe_camera_delta = float(max(min(camera_delta_x, 100.0), -100.0))
            safe_parallax = np.clip(parallax_factor, 0.0, 1.0)
            safe_dt = float(max(min(dt, 0.1), 0.0))
            
            # Verwende explizite Typkonvertierung und np.subtract für kontrollierte Berechnung
            movement = safe_camera_delta * safe_parallax * safe_dt
            self.particle_positions[:, 0] = np.subtract(
                self.particle_positions[:, 0], 
                movement,
                dtype=np.float32  # Expliziter Datentyp zur Vermeidung von Überläufen
            )
        except Exception:
            # Bei Fehlern einfach die Partikel nicht bewegen
            pass
        
        # Partikel neu positionieren, wenn sie außerhalb des Bildschirms sind
        # Dies ist effizienter als individuelle Prüfungen
        screen_width_array = np.ones_like(self.particle_positions[:, 0]) * SCREEN_WIDTH
        
        # Partikel außerhalb des linken Bildschirmrands
        out_left = self.particle_positions[:, 0] < -10
        self.particle_positions[out_left, 0] = screen_width_array[out_left] + 10
        
        # Partikel außerhalb des rechten Bildschirmrands
        out_right = self.particle_positions[:, 0] > SCREEN_WIDTH + 10
        self.particle_positions[out_right, 0] = -10
        
        # Vordergrundpartikel aktualisieren
        if self.active_particles > 0:
            # Aktive Partikel extrahieren
            active_slice = self.foreground_particles[:self.active_particles]
            
            # Partikel in einem Schritt bewegen (vektorisiert)
            active_slice[:, 0] += active_slice[:, 3] * dt  # x += vx * dt
            active_slice[:, 1] += active_slice[:, 4] * dt  # y += vy * dt
            active_slice[:, 5] -= dt  # Lebensdauer verringern
            
            # Tote Partikel identifizieren
            dead_particles = active_slice[:, 5] <= 0
            dead_count = np.sum(dead_particles)
            
            if dead_count > 0:
                # Aktive Partikel kompaktieren (tote entfernen)
                self.active_particles -= dead_count
                if self.active_particles > 0:
                    # Lebende Partikel nach vorne verschieben
                    active_indices = np.where(active_slice[:, 5] > 0)[0]
                    self.foreground_particles[:self.active_particles] = active_slice[active_indices]
        
        # Dimensionsspezifische Partikeleffekte
        if random.random() < 0.05 * dt * 60:
            self._add_dimension_particle(current_dimension, player_x, player_y)
            
        # Gegner, Portale, Collectibles und Powerups aktualisieren
        for enemy in self.enemies:
            enemy.update(dt, current_dimension)
            
        for portal in self.portals:
            portal.update(dt)
            
        for collectible in self.collectibles:
            if not collectible.collected:
                collectible.update(dt)
            
        for powerup in self.powerups:
            if not powerup.collected:
                powerup.update(dt)
            
    def _add_dimension_particle(self, dimension: int, player_x: float, player_y: float) -> None:
        """Erzeugt ein Dimensionspartikel basierend auf aktueller Dimension."""
        # Bei vollem Partikel-Pool keine neuen Partikel erzeugen
        if self.active_particles >= self.particle_pool_size:
            return
            
        try:
            # Offset für zufällige Positionierung im sichtbaren Bereich
            offset_x = random.randint(-100, 100)
            offset_y = random.randint(-100, 100)
            
            # Dimensionsindex (für Farbe) und Parameter
            dim_index = min(max(1, dimension), 3) - 1  # Sicherstellen, dass der Index zwischen 0-2 liegt
            
            # Basisparameter für alle Dimensionen
            size = random.randint(2, 5)
            
            # Dimensionsspezifische Parameter
            if dimension == DIMENSION_NORMAL:
                vx = random.uniform(-0.5, 0.5)
                vy = random.uniform(-0.5, 0.2)
                life = random.uniform(1.0, 3.0)
            elif dimension == DIMENSION_MIRROR:
                vx = random.uniform(-1.0, 1.0)
                vy = random.uniform(-1.0, 1.0)
                life = random.uniform(0.5, 2.0)
            else:  # DIMENSION_TIME_SLOW oder Fallback
                vx = random.uniform(-0.2, 0.2)
                vy = random.uniform(-0.2, 0.2)
                life = random.uniform(2.0, 5.0)
                
            # Stelle sicher, dass wir mit primitiven Datentypen arbeiten
            pos_x = float(player_x) + float(offset_x) - float(self.camera_x)
            pos_y = float(player_y) + float(offset_y) - float(self.camera_y)
                
            # Partikel zum Pool hinzufügen mit expliziten Konvertierungen und Begrenzungen
            try:
                # Werte auf vernünftige Bereiche begrenzen
                safe_pos_x = max(min(float(pos_x), float(SCREEN_WIDTH)), 0.0)
                safe_pos_y = max(min(float(pos_y), float(SCREEN_HEIGHT)), 0.0)
                safe_size = max(min(float(size), 10.0), 1.0)
                safe_vx = max(min(float(vx), 5.0), -5.0)
                safe_vy = max(min(float(vy), 5.0), -5.0)
                safe_life = max(min(float(life), 10.0), 0.1)
                safe_dim_index = int(max(min(int(dim_index), 2), 0))
                
                # Explizit numpy.float32-Arrays verwenden, um Überläufe zu vermeiden
                particle_data = np.array([
                    safe_pos_x,
                    safe_pos_y,
                    safe_size,
                    safe_vx,
                    safe_vy,
                    safe_life,
                    safe_dim_index
                ], dtype=np.float32)
                
                self.foreground_particles[self.active_particles] = particle_data
                self.active_particles += 1
            except Exception as e:
                # Bei Fehlern keine Partikel erzeugen, aber Spielbetrieb aufrechterhalten
                pass
        except Exception as e:
            # Bei Fehlern keine Partikel erzeugen, aber Spielbetrieb aufrechterhalten
            pass
    
    def render(self, surface: pygame.Surface, current_dimension: int) -> None:
        """Rendert die gesamte Spielwelt auf die angegebene Oberfläche."""
        try:
            # Hintergrundpartikel
            for i in range(len(self.background_particles)):
                try:
                    pos = self.particle_positions[i]
                    depth = self.particle_depths[i]
                    
                    # Dimension-spezifische Farbänderungen
                    if current_dimension == DIMENSION_NORMAL:
                        color = self.background_particles[i]['color']
                    elif current_dimension == DIMENSION_MIRROR:
                        color = (
                            self.background_particles[i]['color'][2],
                            self.background_particles[i]['color'][1],
                            self.background_particles[i]['color'][0]
                        )
                    else:  # DIMENSION_TIME_SLOW
                        color = (
                            self.background_particles[i]['color'][0] // 2,
                            self.background_particles[i]['color'][1] // 2,
                            self.background_particles[i]['color'][2]
                        )
                        
                    # Tiefeneffekt (größere Partikel bewegen sich schneller = näher)
                    size = max(1, int(self.particle_sizes[i] * depth))
                    
                    # WICHTIG: NumPy-Array zu Python-Primitiven konvertieren
                    try:
                        # Zuerst zu float konvertieren und dann zu int, um NumPy-Typen zu vermeiden
                        x_pos = int(float(pos[0]))
                        y_pos = int(float(pos[1]))
                        
                        # Explizit ein Python-Tupel erstellen (keine NumPy-Arrays)
                        center_pos = (x_pos, y_pos)
                        pygame.draw.circle(surface, color, center_pos, size)
                    except Exception:
                        # Einzelne Partikel-Fehler ignorieren
                        continue
                except Exception:
                    # Einzelne Partikel-Fehler ignorieren
                    continue
            
            # Kamera-Versatz bestimmen
            camera_offset_x = int(self.camera_x)
            camera_offset_y = int(self.camera_y)
            
            # Plattformen rendern
            for i, platform in enumerate(self.platforms):
                try:
                    # Nur sichtbare Plattformen rendern (Kamera-Culling)
                    if self._is_visible(platform, camera_offset_x, camera_offset_y):
                        # Original-Position speichern
                        original_x, original_y = platform.x, platform.y
                        
                        # Position für Kamera anpassen
                        platform.x -= camera_offset_x
                        platform.y -= camera_offset_y
                        
                        # Rendern mit zusätzlicher Sicherheit für die dritte Plattform im Zeitlevel
                        try:
                            platform.render(surface, current_dimension)
                        except Exception as e:
                            # Fallback bei Rendering-Fehler
                            fallback_rect = pygame.Rect(
                                int(platform.x), 
                                int(platform.y), 
                                int(platform.width), 
                                int(platform.height)
                            )
                            pygame.draw.rect(surface, (150, 150, 150), fallback_rect)
                        
                        # Position wiederherstellen
                        platform.x, platform.y = original_x, original_y
                except Exception:
                    # Bei Fehler mit einer Plattform nicht das gesamte Rendering abbrechen
                    continue
            
            # Sammelobjekte rendern
            for collectible in self.collectibles:
                if not collectible.collected and self._is_visible(collectible, camera_offset_x, camera_offset_y):
                    original_x, original_y = collectible.x, collectible.y
                    collectible.x -= camera_offset_x
                    collectible.y -= camera_offset_y
                    collectible.render(surface, current_dimension)
                    collectible.x, collectible.y = original_x, original_y
            
            # Vordergrundpartikel auf separater Oberfläche mit Alpha-Blending rendern
            if self.active_particles > 0:
                try:
                    # Transparente Oberfläche für Partikel
                    particle_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    
                    # Aktive Partikel zeichnen
                    active_particles = self.foreground_particles[:self.active_particles]
                    
                    for i in range(self.active_particles):
                        try:
                            # Konvertiere explizit NumPy-Werte zu Python-Primitiven durch zweifache Konvertierung
                            x = float(float(active_particles[i, 0]))
                            y = float(float(active_particles[i, 1]))
                            size = float(float(active_particles[i, 2]))
                            life = float(float(active_particles[i, 5]))
                            dim_index = int(int(active_particles[i, 6]))
                            
                            # Falls dim_index außerhalb des gültigen Bereichs liegt, korrigieren
                            if dim_index < 0 or dim_index >= len(self.particle_colors):
                                dim_index = 0
                            
                            # Alpha-Wert basierend auf Lebensdauer
                            alpha = min(255, int(life * 100))
                            
                            # Farbindizes basierend auf Dimension
                            base_color = self.particle_colors[dim_index]
                            color = base_color[:3] + (alpha,)  # RGBA mit berechneter Transparenz
                            
                            # Explizit Python-Tupel erstellen und int-Werte verwenden
                            center_pos = (int(x), int(y))
                            int_size = int(size)
                            
                            # Partikel zeichnen
                            pygame.draw.circle(
                                particle_surface, 
                                color,
                                center_pos, 
                                int_size
                            )
                        except Exception:
                            # Einzelne Partikel-Fehler ignorieren
                            continue
                    
                    # Partikel-Oberfläche auf Hauptoberfläche übertragen
                    surface.blit(particle_surface, (0, 0))
                except Exception:
                    # Fehler beim Partikel-Rendering ignorieren
                    pass
            
            # Gegner rendern
            for enemy in self.enemies:
                if not enemy.is_dead and self._is_visible(enemy, camera_offset_x, camera_offset_y):
                    original_x, original_y = enemy.x, enemy.y
                    enemy.x -= camera_offset_x
                    enemy.y -= camera_offset_y
                    enemy.render(surface, current_dimension)
                    enemy.x, enemy.y = original_x, original_y
            
            # Portale rendern
            for portal in self.portals:
                if self._is_visible(portal, camera_offset_x, camera_offset_y):
                    original_x, original_y = portal.x, portal.y
                    portal.x -= camera_offset_x
                    portal.y -= camera_offset_y
                    portal.render(surface, current_dimension)
                    portal.x, portal.y = original_x, original_y
            
            # Powerups rendern
            for powerup in self.powerups:
                if not powerup.collected and self._is_visible(powerup, camera_offset_x, camera_offset_y):
                    original_x, original_y = powerup.x, powerup.y
                    powerup.x -= camera_offset_x
                    powerup.y -= camera_offset_y
                    powerup.render(surface, current_dimension)
                    powerup.x, powerup.y = original_x, original_y
        except Exception as e:
            # Bei ernsthaften Fehlern Rendering weitermachen ohne Partikel
            pass
    
    def _is_visible(self, obj: GameObject, camera_x: int, camera_y: int) -> bool:
        """Überprüft, ob ein Objekt im sichtbaren Kamerabereich liegt."""
        screen_x = obj.x - camera_x
        screen_y = obj.y - camera_y
        
        # Pruning: Schnelles Verwerfen von Objekten außerhalb des Bildschirms
        if screen_x + obj.width < 0 or screen_x > SCREEN_WIDTH or \
           screen_y + obj.height < 0 or screen_y > SCREEN_HEIGHT:
            return False
            
        return True
    
    def check_player_powerup_collisions(self, player, current_dimension: int = 1) -> Tuple[bool, Optional[str]]:
        """Prüft Kollisionen zwischen Spieler und Powerups."""
        player_rect = player.get_rect()
        powerup_collected = False
        powerup_type = None
        
        for powerup in self.powerups:
            # Nur Powerups prüfen, die in der aktuellen Dimension sichtbar sind
            if powerup.dimension_visible != -1 and powerup.dimension_visible != current_dimension:
                continue
                
            if not powerup.collected:
                # Kollisionsprüfung
                powerup_rect = pygame.Rect(
                    powerup.x, 
                    powerup.y, 
                    powerup.width, 
                    powerup.height
                )
                
                if player_rect.colliderect(powerup_rect):
                    powerup.collected = True
                    powerup_collected = True
                    powerup_type = powerup.powerup_type
                    
                    # Powerup-Effekt anwenden
                    player.add_powerup(powerup_type, powerup.duration)
                    break
                
        return powerup_collected, powerup_type
            
    def spawn_powerup(self, x: float, y: float, powerup_type: Optional[str] = None) -> None:
        """Erzeugt ein neues Powerup an der angegebenen Position."""
        if powerup_type is None:
            # Zufälliges Powerup auswählen
            powerup_type = random.choice([
                "speed", "jump", "invincibility", "gravity"
            ])
            
        # Powerup erstellen
        self.powerups.append(Powerup(x, y, powerup_type))
        
    def get_all_objects(self) -> List[Dict[str, Any]]:
        """Gibt alle Spielobjekte als Liste von Dictionaries für die Minimap zurück."""
        objects = []
        
        # Füge Plattformen hinzu
        for platform in self.platforms:
            objects.append({
                "type": "platform",
                "x": platform.x,
                "y": platform.y,
                "width": platform.width,
                "height": platform.height
            })
        
        # Füge Portale hinzu
        for portal in self.portals:
            objects.append({
                "type": "portal",
                "x": portal.x,
                "y": portal.y,
                "width": portal.width,
                "height": portal.height
            })
        
        # Füge Sammelobjekte hinzu
        for collectible in self.collectibles:
            if not collectible.collected:
                objects.append({
                    "type": "collectible",
                    "x": collectible.x,
                    "y": collectible.y,
                    "width": collectible.width,
                    "height": collectible.height
                })
        
        # Füge Gegner hinzu
        for enemy in self.enemies:
            if not enemy.is_dead:
                objects.append({
                    "type": "enemy",
                    "x": enemy.x,
                    "y": enemy.y,
                    "width": enemy.width,
                    "height": enemy.height
                })
                
        # Füge Powerups hinzu
        for powerup in self.powerups:
            if not powerup.collected:
                objects.append({
                    "type": "powerup",
                    "x": powerup.x,
                    "y": powerup.y,
                    "width": powerup.width,
                    "height": powerup.height,
                    "powerup_type": powerup.powerup_type
                })
        
        return objects 

    def _clear_level(self) -> None:
        """Löscht alle vorhandenen Levelobjekte."""
        # Alle vorhandenen Objekte löschen
        self.platforms.clear()
        self.portals.clear()
        self.collectibles.clear()
        self.enemies.clear()
        self.powerups.clear()
        
        # Aktive Partikel zurücksetzen
        self.active_particles = 0
        
        # Boden erstellen (immer vorhanden)
        floor = Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
        self.platforms.append(floor)
        
        # Welt-Dimensionen zurücksetzen auf Standard
        self.world_width = SCREEN_WIDTH 
        self.world_height = SCREEN_HEIGHT 