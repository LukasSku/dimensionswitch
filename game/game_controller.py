import pygame
import time
import random
from game.constants import *
from game.world import World
from game.player import Player
from game.audio.sound_generator import SoundGenerator
from game.ui import MainMenu, SettingsMenu, ControlsMenu, PauseMenu, GameOverMenu, HUD, MinimapWidget, PowerupWidget, WinMenu
from typing import Dict

class GameController:
    def __init__(self):
        pygame.init()
        
        # Einstellungen laden
        self.settings = DEFAULT_SETTINGS.copy()
        self.controls = DEFAULT_CONTROLS.copy()
        
        # Fenstergröße
        flags = pygame.FULLSCREEN if self.settings.get("fullscreen", False) else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption(GAME_TITLE)
        
        # Spielkomponenten
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.current_level = 0
        self.current_dimension = 1  # Dimension 1 ist die Standarddimension
        self.game_time = 0.0
        self.dimension_cooldown = 0.0
        
        # Aktiver Menüzustand
        self.active_menu = None
        self.game_paused = False
        self.game_started = False
        
        # Sound initialisieren
        self.sound = SoundGenerator(self.settings)
        
        # Spielwelt und Spieler
        self.world = World()
        self.player = Player(100, 300)
        
        # UI-Komponenten
        self._init_ui()
        
        # Performance-Tracking
        self.frame_times = []
        self.max_frame_times = 60  # Speichere die letzten 60 Frames für Durchschnittsberechnung
        self.last_frame_time = time.time()
        
        # Initialisierung abschließen
        self.initialize_game()

    def _init_ui(self):
        """Initialisiert alle UI-Komponenten."""
        # Menüs erstellen
        self.main_menu = MainMenu(
            SCREEN_WIDTH, SCREEN_HEIGHT,
            self._start_game,
            self._show_settings,
            self._quit_game
        )
        
        self.settings_menu = SettingsMenu(
            SCREEN_WIDTH, SCREEN_HEIGHT,
            self._return_to_main_menu,
            self._show_controls,
            self.settings,  # Settings-Dictionary übergeben
            self._save_settings  # Callback für Speichern
        )
        
        self.controls_menu = ControlsMenu(
            SCREEN_WIDTH, SCREEN_HEIGHT,
            self._back_to_settings,
            self.controls,
            self._save_controls
        )
        
        self.pause_menu = PauseMenu(
            SCREEN_WIDTH, SCREEN_HEIGHT,
            self._resume_game,
            self._show_settings,
            self._return_to_main_menu
        )
        
        self.game_over_menu = GameOverMenu(
            SCREEN_WIDTH, SCREEN_HEIGHT,
            self._restart_level,
            self._return_to_main_menu
        )
        
        self.win_menu = WinMenu(
            SCREEN_WIDTH, SCREEN_HEIGHT,
            self._return_to_main_menu,
            self._quit_game
        )
        
        # Spieloberfläche
        self.hud = HUD(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.minimap = MinimapWidget(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.powerup_widget = PowerupWidget(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Startet mit dem Hauptmenü
        self.active_menu = self.main_menu
        self.previous_menu = None

    def _start_game(self):
        """Startet ein neues Spiel."""
        self.game_started = True
        self.game_paused = False
        self.active_menu = None
        self.score = 0
        self.current_level = 0
        self.game_time = 0.0
        self.player.reset(100, 300)
        self.world.generate_level(self.current_level)
        self.sound.play_music(self.current_dimension)
        
    def _resume_game(self):
        """Setzt ein pausiertes Spiel fort."""
        self.game_paused = False
        self.active_menu = None
        
    def _pause_game(self):
        """Pausiert das laufende Spiel."""
        self.game_paused = True
        self.active_menu = self.pause_menu
        
    def _show_settings(self):
        """Öffnet das Einstellungsmenü vom Hauptmenü."""
        if self.active_menu:
            self.active_menu.transition_to(self.settings_menu)
            self.previous_menu = self.active_menu
        
    def _show_controls(self):
        """Öffnet das Steuerungsmenü von den Einstellungen."""
        if self.active_menu:
            self.active_menu.transition_to(self.controls_menu)
            self.previous_menu = self.active_menu
        
    def _return_to_main_menu(self):
        """Kehrt zum Hauptmenü zurück."""
        if self.active_menu:
            self.active_menu.transition_to(self.main_menu)
            self.previous_menu = None
        
    def _back_to_settings(self):
        """Kehrt zum Einstellungsmenü zurück."""
        if self.active_menu:
            self.active_menu.transition_to(self.settings_menu)
            # Vorheriges Menü speichern, damit _back_to_previous_menu funktioniert
            self.previous_menu = self.main_menu
        
    def _quit_game(self):
        """Beendet das Spiel."""
        self.running = False
        
    def _save_controls(self, controls: Dict[str, int]) -> None:
        """Speichert die Steuerungseinstellungen."""
        # Steuerung aktualisieren mit tiefer Kopie
        self.controls = controls.copy()
        
        # Debug-Ausgabe zur Überprüfung
        print("Steuerung aktualisiert:")
        for action, key in self.controls.items():
            print(f"{action}: {pygame.key.name(key)}")
        
        # Zurück zum Einstellungsmenü
        self._back_to_settings()
        
    def _save_settings(self, settings):
        """Speichert die Spieleinstellungen."""
        # Settings aktualisieren
        self.settings = settings
        
        # Lautstärke aktualisieren
        self.sound.update_volume()
        
        # Vollbild-Modus aktualisieren
        fullscreen = self.settings.get("fullscreen", False)
        flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        
        # Zurück zum vorherigen Menü
        self._back_to_previous_menu()
        
    def initialize_game(self):
        """Initialisiert das Spiel."""
        # Level explizit auf 0 setzen
        self.current_level = 0
        # Level mit aktueller Levelnummer generieren
        self.world.generate_level(self.current_level)
        
    def handle_events(self):
        """Verarbeitet Spielereignisse."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
                
            # Wenn ein Menü aktiv ist, leite Events an das Menü weiter
            if self.active_menu:
                sound_played = self.active_menu.handle_event(event)
                if sound_played:
                    self.sound.play_sound("button")
                continue
                
            # Eingaben für das Spiel
            if event.type == pygame.KEYDOWN:
                # Aktuelle Kontrollen verwenden
                if event.key == self.controls.get("pause", pygame.K_ESCAPE):
                    self._pause_game()
                    self.sound.play_sound("button")
        
        # Spielsteuerung auswerten
        if self.game_started and not self.game_paused:
            keys = pygame.key.get_pressed()
            
            # Horizontale Bewegung - aktuelle Kontrollen verwenden
            if keys[self.controls.get("move_left", pygame.K_LEFT)]:
                self.player.move_left()
            elif keys[self.controls.get("move_right", pygame.K_RIGHT)]:
                self.player.move_right()
            else:
                self.player.stop_horizontal_movement()
            
            # Springen - aktuelle Kontrollen verwenden
            if keys[self.controls.get("jump", pygame.K_SPACE)]:
                self.player.jump()
            
            # Dimensionswechsel (mit Cooldown) - aktuelle Kontrollen verwenden
            if keys[self.controls.get("dimension_change", pygame.K_d)] and self.dimension_cooldown <= 0:
                self.switch_dimension()
                self.dimension_cooldown = DIMENSION_CHANGE_COOLDOWN

    def update(self, dt):
        """Aktualisiert den Spielzustand."""
        # Dimensionswechsel-Cooldown aktualisieren
        if self.dimension_cooldown > 0:
            self.dimension_cooldown -= dt
        
        # Menüübergänge aktualisieren
        if self.active_menu:
            # Partikel im aktiven Menü aktualisieren, falls vorhanden
            self.active_menu.update_particles()
            
            # Transitionen überprüfen und verarbeiten
            next_menu = self.active_menu.update_transition()
            if next_menu:
                # Flackern vermeiden durch sauberen Übergang
                self.active_menu = next_menu
                # Stelle sicher, dass Partikel im neuen Menü initialisiert werden
                self.active_menu.update_particles()
            
            # Menü aktualisieren
            self.active_menu.update()
            return
        
        # Nur updaten, wenn das Spiel läuft und nicht pausiert ist
        if self.game_started and not self.game_paused:
            # Spielzeit erhöhen
            self.game_time += dt
            
            # Zeitfaktor je nach Dimension
            time_factor = 0.5 if self.current_dimension == 3 else 1.0  # Dimension 3 = Zeit-Paradox
            
            # Zeitfaktor nach Schwierigkeitsgrad anpassen
            if self.settings["difficulty"] == 0:  # Leicht
                time_factor *= 0.9
            elif self.settings["difficulty"] == 2:  # Schwer
                time_factor *= 1.1
            
            # Spieler aktualisieren und Events empfangen
            player_events = self.player.update(time_factor, self.world.platforms, self.world.portals, 
                                             self.world.collectibles, self.world.enemies, self.current_dimension)
            
            # Sound-Events verarbeiten
            self.sound.handle_player_events(player_events)
            
            # Kollisionsprüfungen für Powerups
            powerup_collected, powerup_type = self.world.check_player_powerup_collisions(self.player, self.current_dimension)
            
            if powerup_collected:
                # Sound für Powerup-Einsammeln abspielen
                self.sound.play_powerup_sound(powerup_type)
                print(f"Powerup gesammelt: {powerup_type}")
                
                # Benachrichtigung anzeigen
                if powerup_type == "double_jump":
                    self.hud.add_notification("Doppelsprung aktiviert!")
                elif powerup_type == "speed_boost":
                    self.hud.add_notification("Geschwindigkeitsboost aktiviert!")
                elif powerup_type == "invincibility":
                    self.hud.add_notification("Unverwundbarkeit aktiviert!")
                elif powerup_type == "extra_life":
                    self.hud.add_notification("Extra-Leben erhalten!")
                
                # Punkte für Powerup
                self.score += 25
            
            # Benachrichtigungen für Events
            if player_events.get("collect", False):
                self.score += COLLECTIBLE_SCORE * (self.current_level + 1)  # Höhere Level geben mehr Punkte
                self.hud.add_notification(f"+{COLLECTIBLE_SCORE * (self.current_level + 1)} Punkte")
                
                # Zufällig Powerups spawnen, wenn Sammelobjekte eingesammelt werden
                if random.random() < 0.15:  # 15% Chance für ein Powerup
                    self.world.spawn_powerup(self.player.x + random.randint(-200, 200),
                                           self.player.y - random.randint(100, 300))
                
            if player_events.get("enemy_death", False):
                self.score += 50 * (self.current_level + 1)
                self.hud.add_notification(f"Gegner besiegt! +{50 * (self.current_level + 1)} Punkte")
                
                # Größere Chance auf Powerups beim Gegner-Tod
                if random.random() < 0.3:  # 30% Chance für ein Powerup
                    self.world.spawn_powerup(self.player.x + random.randint(-100, 100),
                                           self.player.y - random.randint(50, 150))
                
            # Level abgeschlossen
            if player_events.get("level_complete", False):
                self.handle_level_completion()
                
            # Spieler gestorben
            if player_events.get("player_death", False):
                if self.player.lives <= 0:
                    self._game_over()
                else:
                    self.reset_level()
            
            # Welt updaten
            self.world.update(time_factor, self.player.x, self.player.y, self.current_dimension)
            
            # HUD aktualisieren
            self.hud.update(dt)
            
    def handle_level_completion(self):
        """Behandelt den Abschluss eines Levels und lädt das nächste Level."""
        try:
            # Level erhöhen
            self.current_level += 1
            
            # Benachrichtigung anzeigen
            self.hud.add_notification(f"Level {self.current_level} erreicht!")
            
            # Debug-Info vor der Generierung
            print(f"[DEBUG] Level-Wechsel zu Level {self.current_level}")
            print(f"[DEBUG] Alte Welt-Status - Plattformen: {len(self.world.platforms)}")
            
            # Soundeffekt für Level-Aufstieg abspielen
            self.sound.play_sound("level_up")
            
            # KRITISCHE STELLE: Neu-Erstellung der Welt mit klarer Trennung
            # Alte Welt komplett verwerfen
            del self.world
            
            # Kurze Pause für GC
            pygame.time.delay(100)
            
            # Neue Welt-Instanz erstellen
            self.world = World()
            
            # Level mit erhöhter Levelnummer generieren
            print(f"[DEBUG] Neue Welt generiert, generiere Level {self.current_level}")
            self.world.generate_level(self.current_level)
            
            # Validieren, dass Objekte tatsächlich generiert wurden
            print(f"[DEBUG] Neue Welt-Status - Plattformen: {len(self.world.platforms)}")
            
            # Spieler auf Startposition des neuen Levels setzen
            self.player.reset(100, 300)
            
            # Kurze Freeze-Zeit zur Anzeige des Level-Übergangs
            pygame.time.delay(500)
            
            # Nach Verzögerung erneut Plattformen prüfen (Konsistenzprüfung)
            print(f"[DEBUG] Nach Verzögerung - Plattformen: {len(self.world.platforms)}")
        except Exception as e:
            print(f"[FEHLER] Beim Laden des Levels {self.current_level}: {str(e)}")
            # Ausnahmen-Stack ausgeben für bessere Fehleranalyse
            import traceback
            traceback.print_exc()
            
            # Fallback: Zurück zum vorherigen Level
            self.current_level -= 1
            
            try:
                # Komplett neue Welt erstellen
                del self.world
                self.world = World()
                self.world.generate_level(self.current_level)
                self.player.reset(100, 300)
                self.hud.add_notification("FEHLER: Zurück zum vorherigen Level")
            except Exception as fallback_e:
                # Kritischer Fehler, wenn sogar das Fallback fehlschlägt
                print(f"[KRITISCH] Fallback fehlgeschlagen: {str(fallback_e)}")
                traceback.print_exc()
                # Versuche, zum ersten Level zurückzukehren
                self.current_level = 0
                self.world = World()
                self.world.generate_level(0)
                self.player.reset(100, 300)
        
    def switch_dimension(self):
        """Wechselt die aktuelle Dimension."""
        new_dimension = (self.current_dimension % MAX_DIMENSIONS) + 1
        self.current_dimension = new_dimension
        self.sound.handle_dimension_change(new_dimension)
        self.hud.add_notification(f"Dimension {new_dimension} aktiviert!")
        
    def reset_level(self):
        """Setzt das aktuelle Level zurück."""
        # Welt vollständig neu initialisieren
        self.world = World()  # Neue Welt-Instanz erstellen
        
        # Level mit aktueller Levelnummer generieren
        self.world.generate_level(self.current_level)
        
        # Spieler zurücksetzen
        self.player.reset(100, 300)
        
        # Benachrichtigung anzeigen
        self.hud.add_notification("Level neu gestartet!")
        
        # Debug-Information
        print(f"Level {self.current_level} zurückgesetzt. Plattformen: {len(self.world.platforms)}")
        
    def render(self):
        """Zeichnet den aktuellen Spielzustand."""
        # Hintergrund zeichnen
        self.screen.fill(MENU_BG_COLOR if self.active_menu else BLACK)
        
        # Menü oder Spielinhalt rendern
        if self.active_menu:
            self.active_menu.render(self.screen)
        elif self.game_started:
            # Spielwelt und Spieler zeichnen
            self.world.render(self.screen, self.current_dimension)
            self.player.render(self.screen)
            
            # UI-Komponenten zeichnen
            self.hud.render(
                self.screen,
                self.player.lives,  # Leben statt Health
                PLAYER_STARTING_LIVES,
                self.score,
                self.current_dimension,
                self.game_time,
                int(self.clock.get_fps()),
                self.settings.get("show_debug", False)
            )
            
            # Minimap anzeigen, wenn aktiviert
            if self.settings.get("show_minimap", True):
                game_objects = self.world.get_all_objects()
                self.minimap.render(
                    self.screen,
                    game_objects,
                    (self.player.x, self.player.y),
                    LEVEL_WIDTH,
                    LEVEL_HEIGHT,
                    self.hud.time_rect
                )
            
            # Powerups anzeigen
            self.powerup_widget.render(
                self.screen,
                self.player.active_powerups
            )
        
        # Bild anzeigen
        pygame.display.flip()
    
    def run(self):
        """Startet die Hauptspielschleife."""
        try:
            while self.running:
                # Delta-Zeit für gleichmäßige Bewegungen
                dt = self.clock.tick(TARGET_FPS) / 1000.0
                
                # Eingabebehandlung
                self.handle_events()
                
                # Spiellogik aktualisieren
                self.update(dt)
                
                # Rendern
                self.render()
                
                # Performance tracken
                current_time = time.time()
                frame_time = current_time - self.last_frame_time
                self.last_frame_time = current_time
                
                self.frame_times.append(frame_time)
                if len(self.frame_times) > self.max_frame_times:
                    self.frame_times.pop(0)
        finally:
            # Aufräumen bei Spielende oder Ausnahmen
            self.sound.cleanup()
            pygame.quit() 

    def _restart_level(self):
        """Startet das aktuelle Level neu."""
        # Level-Reset mit Soundeffekt
        self.reset_level()
        self.sound.play_sound("respawn")
        self.game_paused = False
        
    def _game_over(self):
        """Zeigt das Game-Over-Menü an."""
        self.active_menu = self.game_over_menu
        
    def _back_to_previous_menu(self):
        """Kehrt zum vorherigen Menü zurück."""
        if self.previous_menu:
            self.active_menu.transition_to(self.previous_menu)
        else:
            self.active_menu.transition_to(self.main_menu) 