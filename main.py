import pygame
import sys
import os
import gc
import time
import tracemalloc
import traceback
from game.game_controller import GameController

def main():
    """
    Hauptfunktion zur Initialisierung und zum Starten des Spiels.
    Enthält Speicher- und Performance-Optimierungen.
    """
    # Sicherstellen, dass das Spiel im Verzeichnis seiner Datei läuft
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Speicherüberwachung starten, wenn DEBUG_MODE aktiviert ist
    DEBUG_MODE = False
    if DEBUG_MODE:
        tracemalloc.start()
    
    try:
        # Pygame initialisieren
        pygame.init()
        pygame.font.init()
        
        # Joysticks initialisieren (optional)
        pygame.joystick.init()
        joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for joystick in joysticks:
            joystick.init()
        
        # Spiel starten
        game = GameController()
        game.run()
        
    except Exception as e:
        # Fehlerbehandlung
        print(f"Ein Fehler ist aufgetreten: {str(e)}")
        if DEBUG_MODE:
            traceback.print_exc()
    finally:
        # Speicher aufräumen
        if DEBUG_MODE:
            current, peak = tracemalloc.get_traced_memory()
            print(f"Aktuelle Speichernutzung: {current / 10**6:.1f} MB")
            print(f"Maximale Speichernutzung: {peak / 10**6:.1f} MB")
            tracemalloc.stop()
        
        # Garbage Collection manuell ausführen, um Ressourcen freizugeben
        gc.collect()
        
        # Pygame herunterfahren
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main() 