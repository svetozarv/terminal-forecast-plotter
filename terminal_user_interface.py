import logging
from typing import Any

import peewee as pw
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import (
    Center,
    Container,
    Grid,
    Horizontal,
    HorizontalGroup,
    VerticalScroll,
)
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
    Favourite,
)
from my_weather_app import MyWeatherApp

logging.getLogger("terminal_user_interface")
logging.basicConfig(filename='terminal_user_interface.log', level=logging.INFO, filemode="w+")


class MainScreen(Screen):
    main_help_label = "Hi!\nWelcome to terminal_forecast_plotter!\n" + \
        "Start by pressing 'w' and entering a city.\nAlert warnings will appear on this screen."

    def compose(self) -> ComposeResult:
        with Center():
            yield Label(self.main_help_label, id="main_help_label")
        with Center():
            yield Label("Alert has been triggered!\n", id="alert_has_been_triggered_label")
        with Center():
            yield VerticalScroll(classes="main_warning_labels_vertical_scroll")
        yield Footer()

    @on(ScreenResume)
    def check_alert_on_resume(self):
        app.asked_for_comparable_city = False
        main_warning_labels_vertical_scroll = self.screen.query_one(VerticalScroll)
        main_warning_labels_vertical_scroll.remove_children(".alert_labels")
        self.check_alerts()
        if not main_warning_labels_vertical_scroll.children:
            self.query_one("#main_help_label", Label).update(self.main_help_label)

    def on_mount(self):
        self.check_alerts()

    def check_alerts(self):
        self.screen.query_one("#alert_has_been_triggered_label", Label).display = False
        self.query_one("#main_help_label", Label).display = True
        for alert in list(Alert.select()):
            self.check_alert_for_city(alert)

    def check_alert_for_city(self, alert: pw.BaseModelSelect):
        current_weather = app.my_weather_app.get_current_weather((alert.lat, alert.lon))
        current_temp = current_weather.temperature_2m
        current_wind_speed = current_weather.wind_speed_10m

        if current_temp < alert.min_temp:
            self.add_warning_label(
                f"The temperature for {alert.city_name} has dropped below {alert.min_temp}°C\n",
                alert.severity,
            )
        if current_temp > alert.max_temp:
            self.add_warning_label(
                f"The temperature for {alert.city_name} has raised above {alert.max_temp}°C\n",
                alert.severity,
            )

        if current_wind_speed > alert.max_wind_speed:
            self.add_warning_label(
                f"The wind speed for {alert.city_name} has raised above {alert.max_wind_speed} m/s\n",
                alert.severity,
            )
        if current_wind_speed < alert.min_wind_speed:
            self.add_warning_label(
                f"The wind speed for {alert.city_name} has dropped below {alert.min_wind_speed} m/s\n",
                alert.severity,
            )

    def add_warning_label(self, text: str, severity: str):
        main_help_label = self.query_one("#main_help_label", Label)
        main_help_label.display = False
        alert_triggered_label = self.screen.query_one("#alert_has_been_triggered_label", Label)
        alert_triggered_label.display = True

        css_classes = "alert_labels "
        if severity == "INFO":
            css_classes += "info_label"
        if severity == "WARNING":
            css_classes += "warning_label"
        if severity == "DANGER":
            css_classes += "danger_label"
        if severity == "CRITICAL":
            css_classes += "critical_label"

        self.screen.query_one(VerticalScroll).mount(Label(text, classes=css_classes))


