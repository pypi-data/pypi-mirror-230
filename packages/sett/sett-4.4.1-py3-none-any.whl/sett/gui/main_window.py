import warnings
from dataclasses import dataclass
from typing import Callable, Type, cast

from libbiomedit.lib import deserialize as serialization

from sett import (
    APP_NAME_LONG,
    URL_READTHEDOCS,
    URL_GITLAB_ISSUES,
    APP_NAME_SHORT,
    URL_GITLAB,
    VERSION_WITH_DEPS,
)
from .component import show_warning, is_macos, NormalMessageBox
from .decrypt_tab import DecryptTab
from .encrypt_tab import EncryptTab
from .keys_tab import KeysTab
from .model import AppData, ConfigProxy
from .parallel import run_thread
from .pyside import QtCore, QtGui, QtWidgets, open_window
from .settings_tab import SettingsTab
from .theme import Icon, IconRepainter, Action, get_icon_repainter
from .transfer_tab import TransferTab
from ..core.versioncheck import check_version
from ..utils.config import Config, load_config, save_config, config_to_dict

QtCore.QThreadPool.globalInstance().setExpiryTimeout(-1)


@dataclass(frozen=True)
class Tab:
    icon_file_name: str
    label: str
    component: Type[QtWidgets.QWidget]


class MainWindow(QtWidgets.QMainWindow):
    """Class that initializes the main QtWidget (window) of the application,
    onto which all other components will be added.
    """

    def __init__(self, icon_repainter: IconRepainter) -> None:
        super().__init__()
        self.icon_repainter = icon_repainter
        self.app_data = AppData(config=ConfigProxy(self.load_config_from_disk()))
        self.tabs = (
            Tab(":icon/feather/lock.png", "&Encrypt", EncryptTab),
            Tab(":icon/feather/send.png", "&Transfer", TransferTab),
            Tab(":icon/feather/unlock.png", "&Decrypt", DecryptTab),
            Tab(":icon/feather/key.png", "&Keys", KeysTab),
            Tab(":icon/feather/settings.png", "&Settings", SettingsTab),
        )
        self.setWindowTitle(APP_NAME_LONG)
        self.add_menu()
        self.add_tabs()
        self.add_status_bar()
        self.check_version()

    def load_config_from_disk(self) -> Config:
        """Load user config settings from the default config file."""
        with warnings.catch_warnings(record=True) as w:
            config = load_config()
            if w:
                show_warning(
                    "Configuration Error",
                    "\n".join(format(warning.message) for warning in w),
                    self,
                )
        return config

    def add_tabs(self) -> None:
        tab_widget = QtWidgets.QTabWidget()
        for tab in self.tabs:
            tab_widget.addTab(
                tab.component(parent=self, app_data=self.app_data),  # type: ignore
                Icon(tab.icon_file_name),
                tab.label,
            )
        get_icon_repainter(self).register(self.repaint_tab_icons)
        scrollArea = QtWidgets.QScrollArea(self)
        scrollArea.setWidget(tab_widget)
        scrollArea.setWidgetResizable(True)
        self.setCentralWidget(scrollArea)

    def repaint_tab_icons(self) -> None:
        for i, tab in enumerate(self.tabs):
            self.tab_widget.setTabIcon(i, Icon(tab.icon_file_name))

    @property
    def tab_widget(self) -> QtWidgets.QTabWidget:
        scroll_area = cast(QtWidgets.QScrollArea, self.centralWidget())
        return cast(QtWidgets.QTabWidget, scroll_area.widget())

    def add_status_bar(self) -> None:
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)

    def add_menu(self) -> None:
        action_exit = Action(":icon/feather/log-out.png", "&Exit", self)
        action_exit.setShortcut(QtGui.QKeySequence("Ctrl+Q"))
        action_exit.setStatusTip("Exit application")
        action_exit.triggered.connect(self.close)

        menu = self.menuBar()
        menu.setNativeMenuBar(not is_macos())
        menu_file = menu.addMenu("&File")
        menu_file.addAction(action_exit)

        action_help = Action(":icon/feather/book-open.png", "&Documentation", self)
        action_help.setStatusTip("Open online documentation")
        action_help.setShortcut(
            QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.HelpContents)
        )
        action_help.triggered.connect(open_url(URL_READTHEDOCS))

        action_bug_report = Action(
            ":icon/feather/alert-triangle.png", "&Report an Issue", self
        )
        action_bug_report.setStatusTip("Open online bug report form")
        action_bug_report.triggered.connect(open_url(URL_GITLAB_ISSUES))

        action_about = Action(":icon/feather/info.png", "&About", self)
        action_about.setStatusTip("Show info about application")
        action_about.triggered.connect(self.show_about)

        menu_help = menu.addMenu("&Help")
        menu_help.addAction(action_help)
        menu_help.addAction(action_bug_report)
        menu_help.addAction(action_about)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Code that is run when the application is closed by the user."""

        # Clear focus on the currently selected widget. This is only needed
        # for the case where a user exits the app while still having the
        # focus on a field in the Settings Tab.
        if self.focusWidget():
            self.focusWidget().clearFocus()

        # Compare the current in-memory config values to those present on disk
        # (in the user's config file). If they differ, ask the user whether
        # they want to save their config value modifications to disk.
        config_on_disk = serialization.serialize(Config)(self.load_config_from_disk())
        config_in_app = serialization.serialize(Config)(self.app_data.config)
        if config_on_disk != config_in_app:
            msg = NormalMessageBox(self, "Persist changed settings?")
            msg.set_text_list(
                (
                    "You made changes to settings you did not persist yet.",
                    "Do you want to permanently save them to your sett "
                    "configuration file?",
                )
            )
            msg.setStandardButtons(
                QtWidgets.QMessageBox.StandardButton.Cancel
                | QtWidgets.QMessageBox.StandardButton.No
                | QtWidgets.QMessageBox.StandardButton.Yes
            )
            msg.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
            msg.setIcon(QtWidgets.QMessageBox.Icon.Question)
            reply = open_window(msg)
            if reply == QtWidgets.QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                save_config(config_to_dict(self.app_data.config.get_config()))

        if self.app_data.config.gui_quit_confirmation:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Quit",
                "Do you really want to quit?",
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No,
            )
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()

    def check_version(self) -> None:
        if not self.app_data.config.check_version:
            return

        def get_warnings() -> str:
            with warnings.catch_warnings(record=True) as w:
                check_version(self.app_data.config.repo_url, gui_formatting=True)
                return "\n".join(format(warning.message) for warning in w)

        run_thread(
            get_warnings,
            f_kwargs={},
            report_config=self.app_data.config,
            signals={
                "result": lambda x: show_warning("Version check", x, self) if x else x
            },
        )

    def show_about(self) -> None:
        msg = QtWidgets.QMessageBox(parent=self)
        msg.setWindowTitle("About")
        msg.setIconPixmap(QtGui.QPixmap(":icon/biomedit_logo.png"))
        msg.setTextFormat(QtCore.Qt.TextFormat.RichText)
        msg.setText(
            f"{APP_NAME_LONG}<br>"
            f"{VERSION_WITH_DEPS}<br><br>"
            f"For documentation go to "
            f"<a href='{URL_READTHEDOCS}'>{URL_READTHEDOCS}</a><br>"
            f"To report an issue go to "
            f"<a href='{URL_GITLAB_ISSUES}'>{URL_GITLAB_ISSUES}</a><br>"
            f"Source code is available at "
            f"<a href='{URL_GITLAB}'>{URL_GITLAB}</a><br><br>"
            f"{APP_NAME_SHORT} is developed as part of the "
            f"<a href='https://www.biomedit.ch/'>BioMedIT "
            f"project</a>"
        )
        msg.show()


def open_url(url: str) -> Callable[[], None]:
    """Returns a function that will open the specified URL in the user's
    default browser when called. The returned function has no arguments.

    :param url: URL to open.
    :returns: function that opens the specified URL.
    """

    def open_url_template() -> None:
        if not QtGui.QDesktopServices.openUrl(QtCore.QUrl(url)):
            msg_warn = QtWidgets.QMessageBox()
            msg_warn.setWindowTitle("Warning")
            msg_warn.setText(f"Unable to open URL at \n{url}.")
            msg_warn.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            open_window(msg_warn)

    return open_url_template
