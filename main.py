from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle
from kivy.utils import platform
from kivy.resources import resource_find
import json, os, random
from datetime import datetime

if platform != 'android':
    Window.fullscreen = 'auto'

GAME_NAME = "СТАЛЬНОЙ РУБЕЖ"
GAME_VERSION = "12.2.0"

def res_path(rel):
    try: return resource_find(rel) or rel
    except: return rel

def get_data_dir():
    try: return App.get_running_app().user_data_dir
    except: return "."

for folder in ["game", "game/images"]:
    try:
        if not os.path.exists(folder): os.makedirs(folder)
    except: pass

DATA_FILE = os.path.join(get_data_dir(), "players.json")
SETTINGS_FILE = os.path.join(get_data_dir(), "settings.json")

def load_json(f, d):
    try:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as file:
                return json.load(file)
    except: pass
    return d

def save_json(f, d):
    try:
        with open(f, 'w', encoding='utf-8') as file:
            json.dump(d, file, ensure_ascii=False, indent=4)
    except: pass

players = load_json(DATA_FILE, {})
settings = load_json(SETTINGS_FILE, {"last_user": "", "last_password": ""})
current_player = None
ADMINS = ["muhammad", "мухаммад"]

def is_admin(u): return u and u.lower() in ADMINS

# ============================================================
# 🚗 ТАНКИ (4 штуки)
# ============================================================
TANKS = {
    "Т-34":     {"hp": 100, "power": 10, "speed": 55, "price": 0,    "color": (0.4,0.6,0.3,1)},
    "КВ-1":     {"hp": 140, "power": 14, "speed": 35, "price": 3000, "color": (0.5,0.5,0.3,1)},
    "ИС-7":     {"hp": 180, "power": 22, "speed": 45, "price": 8000, "color": (0.3,0.4,0.5,1)},
    "Тигр II":  {"hp": 160, "power": 18, "speed": 40, "price": 6000, "color": (0.6,0.5,0.3,1)},
}

# ============================================================
# 🎨 СКИНЫ (6 штук)
# ============================================================
SKINS = {
    "Стандарт":  {"price": 0,    "bonus": 0,  "color": (0.5,0.5,0.5,1)},
    "Пустыня":   {"price": 500,  "bonus": 2,  "color": (0.8,0.7,0.4,1)},
    "Зима":      {"price": 700,  "bonus": 3,  "color": (0.9,0.9,0.95,1)},
    "Ночь":      {"price": 1000, "bonus": 4,  "color": (0.2,0.2,0.4,1)},
    "Кровь":     {"price": 1500, "bonus": 6,  "color": (0.7,0.1,0.1,1)},
    "Золото":    {"price": 3000, "bonus": 10, "color": (1,0.85,0.2,1)},
}

# ============================================================
# 👤 ТИТУЛЫ
# ============================================================
TITLES = {
    "Новичок":       {"unlock": 0,     "desc": "Начало пути"},
    "Танкист":       {"unlock": 10,    "desc": "10 боёв"},
    "Ветеран":       {"unlock": 50,    "desc": "50 боёв"},
    "Мастер":        {"unlock": 100,   "desc": "100 боёв"},
    "Гроза Врагов":  {"unlock": 250,   "desc": "250 боёв"},
    "Легенда":       {"unlock": 500,   "desc": "500 боёв"},
    "Стальной Лорд": {"unlock": 1000,  "desc": "1000 боёв"},
    "Хранитель":     {"unlock": 5000,  "desc": "5000 боёв"},
}

# ============================================================
# 🏅 ДОСТИЖЕНИЯ
# ============================================================
ACHIEVEMENTS = {
    "first_battle":  {"name": "Первый бой",   "desc": "Провести 1 бой",       "reward": 100,  "souls": 5},
    "win_10":        {"name": "Победитель",   "desc": "Выиграть 10 боёв",      "reward": 500,  "souls": 20},
    "win_50":        {"name": "Полководец",   "desc": "Выиграть 50 боёв",      "reward": 2000, "souls": 100},
    "win_100":       {"name": "Легенда",      "desc": "Выиграть 100 боёв",     "reward": 5000, "souls": 250},
    "rich_10k":      {"name": "Богач",        "desc": "Накопить 10000 монет",  "reward": 1000, "souls": 50},
    "daily_7":       {"name": "Постоянный",   "desc": "7 дней входов",         "reward": 800,  "souls": 40},
    "daily_30":      {"name": "Верный",       "desc": "30 дней входов",        "reward": 3000, "souls": 150},
    "tank_master":   {"name": "Танковед",     "desc": "Купить 3 танка",        "reward": 2000, "souls": 100},
    "chests_10":     {"name": "Кладоискатель","desc": "Открыть 10 кейсов",     "reward": 1500, "souls": 75},
    "boss_5":        {"name": "Гроза Боссов", "desc": "Победить 5 боссов",     "reward": 2500, "souls": 120},
}

# ============================================================
# 📦 КЕЙСЫ (3 типа)
# ============================================================
CHESTS = {
    "Обычный":     {"price": 200,  "currency": "coins", "min": 100,  "max": 500,  "soul_chance": 0.10, "soul_min": 1,  "soul_max": 3,  "titan_chance": 0.05},
    "Редкий":      {"price": 1000, "currency": "coins", "min": 500,  "max": 2500, "soul_chance": 0.30, "soul_min": 5,  "soul_max": 15, "titan_chance": 0.15},
    "Легендарный": {"price": 100,  "currency": "titanite", "min": 3000, "max": 15000, "soul_chance": 0.80, "soul_min": 20, "soul_max": 80, "titan_chance": 0.50},
}

SHELLS = {
    "AP":   {"name": "Бронебойный",  "pen": 200, "dmg": 120, "ric": 60},
    "HEAT": {"name": "Кумулятивный", "pen": 250, "dmg": 90,  "ric": 70},
    "HE":   {"name": "Фугасный",     "pen": 50,  "dmg": 200, "ric": 85},
}

def wt_default():
    return {
        "doublers": 3, "repair_kits": 2, "medkits": 2,
        "crew": 4, "max_crew": 4, "mode": "arcade", "shell": "AP",
        "modules": {
            "engine": {"hp": 100, "max": 100, "broken": False},
            "gun":    {"hp": 100, "max": 100, "broken": False},
            "tracks": {"hp": 100, "max": 100, "broken": False},
            "turret": {"hp": 100, "max": 100, "broken": False},
        },
    }

def wt_get(d):
    try:
        if "wt" not in d or not isinstance(d["wt"], dict):
            d["wt"] = wt_default()
        return d["wt"]
    except: return wt_default()

def wt_use_doubler(d):
    try:
        wt = wt_get(d)
        if wt["doublers"] > 0:
            wt["doublers"] -= 1; save_json(DATA_FILE, players)
            return True, "Дублёр! Осталось: %d" % wt["doublers"]
        return False, "Дублёров нет!"
    except Exception as e: return False, str(e)

def wt_add_doubler(d, n=1):
    try:
        wt_get(d)["doublers"] += n; save_json(DATA_FILE, players); return True
    except: return False

def wt_repair_all(d):
    try:
        wt = wt_get(d)
        if wt["repair_kits"] <= 0: return False, "Ремкомплектов нет!"
        wt["repair_kits"] -= 1
        for m in wt["modules"].values():
            m["hp"] = m["max"]; m["broken"] = False
        save_json(DATA_FILE, players)
        return True, "Все модули отремонтированы!"
    except Exception as e: return False, str(e)

def wt_damage_module(d, mod, dmg):
    try:
        wt = wt_get(d); m = wt["modules"].get(mod)
        if not m: return
        m["hp"] = max(0, m["hp"] - dmg)
        if m["hp"] == 0: m["broken"] = True
        save_json(DATA_FILE, players)
    except: pass

def wt_random_damage(d):
    try:
        mod = random.choice(list(wt_get(d)["modules"].keys()))
        dmg = random.randint(20, 60)
        wt_damage_module(d, mod, dmg)
        return mod, dmg
    except: return None, 0

