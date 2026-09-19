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
from kivy.utils import platform
from kivy.resources import resource_find
import json, os, random
import webbrowser
from datetime import datetime, timedelta

try:
    if platform != 'android': Window.fullscreen = 'auto'
except: pass

GAME_NAME = "БРОНЕЛОМ"
GAME_VERSION = "12.3.1"
GAME_COPYRIGHT = "© Автор: Мухаммад. Все права защищены."
SITE_URL = "https://majidovmuhammad23774.github.io/Frontier-site"

def res_path(rel):
    try: return resource_find(rel) or rel
    except: return rel

def get_data_dir():
    try: return App.get_running_app().user_data_dir
    except: return "."

for folder in ["game", "game/images", "game/sound"]:
    try:
        if not os.path.exists(folder): os.makedirs(folder)
    except: pass

DATA_FILE = os.path.join(get_data_dir(), "players.json")
SETTINGS_FILE = os.path.join(get_data_dir(), "settings.json")

def load_json(f, d):
    try:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as file: return json.load(file)
    except: pass
    return d

def save_json(f, d):
    try:
        with open(f, 'w', encoding='utf-8') as file: json.dump(d, file, ensure_ascii=False, indent=4)
    except: pass

players = load_json(DATA_FILE, {})
settings = load_json(SETTINGS_FILE, {"last_user": "", "last_password": "", "premium_infinity_uses": 0})
current_player = None
ADMINS = ["muhammad", "мухаммад"]
def is_admin(u): return u and u.lower() in ADMINS

TANKS = {
    "Т-34": {"hp": 100, "power": 10, "price": 0, "color": (0.4,0.6,0.3,1)},
    "КВ-1": {"hp": 140, "power": 14, "price": 3000, "color": (0.5,0.5,0.3,1)},
    "ИС-7": {"hp": 180, "power": 22, "price": 8000, "color": (0.3,0.4,0.5,1)},
    "Тигр II": {"hp": 160, "power": 18, "price": 6000, "color": (0.6,0.5,0.3,1)},
}
SKINS = {
    "Стандарт": {"price": 0, "bonus": 0, "color": (0.5,0.5,0.5,1)},
    "Пустыня": {"price": 500, "bonus": 2, "color": (0.8,0.7,0.4,1)},
    "Зима": {"price": 700, "bonus": 3, "color": (0.9,0.9,0.95,1)},
    "Ночь": {"price": 1000, "bonus": 4, "color": (0.2,0.2,0.4,1)},
    "Кровь": {"price": 1500, "bonus": 6, "color": (0.7,0.1,0.1,1)},
    "Золото": {"price": 3000, "bonus": 10, "color": (1,0.85,0.2,1)},
    "Робот": {"price": 4000, "bonus": 12, "color": (0.5,0.5,0.6,1)},
}
TITLES = {
    "Новичок": {"unlock": 0, "desc": "Начало пути"},
    "Танкист": {"unlock": 10, "desc": "10 боёв"},
    "Ветеран": {"unlock": 50, "desc": "50 боёв"},
    "Мастер": {"unlock": 100, "desc": "100 боёв"},
    "Гроза Врагов": {"unlock": 250, "desc": "250 боёв"},
    "Легенда": {"unlock": 500, "desc": "500 боёв"},
    "Стальной Лорд": {"unlock": 1000, "desc": "1000 боёв"},
    "Хранитель": {"unlock": 5000, "desc": "5000 боёв"},
}
ACHIEVEMENTS = {
    "first_battle": {"name": "Первый бой", "desc": "Провести 1 бой", "reward": 100, "souls": 5},
    "win_10": {"name": "Победитель", "desc": "Выиграть 10 боёв", "reward": 500, "souls": 20},
    "win_50": {"name": "Полководец", "desc": "Выиграть 50 боёв", "reward": 2000, "souls": 100},
    "win_100": {"name": "Легенда", "desc": "Выиграть 100 боёв", "reward": 5000, "souls": 250},
    "rich_10k": {"name": "Богач", "desc": "Накопить 10000 монет", "reward": 1000, "souls": 50},
    "daily_7": {"name": "Постоянный", "desc": "7 дней входов", "reward": 800, "souls": 40},
    "daily_30": {"name": "Верный", "desc": "30 дней входов", "reward": 3000, "souls": 150},
    "tank_master": {"name": "Танковед", "desc": "Купить 3 танка", "reward": 2000, "souls": 100},
    "chests_10": {"name": "Кладоискатель", "desc": "Открыть 10 кейсов", "reward": 1500, "souls": 75},
    "boss_5": {"name": "Гроза Боссов", "desc": "Победить 5 боссов", "reward": 2500, "souls": 120},
    "robot_master": {"name": "🤖 Восстание машин", "desc": "Купить скин Робот", "reward": 3000, "souls": 300},
}
CHESTS = {
    "Обычный": {"price": 200, "currency": "coins", "min": 100, "max": 500, "soul_chance": 0.1, "soul_min": 1, "soul_max": 3, "titan_chance": 0.05},
    "Редкий": {"price": 1000, "currency": "coins", "min": 500, "max": 2500, "soul_chance": 0.3, "soul_min": 5, "soul_max": 15, "titan_chance": 0.15},
    "Легендарный": {"price": 100, "currency": "titanite", "min": 3000, "max": 15000, "soul_chance": 0.8, "soul_min": 20, "soul_max": 80, "titan_chance": 0.5},
}

