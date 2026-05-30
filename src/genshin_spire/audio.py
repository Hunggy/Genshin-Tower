import os
import pygame

from .config import get_base_path


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        sound_map = {
            "attack": ["attack.mp3", "attack.wav"],
            "shield": ["shield.mp3", "shield.wav"],
            "hurt": ["hurt.mp3", "hurt.wav"],
            "jump": ["星之卡比掉下悬崖_爱给网_aigei_com.mp3", "jump.mp3", "jump.wav"],
            "gta_death": ["GTA V 死亡逮捕音效(GTA V WastedBuste_爱给网_aigei_com.mp3"],
            "mage_death": ["法师死亡_爱给网_aigei_com.mp3"],
        }

        for name, files in sound_map.items():
            found = False
            for filename in files:
                path = os.path.join(get_base_path(), "audio", filename)
                if os.path.exists(path):
                    try:
                        self.sounds[name] = pygame.mixer.Sound(path)
                        self.sounds[name].set_volume(0.5)
                        found = True
                        break
                    except Exception as e:
                        print(f"無法加載音效 {filename}: {e}")

            if not found:
                self.sounds[name] = None

    def play(self, sound_name):
        sound = self.sounds.get(sound_name)
        if sound:
            sound.play()

    def set_volume(self, volume):
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(volume)


def play_bgm(volume=0.5, is_endless=False):
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        bgm_found = False
        if is_endless:
            bgm_path = os.path.join(get_base_path(), "audio", "Nyanyanyanyanyanyanya.mp3")
            if os.path.exists(bgm_path):
                pygame.mixer.music.load(bgm_path)
                bgm_found = True

        if not bgm_found:
            for ext in [".mp3", ".wav"]:
                bgm_path = os.path.join(get_base_path(), "audio", f"bgm{ext}")
                if os.path.exists(bgm_path):
                    pygame.mixer.music.load(bgm_path)
                    bgm_found = True
                    break

        if bgm_found:
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        else:
            print("警告：未找到背景音樂文件 (bgm.mp3 或 bgm.wav)")
    except Exception as e:
        print(f"無法播放背景音樂: {e}")
