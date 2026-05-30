import pygame
import math

from .config import SCREEN_W, SCREEN_H, WHITE, RED, BLUE, GREEN
from .resources import get_ui_font
from .card import CARD_DATABASE  # type reference


class Animation:
    def __init__(self):
        self.active = False

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class FloatText(Animation):
    def __init__(self, x, y, text, color, size=28, duration=2.4):
        super().__init__()
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.alpha = 255
        self.active = True
        self.timer = 0
        self.duration = duration
        self.velocity = -42

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        self.y += self.velocity * dt
        fade_start = self.duration * 0.55
        if self.timer < fade_start:
            self.alpha = 255
        else:
            fade_t = (self.timer - fade_start) / max(0.01, self.duration - fade_start)
            self.alpha = max(0, 255 - int(fade_t * 255))
        if self.timer >= self.duration:
            self.active = False

    def draw(self, surface):
        if not self.active or self.alpha <= 0:
            return
        font = get_ui_font(self.size, bold=True)
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surf, rect)


class CardFly(Animation):
    def __init__(self, card, start_pos, end_pos, callback=None):
        super().__init__()
        self.card = card
        self.start_x, self.start_y = start_pos
        self.end_x, self.end_y = end_pos
        self.x, self.y = start_pos
        self.callback = callback
        self.active = True
        self.timer = 0
        self.duration = 0.3
        self.progress = 0

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        self.progress = min(1.0, self.timer / self.duration)
        t = self.progress
        ease = 1 - (1 - t) * (1 - t)
        self.x = self.start_x + (self.end_x - self.start_x) * ease
        self.y = self.start_y + (self.end_y - self.start_y) * ease
        if self.progress >= 1.0:
            self.active = False
            if self.callback:
                self.callback()

    def draw(self, surface):
        if not self.active:
            return
        self.card.draw(surface, int(self.x), int(self.y), False)


class FlashScreen(Animation):
    def __init__(self, color=(255, 0, 0), duration=0.2):
        super().__init__()
        self.color = color
        self.duration = duration
        self.timer = 0
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        if self.timer >= self.duration:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return
        alpha = int(100 * (1 - self.timer / self.duration))
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((*self.color, alpha))
        surface.blit(overlay, (0, 0))


class ShakeScreen(Animation):
    def __init__(self, intensity=10, duration=0.3):
        super().__init__()
        self.intensity = intensity
        self.duration = duration
        self.timer = 0
        self.active = True
        self.offset_x = 0
        self.offset_y = 0

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        if self.timer < self.duration:
            self.offset_x = math.sin(self.timer * 50) * self.intensity * (1 - self.timer / self.duration)
            self.offset_y = math.cos(self.timer * 50) * self.intensity * (1 - self.timer / self.duration)
        else:
            self.active = False
            self.offset_x = 0
            self.offset_y = 0

    def draw(self, surface):
        pass


class AnimationManager:
    FLOAT_LANE_LEFT = 250
    FLOAT_LANE_RIGHT = SCREEN_W - 400
    FLOAT_STACK_STEP = 34

    def __init__(self):
        self.animations = []
        self.screen_shake = None

    def add(self, anim):
        self.animations.append(anim)

    def _float_lane_x(self, x):
        return self.FLOAT_LANE_LEFT if x < SCREEN_W * 0.5 else self.FLOAT_LANE_RIGHT

    def _count_active_floats_in_lane(self, lane_x):
        return sum(
            1 for a in self.animations
            if isinstance(a, FloatText) and a.active and abs(a.x - lane_x) < 100
        )

    def add_float_text(self, x, y, text, color, size=26, duration=2.4):
        lane_x = self._float_lane_x(x)
        slot = self._count_active_floats_in_lane(lane_x)
        base_y = SCREEN_H * (0.34 if lane_x == self.FLOAT_LANE_LEFT else 0.30)
        stacked_y = base_y - slot * self.FLOAT_STACK_STEP
        self.add(FloatText(lane_x, stacked_y, text, color, size=size, duration=duration))

    def update(self, dt):
        for anim in self.animations[:]:
            anim.update(dt)
            if not anim.active:
                self.animations.remove(anim)
        if self.screen_shake:
            self.screen_shake.update(dt)

    def draw(self, surface):
        for anim in self.animations:
            anim.draw(surface)

    def shake_screen(self, intensity=10, duration=0.3):
        self.screen_shake = ShakeScreen(intensity, duration)

    def get_shake_offset(self):
        if self.screen_shake and self.screen_shake.active:
            return self.screen_shake.offset_x, self.screen_shake.offset_y
        return 0, 0

    def has_active_animations(self):
        return len(self.animations) > 0


