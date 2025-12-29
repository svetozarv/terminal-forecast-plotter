import asyncio

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Center, HorizontalGroup, VerticalScroll, Grid
from textual.events import ScreenResume, ScreenSuspend
from textual.screen import Screen, ModalScreen
from textual.widgets import Footer, Header, Input, Label, Placeholder, Pretty
from textual_plotext import PlotextPlot

import geocoder
from my_weather_app import MyWeatherApp
from database_storage_manager import DatabaseStorageManager


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("MainScreen")
        yield Footer()


class CurrentWeatherScreen(Screen):
    def compose(self) -> ComposeResult:
        help_label = "Hi! In this place you can check the weather in" + \
                " any place in the world by typing it in" + \
                " the field below."
        with Center():
            yield Label(help_label, id="help_label")
        with Center():
            yield Input(placeholder="Enter location...", id="city_input")
        # with Center():
            # yield Placeholder("Curr Weather Screen")
        with Center():
            yield Pretty([])
        yield Footer()

    def get_city_prompt(self):
        app.city_prompt = self.query_one(Input).value
        return app.city_prompt

    def on_input_submitted(self):
        self.query_one(Pretty).update(self.get_city_prompt())
        app.switch_screen("plot")


class AskAlertDetailsScreen(ModalScreen):
    def compose(self):
        dialog_message = "Please, provide the temperatures for alert to trigger." + \
            "You have to fill at least one field."
        yield Grid(
            Label(dialog_message, id="askforalert_dialog"),
            Input(placeholder="Min. temp.", id="min_temp_input"),
            Input(placeholder="Max. temp.", id="max_temp_input"),
            id="dialog",
        )

    def add_alert(self):
        min_temp = self.screen.query_one("#min_temp_input").value
        max_temp = self.screen.query_one("#max_temp_input").value
        app.db.create_temperature_alert(app.city_prompt, min_temp, max_temp)

    def on_input_submitted(self):
        self.add_alert()
        app.pop_screen()


class PlotScreen(Screen):
    BINDINGS = [
        ("j", "draw_daily", "See daily forecast"),
        ("h", "draw_hourly", "See hourly forecast"),
        ("s", "save_to_favourties", "Save to favourites"),
        ("a", "ask_for_details", "Add alert"),
    ]

    def action_ask_for_details(self):
        """Handles keybinding."""
        app.push_screen("ask_alert_details")

    def action_save_to_favourties(self):
        """Handles keybinding."""
        app.db.save_city_to_favourties(geocoder.coords_to_city_name(*app.my_weather_app.current_coords))

    def action_draw_daily(self):
        """Handles keybinding."""
        plt = self.query_one(PlotextPlot).plt
        app.my_weather_app.draw_daily_plot(plt, app.city_prompt)
        self.query_one(PlotextPlot).refresh()

    def draw_hourly(self):
        plt = self.query_one(PlotextPlot).plt
        app.my_weather_app.draw_hourly_plot(plt, app.city_prompt)
        self.query_one(PlotextPlot).refresh()

    def action_draw_hourly(self):
        """Handles keybinding."""
        self.draw_hourly()

    @on(ScreenResume)
    def draw_hourly_on_resume(self):
        self.draw_hourly()

    def on_mount(self):
        self.draw_hourly()

    def compose(self) -> ComposeResult:
        # yield Placeholder("PlotScreen")
        yield PlotextPlot(id="plotext-plot")
        yield Footer()


class FavouritesScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder(f"{app.screen}")
        yield Footer()


class AlertsScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("Alerts Screen")
        yield Footer()


class TerminalUserInterface(App):
    my_weather_app = MyWeatherApp()
    db = DatabaseStorageManager()
    city_prompt = None

    CSS_PATH = "terminal_user_interface.tcss"
    BINDINGS = [
        ("w", "switch_to_screen('current_weather')", "Check weather"),
        ("f", "switch_to_screen('favourites')", "Favourites"),
        ("a", "switch_to_screen('alerts')", "Alerts"),
        ("m", "switch_to_screen('main')", "Return to main"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]
    SCREENS = {
        "main": MainScreen,
        "current_weather": CurrentWeatherScreen,
        "plot": PlotScreen,
        "favourites": FavouritesScreen,
        "alerts": AlertsScreen,
        "ask_alert_details": AskAlertDetailsScreen,
    }

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        # self.install_screen("main")
        # self.install_screen("favourites")
        # self.install_screen("alerts")
        # self.install_screen("current_weather")
        self.push_screen("main")
        # self.theme = "nord"

    def action_switch_to_screen(self, name):
        self.switch_screen(name)
        self.refresh_bindings()

    def check_action(self, action, parameters):
        if isinstance(self.screen, MainScreen):
            if action == "switch_to_screen" and parameters[0] == "main":
                return False
        if not isinstance(self.screen, PlotScreen):
            if action == "draw_daily":
                return False
        if isinstance(self.screen, PlotScreen):
            if action == "switch_to_screen" and parameters[0] == "main":
                return True
            if action == "switch_to_screen" and parameters[0] == "current_weather":
                return False
            if action == "switch_to_screen" and parameters[0] == "alerts":
                return False
            if action == "switch_to_screen" and parameters[0] == "favourites":
                return False
            if action == "toggle_dark":
                return False
        return True


if __name__ == "__main__":
    app = TerminalUserInterface()
    app.run()
