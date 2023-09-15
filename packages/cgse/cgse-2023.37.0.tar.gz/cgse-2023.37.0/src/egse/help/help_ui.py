"""
This module provides a HelpWindow that can be used in GUIs to provide easy access to the
documentation of the GUI. The docs are part of the  overall Common-EGSE documentation, but
are mainly located in the man-pages section.

To use this in your GUI, use the following template:

    url = HELP_TOPICS["puna_ui"]

    help_window = HelpWindow(url=url)
    help_window.show()

Make sure the `help_window` variable is not garbage collected (which will destroy the window).
Keep a reference to the window somewhere in your main window or application setup. The HelpWindow
can be closed and re-opened with the `.close()` and `.show()` methods.
"""

import sys

from PyQt5.QtCore import QSize
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QToolBar

from egse.resource import get_resource

__all__ = [
    "HELP_TOPICS",
    "HelpWindow",
]

BASE_URL = "https://ivs-kuleuven.github.io/plato-common-egse/"

# Below are the topics for the GUIs that are known by the setup.py.

HELP_TOPICS = dict(
    home=BASE_URL,
    ogse_ui=BASE_URL,
    puna_ui=f'{BASE_URL}man-pages/hexapod-gui/',
    zonda_ui=f'{BASE_URL}man-pages/hexapod-gui/',
    smc9300_ui=f'{BASE_URL}man-pages/huber-gui/',
    fpa_ui=f'{BASE_URL}man-pages/source-position-gui/',
    vis_pos_ui=f'{BASE_URL}man-pages/visited-positions-gui/',
    lsci336_ui=f'{BASE_URL}man-pages/lakeshore-gui/',
    gimbal_ui=f'{BASE_URL}man-pages/gimbal-gui/',
)


class HelpWindow(QMainWindow):
    """
    Show the help window for a certain topic. This will open a simple browser window pointing to
    the URL that you pass into the constructor. You will be able to navigate through the
    documentation and used the `backward`, `forward` and `reload` buttons as expected for a
    web browser.

    The _Home_ button brings you back to the page referred to by the `topic_url` argument.
    """

    def __init__(self, topic_url: str):
        """
        Args:
            topic_url (str): the starting point for the Help topic.
        """
        super().__init__()

        self.setGeometry(300, 300, 1000, 600)

        self._url = topic_url

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self._url))

        self.setCentralWidget(self.browser)

        navigation_toolbar = QToolBar("Navigation")
        navigation_toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(navigation_toolbar)

        home_btn = QAction(QIcon(str(get_resource(":/icons/home.svg"))), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navigation_toolbar.addAction(home_btn)

        back_btn = QAction(QIcon(str(get_resource(":/icons/backward.svg"))), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(lambda: self.browser.back())
        navigation_toolbar.addAction(back_btn)

        next_btn = QAction(QIcon(str(get_resource(":/icons/forward.svg"))), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(lambda: self.browser.forward())
        navigation_toolbar.addAction(next_btn)

        navigation_toolbar.addSeparator()

        reload_btn = QAction(QIcon(str(get_resource(":/icons/reload.svg"))), "Reload", self)
        reload_btn.setStatusTip("Reload")
        reload_btn.triggered.connect(self.browser.reload)
        navigation_toolbar.addAction(reload_btn)

    def set_topic_home(self, topic: str):
        url = HELP_TOPICS[topic]
        self._url = url
        self.navigate_home()

    def navigate_home(self):
        """
        Navigate to the home page, i.e. the URL that was passed as an argument when constructing
        the Help Window.
        """
        self.browser.setUrl(QUrl(self._url))


if __name__ == "__main__":

    app = QApplication(sys.argv)

    url = HELP_TOPICS["puna_ui"]
    help_window = HelpWindow(topic_url=url)
    help_window.show()

    app.exec_()
