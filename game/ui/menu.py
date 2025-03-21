"""
Enthält Klassen für die verschiedenen Menüs im Spiel.
"""
import pygame
from game.constants import *
from game.ui.ui_elements import Button, Slider, Toggle, TextInput, KeyBinding
from typing import List, Dict, Callable, Any, Optional, Tuple
import random

class Menu:
    """Basisklasse für Menüs."""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_elements = []
        self.title = ""
        
        # Schriftarten
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 32)
        self.text_font = pygame.font.SysFont('Arial', 20)
        
        # Animationsparameter
        self.transition_in = 0.0
        self.transition_out = 0.0
        self.transitioning_to = None
        
        # Hintergrund-Partikel für visuelle Effekte
        self.particles = []
        self._init_particles()

    def _init_particles(self):
        """Initialisiert Hintergrund-Partikel für visuelle Effekte."""
        self.particles = []
        for _ in range(50):
            # Position als Tupel von float-Werten speichern, nicht als Vector2
            pos_x = random.uniform(0, self.screen_width)
            pos_y = random.uniform(0, self.screen_height)
            
            # Geschwindigkeit als Tupel von float-Werten speichern, nicht als Vector2
            vel_x = random.uniform(-0.5, 0.5)
            vel_y = random.uniform(-0.5, 0.5)
            
            size = random.uniform(1, 3)
            color = (
                int(random.uniform(150, 255)),
                int(random.uniform(150, 255)),
                int(random.uniform(150, 255))
            )
            self.particles.append(((pos_x, pos_y), (vel_x, vel_y), size, color))
    
    def update_particles(self):
        """Aktualisiert die Bewegung der Hintergrund-Partikel."""
        for i, (pos, vel, size, color) in enumerate(self.particles):
            # Bewege Partikel
            pos_x, pos_y = pos
            vel_x, vel_y = vel
            
            pos_x += vel_x
            pos_y += vel_y
            
            # Halte Partikel im Bildschirmbereich
            if pos_x < 0:
                pos_x = self.screen_width
            elif pos_x > self.screen_width:
                pos_x = 0
            if pos_y < 0:
                pos_y = self.screen_height
            elif pos_y > self.screen_height:
                pos_y = 0
                
            self.particles[i] = ((pos_x, pos_y), vel, size, color)
    
    def draw_particles(self, surface):
        """Zeichnet die Hintergrund-Partikel."""
        for pos, _, size, color in self.particles:
            # Stelle sicher, dass die Position ein Paar von Zahlen ist
            pos_x, pos_y = pos
            center = (int(pos_x), int(pos_y))
            pygame.draw.circle(surface, color, center, int(size))
    
    def transition_to(self, next_menu: Optional['Menu'] = None) -> None:
        """Startet eine Übergangsanimation zum nächsten Menü."""
        self.transitioning_to = next_menu
        self.transition_out = 0.0
    
    def update_transition(self) -> Optional['Menu']:
        """Aktualisiert die Übergangsanimation und gibt das nächste Menü zurück, wenn bereit."""
        # Einblend-Animation
        if self.transition_in < 1.0:
            # Langsamere Einblendung für weicheren Übergang
            self.transition_in = min(1.0, self.transition_in + 0.025)
            
        # Ausblend-Animation nur wenn ein Zielmenü existiert
        if self.transitioning_to is not None:
            # Langsamere Ausblendung für weicheren Übergang
            self.transition_out = min(1.0, self.transition_out + 0.025)
            
            # Übergangslogik: Warte bis die Animation vollständig ist
            if self.transition_out >= 1.0:
                next_menu = self.transitioning_to
                self.transitioning_to = None  # Zurücksetzen nach Abschluss
                
                # Stelle sicher, dass das neue Menü komplett zurückgesetzt wird
                next_menu.transition_in = 0.0
                return next_menu
        
        return None
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Verarbeitet Ereignisse und gibt zurück, ob das Ereignis verarbeitet wurde."""
        for element in self.ui_elements:
            if element.handle_event(event):
                return True
        return False
    
    def update(self) -> None:
        """Aktualisiert den Zustand des Menüs."""
        # Mausposition abrufen
        mouse_pos = pygame.mouse.get_pos()
        
        # UI-Elemente mit der aktuellen Mausposition aktualisieren
        for element in self.ui_elements:
            if hasattr(element, 'update'):
                element.update(mouse_pos)
    
    def render(self, surface: pygame.Surface) -> None:
        """Zeichnet das Menü auf die Oberfläche."""
        # Hintergrund
        bg_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        bg_surface.fill(MENU_BG_COLOR)
        surface.blit(bg_surface, (0, 0))
        
        # Titel
        if self.title:
            title_surf = self.title_font.render(self.title, True, UI_ACCENT_COLOR)
            title_rect = title_surf.get_rect(centerx=self.screen_width // 2, top=30)
            surface.blit(title_surf, title_rect)
        
        # UI-Elemente
        for element in self.ui_elements:
            element.render(surface)
            
        # Animationseffekte anwenden
        
        # Einblend-Animation
        if self.transition_in < 1.0:
            alpha = int(255 * (1.0 - self.transition_in))
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(alpha)
            surface.blit(overlay, (0, 0))
            
        # Ausblend-Animation
        if self.transitioning_to is not None:
            alpha = int(255 * self.transition_out)
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(alpha)
            surface.blit(overlay, (0, 0))


class MainMenu(Menu):
    """Hauptmenü des Spiels."""
    def __init__(self, screen_width: int, screen_height: int, 
                start_game_callback: Callable[[], None],
                settings_callback: Callable[[], None],
                quit_callback: Callable[[], None]):
        super().__init__(screen_width, screen_height)
        self.title = "Jump 'n' Run"
        
        # Position und Größe der Buttons
        button_width = 300
        button_height = 60
        spacing = 40  # Größerer Abstand zwischen Buttons
        
        # Y-Position der Buttons (Mitte des Bildschirms + Abwärts)
        start_y = self.screen_height // 2 - 50
        
        # Berechne X-Position, um Buttons zu zentrieren
        button_x = (self.screen_width - button_width) // 2
        
        # Spielstart-Button
        self.ui_elements.append(Button(
            button_x, start_y, 
            button_width, button_height, 
            "Spiel starten", 
            start_game_callback
        ))
        
        # Einstellungen-Button
        self.ui_elements.append(Button(
            button_x, start_y + button_height + spacing, 
            button_width, button_height, 
            "Einstellungen", 
            settings_callback
        ))
        
        # Beenden-Button
        self.ui_elements.append(Button(
            button_x, start_y + 2 * (button_height + spacing), 
            button_width, button_height, 
            "Beenden", 
            quit_callback
        ))
    
    def render(self, surface: pygame.Surface) -> None:
        """Zeichnet das Hauptmenü mit Titel, Untertitel und Buttons."""
        super().render(surface)
        
        # Untertitel
        subtitle_surf = self.subtitle_font.render("Dimensions-Abenteuer", True, UI_TEXT_COLOR)
        subtitle_rect = subtitle_surf.get_rect()
        subtitle_rect.centerx = self.screen_width // 2
        subtitle_rect.top = 100  # Position unter dem Titel
        surface.blit(subtitle_surf, subtitle_rect)


class SettingsMenu(Menu):
    """Menü für Spieleinstellungen."""
    def __init__(self, screen_width: int, screen_height: int, 
                back_callback: Callable[[], None],
                controls_callback: Callable[[], None],
                settings: Dict[str, Any] = None,
                save_settings_callback: Callable[[Dict[str, Any]], None] = None):
        super().__init__(screen_width, screen_height)
        self.title = "Einstellungen"
        self.settings = settings if settings else {}
        self.save_settings_callback = save_settings_callback
        
        # Zurück-Button
        self.back_button = Button(
            20, 20, 100, 40, 
            "Zurück", 
            back_callback
        )
        self.ui_elements.append(self.back_button)
        
        # Position und Größe für Einstellungen
        content_x = self.screen_width // 4
        content_width = self.screen_width // 2
        content_y = 100
        element_height = 40
        element_spacing = 25
        
        curr_y = content_y
        
        # --- Steuerungseinstellungen ---
        self.controls_button = Button(
            content_x, 
            curr_y, 
            content_width, element_height, 
            "Steuerung anpassen", 
            controls_callback
        )
        self.ui_elements.append(self.controls_button)
        curr_y += element_height + element_spacing
        
        # --- Lautstärke-Einstellungen ---
        # Musik-Lautstärke
        music_vol = self.settings.get("music_volume", 0.7)
        
        # Label
        music_label_rect = pygame.Rect(content_x, curr_y, 200, element_height)
        
        # Slider
        music_slider = Slider(
            content_x + 200, curr_y, content_width - 220, element_height,
            0.0, 1.0, music_vol,
            lambda val: self._update_setting("music_volume", val)
        )
        self.ui_elements.append(music_slider)
        curr_y += element_height + element_spacing
        
        # Effekt-Lautstärke
        sfx_vol = self.settings.get("sfx_volume", 0.8)
        
        # Label
        sfx_label_rect = pygame.Rect(content_x, curr_y, 200, element_height)
        
        # Slider
        sfx_slider = Slider(
            content_x + 200, curr_y, content_width - 220, element_height,
            0.0, 1.0, sfx_vol,
            lambda val: self._update_setting("sfx_volume", val)
        )
        self.ui_elements.append(sfx_slider)
        curr_y += element_height + element_spacing
        
        # --- Toggle-Einstellungen ---
        # Vollbild
        fullscreen = self.settings.get("fullscreen", False)
        
        # Label
        fullscreen_label_rect = pygame.Rect(content_x, curr_y, 200, element_height)
        
        # Toggle
        fullscreen_toggle = Toggle(
            content_x + 200, curr_y, 60, element_height,
            fullscreen,
            lambda val: self._update_setting("fullscreen", val)
        )
        self.ui_elements.append(fullscreen_toggle)
        curr_y += element_height + element_spacing
        
        # Partikel
        particles = self.settings.get("particles_enabled", True)
        
        # Label
        particles_label_rect = pygame.Rect(content_x, curr_y, 200, element_height)
        
        # Toggle
        particles_toggle = Toggle(
            content_x + 200, curr_y, 60, element_height,
            particles,
            lambda val: self._update_setting("particles_enabled", val)
        )
        self.ui_elements.append(particles_toggle)
        curr_y += element_height + element_spacing
        
        # Minimap
        minimap = self.settings.get("show_minimap", True)
        
        # Label
        minimap_label_rect = pygame.Rect(content_x, curr_y, 200, element_height)
        
        # Toggle
        minimap_toggle = Toggle(
            content_x + 200, curr_y, 60, element_height,
            minimap,
            lambda val: self._update_setting("show_minimap", val)
        )
        self.ui_elements.append(minimap_toggle)
        curr_y += element_height + element_spacing
        
        # --- Schwierigkeitsgrad ---
        difficulty = self.settings.get("difficulty", 1)
        
        # Label
        difficulty_label_rect = pygame.Rect(content_x, curr_y, 200, element_height)
        
        # Buttons für Schwierigkeitsgrad
        difficulty_width = (content_width - 220) // 3
        
        self.difficulty_buttons = []
        
        # Leicht
        easy_button = Button(
            content_x + 200, curr_y, difficulty_width, element_height,
            "Leicht",
            lambda: self._update_setting("difficulty", 0)
        )
        self.ui_elements.append(easy_button)
        self.difficulty_buttons.append((easy_button, 0))
        
        # Normal
        normal_button = Button(
            content_x + 200 + difficulty_width + 5, curr_y, difficulty_width, element_height,
            "Normal",
            lambda: self._update_setting("difficulty", 1)
        )
        self.ui_elements.append(normal_button)
        self.difficulty_buttons.append((normal_button, 1))
        
        # Schwer
        hard_button = Button(
            content_x + 200 + 2 * (difficulty_width + 5), curr_y, difficulty_width, element_height,
            "Schwer",
            lambda: self._update_setting("difficulty", 2)
        )
        self.ui_elements.append(hard_button)
        self.difficulty_buttons.append((hard_button, 2))
        
        curr_y += element_height + element_spacing
        
        # Speichern-Button
        self.save_button = Button(
            content_x + content_width - 150, 
            self.screen_height - 80,
            150, 50,
            "Speichern",
            self._save_settings
        )
        self.ui_elements.append(self.save_button)
        
        # Speichere Rechtecke für das Rendering der Labels
        self.label_rects = {
            "music": music_label_rect,
            "sfx": sfx_label_rect,
            "fullscreen": fullscreen_label_rect,
            "particles": particles_label_rect,
            "minimap": minimap_label_rect,
            "difficulty": difficulty_label_rect
        }
    
    def _update_setting(self, key: str, value: Any) -> None:
        """Aktualisiert eine Einstellung im Settings-Dictionary."""
        self.settings[key] = value
    
    def _save_settings(self) -> None:
        """Speichert alle Einstellungen und ruft den Callback auf."""
        if self.save_settings_callback:
            self.save_settings_callback(self.settings)
    
    def render(self, surface: pygame.Surface) -> None:
        """Zeichnet das Einstellungsmenü mit zusätzlichen Infos."""
        # Basis-Rendering (Hintergrund, Titel, etc.)
        super().render(surface)
        
        # Animierte Partikel für visuelles Interesse
        self.update_particles()
        self.draw_particles(surface)
        
        # Labels für Einstellungen
        label_texts = {
            "music": "Musik-Lautstärke:",
            "sfx": "Effekt-Lautstärke:",
            "fullscreen": "Vollbild:",
            "particles": "Partikel-Effekte:",
            "minimap": "Minimap anzeigen:",
            "difficulty": "Schwierigkeitsgrad:"
        }
        
        for key, text in label_texts.items():
            if key in self.label_rects:
                label_rect = self.label_rects[key]
                
                # Hintergrund für besseren Kontrast
                bg_rect = pygame.Rect(
                    label_rect.x - 10, 
                    label_rect.y - 5, 
                    220, 
                    label_rect.height + 10
                )
                pygame.draw.rect(surface, (40, 40, 60), bg_rect, border_radius=3)
                pygame.draw.rect(surface, UI_ACCENT_COLOR, bg_rect, 1, border_radius=3)
                
                # Text rendern
                text_surf = self.text_font.render(text, True, UI_TEXT_COLOR)
                text_rect = text_surf.get_rect()
                text_rect.midleft = (label_rect.x, label_rect.centery)
                surface.blit(text_surf, text_rect)
        
        # Aktueller Schwierigkeitsgrad hervorheben
        current_difficulty = self.settings.get("difficulty", 1)
        for button, diff_value in self.difficulty_buttons:
            if diff_value == current_difficulty:
                pygame.draw.rect(surface, UI_ACCENT_COLOR, button.rect.inflate(4, 4), 3)
        
        # Hervorhebung der aktiven Buttons
        pygame.draw.rect(surface, UI_ACCENT_COLOR, self.save_button.rect.inflate(4, 4), 2)
        pygame.draw.rect(surface, UI_ACCENT_COLOR, self.back_button.rect.inflate(4, 4), 2)


class ControlsMenu(Menu):
    """Menü zur Konfiguration der Steuerung."""
    def __init__(self, screen_width: int, screen_height: int, 
                 back_callback: Callable[[], None],
                 controls: Dict[str, int],
                 save_controls_callback: Callable[[Dict[str, int]], None]):
        super().__init__(screen_width, screen_height)
        self.title = "Steuerung"
        self.controls = controls.copy()  # Tiefe Kopie erstellen
        self.original_controls = controls.copy()  # Original-Einstellungen sichern
        self.save_controls_callback = save_controls_callback
        self.waiting_for_key = False
        self.current_action = None
        self.changes_saved = False
        
        # Zurück-Button
        self.back_button = Button(
            20, 20, 100, 40, 
            "Zurück", 
            back_callback
        )
        self.ui_elements.append(self.back_button)
        
        # Position und Größe der Steuerungselemente
        control_x = screen_width // 4
        control_y = 150
        control_width = screen_width // 2
        control_height = 50
        control_spacing = 70
        
        # UI-Header für Steuerungsbereich
        self.control_header_rect = pygame.Rect(
            control_x, control_y - 80, control_width, 40
        )
        
        # Steuerungsbeschriftungen
        self.control_labels = {}
        
        # KeyBinding-Elemente für jede Steuerungsaktion erstellen
        self.keybind_elements = {}
        
        # Speichern-Button
        save_button_width = 150
        save_button_height = 50
        save_button_x = (screen_width - save_button_width) // 2
        save_button_y = screen_height - 120
        
        self.save_button = Button(
            save_button_x, 
            save_button_y, 
            save_button_width, 
            save_button_height, 
            "Speichern", 
            self._save_controls
        )
        self.ui_elements.append(self.save_button)
        
        # Reset-Button
        reset_button_width = 150
        reset_button_height = 50
        reset_button_x = (screen_width - reset_button_width) // 2
        reset_button_y = save_button_y - 70
        
        self.reset_button = Button(
            reset_button_x, 
            reset_button_y, 
            reset_button_width, 
            reset_button_height, 
            "Zurücksetzen", 
            self._reset_controls
        )
        self.ui_elements.append(self.reset_button)
        
        # Info-Text-Bereich
        self.info_rect = pygame.Rect(
            0, screen_height - 60,
            screen_width, 60
        )
        
        # Steuerungsbindungen erstellen
        actions = [
            "move_left", 
            "move_right", 
            "jump", 
            "dimension_change", 
            "pause"
        ]
        
        for i, action in enumerate(actions):
            y_pos = control_y + i * control_spacing
            
            # Label-Rechteck für späteren Zugriff speichern
            self.control_labels[action] = pygame.Rect(
                control_x, 
                y_pos, 
                control_width // 2, 
                control_height
            )
            
            # KeyBinding-Element hinzufügen
            keybind = KeyBinding(
                control_x + control_width // 2 + 20,
                y_pos,
                200,
                control_height,
                self.controls[action],
                lambda a=action: self._start_key_binding(a)  # Lambda mit Default-Argument für Action-Closure
            )
            
            self.keybind_elements[action] = keybind
            self.ui_elements.append(keybind)
    
    def _start_key_binding(self, action: str) -> None:
        """Startet den Prozess zum Umbelegen einer Taste."""
        if not self.waiting_for_key:
            self.waiting_for_key = True
            self.current_action = action
    
    def _reset_controls(self) -> None:
        """Setzt alle Steuerungsbindungen auf die Originalwerte zurück."""
        # Tiefe Kopie der Original-Kontrollen erstellen
        self.controls = self.original_controls.copy()
        
        # UI-Elemente aktualisieren
        for action, keybind in self.keybind_elements.items():
            keybind.key_code = self.controls[action]
            
        # Änderung visuell bestätigen
        self.changes_saved = False
    
    def _save_controls(self) -> None:
        """Speichert alle Steuerungsbindungen und ruft den Callback auf."""
        if self.save_controls_callback:
            # Tiefe Kopie der Kontrollen übergeben
            self.save_controls_callback(self.controls.copy())
            self.changes_saved = True
    
    def update(self):
        """Aktualisiert das Steuerungsmenü."""
        # Prüft auf Tasteneingabe im Wartemodus
        if self.waiting_for_key:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # ESC-Taste zum Abbrechen
                    if event.key == pygame.K_ESCAPE:
                        self.waiting_for_key = False
                        return
                        
                    # Tastenzuweisung aktualisieren
                    if self.current_action:
                        self.controls[self.current_action] = event.key
                        
                        # UI-Element aktualisieren
                        if self.current_action in self.keybind_elements:
                            self.keybind_elements[self.current_action].key_code = event.key
                            
                        self.waiting_for_key = False
                        self.current_action = None
                        self.changes_saved = False
                        return
        else:
            # UI-Elemente im normalen Modus aktualisieren
            mouse_pos = pygame.mouse.get_pos()
            for element in self.ui_elements:
                element.update(mouse_pos)
                
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Verarbeitet Ereignisse, einschließlich Tasteneingaben für Neubelegungen."""
        # Im Wartemodus für Tastenbindungen
        if self.waiting_for_key:
            if event.type == pygame.KEYDOWN:
                # Tastendruck erfassen und Bindung aktualisieren
                if self.current_action:
                    self.controls[self.current_action] = event.key
                    
                    # Entsprechendes KeyBinding-Element aktualisieren
                    if self.current_action in self.keybind_elements:
                        self.keybind_elements[self.current_action].key_code = event.key
                        
                    self.waiting_for_key = False
                    self.current_action = None
                    self.changes_saved = False
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Klick außerhalb - Abbrechen
                self.waiting_for_key = False
                self.current_action = None
                return True
            
            # Im Wartemodus alle Events abfangen
            return True
        
        # Standard-Ereignisverarbeitung für UI-Elemente
        return super().handle_event(event)
    
    def render(self, surface: pygame.Surface) -> None:
        """Zeichnet das Steuerungsmenü mit Beschriftungen."""
        # Klare den Bildschirm zuerst
        background = pygame.Surface((self.screen_width, self.screen_height))
        background.fill(MENU_BG_COLOR)
        surface.blit(background, (0, 0))
        
        # Basis-Rendering (Hintergrund, Titel, etc.)
        super().render(surface)
        
        # Partikel-Animation aktualisieren und zeichnen
        self.update_particles()
        self.draw_particles(surface)
        
        # Überschrift mit Schatten für bessere Lesbarkeit
        header_text = "Tastenbelegung anpassen"
        
        # Schatten
        shadow_surf = self.subtitle_font.render(header_text, True, (30, 30, 30))
        shadow_rect = shadow_surf.get_rect(midtop=(self.screen_width // 2 + 2, self.control_header_rect.y + 2))
        surface.blit(shadow_surf, shadow_rect)
        
        # Text
        header_surf = self.subtitle_font.render(header_text, True, UI_TEXT_COLOR)
        header_rect = header_surf.get_rect(midtop=(self.screen_width // 2, self.control_header_rect.y))
        surface.blit(header_surf, header_rect)
        
        # Hilfstext für Tasteneingabe
        help_text = "Klicke auf eine Taste, um sie neu zu belegen"
        help_surf = self.text_font.render(help_text, True, WHITE)
        help_rect = help_surf.get_rect(midtop=(self.screen_width // 2, self.control_header_rect.y + 40))
        surface.blit(help_surf, help_rect)
        
        # Steuerungsbeschriftungen mit verbesserten visuellen Elementen
        control_labels = {
            "move_left": "Nach links:",
            "move_right": "Nach rechts:",
            "jump": "Springen:",
            "dimension_change": "Dimension wechseln:",
            "pause": "Pause:"
        }
        
        for action, label in control_labels.items():
            if action in self.control_labels:
                label_rect = self.control_labels[action]
                
                # Hintergrund für besseren Kontrast
                bg_rect = pygame.Rect(
                    label_rect.x - 10, 
                    label_rect.y - 5, 
                    label_rect.width + 20, 
                    label_rect.height + 10
                )
                pygame.draw.rect(surface, (40, 40, 60), bg_rect, border_radius=3)
                pygame.draw.rect(surface, UI_ACCENT_COLOR, bg_rect, 1, border_radius=3)
                
                # Text rendern
                text_surf = self.text_font.render(label, True, UI_TEXT_COLOR)
                text_rect = text_surf.get_rect()
                text_rect.midleft = (label_rect.x, label_rect.centery)
                surface.blit(text_surf, text_rect)
        
        # Alle UI-Elemente rendern
        for element in self.ui_elements:
            element.render(surface)
        
        # Info-Text anzeigen
        info_text = "Speichern nicht vergessen!" if not self.changes_saved else "Änderungen gespeichert!"
        info_color = UI_ACCENT_COLOR if not self.changes_saved else (100, 255, 100)
        info_surf = self.text_font.render(info_text, True, info_color)
        info_rect = info_surf.get_rect(midtop=(self.screen_width // 2, self.info_rect.y))
        surface.blit(info_surf, info_rect)
        
        # "Warte auf Tastendruck"-Overlay anzeigen
        if self.waiting_for_key:
            # Halbtransparentes Overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Schwarz mit 70% Transparenz
            surface.blit(overlay, (0, 0))
            
            # Text für Tasteneingabe
            wait_text = "Drücke eine Taste..."
            wait_surf = self.subtitle_font.render(wait_text, True, WHITE)
            wait_rect = wait_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            
            # Hintergrund für bessere Lesbarkeit
            padding = 20
            bg_rect = wait_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(surface, (60, 60, 80), bg_rect, border_radius=5)
            pygame.draw.rect(surface, UI_ACCENT_COLOR, bg_rect, 2, border_radius=5)
            
            surface.blit(wait_surf, wait_rect)
            
            # Hinweis zum Abbrechen
            cancel_text = "ESC zum Abbrechen"
            cancel_surf = self.text_font.render(cancel_text, True, UI_TEXT_COLOR)
            cancel_rect = cancel_surf.get_rect(midtop=(wait_rect.centerx, wait_rect.bottom + 20))
            surface.blit(cancel_surf, cancel_rect)
        
        # Hervorhebung der aktiven Buttons
        pygame.draw.rect(surface, UI_ACCENT_COLOR, self.save_button.rect.inflate(4, 4), 2)
        pygame.draw.rect(surface, UI_ACCENT_COLOR, self.reset_button.rect.inflate(4, 4), 2)
        pygame.draw.rect(surface, UI_ACCENT_COLOR, self.back_button.rect.inflate(4, 4), 2)


class PauseMenu(Menu):
    """Pausemenü während des Spiels."""
    def __init__(self, screen_width: int, screen_height: int, 
                 resume_callback: Callable[[], None],
                 settings_callback: Callable[[], None],
                 main_menu_callback: Callable[[], None]):
        super().__init__(screen_width, screen_height)
        self.title = "Pause"
        self.background_color = (0, 0, 0, 180)  # Halbtransparent
        
        # Buttons erstellen
        button_width = 250
        button_height = 50
        button_spacing = 20
        start_y = self.screen_height // 2 - 50
        
        # Fortsetzen-Button
        self.ui_elements.append(Button(
            self.screen_width // 2 - button_width // 2,
            start_y,
            button_width, button_height,
            "Fortsetzen",
            resume_callback
        ))
        
        # Einstellungen-Button
        self.ui_elements.append(Button(
            self.screen_width // 2 - button_width // 2,
            start_y + button_height + button_spacing,
            button_width, button_height,
            "Einstellungen",
            settings_callback
        ))
        
        # Hauptmenü-Button
        self.ui_elements.append(Button(
            self.screen_width // 2 - button_width // 2,
            start_y + 2 * (button_height + button_spacing),
            button_width, button_height,
            "Hauptmenü",
            main_menu_callback
        ))
    
    def render(self, surface: pygame.Surface) -> None:
        """Zeichnet das Pausemenü mit halbtransparentem Hintergrund."""
        # Halbtransparenter Hintergrund
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # RGBA mit Alpha für Transparenz
        surface.blit(overlay, (0, 0))
        
        # Titel
        if self.title:
            title_surf = self.title_font.render(self.title, True, UI_ACCENT_COLOR)
            title_rect = title_surf.get_rect(centerx=self.screen_width // 2, top=30)
            surface.blit(title_surf, title_rect)
        
        # UI-Elemente zeichnen
        for element in self.ui_elements:
            element.render(surface)
        
        # Keine Partikel im Pausemenü (wird über dem Spiel gezeichnet)
        
        # Übergangsanimationen
        if self.transition_in < 1.0:
            alpha = int(255 * (1.0 - self.transition_in))
            fade_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            fade_overlay.fill((0, 0, 0, alpha))
            surface.blit(fade_overlay, (0, 0))
            
        if self.transitioning_to is not None:
            alpha = int(255 * self.transition_out)
            fade_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            fade_overlay.fill((0, 0, 0, alpha))
            surface.blit(fade_overlay, (0, 0))


class GameOverMenu(Menu):
    """Menü, das nach dem Spielende angezeigt wird."""
    def __init__(self, screen_width: int, screen_height: int, 
                 restart_callback: Callable[[], None],
                 main_menu_callback: Callable[[], None],
                 score: int = 0, 
                 time_played: float = 0.0):
        super().__init__(screen_width, screen_height)
        self.title = "Spiel vorbei"
        self.score = score
        self.time_played = time_played
        
        # Buttons erstellen
        button_width = 250
        button_height = 50
        button_spacing = 20
        start_y = self.screen_height // 2 + 50
        
        # Neustart-Button
        self.ui_elements.append(Button(
            self.screen_width // 2 - button_width // 2,
            start_y,
            button_width, button_height,
            "Neustart",
            restart_callback
        ))
        
        # Hauptmenü-Button
        self.ui_elements.append(Button(
            self.screen_width // 2 - button_width // 2,
            start_y + button_height + button_spacing,
            button_width, button_height,
            "Hauptmenü",
            main_menu_callback
        ))
    
    def render(self, surface: pygame.Surface) -> None:
        """Zeichnet das Spielende-Menü mit Punktestand und Spielzeit."""
        super().render(surface)
        
        # Punktestand
        score_text = f"Punkte: {self.score}"
        score_surf = self.subtitle_font.render(score_text, True, UI_TEXT_COLOR)
        score_rect = score_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40))
        surface.blit(score_surf, score_rect)
        
        # Spielzeit (formatiert als Minuten:Sekunden)
        minutes = int(self.time_played // 60)
        seconds = int(self.time_played % 60)
        time_text = f"Zeit: {minutes:02d}:{seconds:02d}"
        time_surf = self.text_font.render(time_text, True, UI_TEXT_COLOR)
        time_rect = time_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        surface.blit(time_surf, time_rect)


class WinMenu(Menu):
    """Menü, das nach erfolgreichem Abschluss eines Levels angezeigt wird."""
    def __init__(self, screen_width: int, screen_height: int, 
                 main_menu_callback: Callable[[], None],
                 quit_callback: Callable[[], None],
                 score: int = 0, 
                 time_played: float = 0.0):
        super().__init__(screen_width, screen_height)
        self.title = "Level geschafft!"
        self.score = score
        self.time_played = time_played
        
        # Buttons erstellen
        button_width = 250
        button_height = 50
        button_spacing = 20
        start_y = self.screen_height // 2 + 80
        
        # Hauptmenü-Button
        self.ui_elements.append(Button(
            self.screen_width // 2 - button_width // 2,
            start_y,
            button_width, button_height,
            "Hauptmenü",
            main_menu_callback
        ))
        
        # Beenden-Button
        self.ui_elements.append(Button(
            self.screen_width // 2 - button_width // 2,
            start_y + button_height + button_spacing,
            button_width, button_height,
            "Beenden",
            quit_callback
        ))
    
    def render(self, surface: pygame.Surface) -> None:
        """Zeichnet das Gewinn-Menü mit Punktestand und Spielzeit."""
        super().render(surface)
        
        # Glückwunschtext
        congrats_text = "Glückwunsch!"
        congrats_surf = self.subtitle_font.render(congrats_text, True, UI_ACCENT_COLOR)
        congrats_rect = congrats_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 3 - 40))
        surface.blit(congrats_surf, congrats_rect)
        
        # Punktestand
        score_text = f"Punkte: {self.score}"
        score_surf = self.subtitle_font.render(score_text, True, UI_TEXT_COLOR)
        score_rect = score_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40))
        surface.blit(score_surf, score_rect)
        
        # Spielzeit (formatiert als Minuten:Sekunden)
        minutes = int(self.time_played // 60)
        seconds = int(self.time_played % 60)
        time_text = f"Zeit: {minutes:02d}:{seconds:02d}"
        time_surf = self.text_font.render(time_text, True, UI_TEXT_COLOR)
        time_rect = time_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        surface.blit(time_surf, time_rect) 