import pygame

from ..config import GOLD, WHITE
from ..resources import font_big, font_hp, font_main, font_desc, character_images


def draw_settings_surface(surface, game, mx, my, mouse_pressed):
    w, h = surface.get_size()
    title_ts = font_big.render("遊戲設置", True, WHITE)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.1)))

    vol_label = font_hp.render(f"音樂音量: {int(game.volume * 100)}%", True, (200, 200, 200))
    surface.blit(vol_label, (w // 2 - 250, h * 0.22))

    track_rect = pygame.Rect(w // 2 - 80, int(h * 0.23), 250, 10)
    click_area = track_rect.inflate(0, 30)

    if mouse_pressed and click_area.collidepoint((mx, my)):
        relative_x = mx - track_rect.x
        game.volume = max(0.0, min(1.0, relative_x / track_rect.width))
        pygame.mixer.music.set_volume(game.volume)

    pygame.draw.rect(surface, (100, 100, 100), track_rect, border_radius=5)
    fill_width = int(track_rect.width * game.volume)
    fill_rect = pygame.Rect(track_rect.x, track_rect.y, fill_width, track_rect.height)
    pygame.draw.rect(surface, GOLD, fill_rect, border_radius=5)

    knob_x = track_rect.x + fill_width
    knob_y = track_rect.centery
    knob_radius = 12 if click_area.collidepoint((mx, my)) else 10
    knob_color = WHITE if not mouse_pressed else (200, 200, 200)
    pygame.draw.circle(surface, knob_color, (knob_x, knob_y), knob_radius)

    label_ts = font_hp.render("調整解析度：", True, (200, 200, 200))
    surface.blit(label_ts, (w // 2 - 250, h * 0.32))

    res_options = [
        {"id": "RES_1280", "text": "1280 x 720", "w": 1280, "h": 720},
        {"id": "RES_1600", "text": "1600 x 900", "w": 1600, "h": 900}
    ]
    setting_rects = {}
    for i, opt in enumerate(res_options):
        rect = pygame.Rect(w // 2 - 80 + i * 140, h * 0.30, 120, 45)
        setting_rects[opt["id"]] = (rect, opt["w"], opt["h"])
        is_current = (w == opt["w"])
        is_hover = rect.collidepoint((mx, my))
        color = (50, 150, 50) if is_current else ((100, 100, 120) if is_hover else (50, 50, 60))
        pygame.draw.rect(surface, color, rect, border_radius=5)
        if is_hover or is_current: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=5)
        txt = font_main.render(opt["text"], True, WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))

    fs_label_ts = font_hp.render("顯示模式：", True, (200, 200, 200))
    surface.blit(fs_label_ts, (w // 2 - 250, h * 0.42))
    
    fs_options = [
        {"id": "FS_OFF", "text": "視窗模式", "val": False},
        {"id": "FS_ON", "text": "全螢幕", "val": True}
    ]
    for i, opt in enumerate(fs_options):
        rect = pygame.Rect(w // 2 - 80 + i * 140, h * 0.40, 120, 45)
        setting_rects[opt["id"]] = (rect, opt["val"], 0)
        is_current = (game.fullscreen == opt["val"])
        is_hover = rect.collidepoint((mx, my))
        color = (50, 150, 50) if is_current else ((100, 100, 120) if is_hover else (50, 50, 60))
        pygame.draw.rect(surface, color, rect, border_radius=5)
        if is_hover or is_current: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=5)
        txt = font_main.render(opt["text"], True, WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))

    flash_label_ts = font_hp.render("特效閃爍：", True, (200, 200, 200))
    surface.blit(flash_label_ts, (w // 2 - 250, h * 0.52))
    
    flash_options = [
        {"id": "FLASH_ON", "text": "開啟特效", "val": True},
        {"id": "FLASH_OFF", "text": "關閉特效", "val": False}
    ]
    for i, opt in enumerate(flash_options):
        rect = pygame.Rect(w // 2 - 80 + i * 140, h * 0.50, 120, 45)
        setting_rects[opt["id"]] = (rect, opt["val"], 0)
        is_current = (game.flash_enabled == opt["val"])
        is_hover = rect.collidepoint((mx, my))
        color = (50, 150, 50) if is_current else ((100, 100, 120) if is_hover else (50, 50, 60))
        pygame.draw.rect(surface, color, rect, border_radius=5)
        if is_hover or is_current: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=5)
        txt = font_main.render(opt["text"], True, WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))

    char_label_ts = font_hp.render("更換主角：", True, (200, 200, 200))
    surface.blit(char_label_ts, (w // 2 - 250, h * 0.65))
    
    char_names = list(character_images.keys())
    for i, char_name in enumerate(char_names):
        row = i // 3
        col = i % 3
        rect = pygame.Rect(w // 2 - 80 + col * 140, h * 0.63 + row * 65, 120, 60)
        setting_rects[f"CHAR_{char_name}"] = (rect, char_name, 0)
        is_current = (game.current_character == char_name)
        is_hover = rect.collidepoint((mx, my))
        color = (50, 150, 50) if is_current else ((100, 100, 120) if is_hover else (50, 50, 60))
        pygame.draw.rect(surface, color, rect, border_radius=5)
        if is_hover or is_current: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=5)
        
        frames = character_images.get(char_name)
        if frames and len(frames) > 0:
            small_img = pygame.transform.scale(frames[0], (30, 30))
            surface.blit(small_img, (rect.x + 5, rect.y + 15))
            
        display_name = char_name[:8] + ".." if len(char_name) > 8 else char_name
        txt = font_desc.render(display_name, True, WHITE)
        surface.blit(txt, (rect.x + 40, rect.y + 22))

    if game.previous_battle_state == "BATTLE":
        back_rect = pygame.Rect(w // 2 - 320, h * 0.85, 180, 50)
        save_rect = pygame.Rect(w // 2 - 125, h * 0.85, 250, 50)
        quit_rect = pygame.Rect(w // 2 + 140, h * 0.85, 180, 50)
        setting_rects["BACK"] = (back_rect, 0, 0)
        setting_rects["SAVE"] = (save_rect, 0, 0)
        setting_rects["QUIT_BATTLE"] = (quit_rect, 0, 0)

        is_back_hover = back_rect.collidepoint((mx, my))
        pygame.draw.rect(surface, (50, 150, 50) if is_back_hover else (40, 100, 40), back_rect, border_radius=8)
        back_ts = font_main.render("返回戰鬥", True, WHITE)
        surface.blit(back_ts, back_ts.get_rect(center=back_rect.center))

        is_save_hover = save_rect.collidepoint((mx, my))
        pygame.draw.rect(surface, (50, 100, 150) if is_save_hover else (35, 70, 110), save_rect, border_radius=8)
        save_ts = font_main.render("保存並退出", True, WHITE)
        surface.blit(save_ts, save_ts.get_rect(center=save_rect.center))

        is_quit_hover = quit_rect.collidepoint((mx, my))
        pygame.draw.rect(surface, (150, 50, 50) if is_quit_hover else (100, 40, 40), quit_rect, border_radius=8)
        quit_ts = font_main.render("退出對局", True, WHITE)
        surface.blit(quit_ts, quit_ts.get_rect(center=quit_rect.center))
    else:
        back_rect = pygame.Rect(w // 2 - 100, h * 0.85, 200, 50)
        setting_rects["BACK"] = (back_rect, 0, 0)
        is_back_hover = back_rect.collidepoint((mx, my))
        pygame.draw.rect(surface, (150, 50, 50) if is_back_hover else (100, 40, 40), back_rect, border_radius=8)
        back_ts = font_main.render("返回主選單", True, WHITE)
        surface.blit(back_ts, back_ts.get_rect(center=back_rect.center))

    return setting_rects
