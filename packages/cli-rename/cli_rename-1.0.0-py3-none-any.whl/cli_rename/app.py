#!/bin/env python3
from textual.app import App, ComposeResult
import textual.containers
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Footer, ListView, ListItem, Button, Label, Input
from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message
import os
import os.path
import sys
import re

CODE_DIR = os.path.dirname(os.path.realpath(__file__))
CSS_FILE = os.path.join(CODE_DIR, "style.tcss")

class RenameApp(App):
    """A Textual app to manage stopwatches."""
    CSS_PATH = CSS_FILE
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit")
    ]

    def __init__(self, pwd, **kwargs):
        super().__init__(**kwargs)
        self.pwd = pwd
        self.dark = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        self.original = ScrollableContainer(classes="box", id="original")
        self.applied = ScrollableContainer(classes="box", id="applied")
        yield self.original
        yield self.applied
        yield Horizontal(
            Label("Pattern"),
            Input(placeholder="pattern", id="pattern"),
            Button("Filter", id="btn_filter"),
            Label("Replace"),
            Input(placeholder="replace", id="replace"),
            Button("Apply", id="btn_apply"),
            id="tool"
        )
        yield Footer()

    def update_filelist(self, filelist):
        self.filelist = filelist
        self.original.query("Label").remove()
        for f in filelist:
            self.original.mount(Label(f))

    def on_mount(self) -> None:
        """Mount the app."""

        filelist = os.listdir(self.pwd)
        filelist.sort()
        self.update_filelist(filelist)

        self.watch(self.original, "scroll_x", self.on_origin_scrolling)
        self.watch(self.original, "scroll_y", self.on_origin_scrolling)
        self.watch(self.applied, "scroll_x", self.on_applied_scrolling)
        self.watch(self.applied, "scroll_y", self.on_applied_scrolling)

    
    def replace(self, pattern, replace):
        rst = []
        
        pat = None
        errmsg = None
        try:
            pat = re.compile(pattern)
        except Exception as e:
            errmsg = str(e)
        
        if errmsg:
            return [(f, False, errmsg) for f in self.filelist]
        
        for f in self.filelist:
            mat = pat.match(f)
            if mat:
                try:
                    new_name = pat.sub(replace, f)
                    if new_name:
                        rst.append((f, True, new_name))
                    else:
                        rst.append((f, False, "empty name"))
                except Exception as e:
                    rst.append((f, False, str(e)))
            else:
                rst.append((f, False, "mis match"))
        return rst
    
    def on_input_changed(self, *args, **kwargs):
        pattern = self.query_one("#pattern").value
        replace = self.query_one("#replace").value
        rst = self.replace(pattern, replace)

        self.applied.query("Label").remove()
        for f, match, new_name in rst:
            if match:
                self.applied.mount(Label(new_name))
            else:
                label = Label(new_name)
                label.set_styles("color: red;")
                self.applied.mount(label)

        self.applied.scroll_x = self.original.scroll_x
        self.applied.scroll_y = self.original.scroll_y
    
    def on_origin_scrolling(self, old_value, new_value):
        x = self.original.scroll_x
        y = self.original.scroll_y
        self.applied.scroll_x = x
        self.applied.scroll_y = y
    
    def on_applied_scrolling(self, old_value, new_value):
        x = self.applied.scroll_x
        y = self.applied.scroll_y
        self.original.scroll_x = x
        self.original.scroll_y = y

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pat = self.query_one("#pattern").value
        rep = self.query_one("#replace").value
        if event.button.id == "btn_apply":
            rst = self.replace(pat, rep)
            filelist = []
            for f, match, new_name in rst:
                if match:
                    filelist.append(new_name)
                    os.rename(os.path.join(self.pwd, f), os.path.join(self.pwd, new_name))
                else:
                    filelist.append(f)
            self.update_filelist(filelist)
            self.on_input_changed()

        elif event.button.id == "btn_filter":
            rst = self.replace(pat, rep)
            filelist = []
            for f, match, new_name in rst:
                if match:
                    filelist.append(f)
            self.update_filelist(filelist)
            self.on_input_changed()

            
            

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
    
    def action_quit(self) -> None:
        """An action to quit the app."""
        self.exit()
