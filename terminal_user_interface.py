import asyncio
import logging

logging.getLogger("terminal_user_interface")
logging.basicConfig(filename='terminal_user_interface.log', level=logging.INFO, filemode="w+")
import peewee as pw
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Grid, HorizontalGroup, VerticalScroll
from textual.events import ScreenResume, ScreenSuspend
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
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

from database_orm import (
    DATABASE_FILENAME,
    MAX_TEMP,
    MAX_WINDSPEED,
    MIN_TEMP,
    MIN_WINDSPEED,
    Alert,
)
from my_weather_app import MyWeatherApp


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        # TODO: Welcome label
        yield Placeholder("MainScreen")
        yield Label("Alert has been triggered!\n", id="alert_has_beeb_triggered_label")
        yield Label("", id="alerts_label")
        yield Footer()

    @on(ScreenResume)
    def check_alert_on_resume(self):
        self.screen.query_one("#alerts_label", Label).update("")
        self.check_alerts()

    def on_mount(self):
        self.screen.query_one("#alert_triggered_label", Label).display = False
        self.check_alerts()

    def check_alerts(self):
        for alert in list(Alert.select()):
            self.check_alert_for_city(alert)

    def check_alert_for_city(self, alert: pw.BaseModelSelect):
        current_weather = app.my_weather_app.get_current_weather((alert.lat, alert.lon))
        current_temp = current_weather.temperature_2m
        alerts_label = self.screen.query_one("#alerts_label", Label)
        alert_triggered_label = self.screen.query_one("#alert_triggered_label", Label)
        label_text = alerts_label.content
        if current_temp < alert.min_temp:
            label_text += f"The temperature for {alert.city_name} has dropped below {alert.min_temp}°C\n"
            alert_triggered_label.display = True
        if current_temp > alert.max_temp:
            alert_triggered_label.display = True
            label_text += f"The temperature for {alert.city_name} has raised above {alert.max_temp}°C\n"
        alerts_label.update(label_text)


class AskForCityScreen(Screen):
    def compose(self) -> ComposeResult:
        help_label = "Hi! In this place you can check the weather in " + \
            "any place in the world by typing it in " + \
            "the field below."
        with Center():
            yield Label(help_label, classes="help_label")
        with Center():
            yield Input(placeholder="Enter location...", id="city_input")
        with Center():
            yield Pretty([])
        yield Footer()

    def get_city_prompt(self) -> str:
        # TODO: add validataion, results first, then show if results not None else display msg
        app.city_prompt = self.query_one(Input).value
        return app.city_prompt

    def on_input_submitted(self):
        self.query_one(Pretty).update(self.get_city_prompt())
        app.switch_screen("plot")

class DialogPopupScreen(ModalScreen):    # TODO:
    def compose(self) -> ComposeResult:
        with Center():
            yield Label(app.dialog_popup_text)
            yield Button("OK")

    @on(Button.Pressed)
    def close(self):
        app.pop_screen()

class AskAlertDetailsScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        dialog_message = "Please, provide the temperatures for alert to trigger. " + \
            "You can leave some fields empty."
        yield Grid(
            Label(dialog_message, id="ask_for_alert_dialog"),
            Input(placeholder="Name/description", id="name", valid_empty=True),
            Input(placeholder="Min. temp. °C", type='number', id="min_temp_input", valid_empty=True),
            Input(placeholder="Max. temp. °C", type='number', id="max_temp_input", valid_empty=True),
            Input(placeholder="Min. wind speed, m/s", type='number', id="min_windspeed_input", valid_empty=True),
            Input(placeholder="Max. wind speed, m/s", type='number', id="max_windspeed_input", valid_empty=True),
            id="ask_for_alert_grid",
        )
        # TODO: add validation for min and max temps and chars in the input (in can be "")

    def add_alert(self):
        name = self.screen.query_one("#name", Input).value
        min_temp = self.screen.query_one("#min_temp_input", Input).value
        max_temp = self.screen.query_one("#max_temp_input", Input).value
        min_wind_speed = self.screen.query_one("#min_windspeed_input", Input).value
        max_wind_speed = self.screen.query_one("#max_windspeed_input", Input).value

        # if user hasn't provided values (they are "")
        if not name:
            name = "-"
        if not min_temp:
            min_temp = MIN_TEMP
        if not max_temp:
            max_temp = MAX_TEMP
        if not min_wind_speed:
            min_wind_speed = MIN_WINDSPEED
        if not max_wind_speed:
            max_wind_speed = MAX_WINDSPEED
        logging.info(f"Values: {name} {min_temp} {max_temp} {min_wind_speed} {max_wind_speed}")

        if name == "^Q":  # user pressed 'exit' while in the screen
            logging.info("Detected exit input. add_alert aborted.")
            return
        if not min_temp and not max_temp and not min_wind_speed and not max_wind_speed:
            logging.info("No values provided. add_alert aborted.")
            return
        Alert.get_or_create(
            name=name,
            city_name=app.my_weather_app.current_city_name(),
            lat=app.my_weather_app.current_coords[0],
            lon=app.my_weather_app.current_coords[1],
            min_temp=min_temp,
            max_temp=max_temp,
            min_wind_speed=min_wind_speed,
            max_wind_speed=max_wind_speed,
        )
        logging.info("Alert was added.")

    @on(Input.Submitted)
    def process_submit(self):
        self.add_alert()
        app.dialog_popup_text = "Saved!"
        app.switch_screen("dialog_popup")
        app.pop_screen()


