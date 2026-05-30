import math
import pygame

from ..config import GOLD, WHITE, RED, BLUE, GREEN, ORANGE, ELEMENT_COLORS, ELEMENT_COUNTERS
from ..resources import font_main, font_hp, font_desc, font_big, character_images, energy_image, kirby_image
from .common import draw_bar, draw_pile


def draw_ui_surface(surface, game, mx, my):
    w, h = surface.get_size()

    mode_text = "普通" if game.selected_mode == "NORMAL" else (
        "無雙 (傷害+5, 能量+1)" if game.selected_mode == "BURST" else (
            "無限模式" if game.selected_mode == "ENDLESS" else "高難 (怪物強化)"))
    mode_ts = font_main.render(f"當前模式: {mode_text}", True, (180, 180, 180))
    surface.blit(mode_ts, (20, 20))

    wave_str = f"波次: {game.current_wave} / {game.max_waves}"
    if game.is_endless:
        wave_str = f"無限模式 [第 {game.endless_loop_count} 輪] - {wave_str}"
    wave_ts = font_main.render(wave_str, True, GOLD)
    surface.blit(wave_ts, (20, 50))

    if game.enemy_hp > 0:
        enemy_rect = pygame.Rect(w - 430, h * 0.35, 120, 120)
        if game.enemy_image:
            img_x = w - 430 + (120 - game.enemy_image.get_width()) // 2
            img_y = int(h * 0.35) + (120 - game.enemy_image.get_height()) // 2
            surface.blit(game.enemy_image, (img_x, img_y))
        else:
            pygame.draw.rect(surface, (150, 50, 50), enemy_rect, border_radius=10)
            if kirby_image:
                flipped_kirby = pygame.transform.flip(pygame.transform.scale(kirby_image, (100, 100)), True, False)
                surface.blit(flipped_kirby, (w - 420, h * 0.36))
        
        type_color = GOLD if game.stage_type in ["BOSS", "FINAL_BOSS"] else (ORANGE if game.stage_type == "ELITE" else WHITE)
        name_ts = font_hp.render(game.enemy_name, True, type_color)
        surface.blit(name_ts, (w - 480, h * 0.18))
        if game.enemy_stance_enabled:
            buff_ts = font_desc.render("[特殊·節奏大師]", True, GOLD)
            surface.blit(buff_ts, (w - 480, h * 0.205))
        
        hp_y = h * 0.28
        if game.enemy_stance_enabled:
            hp_y = h * 0.34
        draw_bar(surface, w - 480, hp_y, game.enemy_hp, game.enemy_max_hp, 0, RED)
        
        # 敵人意圖顏色編碼：低傷=綠，中傷=黃，高傷=紅
        intent_ratio = game.enemy_intent / max(1, game.player_max_hp)
        if intent_ratio <= 0.15:
            intent_color = GREEN
        elif intent_ratio <= 0.30:
            intent_color = (255, 200, 0)
        else:
            intent_color = RED
        intent_ts = font_main.render(f"意圖攻擊: {game.enemy_intent}", True, intent_color)
        surface.blit(intent_ts, (w - 460, h * 0.22))

        if game.enemy_stance_enabled:
            stance_color = RED if game.enemy_stance == "ATTACK" else BLUE
            status_line = game.get_stance_status_text()
            if status_line:
                cur_ts = font_hp.render(status_line, True, stance_color)
                surface.blit(cur_ts, (w - 480, h * 0.255))
            preview_line = game.get_stance_preview_text()
            if preview_line:
                prev_ts = font_main.render(preview_line, True, GOLD)
                surface.blit(prev_ts, (w - 480, h * 0.295))

        status_y = h * 0.52
        status_spacing = 25
        
        if game.enemy_stun_turns > 0:
            stun_ts = font_desc.render(f"[暈眩] {game.enemy_stun_turns}回合", True, (255, 200, 100))
            surface.blit(stun_ts, (w - 430, status_y))
            status_y += status_spacing
        
        if game.enemy_petrify_turns > 0:
            pet_ts = font_desc.render(f"[石化] {game.enemy_petrify_turns}回合", True, (150, 150, 150))
            surface.blit(pet_ts, (w - 430, status_y))
            status_y += status_spacing
        
        if game.enemy_frozen_turns > 0:
            froz_ts = font_desc.render(f"[凍結] {game.enemy_frozen_turns}回合", True, (100, 200, 255))
            surface.blit(froz_ts, (w - 430, status_y))
            status_y += status_spacing
            
        if game.enemy_wet:
            wet_turns = getattr(game, 'enemy_wet_turns', 0)
            wet_str = f"[潮濕] {wet_turns}回合" if wet_turns > 0 else "[潮濕]"
            wet_ts = font_desc.render(wet_str, True, (50, 150, 255))
            surface.blit(wet_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.bloom_cores > 0:
            bloom_ts = font_desc.render(f"[草原核] x{game.bloom_cores}", True, (50, 200, 100))
            surface.blit(bloom_ts, (w - 430, status_y))
            status_y += status_spacing
            
        if game.enemy_dot_turns > 0:
            dot_ts = font_desc.render(f"[燃燒] {game.enemy_dot_damage}x{game.enemy_dot_turns}", True, (255, 100, 50))
            surface.blit(dot_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.enemy_vulnerable_turns > 0:
            vul_ts = font_desc.render(f"[易傷] {game.enemy_vulnerable_turns}回合", True, (255, 150, 150))
            surface.blit(vul_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.enemy_poison_turns > 0:
            poi_ts = font_desc.render(f"[中毒] {game.enemy_poison_turns}層", True, (150, 255, 150))
            surface.blit(poi_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.cards_played_this_turn > 0:
            combo_ts = font_desc.render(f"本回合連擊: {game.cards_played_this_turn}", True, (200, 255, 200))
            surface.blit(combo_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.reactions_this_turn > 0:
            reac_ts = font_desc.render(f"本回合反應: {game.reactions_this_turn}/3", True, (100, 255, 255))
            surface.blit(reac_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.enemy_hit_shield > 0:
            elem_name_map = {"Pyro": "火", "Hydro": "水", "Cryo": "冰", "Dendro": "草", "Electro": "雷", "Geo": "岩", "None": "次數"}
            elem_text = elem_name_map.get(game.enemy_shield_element, "未知")
            shield_color = ELEMENT_COLORS.get(game.enemy_shield_element, (200, 200, 255))
            shield_ts = font_desc.render(f"[{elem_text}元素盾] {game.enemy_hit_shield}層", True, shield_color)
            surface.blit(shield_ts, (w - 430, status_y))
            
            counters = ELEMENT_COUNTERS.get(game.enemy_shield_element, [])
            if counters:
                hint_map = {"Pyro": "火", "Hydro": "水", "Cryo": "冰", "Dendro": "草", "Electro": "雷", "Geo": "岩", "None": "物理"}
                hint_text = " / ".join([hint_map.get(c, c) for c in counters])
                hint_ts = font_desc.render(f"  (弱點: {hint_text})", True, (200, 200, 200))
                surface.blit(hint_ts, (w - 430, status_y + 20))
                status_y += 20
            
            status_y += status_spacing
            
        if game.enemy_charge_turns > 0:
            charge_color = RED if game.enemy_charge_turns == game.enemy_charge_max else GOLD
            charge_ts = font_desc.render(f"[大招蓄力] {game.enemy_charge_turns}/{game.enemy_charge_max}", True, charge_color)
            surface.blit(charge_ts, (w - 430, status_y))
            status_y += status_spacing
            
        if game.enemy_thorns > 0:
            thorn_ts = font_desc.render(f"[反傷外殼] {game.enemy_thorns}", True, (255, 100, 100))
            surface.blit(thorn_ts, (w - 430, status_y))
            status_y += status_spacing
            
        if game.enemy_scaling_strength > 0:
            scale_ts = font_desc.render(f"[力量成長] +{game.enemy_scaling_strength}/回合", True, (255, 150, 100))
            surface.blit(scale_ts, (w - 430, status_y))
            status_y += status_spacing

    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    frames = character_images.get(game.current_character)
    if frames:
        frame_idx = int(game.animation_tick * 10) % len(frames)
        char_img = frames[frame_idx]
        
        if ui_scale != 1.0:
            char_w, char_h = char_img.get_size()
            char_img = pygame.transform.smoothscale(char_img, (int(char_w * ui_scale), int(char_h * ui_scale)))
            
        float_y = math.sin(game.animation_tick * 3) * 5 * ui_scale
        char_x = 100 * ui_scale
        char_y = h - (320 * ui_scale) + float_y
        surface.blit(char_img, (char_x, char_y))
    else:
        pygame.draw.circle(surface, (200, 200, 200), (int(160 * ui_scale), h - int(250 * ui_scale)), int(40 * ui_scale))
    
    if energy_image:
        img_size = int(80 * ui_scale)
        scaled_energy = pygame.transform.smoothscale(energy_image, (img_size, img_size))
        img_x, img_y = 60 * ui_scale, h - (100 * ui_scale)
        surface.blit(scaled_energy, (img_x, img_y))
        energy_ts = font_hp.render(f"{game.energy}/{game.base_energy}", True, WHITE)
        text_rect = energy_ts.get_rect(midleft=(img_x + 85 * ui_scale, img_y + img_size // 2))
        surface.blit(energy_ts, text_rect)
    else:
        energy_ts = font_big.render(f"E: {game.energy}/{game.base_energy}", True, GOLD)
        surface.blit(energy_ts, (100 * ui_scale, h - 90 * ui_scale))

    draw_bar(surface, 100 * ui_scale, h - 140 * ui_scale, game.player_hp, game.player_max_hp, game.player_block, GREEN)
    
    if game.strength > 0:
        str_ts = font_desc.render(f"力量: {game.strength}", True, (255, 100, 100))
        surface.blit(str_ts, (100 * ui_scale, h - 155 * ui_scale))
    if game.next_turn_energy > 0:
        nxt_ts = font_desc.render(f"下回合能量 +{game.next_turn_energy}", True, GOLD)
        surface.blit(nxt_ts, (180 * ui_scale, h - 155 * ui_scale))
    
    relic_x = 100 * ui_scale
    for relic in game.relics:
        pygame.draw.circle(surface, relic["color"], (int(relic_x), int(h - 175 * ui_scale)), int(15 * ui_scale))
        if pygame.Rect(relic_x - 15 * ui_scale, h - 190 * ui_scale, 30 * ui_scale, 30 * ui_scale).collidepoint((mx, my)):
            r_ts = font_desc.render(relic["name"], True, WHITE)
            surface.blit(r_ts, (relic_x - 30 * ui_scale, h - 210 * ui_scale))
        relic_x += 40 * ui_scale
        
    if game.maya_active:
        maya_ts = font_desc.render("[淨善攝位激活]", True, (100, 255, 100))
        surface.blit(maya_ts, (100 * ui_scale, h - 165 * ui_scale))

    num_cards = len(game.hand)
    draw_queue = []
    hovered_card = None
    
    if num_cards > 0:
        center_x = w // 2
        base_y = h - 100
        card_gap = 60   
        current_hand_width = (num_cards - 1) * card_gap
        max_angle = 30 
        arc_height = 80
        
        for i, card in enumerate(game.hand):
            if num_cards > 1:
                rel_pos = (i / (num_cards - 1)) - 0.5
            else:
                rel_pos = 0
            
            hand_split = 10 if i < num_cards/2 else -10
            card_x = center_x + rel_pos * current_hand_width - hand_split
            card_y = base_y + (rel_pos**2) * arc_height * 2.5
            angle = -rel_pos * max_angle * 2.2
            
            card.rect = pygame.Rect(0, 0, 165, 235)
            card.rect.center = (int(card_x), int(card_y))
        
        for card in reversed(game.hand):
            if card.rect.collidepoint((mx, my)):
                hovered_card = card
                break

        for i, card in enumerate(game.hand):
            if num_cards > 1:
                rel_pos = (i / (num_cards - 1)) - 0.5
            else:
                rel_pos = 0
            
            hand_split = 10 if i < num_cards/2 else -10
            card_x = center_x + rel_pos * current_hand_width - hand_split
            card_y = base_y + (rel_pos**2) * arc_height * 2.5
            angle = -rel_pos * max_angle * 2.2
            
            is_selectable = (game.state == "SELECT_CARD" and card != game.selection_source_card)
            
            d_dmg = 0
            if card.type == "ATTACK":
                d_dmg += game.strength
                if card.base_name == "雷霆连击":
                    d_dmg += getattr(card, 'permanent_dmg_bonus', 0)
                elif card.base_name == "黎明·斩击":
                    d_dmg += game.pyro_damage_bonus
            
            draw_queue.append({
                "card": card,
                "x": card_x,
                "y": card_y,
                "is_hovered": (card == hovered_card),
                "is_selected": is_selectable,
                "extra_dmg": d_dmg,
                "angle": angle
            })

    if num_cards > 0:
        for item in draw_queue:
            if not item["is_hovered"]:
                item["card"].draw(surface, item["x"], item["y"], False,
                                 is_selected=item["is_selected"], extra_dmg=item["extra_dmg"], angle=item["angle"],
                                 has_energy=(game.energy >= item["card"].cost))

    if hovered_card:
        for item in draw_queue:
            if item["is_hovered"]:
                item["card"].draw(surface, item["x"], item["y"], True,
                                 is_selected=item["is_selected"], extra_dmg=item["extra_dmg"], angle=item["angle"],
                                 has_energy=(game.energy >= item["card"].cost))

    draw_pile(surface, 40 * ui_scale, h - 80 * ui_scale, len(game.deck), "牌庫", BLUE)
    draw_pile(surface, w - 40 * ui_scale, h - 80 * ui_scale, len(game.discard), "棄牌", ORANGE)

    btn_w, btn_h = 150 * ui_scale, 50 * ui_scale
    btn_rect = pygame.Rect(w - 230 * ui_scale, h - 120 * ui_scale, btn_w, btn_h)
    pygame.draw.rect(surface, (80, 80, 80), btn_rect, border_radius=int(5 * ui_scale))
    btn_text = font_main.render("結束回合", True, WHITE)
    surface.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

    total_cards = len(game.deck) + len(game.hand) + len(game.discard)
    deck_btn_w, deck_btn_h = 150 * ui_scale, 36 * ui_scale
    deck_btn_rect = pygame.Rect(w - deck_btn_w - 15 * ui_scale, 10 * ui_scale, deck_btn_w, deck_btn_h)
    
    is_deck_hover = deck_btn_rect.collidepoint((mx, my))
    deck_btn_color = (40, 60, 100) if is_deck_hover else (30, 45, 80)
    pygame.draw.rect(surface, deck_btn_color, deck_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD, deck_btn_rect, width=1, border_radius=int(8 * ui_scale))
    
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

    return hovered_card, btn_rect, deck_btn_rect, guide_btn_rect