def check_achievements(d):
    try:
        if "achievements" not in d: d["achievements"] = []
        new = []
        conds = {
            "first_battle": d.get("battles", 0) >= 1, "win_10": d.get("wins", 0) >= 10,
            "win_50": d.get("wins", 0) >= 50, "win_100": d.get("wins", 0) >= 100,
            "rich_10k": d.get("coins", 0) >= 10000, "daily_7": d.get("daily_streak", 0) >= 7,
            "daily_30": d.get("daily_streak", 0) >= 30, "tank_master": d.get("tanks_bought", 0) >= 3,
            "chests_10": d.get("chests_opened", 0) >= 10, "boss_5": d.get("boss_defeated", 0) >= 5,
            "robot_master": "Робот" in d.get("skins", []),
        }
        for key, ok in conds.items():
            if ok and key not in d["achievements"]:
                d["achievements"].append(key); ach = ACHIEVEMENTS[key]
                d["coins"] += ach["reward"]; d["souls"] = d.get("souls", 0) + ach["souls"]
                new.append(ach["name"])
        if new: save_json(DATA_FILE, players)
        return new
    except: return []

def get_titles_for(d):
    b = d.get("battles", 0); return [t for t, i in TITLES.items() if b >= i["unlock"]]

def get_player(u):
    if u not in players:
        players[u] = {"password": "", "coins": 5000, "titanite": 500, "souls": 50,
                      "level": 1, "exp": 0, "power": 10, "hp": 100, "battles": 0, "wins": 0,
                      "current_tank": "Т-34", "tanks": ["Т-34"], "current_skin": "Стандарт",
                      "skins": ["Стандарт"], "current_title": "Новичок", "achievements": [],
                      "daily_claimed": "", "daily_streak": 0, "chests_opened": 0,
                      "boss_defeated": 0, "boss_count": 0, "boss_date": "",
                      "calendar_claimed": "", "tanks_bought": 1, "arena_rating": 1000,
                      "crystals": 100, "ingots": 0, "bank": {"deposit": 0, "date": ""},
                      "clan": None, "friends": [], "guild": None, "second_account": 0,
                      "school_solved": 0, "characters": ["Базовый Робот"],
                      "premium_infinite": False, "lang": "Русский",
                      "company": "Роботы"}
        if is_admin(u): players[u]["characters"].append("Дафак Бума")
        save_json(DATA_FILE, players)
    else:
        d = players[u]
        for k, v in [("titanite", 500), ("souls", 50), ("achievements", []), ("daily_streak", 0),
                     ("tanks", ["Т-34"]), ("skins", ["Стандарт"]), ("current_tank", "Т-34"),
                     ("current_skin", "Стандарт"), ("current_title", "Новичок"), ("tanks_bought", 1),
                     ("arena_rating", 1000), ("crystals", 100), ("ingots", 0),
                     ("bank", {"deposit": 0, "date": ""}), ("clan", None), ("friends", []),
                     ("guild", None), ("second_account", 0), ("school_solved", 0),
                     ("boss_count", 0), ("boss_date", ""), ("calendar_claimed", ""),
                     ("premium_infinite", False), ("lang", "Русский"),
                     ("company", "Роботы"), ("characters", ["Базовый Робот"])]:
            if k not in d: d[k] = v
    return players[u]

