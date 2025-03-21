"""
Enthält Klassen für alle UI-Elemente, die im Menü und der Spieloberfläche verwendet werden.
"""
import pygame
from game.constants import *
from typing import Callable, Optional, Tuple, List, Any
from abc import ABC, abstractmethod

# Konstanten für KeyBinding-Element
KEYBIND_BG_COLOR = (60, 60, 80)      # Hintergrund des Keybinding-Elements
KEYBIND_HOVER_COLOR = (80, 80, 120)  # Hintergrundfarbe bei Hover
KEYBIND_BORDER_COLOR = (100, 100, 150)  # Rahmenfarbe

class UIElement(ABC):
    """Abstrakte Basisklasse für UI-Elemente."""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.hovered = False
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Verarbeitet ein Ereignis und gibt zurück, ob es verarbeitet wurde."""
        pass
    
    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Zeichnet das UI-Element auf die angegebene Oberfläche."""
        pass

class Button(UIElement):
    """Button-UI-Element mit Hover-Effekt und Klick-Funktionalität."""
    def __init__(self, x, y, width, height, text, action=None):
        super().__init__(x, y, width, height)
        self.text = text
        self.action = action
        self.font = pygame.font.SysFont('Arial', 24)
        self.transition_progress = 0  # Für Animationen
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False
    
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Animation aktualisieren
        if self.hovered:
            self.transition_progress = min(1.0, self.transition_progress + 0.1)
        else:
            self.transition_progress = max(0.0, self.transition_progress - 0.1)
    
    def render(self, surface):
        # Hintergrundfarbe basierend auf Hover-Status
        base_color = BUTTON_COLOR
        hover_color = BUTTON_HOVER_COLOR
        
        # Interpoliere zwischen Basis- und Hover-Farbe
        r = int(base_color[0] + (hover_color[0] - base_color[0]) * self.transition_progress)
        g = int(base_color[1] + (hover_color[1] - base_color[1]) * self.transition_progress)
        b = int(base_color[2] + (hover_color[2] - base_color[2]) * self.transition_progress)
        
        current_color = (r, g, b)
        
        # Button zeichnen
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, BUTTON_BORDER_COLOR, self.rect, 2)
        
        # Text zeichnen
        text_color = WHITE  # Farbe auf Weiß geändert statt Schwarz für besseren Kontrast
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Hover-Effekt: Schatten nur wenn nicht gehovert, sonst Hervorhebung
        if self.transition_progress > 0:
            shadow_size = int(4 * self.transition_progress)
            # Hervorhebung statt Schatten (mehr Transparenz)
            pygame.draw.rect(surface, BUTTON_BORDER_COLOR, 
                            self.rect.inflate(shadow_size, shadow_size), 
                            2)  # Nur Umrandung statt gefüllter Schatten


