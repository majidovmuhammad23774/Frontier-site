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

GAME_NAME = "СТАЛЬНОЙ РУБЕЖ"
GAME_VERSION = "12.3.0"
GAME_COPYRIGHT = "© Автор: Мухаммад. Все права защищены."
SITE_URL = "https://majidovmuhammad23774.github.io/Frontier-site"

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

# ============================================================
# ЭКРАНЫ
# ============================================================
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
                if key in done: text = "✅ %s — %s" % (info['name'], info['desc']); col = (0.3,0.6,0.3,1)
                else: text = "🔒 %s (+%d💰)" % (info['name'], info['reward']); col = (0.4,0.4,0.4,1)
                b = BigButton(text=text, background_color=col); self.box.add_widget(b)
        except: pass

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=15, spacing=8)
        L.add_widget(Label(text="👤 ПРОФИЛЬ", font_size=38, bold=True, color=(1,0.8,0.2,1), size_hint_y=0.08))
        self.info = Label(text="", font_size=19, color=(0.9,0.9,0.9,1), size_hint_y=0.3); L.add_widget(self.info)
        scroll = ScrollView(size_hint=(1, 0.54))
        self.box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter('height')); scroll.add_widget(self.box); L.add_widget(scroll)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1), size_hint_y=0.08)
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        try:
            if not current_player: return
            d = get_player(current_player)
            self.info.text = ("%s\n🏷️ %s\n%s\n💰 %d | 💠 %d | 💜 %d\n⚔️ %d боёв | 🏆 %d побед\n🚗 %s" % (
                current_player, d.get('current_title','Новичок'), premium_status(d), d['coins'], d.get('titanite',0), d.get('souls',0), d['battles'], d['wins'], d.get('current_tank','Т-34')))
            self.box.clear_widgets()
            for t in get_titles_for(d):
                col = (0.3,0.6,0.3,1) if t == d.get('current_title') else (0.4,0.5,0.7,1)
                b = BigButton(text="🏷️ %s" % t, background_color=col); b.bind(on_press=lambda x, tt=t: self.set_title(tt)); self.box.add_widget(b)
        except: pass
    def set_title(self, title):
        d = get_player(current_player); d['current_title'] = title; save_json(DATA_FILE, players); self.on_enter()

class BattleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=12, spacing=6)
        L.add_widget(Label(text="⚔️ БОЙ", font_size=34, bold=True, color=(1,0.8,0.2,1), size_hint_y=0.07))
        self.info_l = Label(text="", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.18); L.add_widget(self.info_l)
        self.hp_l = Label(text="", font_size=22, color=(0.9,0.9,0.9,1), size_hint_y=0.12); L.add_widget(self.hp_l)
        self.res_l = Label(text="Нажми ОГОНЬ!", font_size=20, color=(0.9,0.9,0.9,1), size_hint_y=0.13); L.add_widget(self.res_l)
        b = BigButton(text="ОГОНЬ!", background_color=(0.8,0.2,0.2,1)); b.bind(on_press=self.fire); L.add_widget(b)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)
        self.php = 0; self.ehp = 0
    def on_enter(self):
        try:
            if not current_player: return
            d = get_player(current_player)
            tank = TANKS.get(d.get('current_tank','Т-34'), TANKS['Т-34']); skin = SKINS.get(d.get('current_skin','Стандарт'), SKINS['Стандарт'])
            self.php = tank['hp'] + d['power'] * 2 + skin['bonus'] * 5; self.ehp = random.randint(40, 150) + d["level"] * 5; self.upd()
        except: pass
    def upd(self):
        try:
            d = get_player(current_player)
            self.info_l.text = "%s | %s" % (d.get('current_tank','Т-34'), d.get('current_skin','Стандарт'))
            self.hp_l.text = "❤️ Ты: %d\n👾 Враг: %d" % (self.php, self.ehp)
        except: pass
    def fire(self, i):
        try:
            if not current_player: return
            d = get_player(current_player)
            p_dmg = random.randint(10, 30) + d["power"] // 2; e_dmg = random.randint(5, 20) + d["level"] // 2
            self.ehp -= p_dmg; self.php -= e_dmg; self.res_l.text = "💥 Ты: %d | Враг: %d" % (p_dmg, e_dmg)
            if self.ehp <= 0:
                bonus = 100 if is_premium(d) else 50
                self.res_l.text = "🎉 ПОБЕДА! +%d💰" % bonus
                d["coins"] += bonus; d["exp"] += 10
                if d["exp"] >= 100: d["level"] += 1; d["exp"] = 0
                d["battles"] += 1; d["wins"] += 1
                new = check_achievements(d)
                if new: self.res_l.text += "\n🏅 " + ", ".join(new)
                save_json(DATA_FILE, players); self.on_enter(); return
            if self.php <= 0:
                self.res_l.text = "💀 ПОРАЖЕНИЕ... -20💰"
                d["coins"] = max(0, d["coins"] - 20); d["battles"] += 1
                check_achievements(d); save_json(DATA_FILE, players); self.on_enter(); return
            self.upd()
        except Exception as e: self.res_l.text = "Ошибка: %s" % e

