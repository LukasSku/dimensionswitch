"""
Klasse zur Generierung von Sound-Effekten für das Spiel.
"""
import pygame
import numpy as np

class SoundEffects:
    def __init__(self):
        """Initialisiert die Sound-Effects-Klasse."""
        pass
    
    def generate_all_sounds(self):
        """Generiert alle Sound-Effekte und gibt ein Dictionary mit Sound-Objekten zurück."""
        sounds = {}
        
        # Jump-Sound
        sounds["jump"] = self.generate_jump_sound()
        
        # Collect-Sound
        sounds["collect"] = self.generate_collect_sound()
        
        # Dimension-Shift-Sound
        sounds["dimension_shift"] = self.generate_dimension_shift_sound()
        
        # Enemy-Death-Sound
        sounds["enemy_death"] = self.generate_enemy_death_sound()
        
        # Player-Death-Sound
        sounds["player_death"] = self.generate_player_death_sound()
        
        # Portal-Sound
        sounds["portal"] = self.generate_portal_sound()
        
        # Button-Sound
        sounds["button"] = self.generate_button_sound()
        
        # Schritte
        sounds["step"] = self.generate_step_sound()
        
        # Levelabschluss
        sounds["level_complete"] = self.generate_level_complete_sound()
        
        return sounds
    
    def generate_jump_sound(self):
        """Generiert einen Sprung-Sound."""
        # Synthesizer-Parameter
        sample_rate = 44100
        duration = 0.3  # Sekunden
        
        # Frequenzabfall von hoch nach niedrig
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        frequency = np.linspace(800, 400, len(t))
        
        # Sinus-Welle mit variierender Frequenz
        tone = np.sin(2 * np.pi * frequency * t)
        
        # ADSR-Hüllkurve anwenden (Attack, Decay, Sustain, Release)
        envelope = np.ones_like(t)
        attack = int(0.05 * sample_rate)
        decay = int(0.1 * sample_rate)
        release = int(0.15 * sample_rate)
        
        # Attack
        envelope[:attack] = np.linspace(0, 1, attack)
        # Decay und Sustain
        envelope[attack:attack+decay] = np.linspace(1, 0.7, decay)
        # Release
        envelope[-release:] = np.linspace(0.7, 0, release)
        
        # Hüllkurve anwenden
        tone = tone * envelope
        
        # Normalisieren
        tone = np.int16(tone / np.max(np.abs(tone)) * 32767 * 0.7)
        
        # In Bytes konvertieren und als Sound zurückgeben
        return pygame.mixer.Sound(tone.tobytes())
    
    def generate_collect_sound(self):
        """Generiert einen Sammel-Sound."""
        sample_rate = 44100
        duration = 0.2
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Aufsteigende Tonfolge
        tone1 = np.sin(2 * np.pi * 600 * t[:len(t)//2])
        tone2 = np.sin(2 * np.pi * 900 * t[len(t)//2:])
        tone = np.concatenate((tone1, tone2))
        
        # Schneller Attack und Release
        envelope = np.ones_like(t)
        attack = int(0.01 * sample_rate)
        release = int(0.05 * sample_rate)
        
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        tone = tone * envelope * 0.7
        tone = np.int16(tone / np.max(np.abs(tone)) * 32767)
        
        return pygame.mixer.Sound(tone.tobytes())
    
    def generate_dimension_shift_sound(self):
        """Generiert einen Dimensionswechsel-Sound."""
        sample_rate = 44100
        duration = 0.5
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Komplexere Welle für Dimensionswechsel
        frequencies = [300, 500, 700, 900, 700, 500, 300]
        segments = len(frequencies)
        segment_length = len(t) // segments
        
        tone = np.zeros_like(t)
        
        for i, freq in enumerate(frequencies):
            start = i * segment_length
            end = start + segment_length if i < segments - 1 else len(t)
            segment_t = t[start:end]
            segment = np.sin(2 * np.pi * freq * segment_t)
            
            # Jedem Segment ein eigenes Ein- und Ausblenden geben
            segment_envelope = np.ones_like(segment)
            fade = min(100, len(segment) // 4)
            segment_envelope[:fade] = np.linspace(0, 1, fade)
            segment_envelope[-fade:] = np.linspace(1, 0, fade)
            
            segment = segment * segment_envelope
            tone[start:end] = segment
        
        # Einen Hauch von "Rauschen" hinzufügen für kosmischen Effekt
        noise = np.random.uniform(-0.1, 0.1, len(t))
        tone = tone + noise
        
        tone = np.int16(tone / np.max(np.abs(tone)) * 32767 * 0.7)
        
        return pygame.mixer.Sound(tone.tobytes())
    
    def generate_enemy_death_sound(self):
        """Generiert einen Feind-Tod-Sound."""
        sample_rate = 44100
        duration = 0.3
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Abfallende Frequenz
        frequency = np.linspace(300, 50, len(t))
        tone = np.sin(2 * np.pi * frequency * t)
        
        # Rauschen hinzufügen
        noise = np.random.uniform(-0.5, 0.5, len(t))
        mixed = tone * 0.7 + noise * 0.3
        
        # Kurzer Attack, langer Release
        envelope = np.ones_like(t)
        attack = int(0.01 * sample_rate)
        release = int(0.2 * sample_rate)
        
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        mixed = mixed * envelope * 0.8
        mixed = np.int16(mixed / np.max(np.abs(mixed)) * 32767)
        
        return pygame.mixer.Sound(mixed.tobytes())
    
    def generate_player_death_sound(self):
        """Generiert einen Spieler-Tod-Sound."""
        sample_rate = 44100
        duration = 0.6
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Abfallende Tonsequenz
        tone1 = np.sin(2 * np.pi * 400 * t[:len(t)//3])
        tone2 = np.sin(2 * np.pi * 300 * t[len(t)//3:2*len(t)//3])
        tone3 = np.sin(2 * np.pi * 200 * t[2*len(t)//3:])
        
        tone = np.concatenate((tone1, tone2, tone3))
        
        # Dramatischeren Klang mit Obertönen hinzufügen
        overtone = np.sin(2 * np.pi * 800 * t) * 0.3
        tone = tone + overtone
        
        # Anwendung der Hüllkurve
        envelope = np.ones_like(t)
        attack = int(0.05 * sample_rate)
        release = int(0.3 * sample_rate)
        
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        tone = tone * envelope * 0.8
        tone = np.int16(tone / np.max(np.abs(tone)) * 32767)
        
        return pygame.mixer.Sound(tone.tobytes())
    
    def generate_portal_sound(self):
        """Generiert einen Portal-Sound."""
        sample_rate = 44100
        duration = 0.8
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Aufsteigende Frequenz mit Vibrato
        base_freq = np.linspace(200, 1000, len(t))
        vibrato = 40 * np.sin(2 * np.pi * 10 * t)  # Vibrato mit 10 Hz
        freq = base_freq + vibrato
        
        tone = np.sin(2 * np.pi * np.cumsum(freq) / sample_rate)
        
        # Einen "Chor"-Effekt hinzufügen
        detune = np.sin(2 * np.pi * np.cumsum(freq * 1.01) / sample_rate) * 0.5
        detune2 = np.sin(2 * np.pi * np.cumsum(freq * 0.99) / sample_rate) * 0.5
        
        tone = (tone + detune + detune2) / 3
        
        # Langsames Einblenden und Ausblenden
        envelope = np.ones_like(t)
        attack = int(0.2 * sample_rate)
        release = int(0.3 * sample_rate)
        
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        tone = tone * envelope * 0.7
        tone = np.int16(tone / np.max(np.abs(tone)) * 32767)
        
        return pygame.mixer.Sound(tone.tobytes())
    
    def generate_button_sound(self):
        """Generiert einen Button-Klick-Sound."""
        sample_rate = 44100
        duration = 0.1
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Einfacher Klick-Ton
        frequency = 800
        tone = np.sin(2 * np.pi * frequency * t)
        
        # Sehr kurzer Attack und schnelles Abklingen
        envelope = np.ones_like(t)
        attack = int(0.005 * sample_rate)
        release = int(0.08 * sample_rate)
        
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        tone = tone * envelope * 0.6
        tone = np.int16(tone / np.max(np.abs(tone)) * 32767)
        
        return pygame.mixer.Sound(tone.tobytes())
    
    def generate_step_sound(self):
        """Generiert einen Schritt-Sound."""
        sample_rate = 44100
        duration = 0.1
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Ein kurzer, dumpfer Klang
        tone = np.sin(2 * np.pi * 100 * t) * 0.5
        noise = np.random.uniform(-0.5, 0.5, len(t)) * 0.5
        
        mixed = tone + noise
        
        # Schnelles Ein- und Ausblenden
        envelope = np.ones_like(t)
        attack = int(0.01 * sample_rate)
        release = int(0.05 * sample_rate)
        
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        mixed = mixed * envelope * 0.6
        mixed = np.int16(mixed / np.max(np.abs(mixed)) * 32767)
        
        return pygame.mixer.Sound(mixed.tobytes())
    
    def generate_level_complete_sound(self):
        """Generiert einen Level-Abschluss-Sound."""
        sample_rate = 44100
        duration = 1.0
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Aufsteigende Tonfolge für "Erfolg"
        segments = 4
        segment_length = len(t) // segments
        
        tones = []
        frequencies = [440, 554, 659, 880]  # A, C#, E, A (A-Dur-Akkord)
        
        for i, freq in enumerate(frequencies):
            start = i * segment_length
            end = start + segment_length
            segment_t = t[start:end]
            segment = np.sin(2 * np.pi * freq * segment_t)
            
            # Harmonische Obertöne hinzufügen
            overtone1 = np.sin(2 * np.pi * freq * 2 * segment_t) * 0.3
            overtone2 = np.sin(2 * np.pi * freq * 3 * segment_t) * 0.15
            segment = segment + overtone1 + overtone2
            
            # Jedes Segment ein- und ausblenden
            envelope = np.ones_like(segment)
            fade = min(int(0.1 * sample_rate), len(segment) // 4)
            
            envelope[:fade] = np.linspace(0, 1, fade)
            envelope[-fade:] = np.linspace(1, 0, fade)
            
            segment = segment * envelope
            tones.append(segment)
        
        # Alle Töne zusammenfügen
        tone = np.concatenate(tones)
        
        # Globale Hüllkurve anwenden
        global_envelope = np.ones_like(tone)
        attack = int(0.05 * sample_rate)
        release = int(0.2 * sample_rate)
        
        global_envelope[:attack] = np.linspace(0, 1, attack)
        global_envelope[-release:] = np.linspace(1, 0, release)
        
        tone = tone * global_envelope * 0.8
        tone = np.int16(tone / np.max(np.abs(tone)) * 32767)
        
        return pygame.mixer.Sound(tone.tobytes()) 