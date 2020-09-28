#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019  Eugene V. Shcherbatyuk
#
# This program and documentation are distributed under the MIT License terms
#
# *** MIT LICENSE **************************************************************
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# *** Author and contributors **************************************************
# Eugene V. Shcherbatyuk (ugnvs[at]mail.ru, eugene.shcherbatyuk[at]gmail.com)
#
# *** Tested in the environment ************************************************
# Ubuntu MATE 18.04.3 64-bit, Python 3.6.8, Tkinter 8.6
# ******************************************************************************

"""Add tooltip to arbitrary tkinter/ttk widget."""

# === Import ===================================================================

import tkinter as tk
import tkinter.ttk as ttk

# === Classes ==================================================================

class ToolTip():
    """
    Tooltip extension for tk widgets.
    
    Just add extra tooltip attribute to the instance of a widget as follows:
    
    mywidget = <some widget_class>
    mywidget.tooltip =  ToolTip(mywidget, 'Some text')
    
    ToolTip constructor can take extra arguments for delay in ms before tooltip
    is shown and/or tooltip text wrap length in pixels and/or timeout in ms
    before tooltip is automatically hidden. For example:
    
    ToolTip(mywidget, 'Some text', delay=500, wraplengs=200, timeout=2000)
    
    Default delay is 2000 ms and default timeout is 4000 ms. Turn off timeout
    by passing 0 as timeout value.
    
    This code is based on ideas from
    https://www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter
    https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter/36221216#36221216
    http://svn.effbot.org/public/stuff/sandbox/wcklib/wckToolTips.py
    
    Unfortunately, none of the implementations above works smoothly out of the box.
    """
    # ------------------------
    def __init__(self, widget, text, delay=1200, wrap=200, timeout=4000):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wrap = wrap
        self.timeout = timeout
        self.tip = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        try:
            self.bg = "systeminfobackground"
            self.fg = "systeminfotext"
            widget.winfo_rgb(self.fg)
            widget.winfo_rgb(self.bg)
        except:
            self.bg = "#DBDBA2"
            self.fg = "#000000"
    
    # ------------------------
    def enter(self, event):
        # it is possible to extract and pass mouse position as event.x_root, event.y_root
        # do nothing if tip is shown already or is scheduled to be shown
        if (self.id == None) and (self.tip == None):
            self.id = self.widget.after(self.delay, self.display)
        
    # ------------------------
    def leave(self, event):
        # tooltip was shcheduled to be shown
        if not (self.id == None):
            self.widget.after_cancel(self.id)
            self.id = None
                
        # tooltip was shown
        if not (self.tip == None):
            self.tip.destroy()
            self.tip = None
    
    # ------------------------
    def display(self):
        self.id = None
        if self.tip == None:
            # get widget geomesty string
            g = self.widget.winfo_geometry().replace('x','+')
            w, h, dx, dy = g.split('+')
            # docs are unclear but it looks like as an absolute position of widget on screen
            # in the worst case one can revert to mouse coordinates taken from event (see above)
            dx = self.widget.winfo_rootx()
            dy = self.widget.winfo_rooty()
            self.tip = tk.Toplevel(self.widget, background="#505050")
            self.tip.overrideredirect(True)
            # offset tooltip from widget not to overlap with it
            # and do not arrive under mouse pointer so that 'leave' event won't occur
            # it's vital for tip begins to flash because endless leave-enter event stream is generated
            self.tip.geometry("+{}+{}".format(int(dx) + int(w)//2, int(dy) + int(h)+2 ))
            # borderwidth without a relief (i.e. flat) just pads label with its background color
            self.lbl = ttk.Label(self.tip, text=self.text, justify=tk.LEFT,
                                background=self.bg, foreground=self.fg, borderwidth=4,
                                wraplength = self.wrap)
            self.lbl.pack(padx=1, pady=1)
            
            if not (self.timeout == 0):
                self.widget.after(self.timeout, lambda : self.leave(0))
        
# === Definitions over =========================================================
# <EOF>