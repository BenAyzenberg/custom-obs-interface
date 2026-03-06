import pygame
import os
import time

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.soundLibrary = {}
        for entry in os.listdir('./SoundEffects'):
            full_path = os.path.join('./SoundEffects', entry)
            if os.path.isfile(full_path):
                self.soundLibrary[entry.split('.')[0]] = pygame.mixer.Sound(full_path)

    def play(self, sound):
        try:
            print(f"playing {sound}")
            s = self.soundLibrary[sound]
            s.play()
            time.sleep(s.get_length())
        except:
            print(f"Error retrieving sound for {sound}, check the name of the file.")

if __name__ == "__main__":
    print('Testing pygame soundboard')
    noise = SoundManager()
    print(noise.soundLibrary)
    noise.play('Test')
    noise.play('Hydrate')
    noise.play('fail')
    print('test completed')