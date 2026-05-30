import pygame

from ..config import WHITE, BLUE
from ..resources import font_hp, font_big, shield_image


def wrap_text_lines(text, font, max_width):
    lines = []
    current = ""
    for char in text:
        if char == "\n":
            if current:
                lines.append(current)
            lines.append("")
            current = ""
            continue
        test = current + char
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def draw_bar(surface, x, y, cur, mx, block, color):
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    width = 250 * ui_scale
    height = 15 * ui_scale
    pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))
    if mx > 0:
        pygame.draw.rect(surface, color, (x, y, int((cur / mx) * width), height))
    if block > 0:
        shield_w = 30 * ui_scale
        shield_h = 34 * ui_scale
        cx = x - 22 * ui_scale
        cy = y + 8 * ui_scale
        if shield_image:
            img = pygame.transform.smoothscale(shield_image, (int(shield_w), int(shield_h)))
            surface.blit(img, (cx - shield_w // 2, cy - shield_h // 2))
        else:
            shield_points = [
                (cx, cy - shield_h // 2),
                (cx + shield_w // 2, cy - shield_h // 2 + 6 * ui_scale),
                (cx + shield_w // 2, cy + shield_h // 4),
                (cx, cy + shield_h // 2),
                (cx - shield_w // 2, cy + shield_h // 4),
                (cx - shield_w // 2, cy - shield_h // 2 + 6 * ui_scale),
            ]
            pygame.draw.polygon(surface, BLUE, shield_points)
            pygame.draw.polygon(surface, (150, 180, 255), shield_points, width=2)
        b_ts = font_hp.render(str(block), True, WHITE)
        surface.blit(b_ts, b_ts.get_rect(center=(cx, cy)))
    val_ts = font_hp.render(f"{cur}/{mx}", True, WHITE)
    surface.blit(val_ts, (x + width // 2 - val_ts.get_width() // 2, y - 25 * ui_scale))


def draw_pile(surface, x, y, count, label, color):
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    pygame.draw.rect(surface, (40, 40, 50), (x - 25 * ui_scale, y - 60 * ui_scale, 50 * ui_scale, 70 * ui_scale), border_radius=int(4 * ui_scale))
    for i in range(min(count, 5)):
        offset = i * 3 * ui_scale
        pygame.draw.rect(surface, color, (x - 22 * ui_scale + offset * 0.5, y - 57 * ui_scale + offset, 44 * ui_scale - offset, 64 * ui_scale - offset),
                         border_radius=int(3 * ui_scale))
    count_ts = font_big.render(str(count), True, WHITE)
    surface.blit(count_ts, (x - count_ts.get_width() // 2, y - 25 * ui_scale))
    label_ts = font_hp.render(label, True, (180, 180, 180))
    surface.blit(label_ts, (x - label_ts.get_width() // 2, y + 10 * ui_scale))


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