# ============================================================
# ФУНКЦИИ КНОПОК
# ============================================================
def _open_site(inst):
    try:
        webbrowser.open(SITE_URL)
    except Exception as e:
        show_popup("🌐 Сайт", "Не удалось открыть браузер.\n\nСсылка:\n" + SITE_URL)

def _buy_power(inst):
    d = get_player(current_player)
    if d["coins"] >= 30: d["coins"] -= 30; d["power"] += 5; save_json(DATA_FILE, players)
def _buy_hp(inst):
    d = get_player(current_player)
    if d["coins"] >= 20: d["coins"] -= 20; d["hp"] += 20; save_json(DATA_FILE, players)

def _chest_buy(name):
    def h(inst):
        d = get_player(current_player); ch = CHESTS[name]; cur = ch['currency']; price = ch['price']
        if cur == "coins":
            if d['coins'] < price: show_popup("📦", "Мало монет!"); return
            d['coins'] -= price
        else:
            if d.get('titanite',0) < price: show_popup("📦", "Мало Титанита!"); return
            d['titanite'] -= price
        r = random.randint(ch['min'], ch['max']); d['coins'] += r; res = "+%d💰" % r
        if random.random() < ch['soul_chance']:
            s = random.randint(ch['soul_min'], ch['soul_max']); d['souls'] = d.get('souls',0) + s; res += "\n+%d💜" % s
        if random.random() < ch['titan_chance']:
            t = random.randint(5, 50); d['titanite'] = d.get('titanite',0) + t; res += "\n+%d💠" % t
        d['chests_opened'] = d.get('chests_opened',0) + 1
        check_achievements(d); save_json(DATA_FILE, players); show_popup("📦 %s" % name, res)
    return h

def _daily_claim(inst):
    d = get_player(current_player); today = datetime.now().strftime("%Y-%m-%d")
    if d.get("daily_claimed") == today: show_popup("🎁", "Уже получено!"); return
    d["daily_claimed"] = today; d["daily_streak"] = d.get("daily_streak", 0) + 1
    s = d["daily_streak"]; coins = 100 + s * 20
    d["coins"] += coins; d["titanite"] = d.get("titanite",0) + 5 + s
    new = check_achievements(d); save_json(DATA_FILE, players)
    msg = "День %d\n+%d💰" % (s, coins)
    if new: msg += "\n🏅 " + ", ".join(new)
    show_popup("🎁 Ежедневный", msg)

def _boss_fight(inst):
    d = get_player(current_player); today = datetime.now().strftime("%Y-%m-%d")
    if d.get("boss_date", "") != today: d["boss_date"] = today; d["boss_count"] = 0; save_json(DATA_FILE, players)
    boss_count = d.get("boss_count", 0)
    if boss_count >= 4:
        now = datetime.now(); tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        delta = tomorrow - now; hours = delta.seconds // 3600; minutes = (delta.seconds % 3600) // 60
        show_popup("👹 Босс", "🏁 Лимит на сегодня!\n\n⏰ Ждать: %d ч %d мин" % (hours, minutes)); return
    if boss_count % 2 == 0:
        r = 50; d["coins"] = d.get("coins", 0) + r
        d["boss_defeated"] = d.get("boss_defeated", 0) + 1; d["boss_count"] = boss_count + 1
        new = check_achievements(d); save_json(DATA_FILE, players)
        msg = "🎉 ПОБЕДА!\n+%d💰\n\n🎯 Осталось: %d" % (r, 3 - boss_count)
        if new: msg += "\n🏅 " + ", ".join(new)
        show_popup("👹 Босс", msg)
    else:
        d["boss_count"] = boss_count + 1; save_json(DATA_FILE, players)
        show_popup("👹 Босс", "💀 ПОРАЖЕНИЕ!\n\n🎯 Осталось: %d" % (3 - boss_count))
    try: App.get_running_app().root.get_screen("boss").on_enter()
    except: pass

