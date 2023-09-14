from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QInputDialog

from je_editor.pyside_ui.browser.browser_serach_lineedit import BrowserLineSearch
from je_editor.pyside_ui.browser.browser_view import BrowserView


class JEBrowser(QWidget):

    def __init__(self, start_url: str = "https://www.google.com/",
                 search_prefix: str = "https://www.google.com.tw/search?q="):
        super().__init__()
        # Browser setting
        self.browser = BrowserView(start_url)
        self.search_prefix = search_prefix
        # Top bar
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.browser.back)
        self.forward_button = QPushButton("Forward")
        self.forward_button.clicked.connect(self.browser.forward)
        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.browser.reload)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search)
        self.url_input = BrowserLineSearch(self)
        # Action
        self.find_action = QAction()
        self.find_action.setShortcut("Ctrl+f")
        self.find_action.triggered.connect(self.find_text)
        self.addAction(self.find_action)
        # Layout
        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.back_button, 0, 0)
        self.grid_layout.addWidget(self.forward_button, 0, 1)
        self.grid_layout.addWidget(self.reload_button, 0, 2)
        self.grid_layout.addWidget(self.url_input, 0, 3)
        self.grid_layout.addWidget(self.search_button, 0, 4)
        self.grid_layout.addWidget(self.browser, 1, 0, -1, -1)
        self.setLayout(self.grid_layout)

    def search(self):
        self.browser.setUrl(f"{self.search_prefix}{self.url_input.text()}")

    def find_text(self):
        search_box = QInputDialog(self)
        search_text, press_ok = search_box.getText(self, "Search Text", "Input a text")
        if press_ok:
            self.browser.findText(search_text)
        else:
            self.browser.findText("")
