"""Module managing the confirm dialog"""
#      ubiquity
#      Copyright (C) 2023  INSA Rouen Normandie - CIP
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
import webbrowser
from tkinter import ttk
from tkinter.constants import EW

from .base import BaseDialog
from ...utils import LabelEnum, gettext

_ = gettext.gettext

class ConfirmDialog(BaseDialog):
    """Class for the choice dialog"""
    def __init__(self, parent, title=""):
        self.choice = False
        super().__init__(parent, title)

    def _event_setup(self):
        pass

    def _ui_setup(self):
        mainframe = ttk.Frame(self, padding="3 3 12 12")
        mainframe.pack()
        self.resizable(False, False)

        ttk.Label(mainframe, text=LabelEnum.ARE_YOU_SURE.value).grid(column=0, row=0, sticky=EW)

        # Create buttons
        ttk.Button(mainframe, text=LabelEnum.YES.value, command=self.confirm_yes).grid(column=0, row=1, sticky=EW)
        ttk.Button(mainframe, text=LabelEnum.NO.value, command=self.confirm_no).grid(column=1, row=1, sticky=EW)
        ttk.Button(mainframe, text=LabelEnum.DOCUMENTATION.value, command=self.documentation).grid(
            column=2, row=1, sticky=EW)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def confirm_yes(self):
        """Method to choice yes and quit the dialog"""
        self.choice = True
        self.dismiss()

    def confirm_no(self):
        """Method to choice no and quit the dialog"""
        self.dismiss()

    @staticmethod
    def documentation():
        """Method to choice documentation"""
        webbrowser.open(
            "https://gitlab.insa-rouen.fr/cip/ubiquity/-/wikis/Mode-d'emploi-de-l'application-%C3%A9tudiante"
        )