def _arena_fight(inst):
    d = get_player(current_player)
    if d["coins"] < 50: return
    d["coins"] -= 50; e = random.randint(800, 1200); p = d.get("arena_rating", 1000)
    if random.random() < p / (p + e):
        r = random.randint(100, 300); d["coins"] += r; d["arena_rating"] = p + 10; show_popup("⚔️", "🎉 +%d💰" % r)
    else:
        d["arena_rating"] = max(0, p - 5); show_popup("⚔️", "💀 Поражение")
    save_json(DATA_FILE, players)

def _promo_apply(inst):
    try:
        s = App.get_running_app().root.get_screen("promo")
        code = s.inp.text.strip()
        if not code: return
        s.info.text = activate_promo(code); s.inp.text = ""
    except Exception as e: print("Promo error:", e)

def _school_task(inst):
    a, b = random.randint(1, 20), random.randint(1, 20); d = get_player(current_player); d["school_task"] = a + b; save_json(DATA_FILE, players)
    try: App.get_running_app().root.get_screen("school").info.text = "Реши: %d + %d = ?" % (a, b)
    except: pass

def _school_check(inst):
    d = get_player(current_player)
    try:
        s = App.get_running_app().root.get_screen("school"); ans = int(s.answer_inp.text.strip())
        if ans == d.get("school_task", -1):
            r = random.randint(10, 30); d["coins"] += r; d["school_solved"] = d.get("school_solved", 0) + 1; save_json(DATA_FILE, players)
            s.info.text = "✅ +%d💰!" % r; _school_task(None)
        else: s.info.text = "❌ Неправильно!"
    except: pass

def _clan_create(inst):
    d = get_player(current_player)
    try: n = App.get_running_app().root.get_screen("clans").clan_inp.text.strip()
    except: n = ""
    if not n or d["coins"] < 500: return
    d["coins"] -= 500; d["clan"] = n; save_json(DATA_FILE, players); show_popup("👥", "Создан: %s" % n)

def _clan_leave(inst):
    d = get_player(current_player); d["clan"] = None; save_json(DATA_FILE, players); show_popup("👥", "Вы вышли")

def _mini_guess(inst):
    d = get_player(current_player)
    try:
        s = App.get_running_app().root.get_screen("minigame"); n = int(s.inp.text.strip())
        if n == s.secret:
            r = random.randint(30, 100); d["coins"] += r; save_json(DATA_FILE, players)
            s.info.text = "🎉 +%d💰!" % r; s.secret = random.randint(1, 10)
        else: s.info.text = "❌ Загаданное %s." % ("больше" if n < s.secret else "меньше")
    except: pass

def _bank_dep(inst):
    d = get_player(current_player)
    if d["coins"] < 1000: return
    d["coins"] -= 1000; d["bank"]["deposit"] = d["bank"].get("deposit", 0) + 1000
    d["bank"]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_json(DATA_FILE, players); show_popup("🏦", "Вклад сделан!")

def _bank_wit(inst):
    d = get_player(current_player); dep = d["bank"].get("deposit", 0)
    if dep <= 0: return
    try:
        dd = datetime.strptime(d["bank"].get("date",""), "%Y-%m-%d %H:%M"); days = (datetime.now() - dd).days; dep += int(dep * days * 0.1)
    except: pass
    d["coins"] += dep; d["bank"]["deposit"] = 0; d["bank"]["date"] = ""
    save_json(DATA_FILE, players); show_popup("🏦", "+%d💰" % dep)

def _craft(inst):
    d = get_player(current_player)
    if d.get("crystals", 0) < 5: show_popup("🔨", "Нужно 5 💎"); return
    d["crystals"] -= 5; d["ingots"] = d.get("ingots", 0) + 1; save_json(DATA_FILE, players); show_popup("🔨", "✅ Слиток!")

def _market_sell(inst):
    d = get_player(current_player)
    if d.get("ingots", 0) < 1: return
    d["ingots"] -= 1; d["coins"] += 200; save_json(DATA_FILE, players); show_popup("🏪", "+200💰")

def _market_buy(inst):
    d = get_player(current_player)
    if d["coins"] < 300: return
    d["coins"] -= 300; d["crystals"] = d.get("crystals", 0) + 1; save_json(DATA_FILE, players); show_popup("🏪", "+1 💎")

