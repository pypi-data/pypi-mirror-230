#!/usr/bin/python3

# ==================================================boilerplate»=====
# *Tonto2* is a rewrite of *tonto* v1.2.
# 
# Copyright 2006—2023 by Chuck Rhode.
# 
# See LICENSE.txt for your rights.
# =================================================«boilerplate======

"""Code Tables.

Code tables are read from an *.ini file in the home directory.

"""

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1
NOT_AVAIL = "#N/A"

import sys
import os
import pathlib
import configparser
import locale

FN = 'tonto.code_tables.ini'
LANG = locale.getlocale()[ZERO]
LANGS = [
    'es_ES',
    ]


def get_xdg_config_home():

    """The configuration directory.

    Normally $HOME/.config. 

    """
    
    result = pathlib.Path.home() / ".config"
    return result


def get_xdg_data_home():

    """The data directory.

    Normally $HOME/.local.

    """

    path_home = pathlib.Path.home()
    repertoire = [
        path_home / ".local",
        path_home / "Tonto2",
        pathlib.Path(os.getenv("VIRTUAL_ENV", NULL)),
        ]

    for result in repertoire:
        if result.exists():
            yield result
    return


class CodeTable(dict):

    """A single table of codes.

    """
    
    def set_meanings(self, pairs):
        self.inverse = {}
        for (key, val) in pairs:
            self[key] = val
            self.inverse[val] = key
        self.codes = list(self.keys())
        self.meanings = list(self.values())
        return self

    def inc(self, code):
        size = len(self)
        try:
            ndx = self.codes.index(code)
        except ValueError:
            ndx = NA
        ndx += 1
        if ndx >= size:
            ndx = ZERO
        result = self.codes[ndx]
        return result

    def dec(self, code):
        size = len(self.codes)
        try:
            ndx = self.codes.index(code)
        except ValueError:
            ndx = NA
        ndx -= 1
        if ndx <= NA:
            ndx = size - 1
        result = self.codes[ndx]
        return result

    def collection_disp(self):
        return self.meanings

    def disp_to_comp(self, disp, default=NOT_AVAIL):
        result = self.inverse.get(disp, default)
        return result

    def comp_to_disp(self, comp, default=NOT_AVAIL):
        result = self.get(comp, default)
        return result


INI = configparser.ConfigParser()
INI.optionxform = str  # Preserve alphabetic case of keys.
for path_home in get_xdg_data_home():
    PATH = path_home / 'Tonto2' / FN
    if PATH.exists():
        break
else:
    print(_('File "{v0}" not found.'.format(v0=str(PATH))))
    raise NotImplementedError
with open(PATH) as unit:
    INI.read_file(unit)
TAB_BY_NAME = {}
if INI.has_section(LANG):
    XLATE_SECTS = CodeTable().set_meanings(INI.items(LANG))
else:
    XLATE_SECTS = CodeTable()
for section in INI.sections():
    if section in LANGS:
        pass
    else:
        sect_i18n = XLATE_SECTS.comp_to_disp(section, default=section)
        table = CodeTable().set_meanings(INI.items(sect_i18n))  # Create new CodeTable.
        table.name = section
        TAB_BY_NAME[section] = table

if __name__ == "__main__":

    """This code is run when this module is executed, not when it is included.

    """
    
    INI.write(sys.stdout)
    
        
# Fin