class PlotScreen(Screen):
    BINDINGS = [
        ("t", "toggle_precision_mode", "Toggle daily/hourly"),
        ("c", "add_city_to_plot", "Compare to city"),
        ("a", "ask_for_details", "Add alert"),
        ("s", "save_to_favourties", "Save to favourites"),
    ]

    def compose(self) -> ComposeResult:
        yield PlotextPlot(id="plotext-plot")
        yield Footer()

    @on(ScreenResume)
    def on_mount(self):
        if app.asked_for_comparable_city:
            self.draw_hourly(clear=False)
        else:
            self.draw_hourly()
        app.refresh_bindings()

    def draw_hourly(self, clear=True):
        plt = self.query_one(PlotextPlot).plt

        # bad solution. better to redraw plot with both series
        # the plot can be cropped
        app.my_weather_app.draw_hourly_plot(plt, app.city_prompt, clear=clear)

        self.query_one(PlotextPlot).refresh()
        self.displaying_daily = False
        self.displaying_hourly = True

    def draw_daily(self, clear=True):
        plt = self.query_one(PlotextPlot).plt
        app.my_weather_app.draw_daily_plot(plt, app.city_prompt, clear)
        self.query_one(PlotextPlot).refresh()
        self.displaying_daily = True
        self.displaying_hourly = False

    def action_add_city_to_plot(self):
        app.asked_for_comparable_city = True
        app.ask_city_label = "What city would you like to compare the forecast to?"
        app.push_screen("ask_for_city")

    def action_ask_for_details(self):
        """Handles keybinding."""
        app.push_screen("ask_alert_details")

    def action_save_to_favourties(self):
        """Handles keybinding."""
        if Favourite.get_or_none(city_name=app.my_weather_app.current_city_name()):
            app.display_dialog("The city is already in your favourites.")
            return
        Favourite(city_name=app.my_weather_app.current_city_name()).save()
        app.display_dialog("Saved!")

    def action_toggle_precision_mode(self):
        """Handles keybinding."""
        if self.displaying_daily:
            self.draw_hourly()
        else:
            self.draw_daily()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action may run."""
        if app.asked_for_comparable_city:
            if action == "switch_to_screen" and parameters[0] == "main":
                return True
            return False
        return True


class FavouritesScreen(Screen):
    def compose(self) -> ComposeResult:
        # yield Placeholder(f"{app.screen}")
        with Center():
            yield Label("", id="favourites_help")
        with Center():
            yield ListView(initial_index=0)
        with Center():
            yield Label("You can pick one to check it's forecast.", id="fav_pick")
        yield Footer()

    @on(ScreenResume)
    def on_mount(self):
        fav_pick_label = self.screen.query_one("#fav_pick", Label)
        favourites = self.get_favourites_from_db()

        label = self.screen.query_one("#favourites_help", Label)
        if not favourites:
            label.update("You haven't saved any cities yet.")
            fav_pick_label.display = False
        else:
            label.update("Your favourite cities:")
            fav_pick_label.display = True

        list_view = self.screen.query_one(ListView)
        list_view.clear()
        for favourite in favourites:
            list_view.append(ListItem(Label(favourite)))

    def get_favourites_from_db(self) -> list[str]:
        # get a list of all city names as strings from db
        return list(map(lambda f: f.city_name, Favourite.select(Favourite.city_name)))

    @on(ListView.Selected)
    def get_plot_for_city(self):
        highlighted_index = self.screen.query_one(ListView).index
        app.city_prompt = Favourite.select(Favourite.city_name)[highlighted_index].city_name    # TODO: bottleneck to remove
        app.switch_screen("plot")


class AlertsScreen(Screen):
    BINDINGS = [
        ("e", "erase_alerts", "Erase alerts"),
    ]
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
        with Center():
            yield Label("", classes="help_label")
        with Center():
            yield DataTable(id="alerts_data_table")
        yield Footer()

    @on(ScreenResume)
    def update_rows(self):
        data_table = self.screen.query_one("#alerts_data_table", DataTable)
        data_table.clear()
        alerts = self.get_alerts_from_db()
        data_table.add_rows(alerts)
        self.display_table(data_table)

    def get_alerts_from_db(self) -> list[Any]:
        placeholder = "-not set-"
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
        return alerts

    def on_mount(self):
        data_table = self.screen.query_one("#alerts_data_table", DataTable)
        data_table.add_columns(*self.COLUMNS)
        self.update_rows()
        self.display_table(data_table)

    def display_table(self, data_table: DataTable) -> bool:
        """
        Displays the table if db is not empty and returns True else doesn't and returns False.
        """
        label = self.screen.query_one(Label)
        if data_table.row_count == 0:
            label.update("You haven't saved any cities yet.")
            data_table.display = False
            return False
        else:
            label.update(self.label)
            data_table.display = True
            return True

    def action_erase_alerts(self):
        for query in Alert.select():
            query.delete_instance()
        app.switch_to_screen('main')


class AskForCityModal(ModalScreen):
    def compose(self) -> ComposeResult:
        with Center():
            yield Label("", classes="help_label")
        with Center():
            yield Input(placeholder="Enter location...", id="city_input")
        with Center():
            yield Label("Press 'esc' to exit.", id="press_esc")
        yield Footer()

    def on_mount(self):
        self.query_one(".help_label", Label).update(app.ask_city_label)

    def on_input_submitted(self):
        city_prompt = self.get_city_prompt()
        if not self.validate_city_name(city_prompt):
            app.display_dialog("Sorry, we couldn't retrive data for the provided location.")
            return
        app.pop_screen()
        app.switch_screen("plot")

    def get_city_prompt(self) -> str:
        # TODO: add validataion, results first, then show if results not None else display msg
        app.city_prompt = self.query_one(Input).value
        return app.city_prompt

    def validate_city_name(self, city_prompt: str) -> bool: #TODO
        return bool(app.my_weather_app.resolve_location(location=city_prompt))


class AskAlertDetailsModal(ModalScreen):
    BINDINGS = [
        Binding("escape", "app.pop_screen()", show=False, priority=True),
    ]

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
        if not app.alert_severity_button_label:
            app.alert_severity_button_label = "INFO"
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
            severity=app.alert_severity_button_label,
            lat=app.my_weather_app.current_coords[0],
            lon=app.my_weather_app.current_coords[1],
            min_temp=min_temp,
            max_temp=max_temp,
            min_wind_speed=min_wind_speed,
            max_wind_speed=max_wind_speed,
        )
        logging.info("Alert was added to db.")

    @on(Input.Submitted)
    def process_submit(self):
        """Process provided values from user."""

        def after_severity_input(*args):
            """Called when AskAlertSeverity is dismissed."""
            self.add_alert()
            # cannot display_dialog() beacuse we don't want to return to AskAlertDetails
            app.dialog_popup_text = "Saved!"
            app.switch_screen("dialog_popup")

        app.push_screen("ask_alert_severity", after_severity_input)


class AskAlertSeverityModal(ModalScreen):
    def compose(self) -> ComposeResult:
        with Center():
            yield Label("Pick your alert's severity:")
        with Horizontal():
            yield Button("INFO", variant="primary")
            yield Button("WARNING", variant="warning")
            yield Button("DANGER", variant="error")
            yield Button("CRITICAL", variant="primary", id="critical_button")

    @on(Button.Pressed)
    def close(self, event: Button.Pressed):
        app.alert_severity_button_label = event.button.label
        self.dismiss()


class DialogPopupModal(ModalScreen):
    """Simple informative pop up screen with text and 'Ok'."""
    def compose(self) -> ComposeResult:
        with VerticalScroll(id="dialog_pop_up"):
            with Center():
                yield Label(app.dialog_popup_text)
            with Center():
                yield Button("OK")

    def on_mount(self):
        self.query_one(Label).update(app.dialog_popup_text)
        self.query_one(Button).focus()

    @on(Button.Pressed)
    def close(self):
        app.pop_screen()


class TerminalUserInterface(App):
    my_weather_app = MyWeatherApp()
    db = pw.SqliteDatabase(DATABASE_FILENAME)
    db.connect()
    city_prompt = None  # to store the city name entered by user between screens
    dialog_popup_text = None
    alert_severity_button_label = None
    ask_city_label = "Hi! In this place you can check the weather in\n" + \
            "any place in the world by typing it in\n " + \
            "the field below."
    asked_for_comparable_city = False

    CSS_PATH = "terminal_user_interface.tcss"
    BINDINGS = [
        ("w", "push_screen('ask_for_city')", "Check weather"),
        ("f", "switch_to_screen('favourites')", "Favourites"),
        ("a", "switch_to_screen('alerts')", "Alerts"),
        Binding("m, escape", "switch_to_screen('main')", "Return to main", priority=True),
        ("d", "toggle_dark", "Toggle dark mode"),
        Binding("ctrl+q", "quit", "Quit", show=False, priority=True),
    ]
    SCREENS = {
        "main": MainScreen,
        "plot": PlotScreen,
        "favourites": FavouritesScreen,
        "alerts": AlertsScreen,
        "ask_for_city": AskForCityModal,
        "ask_alert_details": AskAlertDetailsModal,
        "ask_alert_severity": AskAlertSeverityModal,
        "dialog_popup": DialogPopupModal,
    }

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        # self.install_screen("plot")
        # self.theme = "nord"
        self.push_screen("main")

    def switch_to_screen(self, name):
        self.switch_screen(name)
        self.refresh_bindings()

    def action_switch_to_screen(self, name):
        """Handles keybinding."""
        self.switch_to_screen(name)

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
        if isinstance(self.screen, AlertsScreen):
            if action == "switch_to_screen" and parameters[0] == "alerts":
                return False
        if isinstance(self.screen, FavouritesScreen):
            if action == "switch_to_screen" and parameters[0] == "favourites":
                return False
        if isinstance(self.screen, PlotScreen):
            if self.asked_for_comparable_city:
                if action == "switch_to_screen" and parameters[0] == "main":
                    return True
                else:
                    return False  # disable binds except return to main for city forecasts comparison
            if action == "switch_to_screen" and parameters[0] == "main":
                return True
            if action == "push_screen" and parameters[0] == 'ask_for_city':
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

    # In case of a crash, enshure the connection is closed
    try:
        app.run()
    finally:
        if not app.db.is_closed():
            app.db.close()
