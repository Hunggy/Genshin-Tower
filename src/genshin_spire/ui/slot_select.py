import pygame

from ..config import GOLD, WHITE
from ..resources import font_big, font_main
from ..save import list_save_slots, MODE_DISPLAY_NAMES


def draw_slot_select_overlay(surface, game, mx, my):
    """繪製存檔槽位選擇遮罩，返回槽位矩形字典 {1: rect, 2: rect, 3: rect, 'BACK': rect}"""
    w, h = surface.get_size()
    ui_scale = h / 720.0

    # 半透明遮罩
    dim = pygame.Surface((w, h), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 200))
    surface.blit(dim, (0, 0))

    panel_h = int(340 * ui_scale)
    panel = pygame.Rect(w // 2 - int(220 * ui_scale), int(h * 0.20), int(440 * ui_scale), panel_h)
    pygame.draw.rect(surface, (32, 34, 52), panel, border_radius=14)
    pygame.draw.rect(surface, GOLD, panel, width=2, border_radius=14)

    title = font_big.render("選擇存檔槽位", True, GOLD)
    surface.blit(title, title.get_rect(center=(w // 2, panel.y + int(35 * ui_scale))))

    slots = list_save_slots()
    slot_rects = {}
    item_h = int(55 * ui_scale)
    gap = int(12 * ui_scale)
    start_y = panel.y + int(75 * ui_scale)

    for i, slot in enumerate([1, 2, 3]):
        info = slots.get(slot, {"has_save": False})
        rect = pygame.Rect(
            w // 2 - int(190 * ui_scale),
            start_y + i * (item_h + gap),
            int(380 * ui_scale),
            item_h
        )
        slot_rects[slot] = rect
        is_hover = rect.collidepoint((mx, my))
        if info["has_save"]:
            color = (60, 80, 60) if is_hover else (40, 60, 40)
            mode_str = MODE_DISPLAY_NAMES.get(info.get("mode", "NORMAL"), info.get("mode", "NORMAL"))
            text = f"槽位 {slot}  —  {mode_str}  波次 {info.get('wave', 1)}"
        else:
            color = (80, 80, 80) if is_hover else (50, 50, 50)
            text = f"槽位 {slot}  —  空"
        pygame.draw.rect(surface, color, rect, border_radius=8)
        if is_hover:
            pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=8)
        ts = font_main.render(text, True, WHITE)
        surface.blit(ts, ts.get_rect(center=rect.center))

    # 返回按鈕
    back_rect = pygame.Rect(
        w // 2 - int(50 * ui_scale),
        panel.bottom - int(45 * ui_scale),
        int(100 * ui_scale),
        int(32 * ui_scale)
    )
    slot_rects["BACK"] = back_rect
    back_hover = back_rect.collidepoint((mx, my))
    pygame.draw.rect(surface, (140, 60, 60) if back_hover else (100, 45, 45), back_rect, border_radius=6)
    back_ts = font_main.render("返回", True, WHITE)
    surface.blit(back_ts, back_ts.get_rect(center=back_rect.center))

    return slot_rects
