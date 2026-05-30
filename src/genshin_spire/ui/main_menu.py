import pygame

from ..config import GOLD, WHITE
from ..resources import font_big, font_main
from ..save import has_savegame, get_savegame_mode, MODE_DISPLAY_NAMES, list_save_slots


def draw_main_menu_surface(surface, game, mx, my):
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    title_ts = font_big.render("Project: Genshin Spire", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.25)))

    buttons = [
        {"id": "START", "text": "開始遊戲"},
        {"id": "SETTINGS", "text": "遊戲設置"},
        {"id": "QUIT", "text": "退出遊戲"}
    ]
    if has_savegame():
        saved_mode = get_savegame_mode()
        if saved_mode:
            mode_name = MODE_DISPLAY_NAMES.get(saved_mode, saved_mode)
            buttons.insert(0, {"id": "CONTINUE", "text": f"繼續{mode_name}"})
        else:
            buttons.insert(0, {"id": "CONTINUE", "text": "繼續遊戲"})
    menu_rects = {}
    btn_start_y = h * 0.40
    btn_gap = 70 if len(buttons) >= 4 else 80
    for i, btn in enumerate(buttons):
        rect = pygame.Rect(w // 2 - 150, btn_start_y + i * btn_gap, 300, 50)
        menu_rects[btn["id"]] = rect
        is_hover = rect.collidepoint((mx, my))
        color = (100, 100, 150) if is_hover else (60, 60, 80)
        pygame.draw.rect(surface, color, rect, border_radius=8)
        if is_hover: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=8)
        text_ts = font_main.render(btn["text"], True, WHITE)
        surface.blit(text_ts, text_ts.get_rect(center=rect.center))
    
    deck_btn_w, deck_btn_h = 150 * ui_scale, 36 * ui_scale
    deck_btn_rect = pygame.Rect(w - deck_btn_w - 15 * ui_scale, 10 * ui_scale, deck_btn_w, deck_btn_h)
    is_deck_hover = deck_btn_rect.collidepoint((mx, my))
    deck_btn_color = (40, 60, 100) if is_deck_hover else (30, 45, 80)
    pygame.draw.rect(surface, deck_btn_color, deck_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD, deck_btn_rect, width=1, border_radius=int(8 * ui_scale))
    total_cards = len(game.deck) + len(game.hand) + len(game.discard)
    deck_ts = font_main.render(f"查看牌組 ({total_cards})", True, WHITE)
    surface.blit(deck_ts, deck_ts.get_rect(center=deck_btn_rect.center))
    menu_rects["DECK"] = deck_btn_rect

    guide_btn_w, guide_btn_h = 120 * ui_scale, 36 * ui_scale
    guide_btn_rect = pygame.Rect(deck_btn_rect.left - guide_btn_w - 10 * ui_scale, 10 * ui_scale, guide_btn_w, guide_btn_h)
    is_guide_hover = guide_btn_rect.collidepoint((mx, my))
    guide_btn_color = (60, 100, 60) if is_guide_hover else (40, 70, 40)
    pygame.draw.rect(surface, guide_btn_color, guide_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD if is_guide_hover else (140, 140, 160), guide_btn_rect, width=2, border_radius=int(8 * ui_scale))
    guide_ts = font_main.render("機制圖鑑", True, WHITE)
    surface.blit(guide_ts, guide_ts.get_rect(center=guide_btn_rect.center))
    menu_rects["GUIDE"] = guide_btn_rect

    # 統計數據小面板
    stats_y = int(h * 0.86)
    stats_bg = pygame.Surface((320, 90), pygame.SRCALPHA)
    stats_bg.fill((30, 30, 45, 180))
    surface.blit(stats_bg, (w // 2 - 160, stats_y))
    stats_lines = [
        f"最高波次: {game.stats_highest_wave}  |  總擊殺: {game.stats_total_kills}",
        f"總傷害: {game.stats_total_damage_dealt}  |  總受傷: {game.stats_total_damage_taken}",
        f"出牌數: {game.stats_total_cards_played}  |  回合數: {game.stats_total_turns}",
    ]
    for i, line in enumerate(stats_lines):
        line_ts = font_main.render(line, True, (180, 180, 180))
        surface.blit(line_ts, line_ts.get_rect(center=(w // 2, stats_y + 18 + i * 22)))

    # --- 存檔槽位選擇遮罩 ---
    slot_rects = {}
    if getattr(game, "show_slot_select", False):
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 200))
        surface.blit(dim, (0, 0))
        panel = pygame.Rect(w // 2 - 220, int(h * 0.25), 440, 320)
        pygame.draw.rect(surface, (32, 34, 52), panel, border_radius=14)
        pygame.draw.rect(surface, GOLD, panel, width=2, border_radius=14)
        title = font_big.render("選擇存檔槽位", True, GOLD)
        surface.blit(title, title.get_rect(center=(w // 2, panel.y + 40)))
        
        slots = list_save_slots()
        for i, slot in enumerate([1, 2, 3]):
            info = slots.get(slot, {"has_save": False})
            rect = pygame.Rect(w // 2 - 190, panel.y + 90 + i * 80, 380, 60)
            slot_rects[slot] = rect
            is_hover = rect.collidepoint((mx, my))
            if info["has_save"]:
                color = (60, 80, 60) if is_hover else (40, 60, 40)
                text = f"槽位 {slot}  —  {MODE_DISPLAY_NAMES.get(info['mode'], info['mode'])}  波次 {info['wave']}"
            else:
                color = (80, 80, 80) if is_hover else (50, 50, 50)
                text = f"槽位 {slot}  —  空"
            pygame.draw.rect(surface, color, rect, border_radius=8)
            if is_hover: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=8)
            ts = font_main.render(text, True, WHITE)
            surface.blit(ts, ts.get_rect(center=rect.center))
        
        back_rect = pygame.Rect(w // 2 - 60, panel.bottom - 50, 120, 36)
        slot_rects["BACK"] = back_rect
        back_hover = back_rect.collidepoint((mx, my))
        pygame.draw.rect(surface, (140, 60, 60) if back_hover else (100, 45, 45), back_rect, border_radius=6)
        back_ts = font_main.render("返回", True, WHITE)
        surface.blit(back_ts, back_ts.get_rect(center=back_rect.center))

    return menu_rects, slot_rects
