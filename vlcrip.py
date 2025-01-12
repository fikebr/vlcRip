#!/usr/bin/env python3
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Input, Button, Static
from textual.binding import Binding
import tomli
import subprocess
import os
from pathlib import Path

STYLES = """
Screen {
    align: center middle;
}

#main-container {
    width: 60;
    height: auto;
    border: heavy $accent;
    padding: 1 2;
}

.title {
    content-align: center middle;
    text-style: bold;
    background: $accent;
    color: $text;
    padding: 1;
    margin-bottom: 1;
}

Input {
    margin: 1 0;
}

Button {
    margin-top: 1;
    width: 100%;
}

#status {
    height: auto;
    margin-top: 1;
    text-align: center;
}
"""

class VLCRipperApp(App):
    CSS = STYLES
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "rip", "Start Ripping", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.config = self.load_config()

    def load_config(self) -> dict:
        config_path = Path("config.toml")
        if not config_path.exists():
            self.exit(message="Config file not found!")
        with open(config_path, "rb") as f:
            return tomli.load(f)

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            yield Static("VLC DVD Ripper", classes="title")
            yield Input(placeholder="Enter output filename (e.g. movie.mp4)", id="filename")
            yield Button("Start Ripping", variant="primary")
            yield Static("Ready to rip DVD...", id="status")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.action_rip()

    def action_rip(self) -> None:
        filename = self.query_one("#filename").value
        if not filename:
            self.query_one("#status").update("Please enter a filename!")
            return

        if not filename.endswith('.mp4'):
            filename += '.mp4'

        vlc_path = self.config["paths"]["vlc_path"]
        output_folder = self.config["paths"]["output_folder"]
        output_path = os.path.join(output_folder, filename)

        self.query_one("#status").update("Ripping DVD... Please wait...")
        
        try:
            cmd = [
                vlc_path,
                "dvdsimple:///d:",
                f'--sout=#standard{{access=file,mux=ts,dst={output_path}}}',
                'vlc://quit'
            ]
            subprocess.run(cmd, check=True)
            self.query_one("#status").update(f"Successfully ripped DVD to: {output_path}")
            self.query_one("#filename").update("")
        except subprocess.CalledProcessError:
            self.query_one("#status").update("Error occurred while ripping DVD!")
        except Exception as e:
            self.query_one("#status").update(f"Error: {str(e)}")

if __name__ == "__main__":
    app = VLCRipperApp()
    app.run()
