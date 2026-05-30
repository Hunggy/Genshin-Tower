import pygame

from ..config import GOLD, WHITE
from ..resources import font_main, font_hp, font_desc


def draw_deck_view_surface(surface, game, mx, my):
    w, h = surface.get_size()
    ui_scale = h / 720.0

    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    surface.blit(overlay, (0, 0))

    type_order = {"ATTACK": 0, "SKILL": 1, "POWER": 2}
    pool = (
        game.owned_cards
        + [c for c in game.sidelined_power_cards if c not in game.owned_cards]
    )
    if game.deck_sort_mode == "TYPE":
        all_cards = sorted(
            pool,
            key=lambda c: (type_order.get(c.type, 3), c.cost, c.name),
        )
    else:
        all_cards = sorted(
            pool,
            key=lambda c: (c.cost, type_order.get(c.type, 3), c.name),
        )

    max_per_row = 5
    card_spacing_x = 220 * ui_scale
    card_spacing_y = 280 * ui_scale
    start_y_base = h * 0.35
    
    clip_rect = pygame.Rect(0, h * 0.18, w, h * 0.65)
    
    num_rows = (len(all_cards) + max_per_row - 1) // max_per_row
    content_h = num_rows * card_spacing_y + 150 * ui_scale
    game.max_deck_scroll = max(0, content_h - (h * 0.7))
    game.deck_scroll = max(0, min(game.deck_scroll, game.max_deck_scroll))
    
    start_x = w // 2 - ((min(len(all_cards), max_per_row) - 1) * card_spacing_x) // 2
    
    hovered_in_deck = None
    for idx, card in enumerate(all_cards):
        row = idx // max_per_row
        col = idx % max_per_row
        x = start_x + col * card_spacing_x
        y = start_y_base + row * card_spacing_y - game.deck_scroll
        
        if clip_rect.top - 100 * ui_scale < y < clip_rect.bottom + 100 * ui_scale:
            is_hover = card.rect.collidepoint((mx, my)) and clip_rect.collidepoint((mx, my))
            card.draw(surface, x, y, is_hover, show_marked=False)
            if is_hover: hovered_in_deck = card

    sort_bar_y = h * 0.08
    sort_bar_h = 45 * ui_scale
    pygame.draw.rect(surface, (20, 40, 60), (0, sort_bar_y, w, sort_bar_h))
    pygame.draw.line(surface, GOLD, (0, sort_bar_y), (w, sort_bar_y), 2)
    pygame.draw.line(surface, GOLD, (0, sort_bar_y + sort_bar_h), (w, sort_bar_y + sort_bar_h), 2)

    sort_options = [
        {"id": "TYPE", "text": "按類型 ▲", "x": w * 0.4},
        {"id": "COST", "text": "按能量 ▲", "x": w * 0.6}
    ]
    
    sort_rects = {}
    for opt in sort_options:
        txt_color = GOLD if game.deck_sort_mode == opt["id"] else WHITE
        ts = font_main.render(opt["text"], True, txt_color)
        rect = ts.get_rect(center=(opt["x"], sort_bar_y + sort_bar_h // 2))
        if rect.collidepoint((mx, my)):
            pygame.draw.rect(surface, (255, 255, 255, 30), rect.inflate(20, 10), border_radius=5)
        surface.blit(ts, rect)
        sort_rects[opt["id"]] = rect

    back_rect = pygame.Rect(40 * ui_scale, h - 90 * ui_scale, 160 * ui_scale, 50 * ui_scale)
    is_back_hover = back_rect.collidepoint((mx, my))
    back_color = (140, 40, 40) if is_back_hover else (100, 30, 30)
    pygame.draw.rect(surface, back_color, back_rect, border_radius=int(10 * ui_scale))
    pygame.draw.rect(surface, GOLD, back_rect, width=2, border_radius=int(10 * ui_scale))
    back_ts = font_hp.render("返回", True, WHITE)
    surface.blit(back_ts, back_ts.get_rect(center=back_rect.center))

    bottom_hint = f"這些卡牌將會出現在每一場戰鬥中。 (總卡數: {len(all_cards)})"
    hint_ts = font_main.render(bottom_hint, True, (180, 180, 180))
    surface.blit(hint_ts, hint_ts.get_rect(center=(w // 2, h - 65 * ui_scale)))

    if game.max_deck_scroll > 0:
        bar_w = 8 * ui_scale
        bar_h = h * 0.5 
        bar_x = w - 30 * ui_scale
        bar_y = h * 0.25
        
        pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=int(4 * ui_scale))
        
        thumb_h = max(30 * ui_scale, (bar_h / content_h) * bar_h)
        thumb_y = bar_y + (game.deck_scroll / game.max_deck_scroll) * (bar_h - thumb_h)
        t_color = (180, 180, 180) if game.is_dragging_deck_scroll else (100, 100, 100)
        pygame.draw.rect(surface, t_color, (bar_x, thumb_y, bar_w, thumb_h), border_radius=int(4 * ui_scale))

    return back_rect, sort_rects
