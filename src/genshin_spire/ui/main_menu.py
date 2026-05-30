import pygame

from ..config import GOLD, WHITE
from ..resources import font_big, font_main
from ..save import get_savegame_mode, MODE_DISPLAY_NAMES


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
    saved_mode = get_savegame_mode()
    if saved_mode:
        mode_name = MODE_DISPLAY_NAMES.get(saved_mode, saved_mode)
        buttons.insert(0, {"id": "CONTINUE", "text": f"繼續{mode_name}"})
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

    return menu_rects