def wt_use_medkit(d):
    try:
        wt = wt_get(d)
        if wt["crew"] >= wt["max_crew"]: return False, "Экипаж полный!"
        if wt["medkits"] <= 0: return False, "Меднаборов нет!"
        wt["medkits"] -= 1; wt["crew"] += 1
        save_json(DATA_FILE, players)
        return True, "Боец возвращён! %d/%d" % (wt["crew"], wt["max_crew"])
    except Exception as e: return False, str(e)

def wt_lose_crewman(d):
    try:
        wt = wt_get(d)
        if wt["crew"] > 0: wt["crew"] -= 1
        save_json(DATA_FILE, players); return wt["crew"]
    except: return 0

def wt_crew_penalty(d):
    try:
        wt = wt_get(d)
        return max(0.2, 1.0 - (wt["max_crew"] - wt["crew"]) * 0.2)
    except: return 1.0

def wt_set_mode(d, mode):
    try:
        if mode in ("arcade", "realistic", "simulator"):
            wt_get(d)["mode"] = mode; save_json(DATA_FILE, players); return True
        return False
    except: return False

def wt_set_shell(d, shell):
    try:
        if shell in SHELLS:
            wt_get(d)["shell"] = shell; save_json(DATA_FILE, players); return True
        return False
    except: return False

def wt_calc_damage(d, armor, angle=0, dist=500):
    try:
        wt = wt_get(d); s = SHELLS.get(wt["shell"], SHELLS["AP"])
        pen = s["pen"] * (1 - dist / 5000)
        if angle >= s["ric"]: return 0, "РИКОШЕТ!"
        pen *= max(0.3, 1 - angle / 90)
        if pen <= armor: return 0, "НЕ ПРОБИЛ!"
        dmg = int(s["dmg"] * (pen / armor) * 0.5 * wt_crew_penalty(d))
        return dmg, "ПРОБИЛ! Урон: %d" % dmg
    except Exception as e: return 0, str(e)

def wt_tactic(hp, hpmax):
    try:
        if hp < hpmax * 0.3: return "отступает"
        r = random.random()
        return "выстрелил-отъехал" if r < 0.4 else ("фланкирует" if r < 0.7 else "бьёт по НЛД")
    except: return "выстрелил-отъехал"

def wt_can_move_shoot(d):
    try:
        wt = wt_get(d)
        return (not wt["modules"]["engine"]["broken"] and not wt["modules"]["tracks"]["broken"],
                not wt["modules"]["gun"]["broken"])
    except: return True, True

def wt_mode_settings(d):
    try:
        m = wt_get(d)["mode"]
        modes = {
            "arcade":    {"name": "Аркадный",     "markers": True,  "hud": "full",   "dbl": True,  "fpv": False},
            "realistic": {"name": "Реалистичный", "markers": False, "hud": "mini",   "dbl": True,  "fpv": False},
            "simulator": {"name": "Симуляторный", "markers": False, "hud": "hidden", "dbl": False, "fpv": True},
        }
        return modes.get(m, modes["arcade"])
    except: return {"name": "Аркадный", "markers": True, "hud": "full", "dbl": True, "fpv": False}

# ============================================================
# 🏅 ДОСТИЖЕНИЯ — ПРОВЕРКА
# ============================================================
def check_achievements(d):
    """Проверить и выдать достижения. Возвращает список новых."""
    try:
        if "achievements" not in d: d["achievements"] = []
        new = []
        wins = d.get("wins", 0)
        battles = d.get("battles", 0)
        coins = d.get("coins", 0)
        daily_streak = d.get("daily_streak", 0)
        tanks_bought = d.get("tanks_bought", 0)
        chests = d.get("chests_opened", 0)
        bosses = d.get("boss_defeated", 0)

        conditions = {
            "first_battle": battles >= 1,
            "win_10": wins >= 10,
            "win_50": wins >= 50,
            "win_100": wins >= 100,
            "rich_10k": coins >= 10000,
            "daily_7": daily_streak >= 7,
            "daily_30": daily_streak >= 30,
            "tank_master": tanks_bought >= 3,
            "chests_10": chests >= 10,
            "boss_5": bosses >= 5,
        }
        for key, ok in conditions.items():
            if ok and key not in d["achievements"]:
                d["achievements"].append(key)
                ach = ACHIEVEMENTS[key]
                d["coins"] = d.get("coins", 0) + ach["reward"]
                d["souls"] = d.get("souls", 0) + ach["souls"]
                new.append(ach["name"])
        if new:
            save_json(DATA_FILE, players)
        return new
    except: return []

def get_titles_for(d):
    """Список доступных титулов по боям."""
    try:
        battles = d.get("battles", 0)
        return [t for t, info in TITLES.items() if battles >= info["unlock"]]
    except: return ["Новичок"]

def get_player(u):
    if u not in players:
        players[u] = {
            "password": "",
            "coins": 5000, "titanite": 500, "souls": 50,
            "crystals": 100, "ingots": 0,
            "level": 1, "exp": 0, "power": 10, "hp": 100,
            "battles": 0, "wins": 0,
            "characters": ["Базовый Робот"],
            "current_tank": "Т-34",
            "tanks": ["Т-34"],
            "current_skin": "Стандарт",
            "skins": ["Стандарт"],
            "current_title": "Новичок",
            "achievements": [],
            "daily_claimed": "",
            "daily_streak": 0,
            "chests_opened": 0,
            "boss_defeated": 0,
            "school_solved": 0,
            "second_account": 0,
            "bank": {"deposit": 0, "date": ""},
            "clan": None, "friends": [], "guild": None,
            "arena_rating": 1000, "company": "Роботы",
            "tanks_bought": 1,
            "wt": wt_default(),
        }
        if is_admin(u): players[u]["characters"].append("Дафак Бума")
        save_json(DATA_FILE, players)
    else:
        d = players[u]
        # миграция старых сохранений
        for k, v in [("titanite", 500), ("souls", 50), ("achievements", []),
                     ("daily_streak", 0), ("tanks", ["Т-34"]), ("skins", ["Стандарт"]),
                     ("current_tank", "Т-34"), ("current_skin", "Стандарт"),
                     ("current_title", "Новичок"), ("tanks_bought", 1)]:
            if k not in d: d[k] = v
        if "wt" not in d: d["wt"] = wt_default()
    return players[u]

def show_popup(title, text):
    try:
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text=text, font_size=24))
        btn = Button(text="OK", font_size=28, size_hint_y=0.3)
        popup = Popup(title=title, content=layout, size_hint=(0.85, 0.5))
        btn.bind(on_press=popup.dismiss)
        layout.add_widget(btn)
        popup.open()
    except: pass

class BigButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 22
        self.size_hint_y = None
        self.height = 58
        self.color = (1, 1, 1, 1)
        self.bold = True

def make_screen(title, color, info_fn, buttons_fn):
    class _S(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = BoxLayout(orientation='vertical', padding=15, spacing=8)
            layout.add_widget(Label(text=title, font_size=36, bold=True, color=color, size_hint_y=0.08))
            self.info = Label(text="", font_size=20, color=(0.9,0.9,0.9,1), size_hint_y=0.20)
            layout.add_widget(self.info)
            scroll = ScrollView(size_hint=(1, 0.62))
            box = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
            box.bind(minimum_height=box.setter('height'))
            for txt, col, fn in buttons_fn(self):
                b = BigButton(text=txt, background_color=col)
                b.bind(on_press=fn)
                box.add_widget(b)
            scroll.add_widget(box)
            layout.add_widget(scroll)
            back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.08)
            back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
            layout.add_widget(back)
            self.add_widget(layout)

        def on_enter(self):
            try:
                if not current_player: return
                self.info.text = info_fn(get_player(current_player))
            except Exception as e:
                self.info.text = "Ошибка: %s" % e
    return _S

