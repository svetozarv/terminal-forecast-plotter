import asyncio

from textual import on
from textual.binding import Binding
from textual.app import App, ComposeResult
from textual.containers import Center, Grid, HorizontalGroup, VerticalScroll
from textual.events import ScreenResume, ScreenSuspend
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Placeholder,
    Pretty,
)
from textual_plotext import PlotextPlot

import geocoder
from database_storage_manager import DatabaseStorageManager
from my_weather_app import MyWeatherApp


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        # TODO: Welcome label
        yield Placeholder("MainScreen")
        yield Label("", id="alert_label")
        yield Footer()

    @on(ScreenResume)
    def check_alert_on_resume(self):
        self.check_alerts()

    def on_mount(self):
        self.check_alerts()

    def check_alerts(self):
        for city, min_temp, max_temp in app.dbm.get_alerts():
            self.check_alert_for_city(city, min_temp, max_temp)

    def check_alert_for_city(self, city: str, min_temp: float, max_temp: float):
        current_weather = app.my_weather_app.get_current_weather(*geocoder.city_name_to_coords(city))
        current_temp = current_weather.temperature_2m
        city_name = geocoder.coords_to_city_name(*app.my_weather_app.current_coords)
        label = self.screen.query_one(Label)
        label_text = "Alert has been triggered!\n"
        if current_temp < min_temp:
            label_text += f"The temperature for {city_name} has dropped below {min_temp}°C\n"
        if current_temp > max_temp:
            label_text += f"The temperature for {city_name} has raised above {max_temp}°C\n"
        label.update(label_text)


class AskForCityScreen(Screen):
    def compose(self) -> ComposeResult:
        help_label = "Hi! In this place you can check the weather in " + \
            "any place in the world by typing it in " + \
            "the field below."
        with Center():
            yield Label(help_label, classes="help_label")
        with Center():
            yield Input(placeholder="Enter location...", id="city_input")
        # with Center():
            # yield Placeholder("Curr Weather Screen")
        with Center():
            yield Pretty([])
        yield Footer()

    def get_city_prompt(self) -> str:
        app.city_prompt = self.query_one(Input).value
        # TODO: if value is 'c' switch to main
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
            Input(placeholder="Min. temp.", type='number', id="min_temp_input"),
            Input(placeholder="Max. temp.", type='number', id="max_temp_input"),
            id="dialog",
        )

    def add_alert(self):
        min_temp = self.screen.query_one("#min_temp_input").value
        max_temp = self.screen.query_one("#max_temp_input").value
        app.dbm.create_temperature_alert(app.city_prompt, min_temp, max_temp)

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
        app.dbm.save_city_to_favourties(geocoder.coords_to_city_name(*app.my_weather_app.current_coords))

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
        # yield Placeholder(f"{app.screen}")
        with Center():
            yield Label()
        with Center():
            yield ListView(initial_index=0)
        yield Footer()

    def on_mount(self):
        favourites = app.dbm.get_favourites()
        label = self.screen.query_one(Label)
        if not favourites:
            label.update("You haven't saved any cities yet.")
        else:
            label.update("Your favourite cities:")

        list_view = self.screen.query_one(ListView)
        for favourite in favourites:
            list_view.append(ListItem(Label(favourite)))

    @on(ListView.Selected)
    def get_plot_for_city(self):
        highlighted_index = self.screen.query_one(ListView).index
        app.city_prompt = app.dbm.get_favourites()[highlighted_index]    # TODO: bottleneck to remove
        app.switch_screen("plot")


class AlertsScreen(Screen):
    COLUMNS = ["City", "Min. temp", "Max. temp"]
    label = "These are your saved alerts:"

    def compose(self) -> ComposeResult:
        # yield Placeholder("Alerts Screen")
        yield Label("", classes="help_label")
        yield DataTable(id="alerts_data_table")
        yield Footer()

    def on_mount(self):
        data_table = self.screen.query_one(DataTable)
        data_table.add_columns(*self.COLUMNS)
        alerts = app.dbm.get_alerts()
        data_table.add_rows(alerts)

        label = self.screen.query_one(Label)
        if not alerts:
            label.update("You haven't saved any cities yet.")
            data_table.display = False
        else:
            label.update(self.label)
            data_table.display = True


class TerminalUserInterface(App):
    my_weather_app = MyWeatherApp()
    dbm = DatabaseStorageManager()
    city_prompt = None

    CSS_PATH = "terminal_user_interface.tcss"
    BINDINGS = [
        ("w", "switch_to_screen('ask_for_city')", "Check weather"),
        ("f", "switch_to_screen('favourites')", "Favourites"),
        ("a", "switch_to_screen('alerts')", "Alerts"),
        Binding("m, escape", "switch_to_screen('main')", "Return to main", priority=True),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]
    SCREENS = {
        "main": MainScreen,
        "favourites": FavouritesScreen,
        "alerts": AlertsScreen,
        "ask_for_city": AskForCityScreen,
        "plot": PlotScreen,
        "ask_alert_details": AskAlertDetailsScreen,
    }

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        # self.install_screen("plot")
        # self.theme = "nord"
        self.push_screen("main")

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
            if action == "switch_to_screen" and parameters[0] == "ask_for_city":
                return False
            if action == "switch_to_screen" and parameters[0] == "alerts":
                return False
            if action == "switch_to_screen" and parameters[0] == "favourites":
                return False
            if action == "toggle_dark":
                return False
        if isinstance(self.screen, AskAlertDetailsScreen):
            pass
        if isinstance(self.screen, AlertsScreen):
            if action == "switch_to_screen" and parameters[0] == "alerts":
                return False
        if isinstance(self.screen, FavouritesScreen):
            if action == "switch_to_screen" and parameters[0] == "favourites":
                return False
        if isinstance(self.screen, AskForCityScreen):
            pass
        return True


if __name__ == "__main__":
    app = TerminalUserInterface()
    app.run()
