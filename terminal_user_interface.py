import asyncio

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Center, HorizontalGroup, VerticalScroll
from textual.events import ScreenResume, ScreenSuspend
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, Placeholder
from textual_plotext import PlotextPlot

from my_weather_app import MyWeatherApp


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("MainScreen")
        yield Footer()

class CurrentWeatherScreen(Screen):
    def compose(self) -> ComposeResult:
        help_label = """Hi! In this place you can check the weather in \
                any place in the world by typing it in \
                the field below."""
        with Center():
            yield Label(help_label, id="help_label")
        with Center():
            yield Input(placeholder="Enter location...", id="city_input")
        # with Center():
            # yield Placeholder("Curr Weather Screen")
        yield Footer()

    def on_input_submitted(self):
        app.switch_screen("plot")

class PlotScreen(Screen):
    BINDINGS = [("m", "switch_screen('main')", "Return to main")]

    @on(ScreenResume)
    def draw(self):
        plt = self.query_one(PlotextPlot).plt
        MyWeatherApp().draw_plot(plt)
        self.query_one(PlotextPlot).refresh()

    def compose(self) -> ComposeResult:
        self.refresh_bindings()
        # yield Placeholder("PlotScreen")
        yield PlotextPlot()
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