# ============================================================
# ЭКРАНЫ
# ============================================================
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ml = FloatLayout()
        BG = res_path("game/images/titan60.jpg")
        if os.path.exists(BG):
            ml.add_widget(Image(source=BG, allow_stretch=True, keep_ratio=False))
        L = BoxLayout(orientation='vertical', padding=40, spacing=20,
                      size_hint=(0.85, 0.65), pos_hint={'center_x':0.5, 'center_y':0.5})
        L.add_widget(Label(text=GAME_NAME, font_size=52, bold=True, color=(1,0.85,0.2,1)))
        self.u = TextInput(hint_text="Никнейм", multiline=False, font_size=30,
                           size_hint_y=0.18, background_color=(0.2,0.2,0.2,0.9), foreground_color=(1,1,1,1))
        L.add_widget(self.u)
        self.p = TextInput(hint_text="Пароль", multiline=False, password=True, font_size=30,
                           size_hint_y=0.18, background_color=(0.2,0.2,0.2,0.9), foreground_color=(1,1,1,1))
        L.add_widget(self.p)
        b = BigButton(text="ВХОД!", background_color=(0.2,0.6,0.2,1))
        b.bind(on_press=self.login)
        L.add_widget(b)
        self.info = Label(text="", font_size=22, color=(0.9,0.9,0.9,1), size_hint_y=0.12)
        L.add_widget(self.info)
        ml.add_widget(L)
        self.add_widget(ml)

    def login(self, inst):
        try:
            name = self.u.text.strip(); pwd = self.p.text.strip()
            if not name: self.info.text = "Введите никнейм!"; return
            if is_admin(name) and pwd != "2026": self.info.text = "Неверный пароль!"; return
            d = get_player(name)
            if d["password"] and d["password"] != pwd: self.info.text = "Неверный пароль!"; return
            global current_player
            current_player = name
            settings["last_user"] = name; settings["last_password"] = pwd
            save_json(SETTINGS_FILE, settings)
            app = App.get_running_app()
            app.main_screen.update_info()
            app.root.current = "main"
        except Exception as e: self.info.text = "Ошибка: %s" % e

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ml = FloatLayout()
        BG = res_path("game/images/titan60.jpg")
        if os.path.exists(BG):
            ml.add_widget(Image(source=BG, allow_stretch=True, keep_ratio=False))
        L = BoxLayout(orientation='vertical', padding=15, spacing=8,
                      size_hint=(0.92, 0.94), pos_hint={'center_x':0.5, 'center_y':0.5})
        self.info_label = Label(text="", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.12)
        L.add_widget(self.info_label)
        scroll = ScrollView(size_hint=(1, 0.84))
        grid = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        btns = [
            ("📰 НОВОСТИ", (0.9,0.5,0.1,1), "news"),
            ("⚔️ В БОЙ!", (0.2,0.6,0.2,1), "battle"),
            ("🚗 АНГАР", (0.4,0.6,0.3,1), "hangar"),
            ("🎨 СКИНЫ", (0.7,0.3,0.7,1), "skins"),
            ("🏅 ДОСТИЖЕНИЯ", (0.9,0.7,0.2,1), "achievements"),
            ("👤 ПРОФИЛЬ", (0.3,0.3,0.5,1), "profile"),
            ("🎖️ ДУБЛЁРЫ", (0.8,0.5,0.2,1), "warthunder"),
            ("📦 КЕЙСЫ", (0.8,0.4,0.6,1), "chests"),
            ("🎁 ЕЖЕДНЕВНЫЕ", (0.8,0.4,0.2,1), "daily"),
            ("🛒 МАГАЗИН", (0.2,0.4,0.6,1), "shop"),
            ("🎓 ШКОЛА", (0.2,0.8,0.4,1), "school"),
            ("📋 КВЕСТЫ", (0.8,0.4,0.2,1), "quest"),
            ("👹 БОСС", (0.8,0.2,0.2,1), "boss"),
            ("🌍 ОТКРЫТЫЙ МИР", (0.2,0.4,0.8,1), "world"),
            ("💹 ЭКОНОМИКА", (0.2,0.8,0.6,1), "economy"),
            ("👥 КЛАНЫ", (0.3,0.6,0.3,1), "clans"),
            ("🤝 ДРУЗЬЯ", (0.6,0.3,0.6,1), "friends"),
            ("📧 ПОДДЕРЖКА", (0.2,0.8,0.4,1), "support"),
            ("🏢 КОМПАНИЯ", (0.8,0.6,0.2,1), "company"),
            ("⚙️ НАСТРОЙКИ", (0.5,0.5,0.5,1), "settings"),
            ("📊 СТАТИСТИКА", (0.6,0.3,0.3,1), "stats"),
            ("🏆 РЕЙТИНГ", (0.3,0.6,0.6,1), "rating"),
            ("👾 ПЕРСОНАЖИ", (0.2,0.5,0.8,1), "characters"),
            ("⚔️ АРЕНА", (0.6,0.2,0.4,1), "arena"),
            ("🎉 СОБЫТИЯ", (0.8,0.6,0.2,1), "events"),
            ("🎥 РЕПЛЕЙ", (0.4,0.2,0.6,1), "replay"),
            ("🏦 БАНК", (0.8,0.6,0.2,1), "bank"),
            ("🔨 КРАФТ", (0.6,0.4,0.8,1), "craft"),
            ("📅 КАЛЕНДАРЬ", (0.2,0.6,0.8,1), "calendar"),
            ("🏛️ ГИЛЬДИИ", (0.8,0.4,0.4,1), "guilds"),
            ("🏪 РЫНОК", (0.4,0.6,0.2,1), "market"),
            ("🎯 МИНИ-ИГРА", (0.9,0.3,0.5,1), "minigame"),
        ]
        for t, c, tgt in btns:
            b = BigButton(text=t, background_color=c)
            b.bind(on_press=lambda x, tt=tgt: setattr(App.get_running_app().root, "current", tt))
            grid.add_widget(b)
        scroll.add_widget(grid)
        L.add_widget(scroll)
        L.add_widget(Label(text="v" + GAME_VERSION, font_size=16, color=(0.5,0.5,0.5,1), size_hint_y=0.04))
        ml.add_widget(L)
        self.add_widget(ml)

    def update_info(self):
        if not current_player: return
        d = get_player(current_player)
        self.info_label.text = "%s | 💰%d | 💠%d | 💜%d | Ур.%d | %s" % (
            current_player, d['coins'], d.get('titanite',0), d.get('souls',0),
            d['level'], d.get('current_title', 'Новичок'))

class NewsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=15, spacing=8)
        L.add_widget(Label(text="📰 НОВОСТИ", font_size=40, bold=True,
                           color=(0.9,0.5,0.1,1), size_hint_y=0.08))
        scroll = ScrollView(size_hint=(1, 0.84))
        box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=(10, 10))
        box.bind(minimum_height=box.setter('height'))
        news_list = [
            ("🆕 ВЕРСИЯ 12.2.0",
             "Крупное обновление!\n• Ангар с 4 танками\n• 6 скинов\n• 10 достижений\n• Титулы\n• 3 типа кейсов\n• 2 валюты: Титанит и Души",
             (0.9, 0.5, 0.1, 1)),
            ("🎖️ ПЕРЕИМЕНОВАНИЕ",
             "Игра называется «СТАЛЬНОЙ РУБЕЖ»!",
             (0.2, 0.6, 0.8, 1)),
            ("🎵 МУЗЫКА",
             "Теперь играет трек biskas.zelye!\nВ формате OGG.",
             (0.5, 0.2, 0.7, 1)),
        ]
        for title, text, color in news_list:
            card = BoxLayout(orientation='vertical', spacing=4, size_hint_y=None, height=180, padding=(10, 10))
            with card.canvas.before:
                Color(color[0], color[1], color[2], 0.15)
                rect = Rectangle(pos=card.pos, size=card.size)
            card.bind(pos=lambda i, v, r=rect: setattr(r, 'pos', v),
                      size=lambda i, v, r=rect: setattr(r, 'size', v))
            card.add_widget(Label(text=title, font_size=22, bold=True, color=color,
                                  size_hint_y=None, height=36, halign='left', valign='middle'))
            card.add_widget(Label(text=text, font_size=17, color=(0.95, 0.95, 0.95, 1),
                                  halign='left', valign='top'))
            box.add_widget(card)
        scroll.add_widget(box)
        L.add_widget(scroll)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.08)
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back)
        self.add_widget(L)

