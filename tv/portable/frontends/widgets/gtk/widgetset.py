# Miro - an RSS based video player application
# Copyright (C) 2005-2008 Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the OpenSSL
# library.
#
# You must obey the GNU General Public License in all respects for all of
# the code used other than OpenSSL. If you modify file(s) with this
# exception, you may extend this exception to your version of the file(s),
# but you are not obligated to do so. If you do not wish to do so, delete
# this exception statement from your version. If you delete this exception
# statement from all source files in the program, then also delete it here.

import gtk

from miro.frontends.widgets.gtk.base import Widget, Bin
from miro.frontends.widgets.gtk.const import *
from miro.frontends.widgets.gtk.controls import TextEntry, SecureTextEntry, \
        SearchTextEntry, Checkbox, RadioButton, RadioButtonGroup
from miro.frontends.widgets.gtk.customcontrols import CustomButton, \
        ContinuousCustomButton, CustomSlider
from miro.frontends.widgets.gtk.drawing import ImageSurface, DrawingContext, \
        DrawingArea, Background, Gradient
from miro.frontends.widgets.gtk.layout import HBox, VBox, Alignment, \
        Splitter, Table
from miro.frontends.widgets.gtk.window import Window, MainWindow, Dialog, \
        FileOpenDialog, FileSaveDialog, AboutDialog, AlertDialog
from miro.frontends.widgets.gtk.tableview import TableView, TableModel, \
        TreeTableModel, CellRenderer, ImageCellRenderer, CustomCellRenderer
from miro.frontends.widgets.gtk.simple import Image, ImageDisplay, Label, \
        Scroller, Expander, SolidBackground, OptionMenu, Button
from miro.frontends.widgets.gtk.video import VideoRenderer

# Just use the GDK Rectangle class
Rect = gtk.gdk.Rectangle

"""
Some controls styling slightly differ between platforms. Specify styles here.
"""

FEEDVIEW_BUTTONS_TEXT_SIZE = 0.85
