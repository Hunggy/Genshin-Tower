import json
import os
from .config import get_save_path, get_meta_save_path


MODE_DISPLAY_NAMES = {
    "TEST": "測試模式",
    "NORMAL": "普通模式",
    "BURST": "無雙模式",
    "HARD": "高難模式",
    "ENDLESS": "無限模式",
}

_MAX_SLOTS = 3


def list_save_slots():
    """列出每個存檔槽位的狀態 {slot: {has_save, mode, wave, is_endless} or None}"""
    result = {}
    for slot in range(1, _MAX_SLOTS + 1):
        path = get_save_path(slot)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                battle = data.get("battle", data)
                result[slot] = {
                    "has_save": True,
                    "mode": battle.get("selected_mode", data.get("selected_mode", "NORMAL")),
                    "wave": battle.get("current_wave", data.get("current_wave", 1)),
                    "is_endless": battle.get("is_endless", data.get("is_endless", False)),
                }
            except Exception:
                result[slot] = {"has_save": True, "mode": "NORMAL", "wave": 1, "is_endless": False}
        else:
            result[slot] = {"has_save": False}
    return result


def has_savegame(slot=None):
    """檢查是否有存檔（未指定 slot 時檢查所有槽位）"""
    if slot is not None:
        return os.path.exists(get_save_path(slot))
    for s in range(1, _MAX_SLOTS + 1):
        if os.path.exists(get_save_path(s)):
            return True
    return False


def get_savegame_mode(slot=1):
    """讀取存檔中的模式"""
    try:
        path = get_save_path(slot)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        battle = data.get("battle", data)
        return battle.get("selected_mode", None)
    except Exception:
        return None


def save_game(game, slot=None):
    """保存當前遊戲狀態到 JSON 文件"""
    if slot is None:
        slot = getattr(game, "current_save_slot", 1)
    try:
        valid_battle = ("BATTLE", "ENEMY_TURN", "DISCOVERY", "SELECT_CARD", "REWARD")
        in_settings = game.state == "SETTINGS" and game.previous_battle_state in valid_battle
        if game.state not in valid_battle and not in_settings:
            print("只可在進行中的對局存檔")
            return False

        data = game.save_to_dict()

        if data.get("state") == "SETTINGS" and game.previous_battle_state in valid_battle:
            data["state"] = game.previous_battle_state

        data["save_slot"] = slot

        filepath = get_save_path(slot)
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"存檔成功 (槽位 {slot})")
        return True
    except Exception as e:
        print(f"存檔失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_game(game, slot=None):
    """從 JSON 文件加載遊戲狀態"""
    if slot is None:
        slot = getattr(game, "current_save_slot", 1)
    try:
        path = get_save_path(slot)
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        ok = game.load_from_dict(data)
        if ok:
            game.current_save_slot = data.get("save_slot", slot)
            from .audio import play_bgm
            play_bgm(game.volume, is_endless=game.is_endless)
            # 從元數據重新加載跨局數據（戰鬥存檔中可能是舊值）
            meta = load_meta_data()
            game.primogem = meta.get("primogem", 0)
            game.difficulty_tier = meta.get("difficulty_tier", 0)
            game.max_difficulty_tier = meta.get("max_difficulty_tier", 5)
            game.blessing_counts = meta.get("blessing_counts", {})
        return ok
    except Exception as e:
        print(f"讀檔失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def delete_savegame(slot=None):
    """刪除存檔文件"""
    if slot is None:
        slot = 1
    path = get_save_path(slot)
    if os.path.exists(path):
        os.remove(path)


def save_meta_data(primogem=0, difficulty_tier=0, max_difficulty_tier=5, blessing_counts=None, amount=0):
    """
    保存元數據到 meta_save.json
    amount > 0 時原石從當前值累加，否則直接覆蓋 primogem
    """
    meta_path = get_meta_save_path()

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            existing_meta = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_meta = {
            "primogem": 0,
            "difficulty_tier": 0,
            "max_difficulty_tier": 5,
            "blessing_counts": {}
        }

    if amount > 0:
        final_primogem = existing_meta.get("primogem", 0) + amount
    else:
        final_primogem = primogem

    # 合併 blessing_counts（保留已購買的次數，只更新有變化的）
    if blessing_counts is not None:
        existing_blessings = existing_meta.get("blessing_counts", {})
        merged_blessings = existing_blessings.copy()
        for b_id, count in blessing_counts.items():
            if count > 0:
                merged_blessings[b_id] = count
            elif b_id not in merged_blessings:
                merged_blessings[b_id] = 0
        final_blessings = merged_blessings
    else:
        final_blessings = existing_meta.get("blessing_counts", {})

    meta_data = {
        "primogem": final_primogem,
        "difficulty_tier": difficulty_tier if difficulty_tier else existing_meta.get("difficulty_tier", 0),
        "max_difficulty_tier": max_difficulty_tier,
        "blessing_counts": final_blessings
    }

    try:
        meta_path_dir = os.path.dirname(meta_path)
        if meta_path_dir and not os.path.exists(meta_path_dir):
            os.makedirs(meta_path_dir)

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"[ERROR] 保存元數據失敗: {e}")
        return False


def load_meta_data():
    """從文件加載元數據"""
    meta_path = get_meta_save_path()
    try:
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        else:
            return {
                "primogem": 0,
                "difficulty_tier": 0,
                "max_difficulty_tier": 5,
                "blessing_counts": {}
            }
    except Exception as e:
        print(f"[ERROR] 加載元數據失敗: {e}")
        return {
            "primogem": 0,
            "difficulty_tier": 0,
            "max_difficulty_tier": 5,
            "blessing_counts": {}
        }


MECHANICS_GUIDE_ENTRIES = [
    ("1. 目標標記", "每回合開始會隨機選一個敵人作為標記 TARGET，該敵人受到的傷害增加 15%"),
    ("2. 呼應聯動", "場上有元素附着時，使用相應元素技能會觸發元素反應"),
    ("3. 共鳴共生", "場上有另一個共鳴敵人時，雷鳴音爆傷害減半"),
    ("4. 元素防禦", "BOSS戰時，每2波觸發一種攻防狀態，傷害增加50%"),
    ("5. 元素增生", "擁有元素增生的敵人每回合承受30%傷害"),
    ("6. 洞天仙力", "每回合開始時，根據剩餘能力牌抽牌+3"),
    ("7. 靈光一閃", "當手牌數量≤5時，元素反應處理效果最佳"),
    ("8. 混沌行狀", "BOSS常態行徑會放大某些狀態的效果"),
    ("9. 洞天仙", "每回合召喚3次能力牌，隨回合數增加獲益"),
    ("10. 元素回", "每次使用元素技能時，會恢復少量體力"),
]
