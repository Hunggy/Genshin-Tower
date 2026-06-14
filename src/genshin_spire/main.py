import pygame
import sys
import os
import random
import math

from .config import (
    SCREEN_W, SCREEN_H,
    WHITE, BLACK, GOLD, GREEN, RED, BLUE, ORANGE,
    ELEMENT_COLORS, ELEMENT_COUNTERS,
    get_base_path, get_save_path,
    IS_WEB,
)
import genshin_spire.config as _cfg
from .resources import (
    load_background, get_ui_font,
    particles, element_icons,
    background_menu, background_battle, background_victory,
    kirby_image, energy_image, shield_image,
    character_images,
    font_main, font_desc, font_hp, font_big,
)
from .card import Card, CARD_DATABASE, CARD_NAME_TO_KEY, RELIC_DATABASE
from .animation import (
    Animation, FloatText, CardFly, FlashScreen, ShakeScreen,
    AnimationManager, process_animation_queue,
    FLOAT_ANIM_TYPES, MAX_ANIMS_PER_FRAME, MAX_FLOATS_PER_FRAME,
)
from .audio import SoundManager, play_bgm
from .save import (
    has_savegame, get_savegame_mode, save_game, load_game, delete_savegame,
)
from .battle import BattleManager
from .ui import (
    draw_main_menu_surface,
    draw_settings_surface,
    draw_mode_select_surface,
    draw_ui_surface,
    draw_reward_screen_surface,
    draw_discovery_screen_surface,
    draw_deck_view_surface,
    draw_upgrade_view_surface,
    draw_mechanics_guide_overlay,
    draw_slot_select_overlay,
)
from .ui.shop import draw_shop_surface


# --- Module-level initialization ---
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Project: Genshin Spire")

if IS_WEB:
    try:
        import platform as _plat
        if _plat.window.navigator.maxTouchPoints > 0:
            _cfg.IS_TOUCH = True
    except Exception:
        pass


import asyncio