class PlotScreen(Screen):
    BINDINGS = [
        ("t", "toggle_precision_mode", "Toggle daily/hourly"),
        ("s", "save_to_favourties", "Save to favourites"),
        ("a", "ask_for_details", "Add alert"),
    ]

    def compose(self) -> ComposeResult:
        # yield Placeholder("PlotScreen")
        yield PlotextPlot(id="plotext-plot")
        yield Footer()

    def on_mount(self):
        self.screen.loading = True
        self.draw_hourly()

    @on(ScreenResume)
    def draw_hourly_on_resume(self):
        self.screen.loading = True
        self.draw_hourly()

    def draw_hourly(self):
        plt = self.query_one(PlotextPlot).plt
        app.my_weather_app.draw_hourly_plot(plt, app.city_prompt)
        self.query_one(PlotextPlot).refresh()
        self.screen.loading = False
        self.displaying_daily = False
        self.displaying_hourly = True

    def draw_daily(self):
        plt = self.query_one(PlotextPlot).plt
        app.my_weather_app.draw_daily_plot(plt, app.city_prompt)
        self.query_one(PlotextPlot).refresh()
        self.screen.loading = False
        self.displaying_daily = True
        self.displaying_hourly = False

    def action_ask_for_details(self):
        """Handles keybinding."""
        app.push_screen("ask_alert_details")

    def action_save_to_favourties(self):
        """Handles keybinding."""
        if Alert.get_or_none(Alert.city_name == app.my_weather_app.current_city_name()):
            app.display_dialog("The city is already in your favourites.")
            return
        Alert(
            city_name=app.my_weather_app.current_city_name(),
            lat=app.my_weather_app.current_coords[0],
            lon=app.my_weather_app.current_coords[1],
        ).save()
        app.display_dialog("Saved!")
        # self.screen.styles.background = "lime"
        # self.screen.styles.animate("opacity", value=0.0, duration=1.0)

    def action_toggle_precision_mode(self):
        """Handles keybinding."""
        self.screen.loading = True
        if self.displaying_daily:
            self.draw_hourly()
        else:
            self.draw_daily()


class FavouritesScreen(Screen):
    def compose(self) -> ComposeResult:
        # yield Placeholder(f"{app.screen}")
        with Center():
            yield Label()
        with Center():
            yield ListView(initial_index=0)
        yield Footer()

    @on(ScreenResume)
    def on_mount(self):
        # get a list of all city names as strings from db
        favourites = list(map(lambda favourite: favourite.city_name, Alert.select(Alert.city_name)))
        label = self.screen.query_one(Label)
        if not favourites:
            label.update("You haven't saved any cities yet.")
        else:
            label.update("Your favourite cities:")

        list_view = self.screen.query_one(ListView)
        list_view.clear()
        for favourite in favourites:
            list_view.append(ListItem(Label(favourite)))

    @on(ListView.Selected)
    def get_plot_for_city(self):
        highlighted_index = self.screen.query_one(ListView).index
        app.city_prompt = Alert.select(Alert.city_name)[highlighted_index].city_name    # TODO: bottleneck to remove
        app.switch_screen("plot")


class AlertsScreen(Screen):
    COLUMNS = [
        "№",
        "City",
        "Alert name",
        "Severity",
        "Min. temp",
        "Max. temp",
        "Min. wind speed",
        "Max. wind speed",
    ]
    label = "These are your saved alerts:"

    def compose(self) -> ComposeResult:
        # yield Placeholder("Alerts Screen")
        yield Label("", classes="help_label")
        yield DataTable(id="alerts_data_table")
        yield Footer()

    @on(ScreenResume)
    def update_rows(self):
        placeholder = "-not set-"
        data_table = self.screen.query_one("#alerts_data_table", DataTable)
        data_table.clear()
        alerts = list(
            map(
                lambda a: (
                    a.id,
                    a.city_name,
                    a.name,
                    a.severity,
                    a.min_temp if a.min_temp > MIN_TEMP else placeholder,
                    a.max_temp if a.max_temp < MAX_TEMP else placeholder,
                    a.min_wind_speed if a.min_wind_speed > MIN_WINDSPEED else placeholder,
                    a.max_wind_speed if a.max_wind_speed < MAX_WINDSPEED else placeholder,
                ),
                Alert.select(),
            )
        )
        data_table.add_rows(alerts)

    def on_mount(self):
        data_table = self.screen.query_one("#alerts_data_table", DataTable)
        data_table.add_columns(*self.COLUMNS)
        self.update_rows()

        label = self.screen.query_one(Label)
        if data_table.row_count == 0:
            label.update("You haven't saved any cities yet.")
            data_table.display = False
        else:
            label.update(self.label)
            data_table.display = True


class TerminalUserInterface(App):
    my_weather_app = MyWeatherApp()
    db = pw.SqliteDatabase(DATABASE_FILENAME)
    db.connect()
    city_prompt = None  # to store the city name entered by user between screens
    dialog_popup_text = None

    CSS_PATH = "terminal_user_interface.tcss"
    BINDINGS = [
        ("w", "switch_to_screen('ask_for_city')", "Check weather"),
        ("f", "switch_to_screen('favourites')", "Favourites"),
        ("a", "switch_to_screen('alerts')", "Alerts"),
        Binding("m, escape", "switch_to_screen('main')", "Return to main", priority=True),
        ("d", "toggle_dark", "Toggle dark mode"),
        Binding("ctrl+q", "quit", "Quit", show=False, priority=True),
    ]
    SCREENS = {
        "main": MainScreen,
        "favourites": FavouritesScreen,
        "alerts": AlertsScreen,
        "ask_for_city": AskForCityScreen,
        "plot": PlotScreen,
        "ask_alert_details": AskAlertDetailsScreen,
        "dialog_popup": DialogPopupScreen,
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

    def display_dialog(self, text):
        """Displays a modal screen with text."""
        self.dialog_popup_text = text
        self.push_screen("dialog_popup")

    def action_quit(self):
        app.db.close()
        return super().action_quit()

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
    app.db.close()