def show_popup(title, text):
    try:
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text=text, font_size=24))
        btn = Button(text="OK", font_size=28, size_hint_y=0.3)
        popup = Popup(title=title, content=layout, size_hint=(0.85, 0.5))
        btn.bind(on_press=popup.dismiss); layout.add_widget(btn); popup.open()
    except: pass

def is_premium(d): return bool(d.get("premium_infinite", False))
def premium_status(d): return "👑 Премиум: БЕСКОНЕЧНО" if is_premium(d) else "👤 Обычный игрок"

def activate_promo(code):
    d = get_player(current_player)
    code = code.strip().upper().replace(" ", "").replace("_", "")
    uses = settings.get("premium_infinity_uses", 0)
    if code in ["PREMIUMINFINITY", "ПРЕМИУМИНФИНИТИ", "INFINITY"]:
        if uses >= 10: return "🚫 ПРОМОКОД В ЧЁРНОМ СПИСКЕ!\nЛимит: 10/10."
        if d.get("premium_infinite"): return "∞ У тебя уже бесконечный премиум!"
        d["premium_infinite"] = True
        settings["premium_infinity_uses"] = uses + 1
        save_json(DATA_FILE, players); save_json(SETTINGS_FILE, settings)
        return "👑 ПРЕМИУМ АКТИВИРОВАН!\nОсталось: %d/10" % (10 - (uses + 1))
    return "❌ Неверный промокод\n\nПодсказка: PREMIUM INFINITY"

class BigButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 22; self.size_hint_y = None; self.height = 58
        self.color = (1, 1, 1, 1); self.bold = True