def _guild_create(inst):
    d = get_player(current_player)
    if d["coins"] < 1000: return
    d["coins"] -= 1000; d["guild"] = "Гильдия_" + current_player; save_json(DATA_FILE, players); show_popup("🏛️", "Создана!")

def _guild_leave(inst):
    d = get_player(current_player); d["guild"] = None; save_json(DATA_FILE, players)

def _event_claim(inst):
    d = get_player(current_player); r = random.randint(50, 200); d["coins"] += r; save_json(DATA_FILE, players); show_popup("🎉", "+%d💰" % r)

def _world_go(inst):
    d = get_player(current_player)
    if d["coins"] < 50: return
    d["coins"] -= 50; r = random.randint(50, 200); d["coins"] += r; save_json(DATA_FILE, players); show_popup("🌍", "+%d💰" % r)

def _eco_to2(inst):
    d = get_player(current_player)
    if d["coins"] < 100: return
    d["coins"] -= 100; d["second_account"] = d.get("second_account", 0) + 100; save_json(DATA_FILE, players)

def _eco_from2(inst):
    d = get_player(current_player); a = d.get("second_account", 0)
    if a <= 0: return
    d["coins"] += a; d["second_account"] = 0; save_json(DATA_FILE, players)

def _friend_add(inst):
    d = get_player(current_player)
    try:
        n = App.get_running_app().root.get_screen("friends").inp.text.strip()
        if not n or n == current_player: return
        if n not in d.get("friends", []):
            d.setdefault("friends", []).append(n); save_json(DATA_FILE, players); show_popup("🤝", "Добавлен: %s" % n)
    except: pass

def _friend_remove(inst):
    d = get_player(current_player)
    try:
        n = App.get_running_app().root.get_screen("friends").inp.text.strip()
        if n in d.get("friends", []):
            d["friends"].remove(n); save_json(DATA_FILE, players); show_popup("🤝", "Удалён: %s" % n)
    except: pass

def _support_send(inst):
    try:
        s = App.get_running_app().root.get_screen("support"); msg = s.inp.text.strip()
        if not msg: return
        s.inp.text = ""; show_popup("📧", "Сообщение отправлено!")
    except: pass

def _company_change(inst):
    d = get_player(current_player)
    try:
        s = App.get_running_app().root.get_screen("company"); new = s.inp.text.strip()
        if not new: return
        d["company"] = new; save_json(DATA_FILE, players); show_popup("🏢", "Компания: %s" % new); s.on_enter()
    except: pass

def _settings_toggle_lang(inst):
    d = get_player(current_player); langs = ["Русский", "English", "Тоҷикӣ"]
    cur = d.get("lang", "Русский"); idx = (langs.index(cur) + 1) % len(langs) if cur in langs else 0
    d["lang"] = langs[idx]; save_json(DATA_FILE, players); show_popup("⚙️", "Язык: %s" % d["lang"])

def _settings_music_toggle(inst):
    try:
        app = App.get_running_app()
        if hasattr(app, "_music") and app._music:
            if app._music.state == "play":
                app._music.stop(); show_popup("🎵", "Музыка выключена")
            else:
                app._music.play(); show_popup("🎵", "Музыка включена")
        else:
            app.play_music(); show_popup("🎵", "Музыка включена")
    except Exception as e:
        show_popup("🎵", "Ошибка: %s" % e)

def _settings_reset(inst):
    d = get_player(current_player)
    d["coins"] = 5000; d["level"] = 1; d["exp"] = 0; d["battles"] = 0; d["wins"] = 0
    d["boss_defeated"] = 0; d["boss_count"] = 0; d["boss_date"] = ""
    save_json(DATA_FILE, players); show_popup("⚙️", "Прогресс сброшен!")

def _replay_play(inst):
    d = get_player(current_player)
    if d["battles"] == 0: show_popup("🎥", "Нет боёв для просмотра"); return
    show_popup("🎥", "Воспроизведение последнего боя...")

def _calendar_claim(inst):
    d = get_player(current_player); today = datetime.now().strftime("%Y-%m-%d")
    if d.get("calendar_claimed") == today: show_popup("📅", "Уже получено сегодня!"); return
    d["calendar_claimed"] = today; r = random.randint(50, 150); d["coins"] += r
    save_json(DATA_FILE, players); show_popup("📅", "+%d💰 за вход!" % r)

