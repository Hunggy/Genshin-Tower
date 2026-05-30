import pygame

from ..config import GOLD, WHITE
from ..resources import font_big, font_hp, font_main, font_desc


def draw_upgrade_view_surface(surface, game, mx, my):
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 230))
    surface.blit(overlay, (0, 0))

    all_cards = sorted(
        game.owned_cards,
        key=lambda c: (c.name, c.upgraded),
    )
    num_cards = len(all_cards)
    max_per_row = 6 
    card_spacing_x = 200 * ui_scale
    card_spacing_y = 280 * ui_scale
    
    start_y_base = h * 0.35
    clip_rect = pygame.Rect(0, h * 0.18, w, h * 0.65)
    
    num_rows = (num_cards + max_per_row - 1) // max_per_row
    content_h = num_rows * card_spacing_y + 100 * ui_scale
    game.max_upgrade_scroll = max(0, content_h - clip_rect.height)
    game.upgrade_scroll = max(0, min(game.upgrade_scroll, game.max_upgrade_scroll))
    
    cols_in_row = min(num_cards, max_per_row)
    total_grid_w = (cols_in_row - 1) * card_spacing_x
    start_x = w // 2 - total_grid_w // 2
    
    hovered_card = None
    for index, card in enumerate(all_cards):
        row = index // max_per_row
        col = index % max_per_row
        card_x = start_x + col * card_spacing_x
        card_y = start_y_base + row * card_spacing_y - game.upgrade_scroll
        
        if clip_rect.top - 200 * ui_scale < card_y < clip_rect.bottom + 200 * ui_scale:
            is_hover = card.rect.collidepoint((mx, my)) and clip_rect.collidepoint((mx, my))
            card.draw(surface, card_x, card_y, is_hover, is_selected=card.upgraded, show_marked=False)
            if is_hover: hovered_card = card
            
            if card.upgraded:
                s_w, s_h = int(165 * ui_scale), int(235 * ui_scale)
                s = pygame.Surface((s_w, s_h), pygame.SRCALPHA)
                s.fill((0, 0, 0, 150))
                surface.blit(s, (card_x - s_w // 2, card_y - s_h // 2))
                up_ts = font_hp.render("MAX", True, GOLD)
                surface.blit(up_ts, up_ts.get_rect(center=(card_x, card_y)))
            elif card in game.sidelined_power_cards:
                act_ts = font_desc.render("本輪生效", True, (120, 255, 160))
                surface.blit(act_ts, act_ts.get_rect(center=(card_x, card_y + 90 * ui_scale)))

    title_ts = font_big.render("【精英/BOSS 獎勵】從已獲得牌組中選一張升級", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.06)))

    close_rect = pygame.Rect(w // 2 - 100 * ui_scale, int(h * 0.13), 200 * ui_scale, 40 * ui_scale)
    is_hover_close = close_rect.collidepoint((mx, my))
    pygame.draw.rect(surface, (100, 100, 100) if is_hover_close else (60, 60, 60), close_rect, border_radius=int(5 * ui_scale))
    close_ts = font_main.render("跳過升級", True, WHITE)
    surface.blit(close_ts, close_ts.get_rect(center=close_rect.center))
    
    if game.max_upgrade_scroll > 0:
        bar_w = 10 * ui_scale
        bar_h = clip_rect.height
        bar_x = w - 25 * ui_scale
        bar_y = clip_rect.y
        pygame.draw.rect(surface, (30, 30, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=int(5 * ui_scale))
        thumb_h = max(40 * ui_scale, (clip_rect.height / content_h) * bar_h)
        thumb_y = bar_y + (game.upgrade_scroll / game.max_upgrade_scroll) * (bar_h - thumb_h)
        t_color = (200, 200, 200) if game.is_dragging_upgrade_scroll else (120, 120, 120)
        pygame.draw.rect(surface, t_color, (bar_x + 1, thumb_y, bar_w - 2, thumb_h), border_radius=int(4 * ui_scale))
        
    deck_btn_w, deck_btn_h = 150 * ui_scale, 36 * ui_scale
    deck_btn_rect = pygame.Rect(w - deck_btn_w - 15 * ui_scale, 10 * ui_scale, deck_btn_w, deck_btn_h)
    is_deck_hover = deck_btn_rect.collidepoint((mx, my))
    deck_btn_color = (40, 60, 100) if is_deck_hover else (30, 45, 80)
    pygame.draw.rect(surface, deck_btn_color, deck_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD, deck_btn_rect, width=1, border_radius=int(8 * ui_scale))
    total_cards = len(game.deck) + len(game.hand) + len(game.discard)
    deck_ts = font_main.render(f"查看牌組 ({total_cards})", True, WHITE)
    surface.blit(deck_ts, deck_ts.get_rect(center=deck_btn_rect.center))

    guide_btn_w, guide_btn_h = 120 * ui_scale, 36 * ui_scale
    guide_btn_rect = pygame.Rect(deck_btn_rect.left - guide_btn_w - 10 * ui_scale, 10 * ui_scale, guide_btn_w, guide_btn_h)
    is_guide_hover = guide_btn_rect.collidepoint((mx, my))
    guide_btn_color = (60, 100, 60) if is_guide_hover else (40, 70, 40)
    pygame.draw.rect(surface, guide_btn_color, guide_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD if is_guide_hover else (140, 140, 160), guide_btn_rect, width=2, border_radius=int(8 * ui_scale))
    guide_ts = font_main.render("機制圖鑑", True, WHITE)
    surface.blit(guide_ts, guide_ts.get_rect(center=guide_btn_rect.center))

    return close_rect, hovered_card, guide_btn_rect, deck_btn_rect