class Slider(UIElement):
    """Ein Schieberegler für numerische Werte."""
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_value: float, max_value: float, 
                 initial_value: float, on_change: Callable[[float], None] = None):
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = initial_value
        self.on_change = on_change
        self.handle_size = height + 6
        self.handle_pos = 0
        self.dragging = False
        self.font = pygame.font.SysFont('Arial', 14)
        self._update_handle_position()
    
    def _update_handle_position(self):
        """Aktualisiert die Position des Sliders basierend auf dem aktuellen Wert."""
        normalized_value = (self.current_value - self.min_value) / (self.max_value - self.min_value)
        self.handle_pos = self.rect.x + int(normalized_value * self.rect.width)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Überprüfen, ob das Handle angeklickt wurde
            handle_rect = pygame.Rect(self.handle_pos - self.handle_size // 2, 
                                     self.rect.y - 3, self.handle_size, self.handle_size)
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
                return True
            # Überprüfen, ob direkt auf den Slider geklickt wurde
            elif self.rect.collidepoint(event.pos):
                self._set_value_from_pos(event.pos[0])
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._set_value_from_pos(event.pos[0])
                return True
                
        return False
    
    def _set_value_from_pos(self, x_pos):
        # Den Bereich auf die Position des Sliders beschränken
        x_pos = max(self.rect.x, min(x_pos, self.rect.x + self.rect.width))
        normalized_pos = (x_pos - self.rect.x) / self.rect.width
        
        # Neuen Wert berechnen
        new_value = self.min_value + normalized_pos * (self.max_value - self.min_value)
        
        # Wert aktualisieren und Callback aufrufen
        self.current_value = new_value
        self._update_handle_position()
        
        if self.on_change:
            self.on_change(self.current_value)
    
    def update(self, mouse_pos):
        pass  # Keine kontinuierliche Aktualisierung notwendig
    
    def render(self, surface):
        # Slider-Hintergrund
        pygame.draw.rect(surface, SLIDER_BACKGROUND_COLOR, self.rect)
        
        # Slider-Fortschritt
        progress_width = int(self.handle_pos - self.rect.x)
        if progress_width > 0:
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            pygame.draw.rect(surface, SLIDER_FILL_COLOR, progress_rect)
        
        # Slider-Rahmen
        pygame.draw.rect(surface, SLIDER_BORDER_COLOR, self.rect, 2)
        
        # Slider-Griff
        handle_x = int(self.handle_pos)
        handle_y = int(self.rect.y + self.rect.height // 2)
        handle_size = int(self.handle_size // 2)
        
        pygame.draw.circle(surface, SLIDER_HANDLE_COLOR, 
                          (handle_x, handle_y), 
                          handle_size)
        
        # Aktueller Wert (gerundet auf 2 Dezimalstellen)
        value_text = self.font.render(f"{self.current_value:.2f}", True, UI_TEXT_COLOR)
        value_rect = value_text.get_rect(midright=(self.rect.x - 10, self.rect.y + self.rect.height // 2))
        surface.blit(value_text, value_rect)


class Toggle(UIElement):
    """Toggle-Button für Ein/Aus-Einstellungen."""
    def __init__(self, x, y, width, height, is_on, on_change=None):
        super().__init__(x, y, width, height)
        self.is_on = is_on
        self.on_change = on_change
        self.transition_progress = 1.0 if is_on else 0.0
        self.font = pygame.font.SysFont('Arial', 18)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_on = not self.is_on
                if self.on_change:
                    self.on_change(self.is_on)
                return True
        return False
    
    def update(self, mouse_pos):
        # Animation aktualisieren
        if self.is_on:
            self.transition_progress = min(1.0, self.transition_progress + 0.1)
        else:
            self.transition_progress = max(0.0, self.transition_progress - 0.1)
    
    def render(self, surface):
        # Griff
        handle_x = int(self.rect.x + (self.rect.width * (1 if self.is_on else 0)))
        handle_y = int(self.rect.y + self.rect.height // 2)
        handle_radius = int(self.rect.height // 2 - 2)
        
        # Hintergrund
        pygame.draw.rect(surface, TOGGLE_BACKGROUND_COLOR, self.rect, 0, 10)
        
        # Aktiver Hintergrund
        if self.transition_progress > 0:
            active_width = int(self.rect.width * self.transition_progress)
            active_rect = pygame.Rect(self.rect.x, self.rect.y, active_width, self.rect.height)
            pygame.draw.rect(surface, TOGGLE_ACTIVE_COLOR, active_rect, 0, 10)
        
        # Griff
        pygame.draw.circle(surface, TOGGLE_HANDLE_COLOR, (handle_x, handle_y), handle_radius)
        
        # Text
        text = "An" if self.is_on else "Aus"
        text_surf = self.font.render(text, True, UI_TEXT_COLOR)
        text_rect = text_surf.get_rect(midright=(self.rect.x - 10, self.rect.y + self.rect.height // 2))
        surface.blit(text_surf, text_rect)


class TextInput(UIElement):
    """Texteingabefeld für Name oder andere Texteingaben."""
    def __init__(self, x, y, width, height, current_text="", on_change=None):
        super().__init__(x, y, width, height)
        self.text = current_text
        self.on_change = on_change
        self.active = False
        self.font = pygame.font.SysFont('Arial', 24)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_chars = width // 12  # Ungefähre Max-Zeichen basierend auf Breite
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            return self.active
            
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_chars and event.unicode.isprintable():
                self.text += event.unicode
                
            if self.on_change:
                self.on_change(self.text)
            return True
                
        return False
    
    def update(self, mouse_pos):
        # Cursor blinken lassen
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Blinken alle 30 Frames
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def render(self, surface):
        # Hintergrund
        bg_color = INPUT_ACTIVE_COLOR if self.active else INPUT_BG_COLOR
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, INPUT_BORDER_COLOR, self.rect, 2)
        
        # Text
        text_surf = self.font.render(self.text, True, UI_TEXT_COLOR)
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))
        
        # Cursor
        if self.active and self.cursor_visible:
            text_width = self.font.size(self.text)[0]
            cursor_x = self.rect.x + 5 + text_width
            cursor_y1 = self.rect.y + 5
            cursor_y2 = self.rect.y + self.rect.height - 5
            pygame.draw.line(surface, UI_TEXT_COLOR, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)


class KeyBinding(UIElement):
    """UI-Element für Tastenbindungen."""
    def __init__(self, x: int, y: int, width: int, height: int, 
                 key_code: int, on_click: Callable[[], None] = None):
        super().__init__(x, y, width, height)
        self.key_code = key_code
        self.on_click = on_click
        self.font = pygame.font.SysFont('Arial', 16)
        self.transition_progress = 0  # Für Hover-Animation
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Verarbeitet Ereignisse für das KeyBinding-Element."""
        # Aktuelle Mausposition abrufen für Hover-Effekt
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            self.hovered = self.rect.collidepoint(mouse_pos)
            return False
        
        # Bei Klick auf das Element den Callback ausführen
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    # Debug-Ausgabe zur Bestätigung des Klicks
                    print(f"KeyBinding clicked: {pygame.key.name(self.key_code)}")
                    self.on_click()
                return True
        return False
    
    def update(self, mouse_pos):
        """Aktualisiert den Hover-Status des Keybinding-Elements."""
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Animation aktualisieren
        if self.hovered:
            self.transition_progress = min(1.0, self.transition_progress + 0.1)
        else:
            self.transition_progress = max(0.0, self.transition_progress - 0.1)
    
    def render(self, surface: pygame.Surface) -> None:
        # Hintergrundfarbe basierend auf Hover-Status und Animation
        base_color = UI_ELEMENT_COLOR
        hover_color = UI_ELEMENT_HOVER_COLOR
        
        # Interpoliere Farben für smoothen Übergang
        r = int(base_color[0] + (hover_color[0] - base_color[0]) * self.transition_progress)
        g = int(base_color[1] + (hover_color[1] - base_color[1]) * self.transition_progress)
        b = int(base_color[2] + (hover_color[2] - base_color[2]) * self.transition_progress)
        
        bg_color = (r, g, b)
        
        # Button zeichnen
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 2)
        
        # Tastenbeschriftung anzeigen
        key_name = pygame.key.name(self.key_code).upper()
        text = key_name
        
        # Text in der Mitte positionieren
        text_surf = self.font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Hover-Effekt mit Hervorhebung
        if self.transition_progress > 0:
            shadow_size = int(4 * self.transition_progress)
            pygame.draw.rect(surface, UI_ACCENT_COLOR, 
                          self.rect.inflate(shadow_size, shadow_size), 
                          2) 