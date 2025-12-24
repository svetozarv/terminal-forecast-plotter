from textual.app import App, ComposeResult
from textual.containers import Center, HorizontalGroup, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, Placeholder
from textual_plotext import PlotextPlot

from tui import TerminalUserInterface


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

class PlotScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Return"),
    ]

    def draw(self):
        plt = self.query_one(PlotextPlot).plt
        TerminalUserInterface().draw_plot(plt)

    def on_mount(self) -> None:
        self.draw()

    def compose(self) -> ComposeResult:
        # yield Placeholder("PlotScreen")
        yield PlotextPlot()
        yield Footer()

class FavouritesScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("Fav Screen")
        yield Footer()

class AlertsScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("Alerts Screen")
        yield Footer()

class TerminalUserInterface(App):
    CSS_PATH = "myweatherapp.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("m", "switch_screen('main')", "Return to main"),
        ("w", "switch_screen('current_weather')", "Check weather"),
        ("f", "switch_screen('favourites')", "Favourites"),
        ("a", "switch_screen('alerts')", "Alerts"),
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
        self.theme = "nord"

    def on_input_submitted(self):
        self.push_screen("plot")

if __name__ == "__main__":
    app = TerminalUserInterface()
    app.run()
