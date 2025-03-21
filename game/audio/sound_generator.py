"""
Sound-Generator-Hauptklasse, die Sound-Effekte und Musik verwaltet.
"""
import pygame
import numpy as np
import os
from pathlib import Path
from game.constants import *
from game.audio.sound_effects import SoundEffects
from game.audio.music_generator import MusicGenerator
import time

class SoundGenerator:
    def __init__(self, settings):
        """Initialisiert den Sound-Generator mit den Spieleinstellungen."""
        self.settings = settings
        self.sounds = {}
        self.music = None
        self.music_playing = False
        self.current_dimension = DIMENSION_NORMAL
        self.temp_music_file = None
        
        # Pygame-Mixer initialisieren
        pygame.mixer.init()
        
        # Volume-Einstellungen
        self.music_volume = self.settings.get("music_volume", 0.7)
        self.sfx_volume = self.settings.get("sfx_volume", 0.8)
        
        # Sound-Effekte und Musik erzeugen
        self.sound_effects = SoundEffects()
        self.sounds = self.sound_effects.generate_all_sounds()
        
        # Cooldowns für Sounds initialisieren (zeitbasiert)
        self.sound_cooldowns = {}
        for sound_name in self.sounds.keys():
            self.sound_cooldowns[sound_name] = 0
        
        # Musik generieren und für Playback vorbereiten
        self.music_generator = MusicGenerator()
        self.music = self.music_generator.generate_all_music()
        
        # Temporäre Dateien für Musik
        self.temp_music_file = None
    
    def generate_sounds(self):
        """Generiert alle Sound-Effekte."""
        self.sounds = self.sound_effects.generate_all_sounds()
    
    def generate_music(self):
        """Generiert Musik für verschiedene Dimensionen."""
        self.music = self.music_generator.generate_all_music()
    
    def play_sound(self, sound_name, volume=1.0, cooldown=0.0):
        """Spielt einen Sound ab, wenn er verfügbar ist und der Cooldown abgelaufen ist."""
        current_time = time.time()
        
        # Prüfen, ob der Sound im Cooldown ist
        if sound_name in self.sound_cooldowns:
            if current_time - self.sound_cooldowns[sound_name] < cooldown:
                return
                
        # Sound abspielen, wenn verfügbar
        if sound_name in self.sounds:
            # Lautstärke anpassen
            self.sounds[sound_name].set_volume(volume * self.settings["sfx_volume"])
            
            # Sound abspielen
            self.sounds[sound_name].play()
            
            # Cooldown aktualisieren
            self.sound_cooldowns[sound_name] = current_time
    
    def handle_player_events(self, events):
        """Verarbeitet Ereignisse des Spielers und spielt entsprechende Sounds ab."""
        # Sprung
        if events.get("jump", False):
            self.play_sound("jump", cooldown=0.2)
            
        # Sammeln
        if events.get("collect", False):
            self.play_sound("collect", cooldown=0.1)
            
        # Gegner besiegt
        if events.get("enemy_death", False):
            self.play_sound("enemy_die", cooldown=0.1)
            
        # Level abgeschlossen
        if events.get("level_complete", False):
            self.play_sound("portal", cooldown=0.5)
            
        # Spieler gestorben
        if events.get("player_death", False):
            self.play_sound("die", cooldown=1.0)
            
        # Schrittgeräusche
        if events.get("step", False):
            self.play_sound("step", cooldown=0.2)
        
        # Powerup erhalten (wird separat in GameController behandelt)
        # if events.get("powerup", False):
        #     self.play_sound("powerup", cooldown=0.5)
    
    def handle_menu_event(self, sound_played):
        """Verarbeitet Menü-Events und spielt UI-Sounds ab."""
        if sound_played:
            self.play_sound("button")
    
    def handle_dimension_change(self, new_dimension):
        """Behandelt Dimensionswechsel und spielt entsprechende Sounds/Musik."""
        if new_dimension != self.current_dimension:
            self.play_sound("dimension_shift")
            self.play_music(new_dimension)
            self.current_dimension = new_dimension
    
    def play_music(self, dimension):
        """Spielt die Musik für eine bestimmte Dimension ab."""
        if dimension in self.music:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            
            self._cleanup_temp_music_file()
            
            # Temporäre Datei für die Musik anlegen
            import tempfile
            import wave
            
            # Wir erstellen einen temporären WAV-Dateinamen
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            self.temp_music_file = temp_file.name
            temp_file.close()
            
            # BytesIO zu WAV-Datei konvertieren
            with wave.open(self.temp_music_file, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes (16 bit)
                wav_file.setframerate(44100)  # 44.1 kHz
                wav_file.writeframes(self.music[dimension].getvalue())
            
            try:
                # Laden der temporären Datei
                pygame.mixer.music.load(self.temp_music_file)
                pygame.mixer.music.set_volume(self.settings["music_volume"])
                pygame.mixer.music.play(-1)  # -1 bedeutet Endlosschleife
                self.music_playing = True
            except Exception as e:
                print(f"Fehler beim Laden der Musik: {e}")
    
    def update(self, dt):
        """Aktualisiert Cooldowns und andere zeitabhängige Audio-Effekte."""
        # Cooldowns aktualisieren
        for sound_name in self.sound_cooldowns:
            if self.sound_cooldowns[sound_name] > 0:
                self.sound_cooldowns[sound_name] -= 1
    
    def update_volume(self):
        """Aktualisiert die Lautstärke basierend auf den Einstellungen."""
        if self.music_playing:
            pygame.mixer.music.set_volume(self.settings["music_volume"])
    
    def _cleanup_temp_music_file(self):
        """Löscht die temporäre Musikdatei, falls vorhanden."""
        if self.temp_music_file and os.path.exists(self.temp_music_file):
            try:
                os.unlink(self.temp_music_file)
            except Exception as e:
                print(f"Fehler beim Löschen der temporären Musikdatei: {e}")
    
    def cleanup(self):
        """Räumt temporäre Dateien auf und beendet den Sound-Generator."""
        # Musik stoppen
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        
        # Temporäre Datei löschen
        self._cleanup_temp_music_file()
        self.temp_music_file = None 

    def generate_sound_effects(self):
        """Erzeugt alle Sound-Effekte und gibt sie als Dictionary zurück."""
        sounds = {}
        
        # Player-Sounds
        sounds["jump"] = self._generate_jump_sound()
        sounds["land"] = self._generate_land_sound()
        sounds["hurt"] = self._generate_hurt_sound()
        sounds["die"] = self._generate_die_sound()
        sounds["step"] = self._generate_step_sound()
        sounds["powerup"] = self._generate_powerup_sound()
        sounds["dimension_change"] = self._generate_dimension_change_sound()
        
        # ... existing code ...
        
    def _generate_powerup_sound(self):
        """Erzeugt den Sound-Effekt für das Einsammeln eines Powerups."""
        sound_buffer = np.zeros(int(44100 * 0.5))  # 0.5 Sekunden
        
        # Basisfrequenz für Powerup-Sound
        base_freq = 800
        
        # Ansteigender Ton
        for i in range(len(sound_buffer) // 3):
            t = i / 44100
            freq = base_freq + i * 2
            sound_buffer[i] = 0.5 * np.sin(2 * np.pi * freq * t)
            
        # Abfallender Ton mit Modulation
        for i in range(len(sound_buffer) // 3, len(sound_buffer)):
            t = i / 44100
            freq = base_freq + (len(sound_buffer) // 3) * 2 - (i - len(sound_buffer) // 3) * 1.5
            mod = 1 + 0.2 * np.sin(2 * np.pi * 25 * t)  # Modulation
            sound_buffer[i] = 0.5 * np.sin(2 * np.pi * freq * t * mod)
            
        # Hüllkurve anwenden
        envelope = np.ones(len(sound_buffer))
        attack = int(0.01 * 44100)
        release = int(0.1 * 44100)
        
        # Attack
        envelope[:attack] = np.linspace(0, 1, attack)
        
        # Release
        release_start = len(sound_buffer) - release
        envelope[release_start:] = np.linspace(1, 0, release)
        
        sound_buffer = sound_buffer * envelope
        
        # Mit zusätzlichem hohen Klang mischen für glitzernden Effekt
        shimmer = np.zeros(len(sound_buffer))
        for i in range(len(shimmer)):
            t = i / 44100
            shimmer[i] = 0.2 * np.sin(2 * np.pi * 1600 * t) * np.exp(-5 * t)
            
        sound_buffer = sound_buffer + shimmer
        
        # Stereo-Effekt: von links nach rechts wandern
        stereo_buffer = np.zeros((len(sound_buffer), 2))
        for i in range(len(sound_buffer)):
            pos = i / len(sound_buffer)
            stereo_buffer[i, 0] = sound_buffer[i] * (1 - pos)  # Links
            stereo_buffer[i, 1] = sound_buffer[i] * pos        # Rechts
            
        # Normalisieren
        stereo_buffer = 0.9 * stereo_buffer / np.max(np.abs(stereo_buffer))
        
        # In 16-bit PCM konvertieren
        return self._create_pygame_sound(stereo_buffer)
        
    def play_powerup_sound(self, powerup_type: str) -> None:
        """Spielt einen Sound basierend auf dem Powerup-Typ ab."""
        # Standardmäßig den generischen Powerup-Sound abspielen
        sound_name = "powerup"
        
        # Spezifische Sounds für verschiedene Powerup-Typen
        if powerup_type == "speed":
            sound_name = "powerup_speed"
        elif powerup_type == "jump":
            sound_name = "powerup_jump"
        elif powerup_type == "invincibility":
            sound_name = "powerup_invincible"
        elif powerup_type == "gravity":
            sound_name = "powerup_gravity"
            
        # Sound abspielen (verwende den generischen, wenn der spezifische nicht existiert)
        if sound_name in self.sounds:
            self.play_sound(sound_name, cooldown=0.5)
        else:
            self.play_sound("powerup", cooldown=0.5)
        