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
)
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


# --- Module-level initialization (mirrors original file top level) ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Project: Genshin Spire")


def main():
    global screen

    game = BattleManager()
    play_bgm(game.volume)

    anim_mgr = AnimationManager()
    sound_mgr = SoundManager()
    sound_mgr.set_volume(game.volume)
    
    clock = pygame.time.Clock()

    menu_rects = {}
    setting_rects = {}
    mode_rects = {}
    last_state = game.state

    while True:
        dt = clock.tick(60) / 1000.0
        game.animation_tick += dt
        
        # 初始化 UI 變量，防止跨狀態衝突
        hovered = None
        hovered_reward = None
        hovered_discovery = None
        btn_rect = pygame.Rect(0,0,0,0)
        deck_btn_rect = pygame.Rect(0,0,0,0)
        confirm_rect = pygame.Rect(0,0,0,0)
        close_rect = pygame.Rect(0,0,0,0)
        mechanics_btn_rect = pygame.Rect(0, 0, 0, 0)
        guide_close_rect = pygame.Rect(0, 0, 0, 0)
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

        # 更新牌組滾動拖拽
        if game.show_deck and game.is_dragging_deck_scroll:
            bar_y = h * 0.25
            bar_h = h * 0.7
            if bar_h > 0:
                rel_y = (my - bar_y) / bar_h
                game.deck_scroll = rel_y * game.max_deck_scroll
                game.deck_scroll = max(0, min(game.deck_scroll, game.max_deck_scroll))
        
        # 更新強化界面滾動拖拽
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
        elif game.state in ("BATTLE", "REWARD", "ENEMY_TURN", "SELECT_CARD", "DISCOVERY", "UPGRADE_CARD"):
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
                pygame.time.delay(300)
                game.state = "MAIN_MENU"
            logo_ts = font_big.render("GENSHIN START", True, GOLD)
            logo_ts.set_alpha(game.alpha)
            main_surface.blit(logo_ts, logo_ts.get_rect(center=(w // 2, h // 2)))

        elif game.state == "MAIN_MENU":
            menu_rects = draw_main_menu_surface(main_surface, game, mx, my)
            # 在主選單也要繪製機制圖 (如果打開的話)
            if game.show_mechanics_guide:
                guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)

        elif game.state == "SETTINGS":
            setting_rects = draw_settings_surface(main_surface, game, mx, my, mouse_pressed)
            sound_mgr.set_volume(game.volume)

        elif game.state == "MODE_SELECT":
            mode_rects = draw_mode_select_surface(main_surface, mx, my)

        elif game.state in ("BATTLE", "ENEMY_TURN"):
            if game.show_deck:
                back_rect, sort_rects = draw_deck_view_surface(main_surface, game, mx, my)
            elif game.show_mechanics_guide:
                guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
            else:
                hovered, btn_rect, deck_btn_rect, guide_btn_rect = draw_ui_surface(main_surface, game, mx, my)

        elif game.state == "REWARD":
            hovered_reward, confirm_rect, guide_btn_rect, deck_btn_rect = draw_reward_screen_surface(main_surface, game, mx, my)

        elif game.state == "UPGRADE_CARD":
            close_rect, clicked_card, guide_btn_rect, deck_btn_rect = draw_upgrade_view_surface(main_surface, game, mx, my)

        elif game.state == "SELECT_CARD":
            hovered, _, _, _ = draw_ui_surface(main_surface, game, mx, my)
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
            # 繪製靈光一閃界面
            hovered_discovery = draw_discovery_screen_surface(main_surface, game, mx, my)

        elif game.state == "JUMP":
            game.jump_progress += dt * 0.4
            
            player_x = w // 2
            player_y = h * 0.65
            
            scale = max(0, 1.0 - game.jump_progress)
            player_size = int(80 * scale)
            
            if kirby_image and player_size > 0:
                scaled_kirby = pygame.transform.scale(kirby_image, (player_size, player_size))
                kirby_x = player_x - player_size // 2
                kirby_y = player_y - player_size // 2
                main_surface.blit(scaled_kirby, (kirby_x, kirby_y))
            elif player_size > 0:
                pygame.draw.circle(main_surface, (255, 150, 180), (player_x, player_y), int(25 * scale))
            
            for i in range(40):
                angle = (i / 40) * 360
                distance = 50 + game.jump_progress * 200 + random.randint(-20, 20)
                px = player_x + math.cos(math.radians(angle)) * distance
                py = player_y + math.sin(math.radians(angle)) * distance
                alpha = max(0, 200 - int(game.jump_progress * 250))
                size = max(2, 6 - int(game.jump_progress * 8))
                pygame.draw.circle(main_surface, (255, 180, 200, alpha), (int(px), int(py)), size)
            
            fade_alpha = int(255 * min(1, game.jump_progress * 1.5))
            if fade_alpha > 0:
                overlay = pygame.Surface((w, h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, fade_alpha))
                main_surface.blit(overlay, (0, 0))
            
            if game.jump_progress >= 1.0:
                game.state = "VICTORY"

        elif game.state in ["VICTORY", "GAMEOVER"]:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            main_surface.blit(overlay, (0, 0))
            msg = "恭喜通關！(30層達成)" if game.state == "VICTORY" else "YOU DIED"
            msg_ts = font_big.render(msg, True, GOLD if game.state == "VICTORY" else RED)
            main_surface.blit(msg_ts, msg_ts.get_rect(center=(w // 2, h // 2 - 30)))
            hint_ts = font_main.render("點擊滑鼠左鍵返回主選單", True, WHITE)
            main_surface.blit(hint_ts, hint_ts.get_rect(center=(w // 2, h // 2 + 50)))

        anim_mgr.draw(main_surface)

        if game.show_mechanics_guide:
            guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)

        # --- 全局存檔槽位選擇遮罩 ---
        slot_rects = {}
        if getattr(game, "show_slot_select", False):
            slot_rects = draw_slot_select_overlay(main_surface, game, mx, my)

        if use_shake:
            screen.fill((30, 30, 40))
            screen.blit(game_surface, (int(shake_x), int(shake_y)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 自動存檔：若在戰鬥中，儲存後再退出
                if game.state in ("BATTLE", "ENEMY_TURN"):
                    save_game(game)
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.show_mechanics_guide:
                        game.show_mechanics_guide = False
                        game.mechanics_scroll = 0
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
                    # 在任何狀態下，存檔槽位選擇遮罩打開時優先處理
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
                            # 保存並退出：先選槽位，存檔後返回主選單
                            game.show_slot_select = True
                            game.slot_select_action = "SAVE"
                        elif setting_rects.get("QUIT_BATTLE") and setting_rects["QUIT_BATTLE"][0].collidepoint((mx, my)):
                            # 退出對局：清除當前槽位存檔並返回主選單，保留設置
                            delete_savegame(game.current_save_slot)
                            game.state = "MAIN_MENU"
                            game.previous_battle_state = None
                            game.reset_game()
                        else:
                            for res_id, (rect, val1, val2) in setting_rects.items():
                                if res_id == "BACK": continue
                                if rect.collidepoint((mx, my)):
                                    if res_id == "FS_ON":
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
                                        flags = pygame.FULLSCREEN if game.fullscreen else 0
                                        screen = pygame.display.set_mode((val1, val2), flags)
                                    break

                    elif game.state == "MODE_SELECT":
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
                                        game.deck_scroll = 0 # 切換排序時重置滾動
                                        break
                            # 檢查是否點擊滾動條區域 (右側 30 像素寬)
                            if mx > w - 40 * ui_scale:
                                game.is_dragging_deck_scroll = True
                        elif game.show_mechanics_guide:
                            guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
                            if guide_close_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = False
                                game.mechanics_scroll = 0
                        else:
                            # 確保獲取最新的按鈕區域
                            _, temp_btn_rect, temp_deck_btn_rect, temp_guide_btn_rect = draw_ui_surface(main_surface, game, mx, my)
                            
                            if temp_deck_btn_rect.collidepoint((mx, my)):
                                game.show_deck = True
                                game.deck_scroll = 0
                            elif temp_guide_btn_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = True
                                game.mechanics_scroll = 0
                            elif game.state == "BATTLE":
                                # 僅在玩家回合允許出牌和結束回合
                                if hovered:
                                    game.play_card(hovered, hovered.rect.x, hovered.rect.y)
                                elif temp_btn_rect.collidepoint((mx, my)):
                                    game.end_turn()

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
                        # 檢查是否點擊滾動條區域
                        elif mx > w - 40 * ui_scale:
                            game.is_dragging_upgrade_scroll = True
                        
                        if clicked_card and not clicked_card.upgraded:
                            clicked_card.upgrade()
                            game._sync_power_entry_for_card(clicked_card)
                            game.pending_upgrade = False
                            game.current_wave += 1
                            if game.current_wave > game.max_waves:
                                game.state = "VICTORY"
                            else:
                                game.start_next_wave()
                        elif close_rect.collidepoint((mx, my)):
                            game.pending_upgrade = False
                            game.current_wave += 1
                            if game.current_wave > game.max_waves:
                                game.state = "VICTORY"
                            else:
                                game.start_next_wave()

                    elif game.state == "DISCOVERY":
                        if hovered_discovery:
                            # 靈光一閃獲得的卡牌不受普通手牌上限 5 的限制（只要不超過總上限 10）
                            if len(game.hand) < game.max_hand:
                                game.hand.append(hovered_discovery)
                                game.anim_queue.append(("status_enemy", f"獲得 {hovered_discovery.name}", 640, 360))
                            else:
                                game.discard.append(hovered_discovery)
                                game.anim_queue.append(("status_enemy", "手牌已滿，加入棄牌堆", 640, 360))
                            
                            game.discovery_selected.append(hovered_discovery)
                            game.discovery_cards.remove(hovered_discovery)
                            
                            # 检查是否已经选够数量
                            if len(game.discovery_selected) >= game.discovery_select_count:
                                # 其他卡牌放回牌組並洗牌
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
                                # 命运豪赌升级版本：自选4张手牌丢弃
                                game.selected_cards.append(hovered)
                                game.hand.remove(hovered)
                                # === 修改这里：临时牌不进入弃牌堆 ===
                                if not getattr(hovered, 'is_temporary', False):
                                    game.discard.append(hovered)
                                game.anim_queue.append(("status_enemy", f"已選擇 {len(game.selected_cards)}/4 張", 250, SCREEN_H - 350))
                                
                                if len(game.selected_cards) >= 4 or len(game.hand) == 0:
                                    # 选够4张或手牌已空，抽4张牌
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
                        # === 修改這裡：防止命運豪賭被右鍵取消導致崩潰 ===
                        if game.selection_mode == "FATE_GAMBLE":
                            game.anim_queue.append(("status_enemy", "無法取消！", 250, SCREEN_H - 350))
                            continue
                        # ==========================================
                        game.energy += game.selection_source_card.cost
                        game.selection_mode = None
                        game.selection_source_card = None
                        game.state = "BATTLE"
                        game.anim_queue.append(("status_enemy", "已取消選擇", 250, SCREEN_H - 350))