FLOAT_ANIM_TYPES = frozenset({
    "damage_enemy", "block_player", "damage_player", "heal_player", "dot_damage",
    "true_damage", "status_enemy",
})
MAX_ANIMS_PER_FRAME = 6
MAX_FLOATS_PER_FRAME = 2


def _collapse_status_messages(game):
    """合併排隊中的連續狀態提示，避免一幀噴出過多紫字。"""
    if not game.anim_queue or game.anim_queue[0][0] != "status_enemy":
        return
    msgs = []
    while game.anim_queue and game.anim_queue[0][0] == "status_enemy":
        msgs.append(game.anim_queue.pop(0))
    if len(msgs) == 1:
        game.anim_queue.insert(0, msgs[0])
        return
    _, _, x, y = msgs[-1]
    if len(msgs) <= 2:
        text = " · ".join(m[1] for m in msgs)
    else:
        text = f"{msgs[-2][1]} · {msgs[-1][1]}"
    game.anim_queue.insert(0, ("status_enemy", text, x, y))


def process_animation_queue(game, anim_mgr, sound_mgr):
    _collapse_status_messages(game)
    processed = 0
    floats_added = 0
    while game.anim_queue and processed < MAX_ANIMS_PER_FRAME:
        if floats_added >= MAX_FLOATS_PER_FRAME:
            atype = game.anim_queue[0][0]
            if atype in FLOAT_ANIM_TYPES:
                break

        anim_data = game.anim_queue.pop(0)
        atype = anim_data[0]
        processed += 1

        if atype == "card_fly":
            _, card, sx, sy, tx, ty = anim_data
            anim_mgr.add(CardFly(card, (sx, sy), (tx, ty)))
        elif atype == "damage_enemy":
            _, dmg, x, y = anim_data
            sound_mgr.play("attack")
            if game.flash_enabled:
                anim_mgr.shake_screen(intensity=8, duration=0.2)
                anim_mgr.add(FlashScreen((255, 255, 255), 0.15))
            anim_mgr.add_float_text(x, y, f"-{dmg}", RED, size=32, duration=1.8)
            floats_added += 1
        elif atype == "block_player":
            _, blk, x, y = anim_data
            sound_mgr.play("shield")
            anim_mgr.add_float_text(x, y, f"+{blk} 護盾", BLUE, size=24)
            floats_added += 1
        elif atype == "damage_player":
            _, dmg, x, y = anim_data
            sound_mgr.play("hurt")
            if game.flash_enabled:
                anim_mgr.shake_screen(intensity=15, duration=0.3)
                anim_mgr.add(FlashScreen((220, 40, 40), 0.2))
            anim_mgr.add_float_text(x, y, f"-{dmg}", RED, size=32, duration=1.9)
            floats_added += 1
        elif atype == "heal_player":
            _, amt, x, y = anim_data
            anim_mgr.add_float_text(x, y, f"+{amt} 生命", GREEN, size=24)
            floats_added += 1
        elif atype == "dot_damage":
            _, dmg, x, y = anim_data
            anim_mgr.add_float_text(x, y, f"{dmg} 燃燒", (255, 100, 50), size=22)
            floats_added += 1
        elif atype == "true_damage":
            _, dmg, x, y = anim_data
            anim_mgr.add_float_text(x, y, f"-{dmg} 真傷", (255, 230, 120), size=26, duration=2.0)
            floats_added += 1
        elif atype == "status_enemy":
            _, msg, x, y = anim_data
            anim_mgr.add_float_text(x, y, msg, (200, 150, 255), size=24, duration=2.6)
            floats_added += 1
        elif atype == "enemy_death":
            sound_mgr.play("mage_death")
