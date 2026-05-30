import pygame

from ..config import GOLD, WHITE
from ..resources import font_big, font_main


def draw_discovery_screen_surface(surface, game, mx, my):
    """繪製每兩回合一次的靈光一閃界面"""
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    title_ts = font_big.render("靈光一閃！", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.25)))
    sub_ts = font_main.render("從牌組中額外挑選一張卡牌加入手牌", True, (200, 200, 200))
    surface.blit(sub_ts, sub_ts.get_rect(center=(w // 2, h * 0.32)))

    hovered_card = None
    for card in game.discovery_cards:
        if card.rect.collidepoint((mx, my)):
            hovered_card = card
            break

    num_cards = len(game.discovery_cards)
    spacing = 200 * ui_scale
    total_width = (num_cards - 1) * spacing
    start_x = w // 2 - total_width // 2
    
    center_y = h * 0.55
    
    for i, card in enumerate(game.discovery_cards):
        card.draw(surface, start_x + i * spacing, center_y, (card == hovered_card), show_marked=False)

    return hovered_card
