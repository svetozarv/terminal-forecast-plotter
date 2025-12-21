from textual.app import App, ComposeResult
from textual.containers import Center, HorizontalGroup, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, Placeholder


class CurrentWeatherScreen(Screen):
    def compose(self):
        with Center():
            yield Label("Hi! In this place you can check the weather in any place in the world by typing it in the field below.", id="help_label")
        with Center():
            yield Input(placeholder="Enter location...", id="city_input")
        # with Center():
            # yield Placeholder("Curr Weather Screen")
        yield Footer()

class PlotScreen(Screen):
    def compose(self):
        yield Placeholder("PlotScreen")
        yield Footer()

class FavouritesScreen(Screen):
    def compose(self):
        yield Placeholder("Fav Screen")
        yield Footer()

class AlertsScreen(Screen):
    def compose(self):
        yield Placeholder("Alerts Screen")
        yield Footer()

class MyWeatherApp(App):
    CSS_PATH = "myweatherapp.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("w", "push_screen('current_weather')", "Check weather"),
        ("f", "push_screen('favourites')", "Favourites"),
        ("a", "push_screen('alerts')", "Alerts"),
    ]
    SCREENS = {
        "current_weather": CurrentWeatherScreen,
        "plot" : PlotScreen,
        "favourites": FavouritesScreen,
        "alerts": AlertsScreen,
    }

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        # self.switch_screen("current_weather")
        self.theme = "nord"

    def on_input_submitted(self):
        self.push_screen("plot")

if __name__ == "__main__":
    app = MyWeatherApp()
    app.run()
