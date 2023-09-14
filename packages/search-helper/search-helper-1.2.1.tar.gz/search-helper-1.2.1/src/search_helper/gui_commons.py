# -*- coding: utf-8 -*-

"""
search_helper.gui_commons

Common GUI parts

Copyright (C) 2020-2023 Rainer Schwarzbach

This file is part of search_helper.

search_helper is free software:
you can redistribute it and/or modify it under the terms of the MIT License.

search_helper is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import tkinter
import webbrowser

from typing import Optional, Tuple, Union


#
# Classes
#


# pylint: disable=too-few-public-methods


class Link:

    """Hyperlink on a line by itself, with an optional label prefix"""

    def __init__(self, url: str, label: Optional[str] = None) -> None:
        """Store the parameters"""
        self.url = url
        self.label = label

    def grid(self, parent: tkinter.Frame, **kwargs) -> None:
        """Build the link widget"""
        if self.label:
            frame = tkinter.Frame(parent)
            prefix = tkinter.Label(frame, text=self.label)
            prefix.grid(row=0, column=0)
            link_obj = self.__class__(self.url, label=None)
            link_obj.grid(frame, row=0, column=1)
            frame.grid(sticky=tkinter.W, padx=5)
        else:
            kwargs.setdefault("sticky", tkinter.W)
            kwargs.setdefault("padx", 5)
            link = tkinter.Label(
                parent, text=self.url, fg="blue", cursor="hand2"
            )
            link.grid(**kwargs)
            link.bind(
                "<Button-1>", lambda e: webbrowser.open_new_tab(self.url)
            )
        #


class TextBlock:

    """Text block"""

    def __init__(self, text: str) -> None:
        """Store the parameters"""
        self.text = text

    def grid(self, parent: tkinter.Frame, **kwargs) -> None:
        """Build the textblock widget"""
        kwargs.setdefault("sticky", tkinter.W)
        kwargs.setdefault("padx", 5)
        kwargs.setdefault("pady", 5)
        text_area = tkinter.Label(parent, text=self.text, justify=tkinter.LEFT)
        text_area.grid(**kwargs)


class Section:

    """Section consisting of a headline, normal text blocks,
    and/or links
    """

    def __init__(
        self, headline: str, *contents: Union[Link, TextBlock]
    ) -> None:
        """Initialize the section"""
        self.headline = headline
        self.contents = contents

    def grid(self, parent: tkinter.Frame) -> None:
        """Build all widgets in the section"""
        heading_area = tkinter.Label(
            parent,
            text=self.headline,
            font=(None, 11, "bold"),
            justify=tkinter.LEFT,
        )
        heading_area.grid(sticky=tkinter.W, padx=5, pady=10)
        for widget in self.contents:
            widget.grid(parent)
        #


# pylint: enable=too-few-public-methods


class ModalDialog(tkinter.Toplevel):

    """Adapted from
    <https://effbot.org/tkinterbook/tkinter-dialog-windows.htm>
    """

    def __init__(
        self,
        parent,
        content: Tuple[Section, ...],
        title=None,
        cancel_button=True,
    ):
        """Create the toplevel window and wait until the dialog is closed"""
        super().__init__(parent)
        self.transient(parent)
        if title:
            self.title(title)
        #
        self.parent = parent
        self.initial_focus = self
        self.body = tkinter.Frame(self)
        self.create_content(content)
        self.body.grid(padx=5, pady=5, sticky=tkinter.E + tkinter.W)
        self.create_buttonbox(cancel_button=cancel_button)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.action_cancel)
        self.initial_focus.focus_set()
        self.wait_window(self)

    def create_content(self, content: Tuple[Section, ...]):
        """Add content to body"""
        raise NotImplementedError

    def create_buttonbox(self, cancel_button=True):
        """Add standard button box."""
        box = tkinter.Frame(self)
        button = tkinter.Button(
            box,
            text="OK",
            width=10,
            command=self.action_ok,
            default=tkinter.ACTIVE,
        )
        button.grid(padx=5, pady=5, row=0, column=0, sticky=tkinter.W)
        if cancel_button:
            button = tkinter.Button(
                box, text="Cancel", width=10, command=self.action_cancel
            )
            button.grid(padx=5, pady=5, row=0, column=1, sticky=tkinter.E)
        #
        self.bind("<Return>", self.action_ok)
        box.grid(padx=5, pady=5, sticky=tkinter.E + tkinter.W)

    #
    # standard button semantics

    def action_ok(self, event=None):
        """Clean up"""
        del event
        self.withdraw()
        self.update_idletasks()
        self.action_cancel()

    def action_cancel(self, event=None):
        """Put focus back to the parent window"""
        del event
        self.parent.focus_set()
        self.destroy()


class InfoDialog(ModalDialog):

    """Info dialog,
    instantiated with series Section instances
    after the parent window
    """

    def __init__(self, parent, *content: Section, title=None):
        """..."""
        super().__init__(parent, content, title=title, cancel_button=False)

    def create_content(self, content: Tuple[Section, ...]):
        """Add content to body"""
        for single_section in content:
            single_section.grid(self.body)
        #


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
