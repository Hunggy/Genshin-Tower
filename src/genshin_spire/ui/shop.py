import pygame
from ..config import GOLD, WHITE, RED, GREEN, ORANGE
from ..resources import font_main, font_hp, font_desc, font_big
from .common import draw_bar

GRAY = (128, 128, 128)
BRIGHT_GREEN = (100, 220, 100)


def draw_shop_surface(surface, game, mx, my):
    w, h = surface.get_size()

    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    title_ts = font_hp.render("商店", True, GOLD)
    surface.blit(title_ts, (w // 2 - title_ts.get_width() // 2, 20))

    gold_ts = font_main.render(f"金幣: {game.gold}", True, GOLD)
    surface.blit(gold_ts, (w // 2 - gold_ts.get_width() // 2, 52))

    card_rects = []
    if game.shop_mode is None:
        for i, item in enumerate(game.shop_cards):
            cx = w // 2 - 200 + i * 210
            cy = 130
            card_rect = pygame.Rect(cx, cy, 190, 260)
            mouse_hover = card_rect.collidepoint(mx, my)
            bg_color = (60, 60, 80) if not mouse_hover else (80, 80, 120)
            border_color = GOLD if mouse_hover else (100, 100, 120)
            pygame.draw.rect(surface, bg_color, card_rect, border_radius=8)
            pygame.draw.rect(surface, border_color, card_rect, 2, border_radius=8)

            card = item["card"]
            name_ts = font_hp.render(card.name, True, WHITE)
            surface.blit(name_ts, (cx + 10, cy + 10))

            if card.type == "ATTACK":
                type_ts = font_desc.render(f"攻擊  傷害:{card.damage}", True, RED)
            else:
                type_ts = font_desc.render(f"技能  護盾:{card.block}", True, GREEN)
            surface.blit(type_ts, (cx + 10, cy + 38))

            if card.custom_desc:
                desc_text = card.custom_desc.replace("{dmg}", str(card.damage)).replace("{blk}", str(card.block)).replace("{hits}", str(card.hits))
                desc_lines = desc_text.split("。")
                for j, line in enumerate(desc_lines[:3]):
                    desc_ts = font_desc.render(line, True, (180, 180, 180))
                    surface.blit(desc_ts, (cx + 10, cy + 62 + j * 18))

            price_ts = font_hp.render(f"{item['price']} G", True, GOLD)
            surface.blit(price_ts, (cx + 10, cy + 200))

            can_buy = game.gold >= item["price"]
            btn_color = BRIGHT_GREEN if can_buy and mouse_hover else (100, 100, 100)
            btn_rect = pygame.Rect(cx + 10, cy + 225, 170, 28)
            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=5)
            btn_text = font_desc.render("購買", True, WHITE if can_buy else GRAY)
            surface.blit(btn_text, (cx + 75, cy + 229))
            card_rects.append({"rect": btn_rect, "index": i, "card_rect": card_rect})

        remove_rect = pygame.Rect(w // 2 - 280, h - 180, 170, 40)
        mouse_hover_remove = remove_rect.collidepoint(mx, my)
        r_color = (180, 80, 80) if mouse_hover_remove else (120, 60, 60)
        can_remove = game.gold >= game.shop_remove_price and len(game.deck) > 5
        r_color = r_color if can_remove else (80, 80, 80)
        pygame.draw.rect(surface, r_color, remove_rect, border_radius=5)
        r_text = font_main.render(f"移除卡牌 ({game.shop_remove_price}G)", True, WHITE if can_remove else GRAY)
        surface.blit(r_text, (remove_rect.x + 10, remove_rect.y + 8))

        heal_rect = pygame.Rect(w // 2 - 80, h - 180, 170, 40)
        mouse_hover_heal = heal_rect.collidepoint(mx, my)
        h_color = (80, 120, 180) if mouse_hover_heal else (60, 80, 120)
        can_heal = game.gold >= game.shop_heal_price and game.player_hp < game.player_max_hp
        h_color = h_color if can_heal else (80, 80, 80)
        pygame.draw.rect(surface, h_color, heal_rect, border_radius=5)
        h_text = font_main.render(f"回復生命 ({game.shop_heal_price}G)", True, WHITE if can_heal else GRAY)
        surface.blit(h_text, (heal_rect.x + 10, heal_rect.y + 8))

        leave_rect = pygame.Rect(w // 2 + 120, h - 180, 140, 40)
        mouse_hover_leave = leave_rect.collidepoint(mx, my)
        l_color = (100, 100, 140) if mouse_hover_leave else (80, 80, 110)
        pygame.draw.rect(surface, l_color, leave_rect, border_radius=5)
        l_text = font_main.render("離開商店", True, WHITE)
        surface.blit(l_text, (leave_rect.x + 10, leave_rect.y + 8))

        hp_y = h - 120
        draw_bar(surface, w // 2 - 150, hp_y, game.player_hp, game.player_max_hp, 0, GREEN)
        hp_text = font_desc.render(f"HP: {game.player_hp}/{game.player_max_hp}", True, WHITE)
        surface.blit(hp_text, (w // 2 + 60, hp_y))

        return card_rects, remove_rect, heal_rect, leave_rect

    elif game.shop_mode == "REMOVE_CARD":
        prompt_ts = font_main.render("選擇要移除的卡牌 (點擊確認, 按 ESC 取消)", True, GOLD)
        surface.blit(prompt_ts, (w // 2 - prompt_ts.get_width() // 2, 110))

        remove_card_rects = []
        for i, card in enumerate(game.deck):
            row = i // 5
            col = i % 5
            cx = 80 + col * 200
            cy = 150 + row * 60
            card_rect = pygame.Rect(cx, cy, 190, 50)
            mouse_hover = card_rect.collidepoint(mx, my)
            bg = (100, 50, 50) if mouse_hover else (50, 50, 70)
            pygame.draw.rect(surface, bg, card_rect, border_radius=5)
            pygame.draw.rect(surface, RED if mouse_hover else (80, 80, 100), card_rect, 1, border_radius=5)
            name_ts = font_desc.render(card.name, True, WHITE)
            surface.blit(name_ts, (cx + 8, cy + 15))
            remove_card_rects.append({"rect": card_rect, "card": card})

        return remove_card_rects, None, None, None

    return card_rects, None, None, None