# ============================================================
# 🚗 АНГАР
# ============================================================
class HangarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=15, spacing=8)
        L.add_widget(Label(text="🚗 АНГАР", font_size=38, bold=True,
                           color=(0.4,0.6,0.3,1), size_hint_y=0.08))
        self.info = Label(text="", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.15)
        L.add_widget(self.info)
        scroll = ScrollView(size_hint=(1, 0.69))
        self.box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter('height'))
        scroll.add_widget(self.box)
        L.add_widget(scroll)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.08)
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back)
        self.add_widget(L)

    def on_enter(self):
        try:
            if not current_player: return
            d = get_player(current_player)
            self.info.text = "💰 %d | 💠 %d\nТекущий: %s" % (
                d['coins'], d.get('titanite',0), d.get('current_tank','Т-34'))
            self.box.clear_widgets()
            for name, info in TANKS.items():
                owned = name in d.get('tanks', [])
                if owned:
                    text = "✅ %s | HP:%d Сила:%d" % (name, info['hp'], info['power'])
                    col = info['color']
                    fn = lambda x, n=name: self.select(n)
                else:
                    text = "🔒 %s — %d💰" % (name, info['price'])
                    col = (0.4,0.4,0.4,1)
                    fn = lambda x, n=name, p=info['price']: self.buy(n, p)
                b = BigButton(text=text, background_color=col)
                b.bind(on_press=fn)
                self.box.add_widget(b)
        except Exception as e: self.info.text = "Ошибка: %s" % e

    def select(self, name):
        d = get_player(current_player)
        d['current_tank'] = name
        save_json(DATA_FILE, players)
        show_popup("🚗 Танк", "Выбран: %s" % name)
        self.on_enter()

    def buy(self, name, price):
        d = get_player(current_player)
        if d['coins'] < price:
            show_popup("🚗 Ангар", "Недостаточно монет!")
            return
        d['coins'] -= price
        d['tanks'] = d.get('tanks', []) + [name]
        d['tanks_bought'] = d.get('tanks_bought', 0) + 1
        d['current_tank'] = name
        save_json(DATA_FILE, players)
        new = check_achievements(d)
        show_popup("🚗 Куплен!", "%s" % name + ("\n\n🏅 " + ", ".join(new) if new else ""))
        self.on_enter()

# ============================================================
# 🎨 СКИНЫ
# ============================================================
class SkinsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=15, spacing=8)
        L.add_widget(Label(text="🎨 СКИНЫ", font_size=38, bold=True,
                           color=(0.7,0.3,0.7,1), size_hint_y=0.08))
        self.info = Label(text="", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.15)
        L.add_widget(self.info)
        scroll = ScrollView(size_hint=(1, 0.69))
        self.box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter('height'))
        scroll.add_widget(self.box)
        L.add_widget(scroll)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.08)
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back)
        self.add_widget(L)

    def on_enter(self):
        try:
            if not current_player: return
            d = get_player(current_player)
            self.info.text = "💰 %d\nТекущий скин: %s" % (
                d['coins'], d.get('current_skin','Стандарт'))
            self.box.clear_widgets()
            for name, info in SKINS.items():
                owned = name in d.get('skins', ['Стандарт'])
                if owned:
                    text = "✅ %s | +%d сила" % (name, info['bonus'])
                    col = info['color']
                    fn = lambda x, n=name: self.select(n)
                else:
                    text = "🔒 %s — %d💰 (+%d)" % (name, info['price'], info['bonus'])
                    col = (0.4,0.4,0.4,1)
                    fn = lambda x, n=name, p=info['price']: self.buy(n, p)
                b = BigButton(text=text, background_color=col)
                b.bind(on_press=fn)
                self.box.add_widget(b)
        except Exception as e: self.info.text = "Ошибка: %s" % e

    def select(self, name):
        d = get_player(current_player)
        d['current_skin'] = name
        save_json(DATA_FILE, players)
        show_popup("🎨 Скин", "Выбран: %s" % name)
        self.on_enter()

    def buy(self, name, price):
        d = get_player(current_player)
        if d['coins'] < price:
            show_popup("🎨 Скины", "Недостаточно монет!")
            return
        d['coins'] -= price
        d['skins'] = d.get('skins', []) + [name]
        d['current_skin'] = name
        save_json(DATA_FILE, players)
        show_popup("🎨 Куплен!", "%s" % name)
        self.on_enter()

# ============================================================
# 🏅 ДОСТИЖЕНИЯ
# ============================================================
class AchievementsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=15, spacing=8)
        L.add_widget(Label(text="🏅 ДОСТИЖЕНИЯ", font_size=38, bold=True,
                           color=(0.9,0.7,0.2,1), size_hint_y=0.08))
        self.info = Label(text="", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.15)
        L.add_widget(self.info)
        scroll = ScrollView(size_hint=(1, 0.69))
        self.box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter('height'))
        scroll.add_widget(self.box)
        L.add_widget(scroll)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.08)
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back)
        self.add_widget(L)

    def on_enter(self):
        try:
            if not current_player: return
            d = get_player(current_player)
            done = d.get('achievements', [])
            self.info.text = "Открыто: %d/%d" % (len(done), len(ACHIEVEMENTS))
            self.box.clear_widgets()
            for key, info in ACHIEVEMENTS.items():
                if key in done:
                    text = "✅ %s — %s" % (info['name'], info['desc'])
                    col = (0.3,0.6,0.3,1)
                else:
                    text = "🔒 %s — %s (+%d💰 +%d💜)" % (
                        info['name'], info['desc'], info['reward'], info['souls'])
                    col = (0.4,0.4,0.4,1)
                b = BigButton(text=text, background_color=col)
                self.box.add_widget(b)
        except Exception as e: self.info.text = "Ошибка: %s" % e

# ============================================================
# 👤 ПРОФИЛЬ (с титулами)
# ============================================================
class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=15, spacing=8)
        L.add_widget(Label(text="👤 ПРОФИЛЬ", font_size=38, bold=True,
                           color=(1,0.8,0.2,1), size_hint_y=0.08))
        self.info = Label(text="", font_size=19, color=(0.9,0.9,0.9,1), size_hint_y=0.30)
        L.add_widget(self.info)
        scroll = ScrollView(size_hint=(1, 0.54))
        self.box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter('height'))
        scroll.add_widget(self.box)
        L.add_widget(scroll)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.08)
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back)
        self.add_widget(L)

    def on_enter(self):
        try:
            if not current_player: return
            d = get_player(current_player)
            self.info.text = (
                "%s\n🏷️ %s\n💰 %d | 💠 %d | 💜 %d\n"
                "⭐ %d | 💪 %d | ❤️ %d\n"
                "⚔️ %d боёв | 🏆 %d побед\n"
                "🚗 %s | 🎨 %s" % (
                current_player, d.get('current_title','Новичок'),
                d['coins'], d.get('titanite',0), d.get('souls',0),
                d['level'], d['power'], d['hp'],
                d['battles'], d['wins'],
                d.get('current_tank','Т-34'), d.get('current_skin','Стандарт')))
            self.box.clear_widgets()
            available = get_titles_for(d)
            for t in available:
                if t == d.get('current_title'):
                    text = "✅ %s" % t
                    col = (0.3,0.6,0.3,1)
                else:
                    text = "🏷️ %s (%s)" % (t, TITLES[t]['desc'])
                    col = (0.4,0.5,0.7,1)
                b = BigButton(text=text, background_color=col)
                b.bind(on_press=lambda x, tt=t: self.set_title(tt))
                self.box.add_widget(b)
        except Exception as e: self.info.text = "Ошибка: %s" % e

    def set_title(self, title):
        d = get_player(current_player)
        d['current_title'] = title
        save_json(DATA_FILE, players)
        self.on_enter()

