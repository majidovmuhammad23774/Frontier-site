from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.audio import SoundLoader
from kivy.resources import resource_find
import os
from data import *
import screens
from screens import *
from screens import (LoginScreen, MainScreen, HangarScreen, SkinsScreen,
                     AchievementsScreen, ProfileScreen, BattleScreen,
                     ShopScreen, ChestsScreen, DailyScreen, BossScreen,
                     ArenaScreen, QuestScreen, WorldMapScreen, EconomyScreen,
                     StatsScreen, RatingScreen, CharactersScreen, EventsScreen,
                     BankScreen, CraftScreen, GuildsScreen, MarketScreen,
                     ReplayScreen, CalendarScreen)

# Простые экраны-заглушки (новости, школа, кланы, промо, мини-игра, друзья, поддержка, компания, настройки)
class NewsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        L = BoxLayout(orientation='vertical', padding=15, spacing=8)
        L.add_widget(Label(text="📰 НОВОСТИ", font_size=34, bold=True, color=(0.9,0.5,0.1,1)))
        L.add_widget(Label(text="БРОНЕЛОМ v12.3.1\n\n🎵 Новая музыка\n🌐 Кнопка сайта\n🤖 Скин Робот\n🎁 Промокод PREMIUM INFINITY", font_size=18))
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back); self.add_widget(L)

class SchoolScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="🎓 ШКОЛА", font_size=38, bold=True, color=(0.4,0.8,0.2,1)))
        self.info = Label(text="Нажми «Задание»", font_size=22); L.add_widget(self.info)
        self.answer_inp = TextInput(hint_text="Ответ", multiline=False, font_size=28, input_filter="int"); L.add_widget(self.answer_inp)
        b1 = BigButton(text="📚 ЗАДАНИЕ", background_color=(0.2,0.5,0.8,1)); b1.bind(on_press=_school_task); L.add_widget(b1)
        b2 = BigButton(text="✅ ПРОВЕРИТЬ", background_color=(0.2,0.6,0.2,1)); b2.bind(on_press=_school_check); L.add_widget(b2)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1)); back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back); self.add_widget(L)

class ClansScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="👥 КЛАНЫ", font_size=38, bold=True, color=(0.3,0.6,0.3,1)))
        self.info = Label(text="", font_size=22); L.add_widget(self.info)
        self.clan_inp = TextInput(hint_text="Название", multiline=False, font_size=26); L.add_widget(self.clan_inp)
        b1 = BigButton(text="🏗️ СОЗДАТЬ (500)", background_color=(0.2,0.5,0.2,1)); b1.bind(on_press=_clan_create); L.add_widget(b1)
        b2 = BigButton(text="🚪 ПОКИНУТЬ", background_color=(0.8,0.2,0.2,1)); b2.bind(on_press=_clan_leave); L.add_widget(b2)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1)); back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        if screens.current_player:
            self.info.text = "Клан: %s" % (get_player(screens.current_player).get("clan") or "нет")

class MiniGameScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        L = BoxLayout(orientation='vertical', padding=25, spacing=12)
        L.add_widget(Label(text="🎯 МИНИ-ИГРА", font_size=38, bold=True, color=(0.9,0.3,0.5,1)))
        self.info = Label(text="Угадай число 1-10!", font_size=24); L.add_widget(self.info)
        self.inp = TextInput(hint_text="Число", multiline=False, font_size=32, input_filter="int"); L.add_widget(self.inp)
        b = BigButton(text="🎲 УГАДАТЬ", background_color=(0.2,0.6,0.2,1)); b.bind(on_press=_mini_guess); L.add_widget(b)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1)); back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back); self.add_widget(L)
        self.secret = random.randint(1, 10)
    def on_enter(self):
        self.secret = random.randint(1, 10); self.info.text = "Угадай число 1-10!"

class PromoScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        L = BoxLayout(orientation='vertical', padding=20, spacing=12)
        L.add_widget(Label(text="🎁 ПРОМОКОДЫ", font_size=38, bold=True, color=(1,0.8,0.2,1)))
        self.info = Label(text="Введи промокод", font_size=22); L.add_widget(self.info)
        self.inp = TextInput(hint_text="PREMIUM INFINITY", multiline=False, font_size=28); L.add_widget(self.inp)
        b = BigButton(text="✅ АКТИВИРОВАТЬ", background_color=(0.2,0.6,0.2,1)); b.bind(on_press=_promo_apply); L.add_widget(b)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1)); back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        if screens.current_player:
            d = get_player(screens.current_player); uses = settings.get("premium_infinity_uses", 0)
            self.info.text = premium_status(d) + "\nАктиваций: %d/10" % uses