# === make_screen экраны ===
ShopScreen = make_screen("🛒 МАГАЗИН", (1,0.8,0.2,1), lambda d: "💰 %d | 💪 %d | ❤️ %d" % (d['coins'], d['power'], d['hp']),
    lambda s: [("💪 СИЛА +5 (30)", (0.2,0.5,0.2,1), _buy_power), ("❤️ HP +20 (20)", (0.5,0.2,0.2,1), _buy_hp)])
ChestsScreen = make_screen("📦 КЕЙСЫ", (0.8,0.4,0.6,1), lambda d: "💰 %d | 💠 %d | 💜 %d" % (d['coins'], d.get('titanite',0), d.get('souls',0)),
    lambda s: [("📦 Обычный (200💰)", (0.4,0.5,0.4,1), _chest_buy("Обычный")), ("📦 Редкий (1000💰)", (0.3,0.5,0.7,1), _chest_buy("Редкий")), ("📦 Легендарный (100💠)", (0.7,0.5,0.2,1), _chest_buy("Легендарный"))])
DailyScreen = make_screen("🎁 ЕЖЕДНЕВНЫЕ", (0.8,0.4,0.2,1), lambda d: "День: %d" % d.get('daily_streak',0), lambda s: [("🎲 ПОЛУЧИТЬ", (0.2,0.6,0.2,1), _daily_claim)])
BossScreen = make_screen("👹 БОСС", (0.8,0.2,0.2,1), lambda d: "❤️ Побед: %d\n🎯 Сегодня: %d/4" % (d.get('boss_defeated',0), d.get('boss_count',0)), lambda s: [("⚔️ СРАЖАТЬСЯ", (0.6,0.1,0.1,1), _boss_fight)])
ArenaScreen = make_screen("⚔️ АРЕНА", (0.6,0.2,0.4,1), lambda d: "🏆 Рейтинг: %d | 💰 %d" % (d.get('arena_rating',1000), d['coins']), lambda s: [("⚡ БОЙ (50)", (0.6,0.2,0.2,1), _arena_fight)])
NewsScreen = make_screen("📰 НОВОСТИ", (0.9,0.5,0.1,1),
    lambda d: "🆕 ВЕРСИЯ 12.3.0\n\n"
              "🎸 НОВАЯ МУЗЫКА!\n"
              "В игре теперь играет трек от разработчика!\n"
              "© Авторские права защищены.\n"
              "Все права принадлежат автору игры «СТАЛЬНОЙ РУБЕЖ».\n\n"
              "🌐 НОВЫЙ САЙТ!\n"
              "Кнопка «САЙТ ИГРЫ» в меню!\n\n"
              "🆕 Что нового:\n"
              "• 🌐 Кнопка сайта игры\n"
              "• 🎸 Собственная музыка\n"
              "• 🚗 4 танка\n"
              "• 🎨 6 скинов\n"
              "• 🏅 10 достижений\n"
              "• 👹 Босс 4 раза в день\n"
              "• 🎁 Промокод PREMIUM INFINITY",
    lambda s: [("✅ ПОНЯТНО", (0.2,0.5,0.2,1), lambda i: None)])