async def main():
    global screen

    game = BattleManager()
    play_bgm(game.volume)

    anim_mgr = AnimationManager()
    sound_mgr = SoundManager()
    sound_mgr.set_volume(game.volume)

    clock = pygame.time.Clock()

    touch_finger = False
    touch_scroll_start_y = 0

    menu_rects = {}
    setting_rects = {}
    mode_rects = {}
    last_state = game.state

    game.running = True

    while game.running:
        dt = clock.tick(60) / 1000.0
        game.animation_tick += dt

        hovered = None
        hovered_reward = None
        hovered_discovery = None
        btn_rect = pygame.Rect(0,0,0,0)
        deck_btn_rect = pygame.Rect(0,0,0,0)
        confirm_rect = pygame.Rect(0,0,0,0)
        close_rect = pygame.Rect(0,0,0,0)
        mechanics_btn_rect = pygame.Rect(0, 0, 0, 0)
        guide_close_rect = pygame.Rect(0, 0, 0, 0)
        settings_btn_rect = pygame.Rect(0, 0, 0, 0)
        menu_rects = {}
        setting_rects = {}
        mode_rects = {}

        if game.state == "JUMP" and last_state != "JUMP":
            pygame.mixer.music.stop()
            sound_mgr.play("jump")
        elif game.state == "GAMEOVER" and last_state != "GAMEOVER":
            pygame.mixer.music.stop()
            sound_mgr.play("gta_death")
        elif game.state == "MAIN_MENU" and last_state in ["VICTORY", "GAMEOVER", "STARTUP"]:
            if not pygame.mixer.music.get_busy():
                play_bgm(game.volume, is_endless=game.is_endless)

        last_state = game.state

        process_animation_queue(game, anim_mgr, sound_mgr)
        anim_mgr.update(dt)

        mx, my = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        w, h = screen.get_size()
        ui_scale = h / 720.0

        if game.show_deck and game.is_dragging_deck_scroll:
            bar_y = h * 0.25
            bar_h = h * 0.7
            if bar_h > 0:
                rel_y = (my - bar_y) / bar_h
                game.deck_scroll = rel_y * game.max_deck_scroll
                game.deck_scroll = max(0, min(game.deck_scroll, game.max_deck_scroll))

        if game.state == "UPGRADE_CARD" and game.is_dragging_upgrade_scroll:
            bar_y = h * 0.25
            bar_h = h * 0.65
            if bar_h > 0:
                rel_y = (my - bar_y) / bar_h
                game.upgrade_scroll = rel_y * game.max_upgrade_scroll
                game.upgrade_scroll = max(0, min(game.upgrade_scroll, game.max_upgrade_scroll))

        shake_x, shake_y = anim_mgr.get_shake_offset()
        use_shake = (shake_x != 0 or shake_y != 0)

        for p in particles:
            p.update()

        current_bg = None
        if game.state in ["STARTUP", "MAIN_MENU", "SETTINGS", "MODE_SELECT"]:
            current_bg = background_menu
        elif game.state in ("BATTLE", "REWARD", "ENEMY_TURN", "SELECT_CARD", "DISCOVERY", "UPGRADE_CARD", "SHOP", "SETTLEMENT"):
            current_bg = background_battle
        elif game.state == "JUMP":
            current_bg = background_victory

        if use_shake:
            game_surface = pygame.Surface((w, h))
            if current_bg:
                game_surface.blit(current_bg, (0, 0))
            else:
                game_surface.fill((30, 30, 40))
            for p in particles:
                pygame.draw.circle(game_surface, (*p.color, p.alpha), (int(p.x), int(p.y)), p.size)
            main_surface = game_surface
        else:
            if current_bg:
                screen.blit(current_bg, (0, 0))
            else:
                screen.fill((30, 30, 40))
            for p in particles:
                pygame.draw.circle(screen, (*p.color, p.alpha), (int(p.x), int(p.y)), p.size)
            main_surface = screen

        if game.state == "STARTUP":
            if game.alpha < 255:
                game.alpha += 5
                if game.alpha > 255: game.alpha = 255
            else:
                if not IS_WEB:
                    pygame.time.delay(300)
                game.state = "MAIN_MENU"
            logo_ts = font_big.render("GENSHIN START", True, GOLD)
            logo_ts.set_alpha(game.alpha)
            main_surface.blit(logo_ts, logo_ts.get_rect(center=(w // 2, h // 2)))

        elif game.state == "MAIN_MENU":
            menu_rects = draw_main_menu_surface(main_surface, game, mx, my)
            if game.show_mechanics_guide:
                guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)

        elif game.state == "SETTINGS":
            setting_rects = draw_settings_surface(main_surface, game, mx, my, mouse_pressed)
            sound_mgr.set_volume(game.volume)

        elif game.state == "MODE_SELECT":
            mode_rects, blessing_rects = draw_mode_select_surface(main_surface, game, mx, my)

        elif game.state in ("BATTLE", "ENEMY_TURN"):
            if game.show_deck:
                back_rect, sort_rects = draw_deck_view_surface(main_surface, game, mx, my)
            elif game.show_mechanics_guide:
                guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
            else:
                hovered, btn_rect, deck_btn_rect, guide_btn_rect, settings_btn_rect = draw_ui_surface(main_surface, game, mx, my)

        elif game.state == "REWARD":
            hovered_reward, confirm_rect, guide_btn_rect, deck_btn_rect = draw_reward_screen_surface(main_surface, game, mx, my)

        elif game.state == "UPGRADE_CARD":
            close_rect, clicked_card, guide_btn_rect, deck_btn_rect = draw_upgrade_view_surface(main_surface, game, mx, my)

        elif game.state == "SHOP":
            shop_card_rects, remove_rect, heal_rect, leave_rect = draw_shop_surface(main_surface, game, mx, my)

        elif game.state == "SETTLEMENT":
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            main_surface.blit(overlay, (0, 0))
            title_ts = font_big.render("結算", True, GOLD)
            main_surface.blit(title_ts, (w // 2 - title_ts.get_width() // 2, 80))

            stats_items = [
                f"最高波次: {game.stats_highest_wave}",
                f"擊殺數: {game.stats_total_kills}",
                f"總傷害: {game.stats_total_damage_dealt}",
                f"承受傷害: {game.stats_total_damage_taken}",
                f"觸發反應: {game.stats_total_reactions}",
                f"打出卡牌: {game.stats_total_cards_played}",
                f"總回合數: {game.stats_total_turns}",
            ]
            for i, text in enumerate(stats_items):
                ts = font_main.render(text, True, WHITE)
                main_surface.blit(ts, (w // 2 - ts.get_width() // 2, 150 + i * 32))

            pg_ts = font_hp.render(f"獲得原石: {game.run_primogems_earned}", True, (200, 150, 255))
            main_surface.blit(pg_ts, (w // 2 - pg_ts.get_width() // 2, 400))

            total_ts = font_hp.render(f"原石總計: {game.primogem}", True, (200, 150, 255))
            main_surface.blit(total_ts, (w // 2 - total_ts.get_width() // 2, 430))

            hint_ts = font_desc.render("原石可在開始遊戲時購買祝福", True, (150, 150, 150))
            main_surface.blit(hint_ts, (w // 2 - hint_ts.get_width() // 2, 460))

            ok_rect = pygame.Rect(w // 2 - 80, 490, 160, 45)
            mouse_hover_ok = ok_rect.collidepoint(mx, my)
            ok_color = (80, 120, 80) if mouse_hover_ok else (60, 90, 60)
            pygame.draw.rect(main_surface, ok_color, ok_rect, border_radius=8)
            ok_ts = font_main.render("確定", True, WHITE)
            main_surface.blit(ok_ts, (ok_rect.x + ok_rect.width // 2 - ok_ts.get_width() // 2, ok_rect.y + 10))

        elif game.state == "SELECT_CARD":
            hovered, _, _, _, _ = draw_ui_surface(main_surface, game, mx, my)
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            main_surface.blit(overlay, (0, 0))

            prompt_text = "請點擊選擇一張手牌發動效果"
            if game.selection_mode == "TIME_STASIS":
                prompt_text = "【時空停滯】請選擇一張手牌變為 0 費"

            prompt_ts = font_big.render(prompt_text, True, GOLD)
            main_surface.blit(prompt_ts, prompt_ts.get_rect(center=(w // 2, h // 2)))

            cancel_ts = font_main.render("點擊右鍵取消選擇", True, WHITE)
            main_surface.blit(cancel_ts, cancel_ts.get_rect(center=(w // 2, h // 2 + 60)))

        elif game.state == "DISCOVERY":
            hovered_discovery = draw_discovery_screen_surface(main_surface, game, mx, my)

        elif game.state == "JUMP":
            game.jump_progress += dt * 0.4
            if game.jump_progress >= 1.0:
                game.state = "VICTORY"
            else:
                jw, jh = kirby_image.get_size() if kirby_image else (60, 60)
                jx = w // 2 - jw // 2
                jy = h * 0.3 + h * 0.5 * game.jump_progress
                if kirby_image:
                    main_surface.blit(kirby_image, (jx, int(jy)))

        elif game.state == "VICTORY":
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            main_surface.blit(overlay, (0, 0))
            ts = font_big.render("勝利！", True, GOLD)
            main_surface.blit(ts, ts.get_rect(center=(w // 2, h // 2)))
            hint = font_main.render("點擊任意處繼續", True, WHITE)
            main_surface.blit(hint, hint.get_rect(center=(w // 2, h // 2 + 60)))

        elif game.state == "GAMEOVER":
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            main_surface.blit(overlay, (0, 0))
            ts = font_big.render("遊戲結束", True, RED)
            main_surface.blit(ts, ts.get_rect(center=(w // 2, h // 2)))
            hint = font_main.render("點擊任意處繼續", True, WHITE)
            main_surface.blit(hint, hint.get_rect(center=(w // 2, h // 2 + 60)))

        if getattr(game, 'show_slot_select', False):
            slot_rects = draw_slot_select_overlay(main_surface, game, mx, my)
        else:
            slot_rects = {}

        anim_mgr.draw(main_surface)

        if use_shake:
            screen.fill((30, 30, 40))
            screen.blit(game_surface, (int(shake_x), int(shake_y)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if game.state in ("BATTLE", "ENEMY_TURN"):
                    save_game(game)
                if IS_WEB:
                    game.running = False
                else:
                    pygame.quit()
                    sys.exit()

            # --- 觸屏事件 ---
            if _cfg.IS_TOUCH and event.type == pygame.FINGERDOWN:
                fx, fy = event.x * w, event.y * h
                mx, my = int(fx), int(fy)
                touch_finger = True
                touch_scroll_start_y = fy

            if _cfg.IS_TOUCH and event.type == pygame.FINGERUP:
                touch_finger = False

            if _cfg.IS_TOUCH and event.type == pygame.FINGERMOTION:
                if touch_finger:
                    fy = event.y * h
                    dy = fy - touch_scroll_start_y
                    if abs(dy) > 5:
                        if game.show_deck:
                            game.deck_scroll -= dy * 0.5
                        elif game.show_mechanics_guide:
                            game.mechanics_scroll -= dy * 0.5
                        elif game.state == "UPGRADE_CARD":
                            game.upgrade_scroll -= dy * 0.5
                        touch_scroll_start_y = fy

            # --- 鍵盤事件 ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.show_mechanics_guide:
                        game.show_mechanics_guide = False
                        game.mechanics_scroll = 0
                    elif game.state == "SHOP" and game.shop_mode == "REMOVE_CARD":
                        game.shop_mode = None
                    elif game.state == "MODE_SELECT":
                        game.state = "MAIN_MENU"
                    elif game.state == "BATTLE":
                        game.state = "SETTINGS"
                        game.previous_battle_state = "BATTLE"
                elif event.key == pygame.K_d and game.state in ("BATTLE", "REWARD", "UPGRADE_CARD") and not game.show_mechanics_guide:
                    game.show_deck = not game.show_deck
                elif event.key == pygame.K_m and game.state in ("BATTLE", "REWARD", "UPGRADE_CARD"):
                    game.show_mechanics_guide = not game.show_mechanics_guide
                    if not game.show_mechanics_guide:
                        game.mechanics_scroll = 0
                elif event.key == pygame.K_l and game.state in ("BATTLE", "ENEMY_TURN"):
                    game.show_battle_log = not game.show_battle_log
                elif event.key in (pygame.K_TAB, pygame.K_SPACE) and game.state == "BATTLE" and not game.show_deck and not game.show_mechanics_guide:
                    game.end_turn()
                elif event.key == pygame.K_q and game.state == "BATTLE" and not game.show_deck and not game.show_mechanics_guide:
                    game.switch_target(-1)
                elif event.key == pygame.K_e and game.state == "BATTLE" and not game.show_deck and not game.show_mechanics_guide:
                    game.switch_target(1)
                elif event.key in (pygame.K_w, pygame.K_UP):
                    if game.show_deck:
                        game.deck_scroll -= 40
                    elif game.show_mechanics_guide:
                        game.mechanics_scroll -= 28
                    elif game.state == "UPGRADE_CARD":
                        game.upgrade_scroll -= 40
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    if game.show_deck:
                        game.deck_scroll += 40
                    elif game.show_mechanics_guide:
                        game.mechanics_scroll += 28
                    elif game.state == "UPGRADE_CARD":
                        game.upgrade_scroll += 40
                elif pygame.K_1 <= event.key <= pygame.K_7 and game.state == "BATTLE" and not game.show_deck and not game.show_mechanics_guide:
                    idx = event.key - pygame.K_1
                    if idx < len(game.hand):
                        card = game.hand[idx]
                        if game.energy >= card.cost:
                            game.play_card(card, card.rect.x, card.rect.y)

            if event.type == pygame.MOUSEWHEEL:
                if game.show_mechanics_guide:
                    game.mechanics_scroll -= event.y * 28
                elif game.show_deck:
                    game.deck_scroll -= event.y * 40
                elif game.state == "UPGRADE_CARD":
                    game.upgrade_scroll -= event.y * 40

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    game.is_dragging_deck_scroll = False
                    game.is_dragging_upgrade_scroll = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if getattr(game, "show_slot_select", False):
                        if slot_rects.get("BACK") and slot_rects["BACK"].collidepoint((mx, my)):
                            game.show_slot_select = False
                        else:
                            for slot, rect in slot_rects.items():
                                if isinstance(slot, int) and rect.collidepoint((mx, my)):
                                    game.current_save_slot = slot
                                    action = getattr(game, "slot_select_action", "LOAD")
                                    if action == "LOAD":
                                        if load_game(game, slot):
                                            game.state = "BATTLE"
                                            game.previous_battle_state = None
                                    elif action == "SAVE":
                                        save_game(game, slot)
                                        game.state = "MAIN_MENU"
                                        game.previous_battle_state = None
                                        game.show_deck = False
                                    game.show_slot_select = False
                                    break
                    elif game.state == "MAIN_MENU":
                        if game.show_mechanics_guide:
                            guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
                            if guide_close_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = False
                                game.mechanics_scroll = 0
                        elif menu_rects.get("CONTINUE") and menu_rects["CONTINUE"].collidepoint((mx, my)):
                            game.show_slot_select = True
                            game.slot_select_action = "LOAD"
                        elif menu_rects.get("START") and menu_rects["START"].collidepoint((mx, my)):
                            game.reset_game()
                            game.state = "MODE_SELECT"
                        elif menu_rects.get("SETTINGS") and menu_rects["SETTINGS"].collidepoint((mx, my)):
                            game.state = "SETTINGS"
                        elif menu_rects.get("QUIT") and menu_rects["QUIT"].collidepoint((mx, my)):
                            if IS_WEB:
                                game.running = False
                            else:
                                pygame.quit()
                                sys.exit()
                        elif menu_rects.get("GUIDE") and menu_rects["GUIDE"].collidepoint((mx, my)):
                            game.show_mechanics_guide = True
                            game.mechanics_scroll = 0

                    elif game.state == "SETTINGS":
                        if setting_rects.get("BACK") and setting_rects["BACK"][0].collidepoint((mx, my)):
                            if game.previous_battle_state == "BATTLE":
                                game.state = "BATTLE"
                                game.previous_battle_state = None
                            else:
                                game.state = "MAIN_MENU"
                        elif setting_rects.get("SAVE") and setting_rects["SAVE"][0].collidepoint((mx, my)):
                            game.show_slot_select = True
                            game.slot_select_action = "SAVE"
                        elif setting_rects.get("QUIT_BATTLE") and setting_rects["QUIT_BATTLE"][0].collidepoint((mx, my)):
                            delete_savegame(game.current_save_slot)
                            game.state = "MAIN_MENU"
                            game.previous_battle_state = None
                            game.reset_game()
                        else:
                            for res_id, (rect, val1, val2) in setting_rects.items():
                                if res_id == "BACK": continue
                                if rect.collidepoint((mx, my)):
                                    if res_id == "FS_ON":
                                        if not IS_WEB:
                                            game.fullscreen = True
                                            screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
                                    elif res_id == "FS_OFF":
                                        game.fullscreen = False
                                        screen = pygame.display.set_mode((w, h))
                                    elif res_id == "FLASH_ON":
                                        game.flash_enabled = True
                                    elif res_id == "FLASH_OFF":
                                        game.flash_enabled = False
                                    elif res_id.startswith("CHAR_"):
                                        game.current_character = val1
                                    elif res_id.startswith("RES_"):
                                        if not IS_WEB:
                                            flags = pygame.FULLSCREEN if game.fullscreen else 0
                                            screen = pygame.display.set_mode((val1, val2), flags)
                                    break

                    elif game.state == "MODE_SELECT":
                        for item in blessing_rects:
                            if item["rect"].collidepoint((mx, my)):
                                b = item["blessing"]
                                cost = item["cost"]
                                bought = item["bought"]
                                if bought < b["max_count"] and game.primogem >= cost:
                                    game.primogem -= cost
                                    game.blessing_counts[b["id"]] = bought + 1
                                    if b["apply"]:
                                        b["apply"](game)
                                break
                        else:
                            for mode_id, rect in mode_rects.items():
                                if rect.collidepoint((mx, my)):
                                    game.apply_mode_modifiers(mode_id)
                                    break

                    elif game.state in ("BATTLE", "ENEMY_TURN"):
                        if game.show_deck:
                            back_rect, sort_rects = draw_deck_view_surface(main_surface, game, mx, my)
                            if back_rect.collidepoint((mx, my)):
                                game.show_deck = False
                            else:
                                for sort_id, rect in sort_rects.items():
                                    if rect.collidepoint((mx, my)):
                                        game.deck_sort_mode = sort_id
                                        game.deck_scroll = 0
                                        break
                                if mx > w - 40 * ui_scale:
                                    game.is_dragging_deck_scroll = True
                        elif game.show_mechanics_guide:
                            guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
                            if guide_close_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = False
                                game.mechanics_scroll = 0
                        else:
                            _, temp_btn_rect, temp_deck_btn_rect, temp_guide_btn_rect, temp_settings_btn_rect = draw_ui_surface(main_surface, game, mx, my)

                            if temp_deck_btn_rect.collidepoint((mx, my)):
                                game.show_deck = True
                                game.deck_scroll = 0
                            elif temp_guide_btn_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = True
                                game.mechanics_scroll = 0
                            elif temp_settings_btn_rect.collidepoint((mx, my)):
                                game.previous_battle_state = "BATTLE"
                                game.state = "SETTINGS"
                            elif game.state == "BATTLE":
                                if hovered:
                                    game.play_card(hovered, hovered.rect.x, hovered.rect.y)
                                elif temp_btn_rect.collidepoint((mx, my)):
                                    game.end_turn()
                                else:
                                    wave_enemies = getattr(game, "wave_enemies", [])
                                    if len(wave_enemies) > 1:
                                        ey = int(h * 0.32)
                                        living = [(i, e) for i, e in enumerate(wave_enemies) if e["hp"] > 0]
                                        slot_w = 200
                                        total_w = len(living) * slot_w
                                        start_x = w - 480 - total_w // 2 + slot_w // 2 - 60
                                        for idx_in_living, (i, e_data) in enumerate(living):
                                            cx = start_x + idx_in_living * slot_w
                                            enemy_rect = pygame.Rect(cx - 5, ey - 5, 130, 185)
                                            if enemy_rect.collidepoint((mx, my)):
                                                game.target_index = i
                                                game.refresh_target_mark()
                                                break

                    elif game.state == "REWARD":
                        hovered_reward, confirm_rect, guide_btn_rect, deck_btn_rect = draw_reward_screen_surface(main_surface, game, mx, my)
                        if game.show_mechanics_guide:
                            guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
                            if guide_close_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = False
                                game.mechanics_scroll = 0
                        elif guide_btn_rect.collidepoint((mx, my)):
                            game.show_mechanics_guide = True
                            game.mechanics_scroll = 0
                        elif deck_btn_rect.collidepoint((mx, my)):
                            game.show_deck = True
                            game.deck_scroll = 0
                        elif hovered_reward:
                            game.selected_reward = hovered_reward
                        elif confirm_rect.collidepoint((mx, my)):
                            game.choose_reward()

                    elif game.state == "UPGRADE_CARD":
                        close_rect, clicked_card, guide_btn_rect, deck_btn_rect = draw_upgrade_view_surface(main_surface, game, mx, my)

                        if game.show_mechanics_guide:
                            guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
                            if guide_close_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = False
                                game.mechanics_scroll = 0
                        elif guide_btn_rect.collidepoint((mx, my)):
                            game.show_mechanics_guide = True
                            game.mechanics_scroll = 0
                        elif deck_btn_rect.collidepoint((mx, my)):
                            game.show_deck = True
                            game.deck_scroll = 0
                        elif mx > w - 40 * ui_scale:
                            game.is_dragging_upgrade_scroll = True

                        if clicked_card and not clicked_card.upgraded:
                            clicked_card.upgrade()
                            game._sync_power_entry_for_card(clicked_card)
                            game.pending_upgrade = False
                            game.choose_reward()
                        elif close_rect.collidepoint((mx, my)):
                            game.pending_upgrade = False
                            game.choose_reward()

                    elif game.state == "SHOP":
                        shop_card_rects, remove_rect, heal_rect, leave_rect = draw_shop_surface(main_surface, game, mx, my)
                        if game.shop_mode == "REMOVE_CARD":
                            for item in shop_card_rects:
                                if item["rect"].collidepoint((mx, my)):
                                    game.shop_remove_confirm(item["card"])
                                    break
                        elif game.shop_mode is None:
                            for item in shop_card_rects:
                                if item["rect"].collidepoint((mx, my)):
                                    game.shop_buy_card(item["index"])
                                    break
                            if remove_rect and remove_rect.collidepoint((mx, my)):
                                game.shop_remove_card()
                            elif heal_rect and heal_rect.collidepoint((mx, my)):
                                game.shop_heal()
                            elif leave_rect and leave_rect.collidepoint((mx, my)):
                                game.shop_leave()

                    elif game.state == "SETTLEMENT":
                        ok_rect = pygame.Rect(w // 2 - 80, 490, 160, 45)
                        if ok_rect.collidepoint((mx, my)):
                            game.state = "MAIN_MENU"

                    elif game.state == "DISCOVERY":
                        if hovered_discovery:
                            if len(game.hand) < game.max_hand:
                                game.hand.append(hovered_discovery)
                                game.anim_queue.append(("status_enemy", f"獲得 {hovered_discovery.name}", 640, 360))
                            else:
                                game.discard.append(hovered_discovery)
                                game.anim_queue.append(("status_enemy", "手牌已滿，加入棄牌堆", 640, 360))

                            game.discovery_selected.append(hovered_discovery)
                            game.discovery_cards.remove(hovered_discovery)

                            if len(game.discovery_selected) >= game.discovery_select_count:
                                game.deck.extend(game.discovery_cards)
                                game.discovery_cards.clear()
                                game.discovery_selected.clear()
                                random.shuffle(game.deck)
                                game.state = "BATTLE"
                                game.refresh_target_mark()

                    elif game.state == "SELECT_CARD":
                        if hovered and hovered != game.selection_source_card:
                            if game.selection_mode == "TIME_STASIS":
                                hovered.cost = 0
                                game.modified_cards.append(hovered)
                                game.anim_queue.append(("status_enemy", f"{hovered.name} 變為 0 費", 250, SCREEN_H - 350))
                                game.finish_card_play(game.selection_source_card, SCREEN_W // 2, SCREEN_H // 2)

                            elif game.selection_mode == "FATE_GAMBLE":
                                game.selected_cards.append(hovered)
                                game.hand.remove(hovered)
                                if not getattr(hovered, 'is_temporary', False):
                                    game.discard.append(hovered)
                                game.anim_queue.append(("status_enemy", f"已選擇 {len(game.selected_cards)}/4 張", 250, SCREEN_H - 350))

                                if len(game.selected_cards) >= 4 or len(game.hand) == 0:
                                    game.draw_cards(4)
                                    game.selected_cards.clear()
                                    game.selection_mode = None
                                    game.state = "BATTLE"

                            if game.selection_mode != "FATE_GAMBLE":
                                game.selection_mode = None
                                game.selection_source_card = None
                                game.state = "BATTLE"

                    elif game.state in ["VICTORY", "GAMEOVER"]:
                        if game.state == "GAMEOVER":
                            delete_savegame(game.current_save_slot)
                        game.reset_game()
                        sound_mgr.set_volume(game.volume)

                elif event.button == 3:
                    if game.state == "SELECT_CARD":
                        if game.selection_mode == "FATE_GAMBLE":
                            game.anim_queue.append(("status_enemy", "無法取消！", 250, SCREEN_H - 350))
                            continue
                        game.energy += game.selection_source_card.cost
                        game.selection_mode = None
                        game.selection_source_card = None
                        game.state = "BATTLE"
                        game.anim_queue.append(("status_enemy", "已取消選擇", 250, SCREEN_H - 350))

        await asyncio.sleep(0)
