import pygame

from ..config import GOLD, WHITE
from ..resources import font_big, font_main, font_hp, font_desc


def draw_reward_screen_surface(surface, game, mx, my):
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    title_ts = font_big.render("戰鬥勝利！", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.15)))
    sub_ts = font_main.render("請選擇一項獎勵", True, (200, 200, 200))
    surface.blit(sub_ts, sub_ts.get_rect(center=(w // 2, h * 0.22)))

    hovered_reward = None
    for card in game.reward_cards:
        if card.rect.collidepoint((mx, my)):
            hovered_reward = card
            break

    num_rewards = len(game.reward_cards)
    spacing = 180 * ui_scale
    total_width = (num_rewards - 1) * spacing
    start_x = w // 2 - total_width // 2
    
    center_y = h * 0.5
    
    for i, card in enumerate(game.reward_cards):
        card.draw(surface, start_x + i * spacing, center_y, (card == hovered_reward), (card == game.selected_reward))

    if game.pending_relic:
        relic = game.pending_relic
        relic_rect = pygame.Rect(w // 2 - 150 * ui_scale, h * 0.75, 300 * ui_scale, 60 * ui_scale)
        pygame.draw.rect(surface, (50, 50, 70), relic_rect, border_radius=int(10 * ui_scale))
        pygame.draw.rect(surface, GOLD, relic_rect, width=2, border_radius=int(10 * ui_scale))
        
        pygame.draw.circle(surface, relic["color"], (int(w // 2 - 110 * ui_scale), int(h * 0.78)), int(20 * ui_scale))
        
        r_name_ts = font_hp.render(f"額外獲得：{relic['name']}", True, WHITE)
        r_desc_ts = font_desc.render(relic["desc"], True, (200, 200, 200))
        surface.blit(r_name_ts, (w // 2 - 80 * ui_scale, h * 0.755))
        surface.blit(r_desc_ts, (w // 2 - 80 * ui_scale, h * 0.785))

    confirm_rect = pygame.Rect(w // 2 - 100 * ui_scale, h * 0.88, 200 * ui_scale, 50 * ui_scale)
    btn_color = (50, 180, 50) if game.selected_reward else (60, 60, 60)
    pygame.draw.rect(surface, btn_color, confirm_rect, border_radius=int(5 * ui_scale))
    btn_text = font_main.render("點擊跳過" if not game.selected_reward else "確認領取", True, WHITE)
    surface.blit(btn_text, btn_text.get_rect(center=confirm_rect.center))

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

    return hovered_reward, confirm_rect, guide_btn_rect, deck_btn_rect