# ============================================================
# БОЙ
# ============================================================
class BattleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=12, spacing=6)
        L.add_widget(Label(text="⚔️ БОЙ", font_size=34, bold=True, color=(1,0.8,0.2,1), size_hint_y=0.07))
        self.info_l = Label(text="", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.18)
        L.add_widget(self.info_l)
        self.hp_l = Label(text="", font_size=22, color=(0.9,0.9,0.9,1), size_hint_y=0.12)
        L.add_widget(self.hp_l)
        self.res_l = Label(text="Нажми ОГОНЬ!", font_size=20, color=(0.9,0.9,0.9,1), size_hint_y=0.13)
        L.add_widget(self.res_l)
        for t, c, f in [
            ("🔥 ОГОНЬ!", (0.8,0.2,0.2,1), self.fire),
            ("🎖️ ДУБЛЁР", (0.8,0.5,0.2,1), self.dbl),
            ("🔧 РЕМОНТ", (0.4,0.6,0.2,1), self.rep),
            ("⚕️ МЕДНАБОР", (0.6,0.2,0.4,1), self.med),
        ]:
            b = BigButton(text=t, background_color=c); b.bind(on_press=f); L.add_widget(b)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back)
        self.add_widget(L)
        self.php = 0; self.ehp = 0; self.ehpm = 0

    def on_enter(self):
        try:
            if not current_player: return
            d = get_player(current_player)
            tank = TANKS.get(d.get('current_tank','Т-34'), TANKS['Т-34'])
            skin = SKINS.get(d.get('current_skin','Стандарт'), SKINS['Стандарт'])
            bonus = skin['bonus']
            self.php = tank['hp'] + d['power'] * 2 + bonus * 5
            self.ehp = random.randint(40, 150) + d["level"] * 5
            self.ehpm = self.ehp
            self.upd()
        except Exception as e: self.res_l.text = "Ошибка: %s" % e

    def upd(self):
        try:
            d = get_player(current_player); wt = wt_get(d)
            self.info_l.text = "%s | %s | %s\nЭкипаж: %d/%d | 🎖️%d 🔧%d ⚕️%d" % (
                d.get('current_tank','Т-34'), d.get('current_skin','Стандарт'),
                wt_mode_settings(d)['name'],
                wt['crew'], wt['max_crew'], wt['doublers'], wt['repair_kits'], wt['medkits'])
            self.hp_l.text = "❤️ Ты: %d\n👾 Враг: %d" % (self.php, self.ehp)
        except Exception as e: print(e)

    def dbl(self, i):
        d = get_player(current_player); ok, m = wt_use_doubler(d)
        if ok: self.php = 100 + d["power"] * 2
        self.res_l.text = m; self.upd()

    def rep(self, i):
        d = get_player(current_player); ok, m = wt_repair_all(d)
        self.res_l.text = m; self.upd()

    def med(self, i):
        d = get_player(current_player); ok, m = wt_use_medkit(d)
        self.res_l.text = m; self.upd()

    def fire(self, i):
        try:
            if not current_player: return
            d = get_player(current_player)
            _, can_shoot = wt_can_move_shoot(d)
            if not can_shoot:
                self.res_l.text = "❌ Орудие сломано! Жми РЕМОНТ."; return
            skin = SKINS.get(d.get('current_skin','Стандарт'), SKINS['Стандарт'])
            bonus = skin['bonus']
            pen = wt_crew_penalty(d)
            p_dmg = int((random.randint(10, 30) + d["power"] // 2 + bonus) * pen)
            e_dmg = random.randint(5, 20) + d["level"] // 2
            dmg, msg = wt_calc_damage(d, random.randint(30, 120),
                                      angle=random.randint(0, 70), dist=random.randint(100, 1500))
            if dmg > 0: p_dmg = dmg + bonus
            else: p_dmg = 0; self.res_l.text = msg
            if random.random() < 0.35:
                mod, dm = wt_random_damage(d)
                if mod: self.res_l.text += " (🔧 %s -%d)" % (mod, dm)
            if random.random() < 0.2: wt_lose_crewman(d)
            self.ehp -= p_dmg; self.php -= e_dmg
            if not self.res_l.text or self.res_l.text.startswith("ПРОБИЛ"):
                self.res_l.text = "💥 Ты: %d | Враг: %d | 🤖 %s" % (p_dmg, e_dmg, wt_tactic(self.ehp, self.ehpm))
            if self.ehp <= 0:
                self.res_l.text = "🎉 ПОБЕДА! +50💰 +10⭐ +1🎖️"
                d["coins"] += 50; d["exp"] += 10
                d["titanite"] = d.get("titanite",0) + random.randint(1, 5)
                d["souls"] = d.get("souls",0) + random.randint(0, 2)
                if d["exp"] >= 100: d["level"] += 1; d["exp"] = 0
                d["battles"] += 1; d["wins"] += 1
                wt_add_doubler(d, 1)
                new = check_achievements(d)
                if new: self.res_l.text += "\n🏅 " + ", ".join(new)
                save_json(DATA_FILE, players)
                self.on_enter(); return
            if self.php <= 0:
                self.res_l.text = "💀 ПОРАЖЕНИЕ... -20💰"
                d["coins"] = max(0, d["coins"] - 20); d["battles"] += 1
                check_achievements(d)
                save_json(DATA_FILE, players); self.on_enter(); return
            self.upd()
        except Exception as e: self.res_l.text = "Ошибка: %s" % e

class WarThunderScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=12, spacing=6)
        L.add_widget(Label(text="🎖️ WAR THUNDER", font_size=28, bold=True,
                           color=(1,0.8,0.2,1), size_hint_y=0.07))
        self.info = Label(text="", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.18)
        L.add_widget(self.info)
        scroll = ScrollView(size_hint=(1, 0.67))
        box = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        acts = [
            ("🎖️ ДУБЛЁР", (0.8,0.5,0.2,1), self.do_dbl),
            ("🔧 РЕМОНТ", (0.4,0.6,0.2,1), self.do_rep),
            ("⚕️ МЕДНАБОР", (0.6,0.2,0.4,1), self.do_med),
            ("🛒 КУПИТЬ ДУБЛЁР (300)", (0.2,0.4,0.6,1), self.buy_dbl),
            ("🛒 КУПИТЬ РЕМКОМПЛЕКТ (200)", (0.2,0.5,0.5,1), self.buy_rep),
            ("🛒 КУПИТЬ МЕДНАБОР (250)", (0.5,0.2,0.5,1), self.buy_med),
        ]
        for t, c, f in acts:
            b = BigButton(text=t, background_color=c); b.bind(on_press=f); box.add_widget(b)
        box.add_widget(Label(text="РЕЖИМ", font_size=20, bold=True, color=(1,0.9,0.4,1),
                             size_hint_y=None, height=34))
        for m, nm in [("arcade","АРКАДНЫЙ"), ("realistic","РЕАЛИСТИЧНЫЙ"), ("simulator","СИМУЛЯТОРНЫЙ")]:
            b = BigButton(text=nm, background_color=(0.3,0.4,0.6,1))
            b.bind(on_press=lambda x, mm=m: self.set_mode(mm)); box.add_widget(b)
        box.add_widget(Label(text="СНАРЯД", font_size=20, bold=True, color=(1,0.9,0.4,1),
                             size_hint_y=None, height=34))
        for s in SHELLS:
            b = BigButton(text=SHELLS[s]["name"], background_color=(0.6,0.4,0.2,1))
            b.bind(on_press=lambda x, ss=s: self.set_shell(ss)); box.add_widget(b)
        scroll.add_widget(box); L.add_widget(scroll)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.07)
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back)
        self.add_widget(L)

    def on_enter(self):
        try:
            if not current_player: return
            d = get_player(current_player); wt = wt_get(d)
            self.info.text = "🎖️%d | 🔧%d | ⚕️%d\n👥%d/%d | %s | %s" % (
                wt['doublers'], wt['repair_kits'], wt['medkits'],
                wt['crew'], wt['max_crew'],
                wt_mode_settings(d)['name'], SHELLS[wt['shell']]['name'])
        except Exception as e: self.info.text = "Ошибка: %s" % e

    def do_dbl(self, i):
        ok, m = wt_use_doubler(get_player(current_player)); show_popup("Дублёр", m); self.on_enter()
    def do_rep(self, i):
        ok, m = wt_repair_all(get_player(current_player)); show_popup("Ремонт", m); self.on_enter()
    def do_med(self, i):
        ok, m = wt_use_medkit(get_player(current_player)); show_popup("Меднабор", m); self.on_enter()
    def buy_dbl(self, i):
        d = get_player(current_player)
        if d["coins"] < 300: show_popup("Магазин", "Мало монет!"); return
        d["coins"] -= 300; wt_add_doubler(d, 1); show_popup("Магазин", "✅ Дублёр!"); self.on_enter()
    def buy_rep(self, i):
        d = get_player(current_player)
        if d["coins"] < 200: show_popup("Магазин", "Мало монет!"); return
        d["coins"] -= 200; wt_get(d)["repair_kits"] += 1; save_json(DATA_FILE, players)
        show_popup("Магазин", "✅ Ремкомплект!"); self.on_enter()
    def buy_med(self, i):
        d = get_player(current_player)
        if d["coins"] < 250: show_popup("Магазин", "Мало монет!"); return
        d["coins"] -= 250; wt_get(d)["medkits"] += 1; save_json(DATA_FILE, players)
        show_popup("Магазин", "✅ Меднабор!"); self.on_enter()
    def set_mode(self, m):
        wt_set_mode(get_player(current_player), m); self.on_enter()
    def set_shell(self, s):
        wt_set_shell(get_player(current_player), s); self.on_enter()

class MiniGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=25, spacing=12)
        L.add_widget(Label(text="🎯 МИНИ-ИГРА", font_size=38, bold=True, color=(0.9,0.3,0.5,1)))
        self.info = Label(text="Угадай число от 1 до 10!", font_size=24, color=(0.9,0.9,0.9,1))
        L.add_widget(self.info)
        self.inp = TextInput(hint_text="Число", multiline=False, font_size=32,
                             size_hint_y=0.12, input_filter="int")
        L.add_widget(self.inp)
        b = BigButton(text="🎲 УГАДАТЬ", background_color=(0.2,0.6,0.2,1))
        b.bind(on_press=self.guess); L.add_widget(b)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back); self.add_widget(L)
        self.secret = None

    def on_enter(self):
        self.secret = random.randint(1, 10)
        self.info.text = "Угадай число от 1 до 10!"

    def guess(self, i):
        try:
            if not current_player or not self.inp.text.strip(): return
            n = int(self.inp.text.strip()); d = get_player(current_player)
            if n == self.secret:
                r = random.randint(30, 100); d["coins"] += r; save_json(DATA_FILE, players)
                self.info.text = "🎉 +%d монет!" % r; self.secret = random.randint(1, 10)
            else:
                hint = "больше" if n < self.secret else "меньше"
                self.info.text = "❌ Загаданное %s." % hint
        except Exception as e: self.info.text = "Ошибка: %s" % e

# ============================================================
# ФУНКЦИИ ЭКРАНОВ
# ============================================================
def _buy_power(inst):
    d = get_player(current_player)
    if d["coins"] >= 30: d["coins"] -= 30; d["power"] += 5; save_json(DATA_FILE, players)
def _buy_hp(inst):
    d = get_player(current_player)
    if d["coins"] >= 20: d["coins"] -= 20; d["hp"] += 20; save_json(DATA_FILE, players)
def _school_task(inst):
    app = App.get_running_app().root.get_screen("school")
    a, b = random.randint(1, 20), random.randint(1, 20)
    app.task = a + b
    app.info.text = "Реши: %d + %d = ?" % (a, b)
def _school_check(inst):
    app = App.get_running_app().root.get_screen("school")
    try:
        if not hasattr(app, "task") or app.task is None: return
        ans = int(app.answer_inp.text.strip())
        if ans == app.task:
            d = get_player(current_player); r = random.randint(10, 30)
            d["coins"] += r; d["school_solved"] = d.get("school_solved", 0) + 1
            save_json(DATA_FILE, players)
            app.info.text = "✅ +%d! Следующее:" % r
            _school_task(None)
        else:
            app.info.text = "❌ Неправильно!"
    except: app.info.text = "❌ Введи число!"

def _chest_buy(chest_name):
    def handler(inst):
        d = get_player(current_player)
        ch = CHESTS[chest_name]
        currency = ch['currency']
        price = ch['price']
        if currency == "coins":
            if d['coins'] < price: show_popup("📦", "Мало монет!"); return
            d['coins'] -= price
        else:
            if d.get('titanite',0) < price: show_popup("📦", "Мало Титанита!"); return
            d['titanite'] -= price
        r_coins = random.randint(ch['min'], ch['max'])
        d['coins'] += r_coins
        result = "+%d💰" % r_coins
        if random.random() < ch['soul_chance']:
            s = random.randint(ch['soul_min'], ch['soul_max'])
            d['souls'] = d.get('souls',0) + s
            result += "\n+%d💜" % s
        if random.random() < ch['titan_chance']:
            t = random.randint(5, 50)
            d['titanite'] = d.get('titanite',0) + t
            result += "\n+%d💠" % t
        d['chests_opened'] = d.get('chests_opened',0) + 1
        check_achievements(d)
        save_json(DATA_FILE, players)
        show_popup("📦 %s" % chest_name, result)
    return handler

def _daily_claim(inst):
    d = get_player(current_player)
    today = datetime.now().strftime("%Y-%m-%d")
    if d.get("daily_claimed") == today:
        show_popup("🎁", "Уже получено!"); return
    d["daily_claimed"] = today
    d["daily_streak"] = d.get("daily_streak", 0) + 1
    streak = d["daily_streak"]
    coins = 100 + streak * 20
    titanite = 5 + streak
    souls = 2 + streak // 3
    d["coins"] += coins
    d["titanite"] = d.get("titanite",0) + titanite
    d["souls"] = d.get("souls",0) + souls
    wt_add_doubler(d, 1)
    new = check_achievements(d)
    save_json(DATA_FILE, players)
    msg = "День %d/500\n+%d💰 +%d💠 +%d💜 +1🎖️" % (streak, coins, titanite, souls)
    if new: msg += "\n🏅 " + ", ".join(new)
    show_popup("🎁 Ежедневный", msg)

def _quest_get(inst):
    q = random.choice([("Выиграй 3 боя", 100), ("Собери 500 монет", 150), ("Открой 2 кейса", 80)])
    show_popup("📋 Квест", "%s\nНаграда: %d" % q)
def _boss_fight(inst):
    d = get_player(current_player)
    bh = 100 + d["hp"] + d["power"] * 2
    pd = 25 + d["power"] // 2; bd = 10 + d["level"] // 2
    ph = d["hp"] + d["power"] * 2
    while bh > 0 and ph > 0:
        bh -= pd
        if bh <= 0:
            r = random.randint(200, 600); d["coins"] += r
            d["boss_defeated"] = d.get("boss_defeated", 0) + 1
            new = check_achievements(d)
            save_json(DATA_FILE, players)
            msg = "🎉 +%d💰" % r
            if new: msg += "\n🏅 " + ", ".join(new)
            show_popup("👹 Босс", msg); return
        ph -= bd
    show_popup("👹 Босс", "💀 Поражение!")
def _world_go(inst):
    d = get_player(current_player)
    if d["coins"] < 50: return
    d["coins"] -= 50; r = random.randint(50, 200); d["coins"] += r
    save_json(DATA_FILE, players); show_popup("🌍 Мир", "+%d💰" % r)