QuestScreen = make_screen("📋 КВЕСТЫ", (0.8,0.4,0.2,1), lambda d: "Заданий решено: %d" % d.get('school_solved',0), lambda s: [("🔄 НОВЫЙ", (0.2,0.4,0.6,1), lambda i: show_popup("📋", "Выиграй 3 боя\n+100💰"))])
WorldMapScreen = make_screen("🌍 МИР", (0.2,0.8,0.6,1), lambda d: "💰 %d" % d['coins'], lambda s: [("🌲 ЛЕС (50)", (0.3,0.5,0.3,1), _world_go), ("🏭 ЗАВОД (50)", (0.4,0.4,0.4,1), _world_go)])
EconomyScreen = make_screen("💹 ЭКОНОМИКА", (0.2,0.8,0.6,1), lambda d: "💰 %d | 🔄 %d" % (d['coins'], d.get('second_account',0)), lambda s: [("📤 НА 2-Й (100)", (0.2,0.4,0.6,1), _eco_to2), ("📥 СНЯТЬ", (0.6,0.4,0.2,1), _eco_from2)])
StatsScreen = make_screen("📊 СТАТИСТИКА", (0.6,0.3,0.3,1), lambda d: "%s\n⭐ Ур.%d\n⚔️ %d боёв | 🏆 %d побед\n💰 %d" % (current_player, d['level'], d['battles'], d['wins'], d['coins']), lambda s: [])
RatingScreen = make_screen("🏆 РЕЙТИНГ", (0.3,0.6,0.6,1), lambda d: "🏆 ТОП:\n" + "\n".join(["%d. %s — %d" % (i, n, p.get('wins',0)) for i,(n,p) in enumerate(sorted(players.items(), key=lambda x: x[1].get('wins',0), reverse=True)[:8], 1)]), lambda s: [])
CharactersScreen = make_screen("👾 ПЕРСОНАЖИ", (0.2,0.5,0.8,1), lambda d: "\n".join(d.get('characters', ["Базовый Робот"])), lambda s: [])
EventsScreen = make_screen("🎉 СОБЫТИЯ", (0.8,0.6,0.2,1), lambda d: "🔥 'Весенний шторм'", lambda s: [("🎁 ЗАБРАТЬ", (0.2,0.6,0.2,1), _event_claim)])
BankScreen = make_screen("🏦 БАНК", (0.8,0.6,0.2,1), lambda d: "Депозит: %d" % d['bank'].get('deposit',0), lambda s: [("📥 ВНЕСТИ (1000)", (0.2,0.6,0.2,1), _bank_dep), ("📤 СНЯТЬ +10%", (0.6,0.4,0.2,1), _bank_wit)])
CraftScreen = make_screen("🔨 КРАФТ", (0.6,0.4,0.8,1), lambda d: "💎 %d | 🔩 %d" % (d.get('crystals',0), d.get('ingots',0)), lambda s: [("⚒️ СКРАФТИТЬ (5💎)", (0.2,0.5,0.2,1), _craft)])
GuildsScreen = make_screen("🏛️ ГИЛЬДИИ", (0.8,0.4,0.4,1), lambda d: "Гильдия: %s" % (d.get('guild') or "нет"), lambda s: [("🏗️ СОЗДАТЬ (1000)", (0.2,0.5,0.2,1), _guild_create), ("🚪 ПОКИНУТЬ", (0.8,0.2,0.2,1), _guild_leave)])
MarketScreen = make_screen("🏪 РЫНОК", (0.4,0.6,0.2,1), lambda d: "💰 %d | 💎 %d | 🔩 %d" % (d['coins'], d.get('crystals',0), d.get('ingots',0)), lambda s: [("💰 ПРОДАТЬ (200)", (0.2,0.5,0.2,1), _market_sell), ("🛒 КУПИТЬ (300)", (0.2,0.4,0.6,1), _market_buy)])
ReplayScreen = make_screen("🎥 РЕПЛЕЙ", (0.4,0.2,0.6,1), lambda d: "Боёв: %d\nПобед: %d" % (d['battles'], d['wins']), lambda s: [("▶️ ВОСПРОИЗВЕСТИ", (0.2,0.5,0.8,1), _replay_play)])
CalendarScreen = make_screen("📅 КАЛЕНДАРЬ", (0.2,0.6,0.8,1), lambda d: "📅 День подряд: %d\nСегодня: %s" % (d.get('daily_streak',0), "✅" if d.get("calendar_claimed") == datetime.now().strftime("%Y-%m-%d") else "❌"), lambda s: [("🎁 ЗАБРАТЬ", (0.2,0.6,0.2,1), _calendar_claim)])

# === Специальные экраны ===
class SchoolScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="🎓 ШКОЛА", font_size=38, bold=True, color=(0.4,0.8,0.2,1)))
        self.info = Label(text="Нажми «Задание»", font_size=22, color=(0.9,0.9,0.9,1), size_hint_y=0.18); L.add_widget(self.info)
        self.answer_inp = TextInput(hint_text="Ответ", multiline=False, font_size=28, size_hint_y=0.12, input_filter="int"); L.add_widget(self.answer_inp)
        b1 = BigButton(text="📚 ЗАДАНИЕ", background_color=(0.2,0.5,0.8,1)); b1.bind(on_press=_school_task); L.add_widget(b1)
        b2 = BigButton(text="✅ ПРОВЕРИТЬ", background_color=(0.2,0.6,0.2,1)); b2.bind(on_press=_school_check); L.add_widget(b2)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)

class ClansScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="👥 КЛАНЫ", font_size=38, bold=True, color=(0.3,0.6,0.3,1)))
        self.info = Label(text="", font_size=22, color=(0.9,0.9,0.9,1), size_hint_y=0.15); L.add_widget(self.info)
        self.clan_inp = TextInput(hint_text="Название", multiline=False, font_size=26, size_hint_y=0.10); L.add_widget(self.clan_inp)
        b1 = BigButton(text="🏗️ СОЗДАТЬ (500)", background_color=(0.2,0.5,0.2,1)); b1.bind(on_press=_clan_create); L.add_widget(b1)
        b2 = BigButton(text="🚪 ПОКИНУТЬ", background_color=(0.8,0.2,0.2,1)); b2.bind(on_press=_clan_leave); L.add_widget(b2)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        if not current_player: return
        d = get_player(current_player); self.info.text = "Клан: %s" % (d.get("clan") or "нет")

class MiniGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=25, spacing=12)
        L.add_widget(Label(text="🎯 МИНИ-ИГРА", font_size=38, bold=True, color=(0.9,0.3,0.5,1)))
        self.info = Label(text="Угадай число 1-10!", font_size=24, color=(0.9,0.9,0.9,1)); L.add_widget(self.info)
        self.inp = TextInput(hint_text="Число", multiline=False, font_size=32, size_hint_y=0.12, input_filter="int"); L.add_widget(self.inp)
        b = BigButton(text="🎲 УГАДАТЬ", background_color=(0.2,0.6,0.2,1)); b.bind(on_press=_mini_guess); L.add_widget(b)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)
        self.secret = random.randint(1, 10)
    def on_enter(self):
        self.secret = random.randint(1, 10); self.info.text = "Угадай число 1-10!"

class PromoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=20, spacing=12)
        L.add_widget(Label(text="🎁 ПРОМОКОДЫ", font_size=38, bold=True, color=(1,0.8,0.2,1)))
        self.info = Label(text="Введи промокод", font_size=22, color=(0.9,0.9,0.9,1), size_hint_y=0.20); L.add_widget(self.info)
        self.inp = TextInput(hint_text="PREMIUM INFINITY", multiline=False, font_size=28, size_hint_y=0.12); L.add_widget(self.inp)
        b = BigButton(text="✅ АКТИВИРОВАТЬ", background_color=(0.2,0.6,0.2,1)); b.bind(on_press=_promo_apply); L.add_widget(b)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        if not current_player: return
        d = get_player(current_player); uses = settings.get("premium_infinity_uses", 0)
        cnt = "🚫 ЧЁРНЫЙ СПИСОК (10/10)" if uses >= 10 else "🎁 Активаций: %d/10" % uses
        self.info.text = premium_status(d) + "\n" + cnt + "\n\nВведи промокод:"

class FriendsScreenFull(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="🤝 ДРУЗЬЯ", font_size=38, bold=True, color=(0.6,0.3,0.6,1)))
        self.info = Label(text="", font_size=20, color=(0.9,0.9,0.9,1), size_hint_y=0.3); L.add_widget(self.info)
        self.inp = TextInput(hint_text="Ник друга", multiline=False, font_size=26, size_hint_y=0.10); L.add_widget(self.inp)
        b1 = BigButton(text="➕ ДОБАВИТЬ", background_color=(0.2,0.5,0.2,1)); b1.bind(on_press=_friend_add); L.add_widget(b1)
        b2 = BigButton(text="❌ УДАЛИТЬ", background_color=(0.7,0.2,0.2,1)); b2.bind(on_press=_friend_remove); L.add_widget(b2)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        if not current_player: return
        d = get_player(current_player)
        self.info.text = "Друзья (%d):\n%s" % (len(d.get("friends", [])), ", ".join(d.get("friends", [])) or "нет")

class SupportScreenFull(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="📧 ПОДДЕРЖКА", font_size=38, bold=True, color=(0.2,0.8,0.4,1)))
        self.info = Label(text="support@steelline.com\n\nОпиши проблему:", font_size=18, color=(0.9,0.9,0.9,1), size_hint_y=0.2); L.add_widget(self.info)
        self.inp = TextInput(hint_text="Твоё сообщение", multiline=True, font_size=20, size_hint_y=0.3); L.add_widget(self.inp)
        b = BigButton(text="📧 ОТПРАВИТЬ", background_color=(0.2,0.6,0.2,1)); b.bind(on_press=_support_send); L.add_widget(b)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)

