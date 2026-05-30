import json
import os

from .config import get_save_path, SAVE_VERSION
from .battle import BattleManager


MODE_DISPLAY_NAMES = {
    "TEST": "測試模式",
    "NORMAL": "普通模式",
    "BURST": "無雙模式",
    "HARD": "高難模式",
    "ENDLESS": "無限模式",
}


def has_savegame():
    """檢查是否存在存檔"""
    return os.path.exists(get_save_path())


def get_savegame_mode():
    """讀取存檔中的模式名稱，若無存檔或讀取失敗則返回 None"""
    try:
        if not os.path.exists(get_save_path()):
            return None
        with open(get_save_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("battle", {}).get("selected_mode", None)
    except Exception:
        return None


def save_game(game):
    """保存當前遊戲狀態到 JSON 文件"""
    try:
        # 允許在戰鬥相關狀態存檔（包含從戰鬥進入的設置界面）
        valid_battle = ("BATTLE", "ENEMY_TURN")
        in_settings = game.state == "SETTINGS" and game.previous_battle_state in valid_battle
        if game.state not in valid_battle and not in_settings:
            print("只能在戰鬥中存檔")
            return False
        data = game.save_to_dict()
        # 若從設置界面存檔，修正記錄的狀態為實際戰鬥狀態
        if data.get("state") == "SETTINGS" and game.previous_battle_state in valid_battle:
            data["state"] = game.previous_battle_state
        with open(get_save_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("存檔成功")
        return True
    except Exception as e:
        print(f"存檔失敗: {e}")
        return False


def load_game(game):
    """從 JSON 文件加載遊戲狀態"""
    try:
        if not os.path.exists(get_save_path()):
            return False
        with open(get_save_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        ok = game.load_from_dict(data)
        if ok:
            from .audio import play_bgm
            play_bgm(game.volume, is_endless=game.is_endless)
        return ok
    except Exception as e:
        print(f"讀檔失敗: {e}")
        return False


def delete_savegame():
    """刪除存檔文件"""
    if os.path.exists(get_save_path()):
        os.remove(get_save_path())


# --- 特殊機制圖鑑 ---
MECHANICS_GUIDE_ENTRIES = [
    ("1. 標記追擊", "每回合開始隨機標記一張手牌（TARGET 紅標）。本回合打出該牌時，額外造成 15 點真實傷害（無視護盾）。"),
    ("2. 反應超載", "單回合內觸發 3 次及以上元素反應（蒸發、凍結、感電、結晶、擴散、碎冰、草原核等）。結束回合後，敵人下回合強制暈眩。"),
    ("3. 能量浪費", "結束回合時若仍有剩餘能量，敵人吸收能量：每剩 1 點，敵人意圖傷害永久 +2。"),
    ("4. 節奏大師", "僅部分精英/BOSS 擁有（波次 10/15/20/25/30）。每 2 回合切換：進攻姿態意圖 +50%；防禦姿態每回合回復 10 HP。切換前 1 回合有金色預告。"),
    ("5. 大招打斷", "BOSS 蓄力期間，若本回合使敵人凍結、石化或暈眩，蓄力進度重置為 1。"),
    ("6. 元素震懾", "用克制元素攻擊元素盾時，一次削 3 層盾，且敵人下次攻擊意圖傷害降低 15%。"),
    ("7. 連擊壓制", "單回合打出 ≥5 張牌，敵人該次攻擊傷害降低 30%。"),
    ("8. 元素護盾", "部分敵人帶元素盾層數；克制元素破盾更快，破盾後敵人暈眩 1 回合。"),
    ("9. 大招蓄力", "BOSS 蓄力滿後釋放高倍率攻擊；留意頭頂蓄力計數並用控制打斷。"),
    ("10. 元素反應系統", "本遊戲包含以下元素反應：\n\n【潮濕】水元素附著，使敵人進入潮濕狀態。可觸發多種元素反應。水刃、雨神之护、潮汐波可使敵人潮濕。\n\n【蒸發】火+潮濕。傷害翻倍。若裝備「熾烈的炎之魔女」，蒸發不消耗潮濕。不灭之火、黎明·斩击、天基烈焰可觸發。\n\n【感電】雷+潮濕。敵人獲得 2 層易傷（受到傷害+50%），不消耗潮濕。天街巡游、雷霆连击可觸發。\n\n【凍結】冰+水。敵人跳過下回合攻擊。冰霜新星可使敵人凍結。\n\n【碎冰】冰攻擊凍結的敵人。傷害變為 3 倍。碎冰重击可觸發。\n\n【結晶】岩+潮濕。玩家獲得護甲盾。千岩固牢、荒星防护可觸發。\n\n【擴散】風+潮濕。敵人當前意圖傷害降低 15%。旋风护盾可觸發。\n\n【草原核】攻擊潮濕敵人時生成草原核。回合開始時草原核爆炸，造成 8×數量 傷害（基礎）。裝備「深林的記憶」草原核傷害+10；裝備「草原的催化者」攻擊潮濕敵人時生成草原核；裝備「净善摄位」攻擊潮濕敵人時本回合生成草原核且草原核傷害+50%。"),
]