def _eco_to2(inst):
    d = get_player(current_player)
    if d["coins"] < 100: return
    d["coins"] -= 100; d["second_account"] = d.get("second_account", 0) + 100
    save_json(DATA_FILE, players)
def _eco_from2(inst):
    d = get_player(current_player); a = d.get("second_account", 0)
    if a <= 0: return
    d["coins"] += a; d["second_account"] = 0; save_json(DATA_FILE, players)
def _clan_create(inst):
    app = App.get_running_app().root.get_screen("clans")
    n = app.clan_inp.text.strip() if hasattr(app, "clan_inp") else ""
    if not n: return
    d = get_player(current_player)
    if d["coins"] < 500: return
    d["coins"] -= 500; d["clan"] = n; save_json(DATA_FILE, players)
    show_popup("👥 Клан", "Создан: %s" % n)
def _clan_leave(inst):
    d = get_player(current_player); d["clan"] = None
    save_json(DATA_FILE, players); show_popup("👥 Клан", "Вы вышли")
def _arena_fight(inst):
    d = get_player(current_player)
    if d["coins"] < 50: return
    d["coins"] -= 50
    e = random.randint(800, 1200); p = d.get("arena_rating", 1000)
    if random.random() < p / (p + e):
        r = random.randint(100, 300); d["coins"] += r; d["arena_rating"] = p + 10
        show_popup("⚔️ Арена", "🎉 +%d💰" % r)
    else:
        d["arena_rating"] = max(0, p - 5); show_popup("⚔️ Арена", "💀 Поражение")
    save_json(DATA_FILE, players)
def _event_claim(inst):
    d = get_player(current_player); r = random.randint(50, 200)
    d["coins"] += r; save_json(DATA_FILE, players)
    show_popup("🎉 Событие", "+%d💰" % r)
def _bank_dep(inst):
    d = get_player(current_player)
    if d["coins"] < 1000: return
    d["coins"] -= 1000
    d["bank"]["deposit"] = d["bank"].get("deposit", 0) + 1000
    d["bank"]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_json(DATA_FILE, players)
def _bank_wit(inst):
    d = get_player(current_player); dep = d["bank"].get("deposit", 0)
    if dep <= 0: return
    try:
        dd = datetime.strptime(d["bank"].get("date",""), "%Y-%m-%d %H:%M")
        days = (datetime.now() - dd).days
        dep += int(dep * days * 0.1)
    except: pass
    d["coins"] += dep; d["bank"]["deposit"] = 0; d["bank"]["date"] = ""
    save_json(DATA_FILE, players)
def _craft(inst):
    d = get_player(current_player)
    if d.get("crystals", 0) < 5: return
    d["crystals"] -= 5; d["ingots"] = d.get("ingots", 0) + 1
    save_json(DATA_FILE, players); show_popup("🔨", "✅ Слиток!")
def _market_sell(inst):
    d = get_player(current_player)
    if d.get("ingots", 0) < 1: return
    d["ingots"] -= 1; d["coins"] += 200; save_json(DATA_FILE, players)
def _market_buy(inst):
    d = get_player(current_player)
    if d["coins"] < 300: return
    d["coins"] -= 300; d["crystals"] = d.get("crystals", 0) + 1
    save_json(DATA_FILE, players)
def _guild_create(inst):
    d = get_player(current_player)
    if d["coins"] < 1000: return
    d["coins"] -= 1000; d["guild"] = "Гильдия_" + current_player
    save_json(DATA_FILE, players); show_popup("🏛️", "Гильдия создана!")
def _guild_leave(inst):
    d = get_player(current_player); d["guild"] = None
    save_json(DATA_FILE, players)

# ============================================================
# ПРОСТЫЕ ЭКРАНЫ
# ============================================================
class SchoolScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="🎓 ШКОЛА", font_size=38, bold=True, color=(0.4,0.8,0.2,1)))
        self.info = Label(text="Нажми «Получить задание»", font_size=22, color=(0.9,0.9,0.9,1), size_hint_y=0.18)
        L.add_widget(self.info)
        self.answer_inp = TextInput(hint_text="Ответ", multiline=False, font_size=28, size_hint_y=0.12)
        L.add_widget(self.answer_inp)
        b1 = BigButton(text="📚 ЗАДАНИЕ", background_color=(0.2,0.5,0.8,1))
        b1.bind(on_press=_school_task); L.add_widget(b1)
        b2 = BigButton(text="✅ ПРОВЕРИТЬ", background_color=(0.2,0.6,0.2,1))
        b2.bind(on_press=_school_check); L.add_widget(b2)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back)
        self.add_widget(L)
        self.task = None

class ClansScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="👥 КЛАНЫ", font_size=38, bold=True, color=(0.3,0.6,0.3,1)))
        self.info = Label(text="", font_size=22, color=(0.9,0.9,0.9,1), size_hint_y=0.15)
        L.add_widget(self.info)
        self.clan_inp = TextInput(hint_text="Название клана", multiline=False, font_size=26, size_hint_y=0.10)
        L.add_widget(self.clan_inp)
        b1 = BigButton(text="🏗️ СОЗДАТЬ (500)", background_color=(0.2,0.5,0.2,1))
        b1.bind(on_press=_clan_create); L.add_widget(b1)
        b2 = BigButton(text="🚪 ПОКИНУТЬ", background_color=(0.8,0.2,0.2,1))
        b2.bind(on_press=_clan_leave); L.add_widget(b2)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back); self.add_widget(L)

    def on_enter(self):
        if not current_player: return
        d = get_player(current_player)
        self.info.text = "Клан: %s" % (d.get("clan") or "нет")

ShopScreen = make_screen("🛒 МАГАЗИН", (1,0.8,0.2,1),
    lambda d: "💰 %d | 💪 %d | ❤️ %d" % (d['coins'], d['power'], d['hp']),
    lambda s: [("💪 СИЛА +5 (30)", (0.2,0.5,0.2,1), _buy_power),
               ("❤️ HP +20 (20)", (0.5,0.2,0.2,1), _buy_hp)])

ChestsScreen = make_screen("📦 КЕЙСЫ", (0.8,0.4,0.6,1),
    lambda d: "💰 %d | 💠 %d | 💜 %d\nОткрыто: %d" % (
        d['coins'], d.get('titanite',0), d.get('souls',0), d.get('chests_opened',0)),
    lambda s: [
        ("📦 Обычный (200💰)", (0.4,0.5,0.4,1), _chest_buy("Обычный")),
        ("📦 Редкий (1000💰)", (0.3,0.5,0.7,1), _chest_buy("Редкий")),
        ("📦 Легендарный (100💠)", (0.7,0.5,0.2,1), _chest_buy("Легендарный")),
    ])

DailyScreen = make_screen("🎁 ЕЖЕДНЕВНЫЕ", (0.8,0.4,0.2,1),
    lambda d: "День: %d/500\nСегодня: %s\nСтатус: %s" % (
        d.get('daily_streak',0), datetime.now().strftime("%Y-%m-%d"),
        "✅" if d.get("daily_claimed") == datetime.now().strftime("%Y-%m-%d") else "❌"),
    lambda s: [("🎲 ПОЛУЧИТЬ", (0.2,0.6,0.2,1), _daily_claim)])

QuestScreen = make_screen("📋 КВЕСТЫ", (0.3,0.8,0.6,1),
    lambda d: "Заданий: %d" % d.get('school_solved', 0),
    lambda s: [("🔄 НОВЫЙ КВЕСТ", (0.2,0.4,0.6,1), _quest_get)])