def make_screen(title, color, info_fn, buttons_fn):
    class _S(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = BoxLayout(orientation='vertical', padding=15, spacing=8)
            layout.add_widget(Label(text=title, font_size=36, bold=True, color=color, size_hint_y=0.08))
            self.info = Label(text="", font_size=20, color=(0.9,0.9,0.9,1), size_hint_y=0.2)
            layout.add_widget(self.info)
            scroll = ScrollView(size_hint=(1, 0.62))
            box = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
            box.bind(minimum_height=box.setter('height'))
            for txt, col, fn in buttons_fn(self):
                b = BigButton(text=txt, background_color=col); b.bind(on_press=fn); box.add_widget(b)
            scroll.add_widget(box); layout.add_widget(scroll)
            back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.08)
            back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
            layout.add_widget(back); self.add_widget(layout)
        def on_enter(self):
            try:
                if current_player: self.info.text = info_fn(get_player(current_player))
            except Exception as e: self.info.text = "Ошибка: %s" % e
    return _S

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ml = FloatLayout()
        BG = res_path("game/images/titan60.jpg")
        if os.path.exists(BG):
            try: ml.add_widget(Image(source=BG, allow_stretch=True, keep_ratio=False))
            except: pass
        L = BoxLayout(orientation='vertical', padding=40, spacing=14, size_hint=(0.85, 0.85), pos_hint={'center_x':0.5, 'center_y':0.5})
        L.add_widget(Label(text=GAME_NAME, font_size=44, bold=True, color=(1,0.85,0.2,1), size_hint_y=0.12))
        L.add_widget(Label(text="© Все права защищены", font_size=13, color=(0.7,0.7,0.7,1), size_hint_y=0.05))
        self.info = Label(text="Вход в игру", font_size=20, color=(0.9,0.9,0.9,1), size_hint_y=0.07); L.add_widget(self.info)
        self.u = TextInput(hint_text="Никнейм", multiline=False, font_size=26, size_hint_y=0.1, background_color=(0.2,0.2,0.2,0.9), foreground_color=(1,1,1,1)); L.add_widget(self.u)
        self.p = TextInput(hint_text="Пароль", multiline=False, password=True, font_size=26, size_hint_y=0.1, background_color=(0.2,0.2,0.2,0.9), foreground_color=(1,1,1,1)); L.add_widget(self.p)
        b1 = BigButton(text="ВХОД!", background_color=(0.2,0.6,0.2,1)); b1.bind(on_press=self.do_login); L.add_widget(b1)
        b2 = BigButton(text="РЕГИСТРАЦИЯ", background_color=(0.2,0.4,0.8,1)); b2.bind(on_press=self.do_register); L.add_widget(b2)
        b3 = BigButton(text="ГОСТЬ", background_color=(0.5,0.5,0.5,1)); b3.bind(on_press=self.do_guest); L.add_widget(b3)
        ml.add_widget(L); self.add_widget(ml)
    def do_login(self, inst):
        try:
            name = self.u.text.strip(); pwd = self.p.text.strip()
            if not name: self.info.text = "❌ Введите никнейм!"; return
            if name not in players: self.info.text = "❌ Не найден! Зарегистрируйся."; return
            if is_admin(name) and pwd != "2026": self.info.text = "❌ Неверный пароль!"; return
            d = get_player(name)
            if d["password"] and d["password"] != pwd: self.info.text = "❌ Неверный пароль!"; return
            global current_player; current_player = name
            settings["last_user"] = name; settings["last_password"] = pwd; save_json(SETTINGS_FILE, settings)
            app = App.get_running_app(); app.main_screen.update_info(); app.root.current = "main"
        except Exception as e: self.info.text = "Ошибка: %s" % e
    def do_register(self, inst):
        try:
            name = self.u.text.strip(); pwd = self.p.text.strip()
            if not name: self.info.text = "❌ Введите никнейм!"; return
            if len(pwd) < 3: self.info.text = "❌ Пароль минимум 3 символа!"; return
            if name in players and players[name].get("password"): self.info.text = "❌ Ник занят!"; return
            d = get_player(name); d["password"] = pwd; save_json(DATA_FILE, players)
            global current_player; current_player = name
            settings["last_user"] = name; settings["last_password"] = pwd; save_json(SETTINGS_FILE, settings)
            app = App.get_running_app(); app.main_screen.update_info(); app.root.current = "main"
        except Exception as e: self.info.text = "Ошибка: %s" % e
    def do_guest(self, inst):
        try:
            gname = "Гость_%d" % random.randint(1000, 9999)
            d = get_player(gname); d["password"] = ""; save_json(DATA_FILE, players)
            global current_player; current_player = gname
            app = App.get_running_app(); app.main_screen.update_info(); app.root.current = "main"
        except Exception as e: self.info.text = "Ошибка: %s" % e

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ml = FloatLayout()
        BG = res_path("game/images/titan60.jpg")
        if os.path.exists(BG):
            try: ml.add_widget(Image(source=BG, allow_stretch=True, keep_ratio=False))
            except: pass
        L = BoxLayout(orientation='vertical', padding=15, spacing=8, size_hint=(0.92, 0.94), pos_hint={'center_x':0.5, 'center_y':0.5})
        self.info_label = Label(text="", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.12); L.add_widget(self.info_label)
        scroll = ScrollView(size_hint=(1, 0.84))
        grid = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        btns = [
            ("НОВОСТИ", (0.9,0.5,0.1,1), "news"),
            ("В БОЙ!", (0.2,0.6,0.2,1), "battle"),
            ("АНГАР", (0.4,0.6,0.3,1), "hangar"),
            ("СКИНЫ", (0.7,0.3,0.7,1), "skins"),
            ("ДОСТИЖЕНИЯ", (0.9,0.7,0.2,1), "achievements"),
            ("ПРОФИЛЬ", (0.3,0.3,0.5,1), "profile"),
            ("КЕЙСЫ", (0.8,0.4,0.6,1), "chests"),
            ("ЕЖЕДНЕВНЫЕ", (0.8,0.4,0.2,1), "daily"),
            ("ПРОМОКОДЫ", (1,0.8,0.2,1), "promo"),
            ("МАГАЗИН", (0.2,0.4,0.6,1), "shop"),
            ("ШКОЛА", (0.2,0.8,0.4,1), "school"),
            ("КВЕСТЫ", (0.8,0.4,0.2,1), "quest"),
            ("БОСС", (0.8,0.2,0.2,1), "boss"),
            ("ОТКРЫТЫЙ МИР", (0.2,0.4,0.8,1), "world"),
            ("ЭКОНОМИКА", (0.2,0.8,0.6,1), "economy"),
            ("КЛАНЫ", (0.3,0.6,0.3,1), "clans"),
            ("ДРУЗЬЯ", (0.6,0.3,0.6,1), "friends"),
            ("ПОДДЕРЖКА", (0.2,0.8,0.4,1), "support"),
            ("🌐 САЙТ ИГРЫ", (0.2,0.7,0.9,1), "SITE"),
            ("КОМПАНИЯ", (0.8,0.6,0.2,1), "company"),
            ("НАСТРОЙКИ", (0.5,0.5,0.5,1), "settings"),
            ("СТАТИСТИКА", (0.6,0.3,0.3,1), "stats"),
            ("РЕЙТИНГ", (0.3,0.6,0.6,1), "rating"),
            ("ПЕРСОНАЖИ", (0.2,0.5,0.8,1), "characters"),
            ("АРЕНА", (0.6,0.2,0.4,1), "arena"),
            ("СОБЫТИЯ", (0.8,0.6,0.2,1), "events"),
            ("РЕПЛЕЙ", (0.4,0.2,0.6,1), "replay"),
            ("БАНК", (0.8,0.6,0.2,1), "bank"),
            ("КРАФТ", (0.6,0.4,0.8,1), "craft"),
            ("КАЛЕНДАРЬ", (0.2,0.6,0.8,1), "calendar"),
            ("ГИЛЬДИИ", (0.8,0.4,0.4,1), "guilds"),
            ("РЫНОК", (0.4,0.6,0.2,1), "market"),
            ("МИНИ-ИГРА", (0.9,0.3,0.5,1), "minigame"),
        ]
        for t, c, tgt in btns:
            b = BigButton(text=t, background_color=c)
            if tgt == "SITE":
                b.bind(on_press=_open_site)
            else:
                b.bind(on_press=lambda x, tt=tgt: setattr(App.get_running_app().root, "current", tt))
            grid.add_widget(b)
        scroll.add_widget(grid); L.add_widget(scroll)
        L.add_widget(Label(text="v" + GAME_VERSION + "  " + GAME_COPYRIGHT, font_size=12, color=(0.5,0.5,0.5,1), size_hint_y=0.04))
        ml.add_widget(L); self.add_widget(ml)
    def update_info(self):
        try:
            if not current_player: return
            d = get_player(current_player)
            prem = "👑 " if is_premium(d) else ""
            self.info_label.text = "%s%s | 💰%d | 💠%d | 💜%d | Ур.%d | %s" % (
                prem, current_player, d['coins'], d.get('titanite',0), d.get('souls',0), d['level'], d.get('current_title', 'Новичок'))
        except: pass

class HangarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=15, spacing=8)
        L.add_widget(Label(text="🚗 АНГАР", font_size=38, bold=True, color=(0.4,0.6,0.3,1), size_hint_y=0.08))
        self.info = Label(text="", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.15); L.add_widget(self.info)
        scroll = ScrollView(size_hint=(1, 0.69))
        self.box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter('height')); scroll.add_widget(self.box); L.add_widget(scroll)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.08)
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        try:
            if not current_player: return
            d = get_player(current_player)
            self.info.text = "💰 %d\nТекущий: %s" % (d['coins'], d.get('current_tank','Т-34'))
            self.box.clear_widgets()
            for name, info in TANKS.items():
                owned = name in d.get('tanks', [])
                if owned:
                    text = "✅ %s | HP:%d Сила:%d" % (name, info['hp'], info['power'])
                    col = info['color']; fn = lambda x, n=name: self.select(n)
                else:
                    text = "🔒 %s — %d💰" % (name, info['price'])
                    col = (0.4,0.4,0.4,1); fn = lambda x, n=name, p=info['price']: self.buy(n, p)
                b = BigButton(text=text, background_color=col); b.bind(on_press=fn); self.box.add_widget(b)
        except: pass
    def select(self, name):
        d = get_player(current_player); d['current_tank'] = name; save_json(DATA_FILE, players); show_popup("🚗", "Выбран: %s" % name); self.on_enter()
    def buy(self, name, price):
        d = get_player(current_player)
        if d['coins'] < price: show_popup("🚗", "Мало монет!"); return
        d['coins'] -= price; d['tanks'] = d.get('tanks', []) + [name]
        d['tanks_bought'] = d.get('tanks_bought', 0) + 1; d['current_tank'] = name
        save_json(DATA_FILE, players); new = check_achievements(d)
        show_popup("🚗 Куплен!", name + ("\n🏅 " + ", ".join(new) if new else "")); self.on_enter()

class SkinsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=15, spacing=8)
        L.add_widget(Label(text="🎨 СКИНЫ", font_size=38, bold=True, color=(0.7,0.3,0.7,1), size_hint_y=0.08))
        self.info = Label(text="", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.15); L.add_widget(self.info)
        scroll = ScrollView(size_hint=(1, 0.69))
        self.box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter('height')); scroll.add_widget(self.box); L.add_widget(scroll)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.08)
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        try:
            if not current_player: return
            d = get_player(current_player)
            self.info.text = "💰 %d | Текущий: %s" % (d['coins'], d.get('current_skin','Стандарт'))
            self.box.clear_widgets()
            for name, info in SKINS.items():
                owned = name in d.get('skins', ['Стандарт'])
                if owned:
                    text = "✅ %s | +%d" % (name, info['bonus']); col = info['color']; fn = lambda x, n=name: self.select(n)
                else:
                    text = "🔒 %s — %d💰" % (name, info['price']); col = (0.4,0.4,0.4,1); fn = lambda x, n=name, p=info['price']: self.buy(n, p)
                b = BigButton(text=text, background_color=col); b.bind(on_press=fn); self.box.add_widget(b)
        except: pass
    def select(self, name):
        d = get_player(current_player); d['current_skin'] = name; save_json(DATA_FILE, players); show_popup("🎨", "Выбран: %s" % name); self.on_enter()
    def buy(self, name, price):
        d = get_player(current_player)
        if d['coins'] < price: show_popup("🎨", "Мало монет!"); return
        d['coins'] -= price; d['skins'] = d.get('skins', []) + [name]; d['current_skin'] = name
        save_json(DATA_FILE, players); show_popup("🎨 Куплен!", name); self.on_enter()

class AchievementsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=15, spacing=8)
        L.add_widget(Label(text="🏅 ДОСТИЖЕНИЯ", font_size=38, bold=True, color=(0.9,0.7,0.2,1), size_hint_y=0.08))
        self.info = Label(text="", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.15); L.add_widget(self.info)
        scroll = ScrollView(size_hint=(1, 0.69))
        self.box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter('height')); scroll.add_widget(self.box); L.add_widget(scroll)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.08)
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        try:
            if not current_player: return
            d = get_player(current_player); done = d.get('achievements', [])
            self.info.text = "Открыто: %d/%d" % (len(done), len(ACHIEVEMENTS))
            self.box.clear_widgets()
            for key, info in ACHIEVEMENTS.items():
                if key in done: text = "✅ %s — %s" % (info['name'], info['desc']); col = (0.3,0.6,0.3,