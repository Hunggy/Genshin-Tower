import pygame

from ..config import GOLD, WHITE, GRAY, LIGHT_BG
from ..resources import font_big, font_hp, font_main, font_desc


def draw_mode_select_surface(surface, game, mx, my):
    w, h = surface.get_size()

    # 祝福選擇區域
    if game.primogem > 0:
        blessing_y = h * 0.05
        pg_ts = font_hp.render(f"原石: {game.primogem}", True, (200, 150, 255))
        surface.blit(pg_ts, (20, blessing_y))

        from ..battle import BLESSINGS
        blessing_rects = []
        for i, b in enumerate(BLESSINGS):
            bx = 20 + i * 190
            by = blessing_y + 28
            br = pygame.Rect(bx, by, 180, 50)
            blessing_rects.append({"rect": br, "blessing": b})
            is_hover = br.collidepoint((mx, my))
            can_afford = game.primogem >= b["cost"]
            bg = tuple(min(255, c + 30) if is_hover else c for c in b["color"]) if can_afford else (60, 60, 60)
            pygame.draw.rect(surface, bg, br, border_radius=5)
            name_ts = font_desc.render(f"{b['name']} ({b['cost']}原石)", True, WHITE if can_afford else GRAY)
            surface.blit(name_ts, (bx + 5, by + 5))
            desc_ts = font_desc.render(b["desc"], True, (180, 180, 180) if can_afford else (80, 80, 80))
            surface.blit(desc_ts, (bx + 5, by + 25))
    else:
        blessing_rects = []
        pg_ts = font_hp.render("原石: 0", True, GRAY)
        surface.blit(pg_ts, (20, h * 0.05))

    # 模式選擇
    title_ts = font_big.render("請選擇遊戲模式", True, GOLD)
    mode_y_start = h * 0.25 if game.primogem > 0 else h * 0.15
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, mode_y_start)))

    modes = [
        {"id": "TEST", "title": "測試模式", "desc": "快速測試：1輪10血敵人，直達結局", "color": (100, 100, 200)},
        {"id": "NORMAL", "title": "普通模式", "desc": "原汁原味的標準冒險體驗", "color": (100, 100, 100)},
        {"id": "BURST", "title": "無雙模式", "desc": "數值增加：初始能量變 4，卡牌傷害增加 5", "color": (50, 150, 50)},
        {"id": "HARD", "title": "高難模式", "desc": "數值增加：敵人血量增至 120，攻擊傷害增加 6", "color": (150, 50, 50)},
        {"id": "ENDLESS", "title": "無限模式", "desc": "挑戰極限：每 30 波一輪，難度不斷攀升", "color": (150, 150, 50)}
    ]
    btn_rects = {}
    for i, mode in enumerate(modes):
        rect = pygame.Rect(w // 2 - 300, mode_y_start + 40 + i * 105, 600, 85)
        btn_rects[mode["id"]] = rect
        is_hover = rect.collidepoint((mx, my))
        bg_color = [min(255, c + 30) if is_hover else c for c in mode["color"]]
        pygame.draw.rect(surface, bg_color, rect, border_radius=10)
        if is_hover: pygame.draw.rect(surface, GOLD, rect, width=3, border_radius=10)
        t_ts = font_hp.render(mode["title"], True, WHITE)
        d_ts = font_main.render(mode["desc"], True, (220, 220, 220))
        surface.blit(t_ts, (rect.x + 30, rect.y + 15))
        surface.blit(d_ts, (rect.x + 30, rect.y + 45))

    return btn_rects, blessing_rects