BossScreen = make_screen("👹 БОСС", (0.8,0.2,0.2,1),
    lambda d: "❤️ HP: %d | 💪 Урон: %d\nПобед: %d" % (
        d['hp'] + d['power']*2, 25 + d['power']//2, d.get('boss_defeated',0)),
    lambda s: [("⚔️ СРАЖАТЬСЯ", (0.6,0.1,0.1,1), _boss_fight)])

WorldMapScreen = make_screen("🌍 ОТКРЫТЫЙ МИР", (0.2,0.8,0.6,1),
    lambda d: "💰 %d" % d['coins'],
    lambda s: [("🌲 ЛЕС (50)", (0.3,0.5,0.3,1), _world_go),
               ("🏭 ЗАВОД (100)", (0.4,0.4,0.4,1), _world_go)])

EconomyScreen = make_screen("💹 ЭКОНОМИКА", (0.2,0.8,0.6,1),
    lambda d: "💰 Осн: %d | 🔄 2-й: %d" % (d['coins'], d.get('second_account',0)),
    lambda s: [("📤 НА 2-Й (100)", (0.2,0.4,0.6,1), _eco_to2),
               ("📥 СНЯТЬ", (0.6,0.4,0.2,1), _eco_from2)])

FriendsScreen = make_screen("🤝 ДРУЗЬЯ", (0.6,0.3,0.6,1),
    lambda d: "Друзья: %s" % (", ".join(d.get('friends',[])) or "нет"), lambda s: [])

SupportScreen = make_screen("📧 ПОДДЕРЖКА", (0.2,0.8,0.4,1),
    lambda d: "support@steelline.com", lambda s: [])

CompanyScreen = make_screen("🏢 КОМПАНИЯ", (0.8,0.6,0.2,1),
    lambda d: "Текущая: %s" % d.get('company','Роботы'), lambda s: [])

SettingsScreen = make_screen("⚙️ НАСТРОЙКИ", (0.5,0.5,0.5,1),
    lambda d: "Звук: Вкл\nЯзык: Русский", lambda s: [])

StatsScreen = make_screen("📊 СТАТИСТИКА", (0.6,0.3,0.3,1),
    lambda d: "%s\n⭐ %d | ⚔️ %d | 🏆 %d\n💪 %d\n💰 %d | 💠 %d | 💜 %d" % (
        current_player, d['level'], d['battles'], d['wins'], d['power'],
        d['coins'], d.get('titanite',0), d.get('souls',0)), lambda s: [])

RatingScreen = make_screen("🏆 РЕЙТИНГ", (0.3,0.6,0.6,1),
    lambda d: "🏆 ТОП:\n" + "\n".join(["%d. %s — %d" % (i, n, p.get('wins',0))
        for i,(n,p) in enumerate(sorted(players.items(), key=lambda x: x[1].get('wins',0), reverse=True)[:8], 1)]),
    lambda s: [])

CharactersScreen = make_screen("👾 ПЕРСОНАЖИ", (0.2,0.5,0.8,1),
    lambda d: "\n".join(d.get('characters', [])), lambda s: [])

ArenaScreen = make_screen("⚔️ АРЕНА", (0.6,0.2,0.4,1),
    lambda d: "🏆 Рейтинг: %d | 💰 %d" % (d.get('arena_rating',1000), d['coins']),
    lambda s: [("⚡ БОЙ (50)", (0.6,0.2,0.2,1), _arena_fight)])

EventsScreen = make_screen("🎉 СОБЫТИЯ", (0.8,0.6,0.2,1),
    lambda d: "🔥 'Весенний шторм'",
    lambda s: [("🎁 ЗАБРАТЬ", (0.2,0.6,0.2,1), _event_claim)])

ReplayScreen = make_screen("🎥 РЕПЛЕЙ", (0.4,0.2,0.6,1),
    lambda d: "Последние бои: %d" % d['battles'], lambda s: [])

BankScreen = make_screen("🏦 БАНК", (0.8,0.6,0.2,1),
    lambda d: "💰 Депозит: %d" % d['bank'].get('deposit',0),
    lambda s: [("📥 ВНЕСТИ (1000)", (0.2,0.6,0.2,1), _bank_dep),
               ("📤 СНЯТЬ +%", (0.6,0.4,0.2,1), _bank_wit)])

CraftScreen = make_screen("🔨 КРАФТ", (0.6,0.4,0.8,1),
    lambda d: "💎 %d | 🔩 %d" % (d.get('crystals',0), d.get('ingots',0)),
    lambda s: [("⚒️ СКРАФТИТЬ (5💎)", (0.2,0.5,0.2,1), _craft)])

CalendarScreen = make_screen("📅 КАЛЕНДАРЬ", (0.2,0.6,0.8,1),
    lambda d: "500 дней наград!\nДень: %d" % d.get('daily_streak',0), lambda s: [])

GuildsScreen = make_screen("🏛️ ГИЛЬДИИ", (0.8,0.4,0.4,1),
    lambda d: "Гильдия: %s" % (d.get('guild') or "нет"),
    lambda s: [("🏗️ СОЗДАТЬ (1000)", (0.2,0.5,0.2,1), _guild_create),
               ("🚪 ПОКИНУТЬ", (0.8,0.2,0.2,1), _guild_leave)])

MarketScreen = make_screen("🏪 РЫНОК", (0.4,0.6,0.2,1),
    lambda d: "💰 %d | 💎 %d | 🔩 %d" % (d['coins'], d.get('crystals',0), d.get('ingots',0)),
    lambda s: [("💰 ПРОДАТЬ СЛИТОК (200)", (0.2,0.5,0.2,1), _market_sell),
               ("🛒 КУПИТЬ КРИСТАЛЛ (300)", (0.2,0.4,0.6,1), _market_buy)])

# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class SteelLineApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        self.main_screen = MainScreen(name='main')
        sm.add_widget(self.main_screen)
        sm.add_widget(NewsScreen(name='news'))
        sm.add_widget(HangarScreen(name='hangar'))
        sm.add_widget(SkinsScreen(name='skins'))
        sm.add_widget(AchievementsScreen(name='achievements'))
        sm.add_widget(BattleScreen(name='battle'))
        sm.add_widget(WarThunderScreen(name='warthunder'))
        sm.add_widget(MiniGameScreen(name='minigame'))
        sm.add_widget(SchoolScreen(name='school'))
        sm.add_widget(ClansScreen(name='clans'))
        sm.add_widget(ShopScreen(name='shop'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(ChestsScreen(name='chests'))
        sm.add_widget(QuestScreen(name='quest'))
        sm.add_widget(BossScreen(name='boss'))
        sm.add_widget(WorldMapScreen(name='world'))
        sm.add_widget(EconomyScreen(name='economy'))
        sm.add_widget(FriendsScreen(name='friends'))
        sm.add_widget(SupportScreen(name='support'))
        sm.add_widget(CompanyScreen(name='company'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(StatsScreen(name='stats'))
        sm.add_widget(RatingScreen(name='rating'))
        sm.add_widget(DailyScreen(name='daily'))
        sm.add_widget(CharactersScreen(name='characters'))
        sm.add_widget(ArenaScreen(name='arena'))
        sm.add_widget(EventsScreen(name='events'))
        sm.add_widget(ReplayScreen(name='replay'))
        sm.add_widget(BankScreen(name='bank'))
        sm.add_widget(CraftScreen(name='craft'))
        sm.add_widget(CalendarScreen(name='calendar'))
        sm.add_widget(GuildsScreen(name='guilds'))
        sm.add_widget(MarketScreen(name='market'))
        sm.current = 'login'
        return sm

    def play_music(self):
        try:
            p = res_path("game/sound/biskas.zelye.ogg")
            if not os.path.exists(p):
                p = res_path("game/sound/biskas.zelye.mp3")
            if os.path.exists(p):
                self._music = SoundLoader.load(p)
                if self._music:
                    self._music.loop = True
                    self._music.play()
                    print("🎵 Музыка играет:", p)
                else:
                    print("❌ Не удалось загрузить:", p)
            else:
                print("❌ Файл не найден")
        except Exception as e:
            print("❌ Music error:", e)

    def on_start(self):
        try:
            lu = settings.get("last_user", ""); lp = settings.get("last_password", "")
            if lu and lp and lu in players and players[lu].get("password","") == lp:
                global current_player
                current_player = lu
                self.main_screen.update_info()
                self.root.current = 'main'
            self.play_music()
        except Exception as e: print("on_start:", e)

if __name__ == '__main__':
    SteelLineApp().run()