class CompanyScreenFull(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="🏢 КОМПАНИЯ", font_size=38, bold=True, color=(0.8,0.6,0.2,1)))
        self.info = Label(text="", font_size=22, color=(0.9,0.9,0.9,1), size_hint_y=0.2); L.add_widget(self.info)
        self.inp = TextInput(hint_text="Название компании", multiline=False, font_size=26, size_hint_y=0.12); L.add_widget(self.inp)
        b = BigButton(text="🏢 СМЕНИТЬ", background_color=(0.2,0.5,0.8,1)); b.bind(on_press=_company_change); L.add_widget(b)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        if not current_player: return
        d = get_player(current_player); self.info.text = "Текущая: %s" % d.get("company", "Роботы")

class SettingsScreenFull(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="⚙️ НАСТРОЙКИ", font_size=38, bold=True, color=(0.7,0.7,0.7,1)))
        self.info = Label(text="", font_size=20, color=(0.9,0.9,0.9,1), size_hint_y=0.2); L.add_widget(self.info)
        b1 = BigButton(text="🎵 МУЗЫКА ВКЛ/ВЫКЛ", background_color=(0.5,0.3,0.7,1)); b1.bind(on_press=_settings_music_toggle); L.add_widget(b1)
        b2 = BigButton(text="🌍 ЯЗЫК", background_color=(0.3,0.5,0.3,1)); b2.bind(on_press=_settings_toggle_lang); L.add_widget(b2)
        b3 = BigButton(text="🗑 СБРОСИТЬ ПРОГРЕСС", background_color=(0.8,0.2,0.2,1)); b3.bind(on_press=_settings_reset); L.add_widget(b3)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main")); L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        if not current_player: return
        d = get_player(current_player)
        self.info.text = "🌍 Язык: %s" % d.get("lang", "Русский")

# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class SteelLineApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        self.main_screen = MainScreen(name='main'); sm.add_widget(self.main_screen)
        sm.add_widget(HangarScreen(name='hangar'))
        sm.add_widget(SkinsScreen(name='skins'))
        sm.add_widget(AchievementsScreen(name='achievements'))
        sm.add_widget(BattleScreen(name='battle'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(ShopScreen(name='shop'))
        sm.add_widget(ChestsScreen(name='chests'))
        sm.add_widget(DailyScreen(name='daily'))
        sm.add_widget(BossScreen(name='boss'))
        sm.add_widget(ArenaScreen(name='arena'))
        sm.add_widget(NewsScreen(name='news'))
        sm.add_widget(SchoolScreen(name='school'))
        sm.add_widget(QuestScreen(name='quest'))
        sm.add_widget(WorldMapScreen(name='world'))
        sm.add_widget(EconomyScreen(name='economy'))
        sm.add_widget(ClansScreen(name='clans'))
        sm.add_widget(FriendsScreenFull(name='friends'))
        sm.add_widget(SupportScreenFull(name='support'))
        sm.add_widget(CompanyScreenFull(name='company'))
        sm.add_widget(SettingsScreenFull(name='settings'))
        sm.add_widget(StatsScreen(name='stats'))
        sm.add_widget(RatingScreen(name='rating'))
        sm.add_widget(CharactersScreen(name='characters'))
        sm.add_widget(EventsScreen(name='events'))
        sm.add_widget(ReplayScreen(name='replay'))
        sm.add_widget(BankScreen(name='bank'))
        sm.add_widget(CraftScreen(name='craft'))
        sm.add_widget(CalendarScreen(name='calendar'))
        sm.add_widget(GuildsScreen(name='guilds'))
        sm.add_widget(MarketScreen(name='market'))
        sm.add_widget(MiniGameScreen(name='minigame'))
        sm.add_widget(PromoScreen(name='promo'))
        sm.current = 'login'
        return sm

    def play_music(self):
        try:
            candidates = [
                res_path("game/sound/biskas.zelye.wav"),
                res_path("game/sound/biskas.zelye.ogg"),
                res_path("game/sound/biskas.zelye.mp3"),
            ]
            for p in candidates:
                if os.path.exists(p):
                    self._music = SoundLoader.load(p)
                    if self._music:
                        self._music.loop = True
                        self._music.volume = 0.6
                        self._music.play()
                        print("🎵 Музыка играет:", p)
                        return
            print("❌ Файл музыки не найден")
        except Exception as e:
            print("❌ Music error:", e)

    def on_start(self):
        try:
            lu = settings.get("last_user", ""); lp = settings.get("last_password", "")
            if lu and lp and lu in players and players[lu].get("password","") == lp:
                global current_player; current_player = lu
                self.main_screen.update_info(); self.root.current = 'main'
            self.play_music()
        except Exception as e:
            print("on_start error:", e)

if __name__ == '__main__':
    SteelLineApp().run()
