"""
Klasse zur Generierung von Hintergrundmusik für die verschiedenen Dimensionen.
"""
import numpy as np
import io
from game.constants import *

class MusicGenerator:
    def __init__(self):
        """Initialisiert den Musikgenerator."""
        pass
    
    def generate_all_music(self):
        """Generiert Musik für alle Dimensionen und gibt ein Dictionary mit Musik-Objekten zurück."""
        music = {
            DIMENSION_NORMAL: self.generate_normal_dimension_music(),
            DIMENSION_MIRROR: self.generate_mirror_dimension_music(),
            DIMENSION_TIME_SLOW: self.generate_time_dimension_music()
        }
        return music
    
    def generate_normal_dimension_music(self):
        """Generiert Musik für die normale Dimension."""
        # Eine einfache Melodie für die normale Dimension
        sample_rate = 44100
        bpm = 90  # Beats pro Minute
        beat_length = 60 / bpm  # Länge eines Beats in Sekunden
        
        # 8 Takte mit je 4 Beats
        duration = beat_length * 4 * 8
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        music = np.zeros_like(t, dtype=float)
        
        # Melodiemuster definieren (C-Dur-Tonleiter: C, D, E, F, G, A, B)
        base_freq = 261.63  # C4
        notes = [0, 2, 4, 5, 7, 9, 11]  # Halbtonschritte in der Durtonleiter
        
        melody = [0, 2, 4, 2, 0, 2, 4, 7,
                 4, 2, 0, 2, 4, 7, 4, 2,
                 0, 2, 4, 2, 0, 2, 4, 7,
                 4, 2, 0, 2, 4, 7, 4, 2]
        
        # Bass hinzufügen
        bass = [0, 0, 4, 4, 5, 5, 7, 7] * 4
        bass_octave = -1  # Eine Oktave tiefer
        
        note_duration = beat_length / 2  # Sechzehntel-Noten
        
        # Melodie rendern
        music = self._render_melody(t, sample_rate, music, base_freq, notes, melody, note_duration)
        
        # Bass rendern
        music = self._render_bass(t, sample_rate, music, base_freq, notes, bass, bass_octave, beat_length)
        
        # Normalisieren und konvertieren
        music = np.int16(music / np.max(np.abs(music)) * 32767 * 0.7)
        
        # BytesIO-Objekt erstellen und zurückgeben
        buffer = io.BytesIO()
        
        # 16-bit signed Integers, Mono-Audio
        buffer.write(music.tobytes())
        buffer.seek(0)
        
        return buffer
    
    def generate_mirror_dimension_music(self):
        """Generiert Musik für die Spiegel-Dimension."""
        # Für Spiegeldimension: die normale Melodie, aber mit einigen Änderungen
        sample_rate = 44100
        bpm = 90
        beat_length = 60 / bpm
        
        duration = beat_length * 4 * 8
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        music = np.zeros_like(t, dtype=float)
        
        # Melodiemuster, aber in Moll statt Dur
        base_freq = 261.63  # C4
        notes_minor = [0, 2, 3, 5, 7, 8, 10]  # Moll-Tonleiter
        
        # Umgekehrte Melodie für Spiegeldimension
        melody = [7, 4, 2, 0, 2, 4, 7, 4,
                 2, 4, 7, 4, 2, 0, 2, 4,
                 7, 4, 2, 0, 2, 4, 7, 4,
                 2, 4, 7, 4, 2, 0, 2, 0]
        
        # Bass auch umgekehrt
        bass = [7, 7, 5, 5, 4, 4, 0, 0] * 4
        bass_octave = -1
        
        note_duration = beat_length / 2
        
        # Echo-Effekt hinzufügen
        echo_delay = int(0.25 * sample_rate)  # 250ms Verzögerung
        echo_strength = 0.3
        
        # Melodie rendern mit Echo-Effekt
        music = self._render_melody_with_echo(t, sample_rate, music, base_freq, notes_minor, 
                                              melody, note_duration, echo_delay, echo_strength)
        
        # Bass rendern
        music = self._render_bass(t, sample_rate, music, base_freq, notes_minor, 
                                  bass, bass_octave, beat_length)
        
        # Reverb-Effekt simulieren durch mehrere verzögerte Echos
        reverb_music = music.copy()
        for delay in [int(0.1 * sample_rate), int(0.15 * sample_rate), int(0.2 * sample_rate)]:
            reverb_strength = 0.2 * (1 - delay / (0.3 * sample_rate))
            reverb = np.zeros_like(music)
            reverb[delay:] = music[:-delay] * reverb_strength
            reverb_music += reverb
        
        music = reverb_music
        
        # Normalisieren und konvertieren
        music = np.int16(music / np.max(np.abs(music)) * 32767 * 0.7)
        
        buffer = io.BytesIO()
        buffer.write(music.tobytes())
        buffer.seek(0)
        
        return buffer
    
    def generate_time_dimension_music(self):
        """Generiert Musik für die Zeitdimension."""
        # Für die Zeitdimension: langsameres Tempo, verträumtere Klänge
        sample_rate = 44100
        bpm = 60  # Langsameres Tempo
        beat_length = 60 / bpm
        
        duration = beat_length * 4 * 8
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        music = np.zeros_like(t, dtype=float)
        
        base_freq = 261.63  # C4
        # Lydischer Modus für einen "schwebenden" Klang
        notes_lydian = [0, 2, 4, 6, 7, 9, 11]
        
        # Eine langsamere, ausgedehnte Melodie
        melody = [0, None, 4, None, 7, None, 9, None,
                 7, None, 4, None, 2, None, 0, None,
                 0, None, 4, None, 7, None, 9, None,
                 7, None, 11, None, 12, None, 9, None]
        
        # Drone-Bass für stetigen, meditativeren Klang
        bass = [0, None, None, None, 5, None, None, None] * 4
        bass_octave = -2
        
        note_duration = beat_length / 2
        
        # Melodie rendern mit Pad-Sound
        for i, note in enumerate(melody):
            start = int(i * note_duration * sample_rate)
            end = int((i + 1) * note_duration * sample_rate)
            
            if end > len(t):
                break
                
            if note is not None:
                freq = base_freq * 2 ** (notes_lydian[note % len(notes_lydian)] / 12)
                
                # Längere Attack- und Release-Zeiten für träumerischen Effekt
                attack = int(min(0.1 * sample_rate, (end - start) * 0.3))
                release = int(min(0.2 * sample_rate, (end - start) * 0.5))
                
                note_sound = self._generate_pad(freq, end - start, attack, release, sample_rate)
                
                if start + len(note_sound) <= len(music):
                    music[start:start + len(note_sound)] += note_sound
        
        # Bass rendern (tiefer, mit längerem Sustain)
        for i, note in enumerate(bass):
            start = int(i * beat_length * sample_rate)
            end = int((i + 1) * beat_length * sample_rate)
            
            if end > len(t):
                break
                
            if note is not None:
                freq = base_freq * 2 ** (bass_octave + notes_lydian[note % len(notes_lydian)] / 12)
                
                # Sehr langer Sustain für den Bass
                attack = int(min(0.2 * sample_rate, (end - start) * 0.2))
                release = int(min(0.4 * sample_rate, (end - start) * 0.4))
                
                bass_sound = self._generate_pad(freq, end - start, attack, release, sample_rate) * 0.5
                
                if start + len(bass_sound) <= len(music):
                    music[start:start + len(bass_sound)] += bass_sound
        
        # Einen subtilen Zeiteffekt hinzufügen
        time_effect = np.zeros_like(music)
        for i in range(0, len(music), int(sample_rate * 0.5)):
            if i + sample_rate < len(music):
                time_effect[i:i+sample_rate] += np.sin(2 * np.pi * 8000 * t[0:sample_rate]) * 0.01
        
        music += time_effect
        
        # Normalisieren und konvertieren
        music = np.int16(music / np.max(np.abs(music)) * 32767 * 0.7)
        
        buffer = io.BytesIO()
        buffer.write(music.tobytes())
        buffer.seek(0)
        
        return buffer
    
    def _render_melody(self, t, sample_rate, music, base_freq, notes, melody, note_duration):
        """Rendert eine Melodie mit den angegebenen Parametern."""
        for i, note in enumerate(melody):
            start = int(i * note_duration * sample_rate)
            end = int((i + 1) * note_duration * sample_rate)
            
            if end > len(t):
                break
                
            if note >= 0:  # -1 würde eine Pause sein
                freq = base_freq * 2 ** (notes[note % len(notes)] / 12)
                segment_t = t[start:end] - t[start]
                note_env = np.ones(end - start)
                
                # ADSR-Hüllkurve
                attack = int(min(0.02 * sample_rate, (end - start) * 0.1))
                release = int(min(0.05 * sample_rate, (end - start) * 0.2))
                
                if attack > 0:
                    note_env[:attack] = np.linspace(0, 1, attack)
                if release > 0 and release < len(note_env):
                    note_env[-release:] = np.linspace(1, 0, release)
                    
                note_sound = np.sin(2 * np.pi * freq * segment_t) * note_env * 0.3
                
                # Oberton hinzufügen
                note_sound += np.sin(2 * np.pi * freq * 2 * segment_t) * note_env * 0.1
                
                if start + len(note_sound) <= len(music):
                    music[start:start + len(note_sound)] += note_sound
        
        return music
    
    def _render_melody_with_echo(self, t, sample_rate, music, base_freq, notes, melody, 
                                 note_duration, echo_delay, echo_strength):
        """Rendert eine Melodie mit Echo-Effekt."""
        for i, note in enumerate(melody):
            start = int(i * note_duration * sample_rate)
            end = int((i + 1) * note_duration * sample_rate)
            
            if end > len(t):
                break
                
            if note >= 0:
                freq = base_freq * 2 ** (notes[note % len(notes)] / 12)
                segment_t = t[start:end] - t[start]
                note_env = np.ones(end - start)
                
                attack = int(min(0.02 * sample_rate, (end - start) * 0.1))
                release = int(min(0.05 * sample_rate, (end - start) * 0.2))
                
                if attack > 0:
                    note_env[:attack] = np.linspace(0, 1, attack)
                if release > 0 and release < len(note_env):
                    note_env[-release:] = np.linspace(1, 0, release)
                    
                # Etwas mehr Obertöne für gespenstischeren Klang
                note_sound = np.sin(2 * np.pi * freq * segment_t) * note_env * 0.3
                note_sound += np.sin(2 * np.pi * freq * 2 * segment_t) * note_env * 0.15
                note_sound += np.sin(2 * np.pi * freq * 3 * segment_t) * note_env * 0.05
                
                if start + len(note_sound) <= len(music):
                    music[start:start + len(note_sound)] += note_sound
                    
                    # Echo hinzufügen
                    echo_start = start + echo_delay
                    if echo_start + len(note_sound) <= len(music):
                        music[echo_start:echo_start + len(note_sound)] += note_sound * echo_strength
        
        return music
    
    def _render_bass(self, t, sample_rate, music, base_freq, notes, bass, bass_octave, beat_length):
        """Rendert eine Basslinie mit den angegebenen Parametern."""
        for i, note in enumerate(bass):
            start = int(i * beat_length * sample_rate)
            end = int((i + 1) * beat_length * sample_rate)
            
            if end > len(t):
                break
                
            if note >= 0:
                freq = base_freq * 2 ** (bass_octave + notes[note % len(notes)] / 12)
                segment_t = t[start:end] - t[start]
                note_env = np.ones(end - start)
                
                # Längerer Release für den Bass
                attack = int(min(0.05 * sample_rate, (end - start) * 0.1))
                release = int(min(0.3 * sample_rate, (end - start) * 0.7))
                
                if attack > 0:
                    note_env[:attack] = np.linspace(0, 1, attack)
                if release > 0 and release < len(note_env):
                    note_env[-release:] = np.linspace(1, 0, release)
                    
                bass_sound = np.sin(2 * np.pi * freq * segment_t) * note_env * 0.4
                
                if start + len(bass_sound) <= len(music):
                    music[start:start + len(bass_sound)] += bass_sound
        
        return music
    
    def _generate_pad(self, freq, duration_samples, attack_samples, release_samples, sample_rate):
        """Generiert einen Pad-Sound mit der angegebenen Frequenz und Hüllkurve."""
        t_pad = np.linspace(0, duration_samples / sample_rate, duration_samples)
        
        # Mehrere Sinuswellen mit leicht verstimmten Frequenzen für einen reicheren Klang
        sound = np.sin(2 * np.pi * freq * t_pad) * 0.3
        sound += np.sin(2 * np.pi * (freq * 1.01) * t_pad) * 0.2
        sound += np.sin(2 * np.pi * (freq * 0.99) * t_pad) * 0.2
        sound += np.sin(2 * np.pi * (freq * 2) * t_pad) * 0.1
        
        # Sanfte Hüllkurve
        envelope = np.ones_like(sound)
        
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        if release_samples > 0 and release_samples < len(envelope):
            envelope[-release_samples:] = np.linspace(1, 0, release_samples)
            
        return sound * envelope 