class FriendsScreenFull(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="🤝 ДРУЗЬЯ", font_size=38, bold=True, color=(0.6,0.3,0.6,1)))
        self.info = Label(text="", font_size=20); L.add_widget(self.info)
        self.inp = TextInput(hint_text="Ник друга", multiline=False, font_size=26); L.add_widget(self.inp)
        b1 = BigButton(text="➕ ДОБАВИТЬ", background_color=(0.2,0.5,0.2,1)); b1.bind(on_press=_friend_add); L.add_widget(b1)
        b2 = BigButton(text="❌ УДАЛИТЬ", background_color=(0.7,0.2,0.2,1)); b2.bind(on_press=_friend_remove); L.add_widget(b2)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1)); back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        if screens.current_player:
            d = get_player(screens.current_player)
            self.info.text = "Друзья (%d): %s" % (len(d.get("friends", [])), ", ".join(d.get("friends", [])) or "нет")

class SupportScreenFull(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="📧 ПОДДЕРЖКА", font_size=38, bold=True, color=(0.2,0.8,0.4,1)))
        self.info = Label(text="support@steelline.com", font_size=18); L.add_widget(self.info)
        self.inp = TextInput(hint_text="Сообщение", multiline=True, font_size=20); L.add_widget(self.inp)
        b = BigButton(text="📧 ОТПРАВИТЬ", background_color=(0.2,0.6,0.2,1)); b.bind(on_press=_support_send); L.add_widget(b)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1)); back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back); self.add_widget(L)

class CompanyScreenFull(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="🏢 КОМПАНИЯ", font_size=38, bold=True, color=(0.8,0.6,0.2,1)))
        self.info = Label(text="", font_size=22); L.add_widget(self.info)
        self.inp = TextInput(hint_text="Название компании", multiline=False, font_size=26); L.add_widget(self.inp)
        b = BigButton(text="🏢 СМЕНИТЬ", background_color=(0.2,0.5,0.8,1)); b.bind(on_press=_company_change); L.add_widget(b)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1)); back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        if screens.current_player:
            self.info.text = "Текущая: %s" % get_player(screens.current_player).get("company", "Роботы")

class SettingsScreenFull(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        L = BoxLayout(orientation='vertical', padding=20, spacing=10)
        L.add_widget(Label(text="⚙️ НАСТРОЙКИ", font_size=38, bold=True, color=(0.7,0.7,0.7,1)))
        self.info = Label(text="", font_size=20); L.add_widget(self.info)
        b1 = BigButton(text="🎵 МУЗЫКА ВКЛ/ВЫКЛ", background_color=(0.5,0.3,0.7,1)); b1.bind(on_press=_settings_music_toggle); L.add_widget(b1)
        b2 = BigButton(text="🌍 ЯЗЫК", background_color=(0.3,0.5,0.3,1)); b2.bind(on_press=_settings_toggle_lang); L.add_widget(b2)
        b3 = BigButton(text="🗑 СБРОСИТЬ ПРОГРЕСС", background_color=(0.8,0.2,0.2,1)); b3.bind(on_press=_settings_reset); L.add_widget(b3)
        back = BigButton(text="НАЗАД", background_color=(0.3,0.3,0.3,1)); back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "main"))
        L.add_widget(back); self.add_widget(L)
    def on_enter(self):
        if screens.current_player:
            self.info.text = "🌍 Язык: %s" % get_player(screens.current_player).get("lang", "Русский")

# ============================================================
# ПРИЛОЖЕНИЕ
# ============================================================
class BronelomApp(App):
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
            for p in ["game/sound/bronelom_song.mp3", "game/sound/bronelom_song.ogg", "game/sound/bronelom_song.wav"]:
                rp = resource_find(p) or p
                if os.path.exists(rp):
                    self._music = SoundLoader.load(rp)
                    if self._music:
                        self._music.loop = True; self._music.volume = 0.6; self._music.play()
                        print("🎵 Музыка играет:", rp); return
            print("❌ Файл музыки не найден")
        except Exception as e: print("❌ Music error:", e)

    def on_start(self):
        try:
            lu = settings.get("last_user", ""); lp = settings.get("last_password", "")
            if lu and lp and lu in players and players[lu].get("password","") == lp:
                screens.current_player = lu
                self.main_screen.update_info(); self.root.current = 'main'
            self.play_music()
        except Exception as e: print("on_start error:", e)

if __name__ == '__main__':
    BronelomApp().run()