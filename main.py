# Python version: 3.11.2

import sys
from scripts.app import App

if __name__ == "__main__":
    app = App()

    while True:
        app.update()