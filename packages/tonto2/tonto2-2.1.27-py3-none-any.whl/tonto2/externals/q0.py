#!/usr/bin/python3

# q0.py
# ccr . 2021 May 27

# ==================================================boilerplate»=====
# Copyright 2006—2023 by Chuck Rhode.
# 
# See LICENSE.txt for your rights.
# =================================================«boilerplate======

"""Refactor Qt5 for Python.

This is a collection of subclasses to those provided by various Qt
modules.  The goal is to mask the arcane module structure of Qt.  This
comes at the expense of importing everything from Qt at once, of
course.  The classes exposed by this module are intended for slightly
higher-level use than the common Qt classes.

"""

# ccr . 2023 Sep 05 . Mods for Windows install of Tonto2.

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1

import sys
import locale
import datetime
from PyQt5 import QtCore, QtWidgets, QtGui, QtMultimedia, Qt


def invert(relationship):

    """Invert keys and values in a dictionary.

    What follows are mnemonic names for QtCore constants.  These are
    arranged in dictionaries of constants my mnemonic name.  We then
    invert each dictionary into another dictionary of mnemonic name by
    constant.

    """

    result = {}
    for (key, val) in relationship.items():
        result[val] = key
    return result


Q0_CODE_ALIGNMENT = {
    'no alignment': QtCore.Qt.AlignLeft,
    'northwest': QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop,
    'west': QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
    'southwest': QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom,
    'north': QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop,
    'center': QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
    'south': QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom,
    'northeast': QtCore.Qt.AlignRight | QtCore.Qt.AlignTop,
    'east': QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
    'southeast': QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom,
    'top': QtCore.Qt.AlignTop,
    'bottom': QtCore.Qt.AlignBottom,
    'left': QtCore.Qt.AlignLeft,
    'right': QtCore.Qt.AlignRight,
    }
Q0_MNEMONIC_ALIGNMENT = invert(Q0_CODE_ALIGNMENT)
for (key_new, key_old) in [
    ('nw', 'northwest'),
    ('↖', 'northwest'),
    ('sw', 'southwest'),
    ('↙', 'southwest'),
    ('ne', 'northeast'),
    ('↗', 'northeast'),
    ('se', 'southeast'),
    ('↘', 'southeast'),
    ('w', 'west'),
    ('←', 'west'),
    ('n', 'north'),
    ('↑', 'north'),
    ('e', 'east'),
    ('→', 'east'),
    ('s', 'south'),
    ('↓', 'south'),
    ('c', 'center'),
    ('x', 'center'),
    ('*', 'center'),
    ]:
    Q0_CODE_ALIGNMENT[key_new] = Q0_CODE_ALIGNMENT[key_old]

Q0_CODE_MSGBOX_BUTTONS = {
    'abort': QtWidgets.QMessageBox.Abort,
    'apply': QtWidgets.QMessageBox.Apply,
    'cancel': QtWidgets.QMessageBox.Cancel,
    'close': QtWidgets.QMessageBox.Close,
    'discard': QtWidgets.QMessageBox.Discard,
    'help': QtWidgets.QMessageBox.Help,
    'ignore': QtWidgets.QMessageBox.Ignore,
    'no': QtWidgets.QMessageBox.No,
    'nobutton': QtWidgets.QMessageBox.NoButton,
    'notoall': QtWidgets.QMessageBox.NoToAll,
    'ok': QtWidgets.QMessageBox.Ok,
    'open': QtWidgets.QMessageBox.Open,
    'reset': QtWidgets.QMessageBox.Reset,
    'restoredefaults': QtWidgets.QMessageBox.RestoreDefaults,
    'retry': QtWidgets.QMessageBox.Retry,
    'save': QtWidgets.QMessageBox.Save,
    'saveall': QtWidgets.QMessageBox.SaveAll,
    'yes': QtWidgets.QMessageBox.Yes,
    'yestoall': QtWidgets.QMessageBox.YesToAll,
    }
Q0_MNEMONIC_MSGBOX_BUTTONS = invert(Q0_CODE_MSGBOX_BUTTONS)

Q0_CODE_DLGBOX_BUTTONS = {
    'abort': QtWidgets.QDialogButtonBox.Abort,
    'apply': QtWidgets.QDialogButtonBox.Apply,
    'cancel': QtWidgets.QDialogButtonBox.Cancel,
    'close': QtWidgets.QDialogButtonBox.Close,
    'discard': QtWidgets.QDialogButtonBox.Discard,
    'help': QtWidgets.QDialogButtonBox.Help,
    'ignore': QtWidgets.QDialogButtonBox.Ignore,
    'no': QtWidgets.QDialogButtonBox.No,
    'nobutton': QtWidgets.QDialogButtonBox.NoButton,
    'notoall': QtWidgets.QDialogButtonBox.NoToAll,
    'ok': QtWidgets.QDialogButtonBox.Ok,
    'open': QtWidgets.QDialogButtonBox.Open,
    'reset': QtWidgets.QDialogButtonBox.Reset,
    'restoredefaults': QtWidgets.QDialogButtonBox.RestoreDefaults,
    'retry': QtWidgets.QDialogButtonBox.Retry,
    'save': QtWidgets.QDialogButtonBox.Save,
    'saveall': QtWidgets.QDialogButtonBox.SaveAll,
    'yes': QtWidgets.QDialogButtonBox.Yes,
    'yestoall': QtWidgets.QDialogButtonBox.YesToAll,
    }
Q0_MNEMONIC_DLGBOX_BUTTONS = invert(Q0_CODE_DLGBOX_BUTTONS)

Q0_CODE_DLGBOX_BUTTON_ROLES = {
    'Invalid': QtWidgets.QDialogButtonBox.InvalidRole,
    'Accept': QtWidgets.QDialogButtonBox.AcceptRole,
    'Reject': QtWidgets.QDialogButtonBox.RejectRole,
    'Destructive': QtWidgets.QDialogButtonBox.DestructiveRole,
    'Action': QtWidgets.QDialogButtonBox.ActionRole,
    'Help': QtWidgets.QDialogButtonBox.HelpRole,
    'Yes': QtWidgets.QDialogButtonBox.YesRole,
    'No': QtWidgets.QDialogButtonBox.NoRole,
    'Apply': QtWidgets.QDialogButtonBox.ApplyRole,
    'Reset': QtWidgets.QDialogButtonBox.ResetRole,
    }
Q0_MNEMONIC_DLGBOX_BUTTON_ROLES = invert(Q0_CODE_DLGBOX_BUTTONS)

Q0_CODE_FD_FILE_MODE = {
    'any': QtWidgets.QFileDialog.AnyFile,
    'exists':  QtWidgets.QFileDialog.ExistingFile,
    'dir': QtWidgets.QFileDialog.Directory,
    'multi': QtWidgets.QFileDialog.ExistingFiles,
    }
Q0_MNEMONIC_FD_FILE_MODE = invert(Q0_CODE_FD_FILE_MODE)

Q0_CODE_FD_VIEW_MODE = {
    'list': QtWidgets.QFileDialog.List,
    'detail': QtWidgets.QFileDialog.Detail,
    }
Q0_MNEMONIC_FD_VIEW_MODE = invert(Q0_CODE_FD_VIEW_MODE)

Q0_CODE_FD_OPTIONS = {
    'show dirs only': QtWidgets.QFileDialog.ShowDirsOnly,
    'no symlinks': QtWidgets.QFileDialog.DontResolveSymlinks,
    'no question overwrite': QtWidgets.QFileDialog.DontConfirmOverwrite,
    'no native dialog': QtWidgets.QFileDialog.DontUseNativeDialog,
    'readonly': QtWidgets.QFileDialog.ReadOnly,
    'hide filter details': QtWidgets.QFileDialog.HideNameFilterDetails,
    'no custom icons': QtWidgets.QFileDialog.DontUseCustomDirectoryIcons,
    }
Q0_MNEMONIC_FD_OPTIONS = invert(Q0_CODE_FD_OPTIONS)

Q0_CODE_LIST_DIR_FILTER = {
    'matched dirs': QtCore.QDir.Dirs,
    'all dirs': QtCore.QDir.AllDirs,
    'files': QtCore.QDir.Files,
    'drives': QtCore.QDir.Drives,
    'no symlinks': QtCore.QDir.NoSymLinks,
    'no special dotted': QtCore.QDir.NoDot,
    'no special double dotted': QtCore.QDir.NoDotDot,
    'readable': QtCore.QDir.Readable,
    'writeable': QtCore.QDir.Writable,
    'executable': QtCore.QDir.Executable,
    'modified': QtCore.QDir.Modified,
    'hidden': QtCore.QDir.Hidden,
    'system': QtCore.QDir.System,
    'case sensitive': QtCore.QDir.CaseSensitive,
    }
Q0_MNEMONIC_LIST_DIR_FILTER = invert(Q0_CODE_LIST_DIR_FILTER)

Q0_CODE_ITEM_DATA_ROLE = {
    'display': QtCore.Qt.DisplayRole,
    'decoration': QtCore.Qt.DecorationRole,
    'edit': QtCore.Qt.EditRole,
    'tool tip': QtCore.Qt.ToolTipRole,
    'status tip': QtCore.Qt.StatusTipRole,
    'what': QtCore.Qt.WhatsThisRole,
    'size hint': QtCore.Qt.SizeHintRole,
    'font': QtCore.Qt.FontRole,
    'text alignment': QtCore.Qt.TextAlignmentRole,
    'background': QtCore.Qt.BackgroundRole,
    'foreground': QtCore.Qt.ForegroundRole,
    'check state': QtCore.Qt.CheckStateRole,
    'initial sort order': QtCore.Qt.InitialSortOrderRole,
    'accessible text': QtCore.Qt.AccessibleTextRole,
    'accessible desc': QtCore.Qt.AccessibleDescriptionRole,
    'user': QtCore.Qt.UserRole,
    }
Q0_MNEMONIC_ITEM_DATA_ROLE = invert(Q0_CODE_ITEM_DATA_ROLE)

Q0_CODE_ORIENTATION = {
    'horizontal': QtCore.Qt.Horizontal,
    'vertical': QtCore.Qt.Vertical,
    }
Q0_MNEMONIC_ORIENTATION = invert(Q0_CODE_ORIENTATION)
for (key_new, key_old) in [
    ('h', 'horizontal'),
    ('hor', 'horizontal'),
    ('hori', 'horizontal'),
    ('horiz', 'horizontal'),
    ('v', 'vertical'),
    ('ver', 'vertical'),
    ('vert', 'vertical'),
    ('verti', 'vertical'),
    ]:
    Q0_CODE_ORIENTATION[key_new] = Q0_CODE_ORIENTATION[key_old]

Q0_CODE_RESIZE_MODE = {
    'interactive': Qt.QHeaderView.Interactive,
    'fixed': Qt.QHeaderView.Fixed,
    'stretch': Qt.QHeaderView.Stretch,
    'resize to contents': Qt.QHeaderView.ResizeToContents,
    }
Q0_MNEMONIC_RESIZE_MODE = invert(Q0_CODE_RESIZE_MODE)

Q0_CODE_MATCH_FLAGS = {
    'exact_qvariant':QtCore.Qt.MatchExactly,
    'exact_string':QtCore.Qt.MatchFixedString,
    'contains':QtCore.Qt.MatchContains,
    'starts_with':QtCore.Qt.MatchStartsWith,
    'ends_with':QtCore.Qt.MatchEndsWith,
    'case_sensitive':QtCore.Qt.MatchCaseSensitive,
    'regex':QtCore.Qt.MatchRegExp,  # Qt5.11
    'wildcard':QtCore.Qt.MatchWildcard,
    'wrap':QtCore.Qt.MatchWrap,
    'recursive':QtCore.Qt.MatchRecursive,
    }
Q0_MNEMONIC_MATCH_FLAGS = invert(Q0_CODE_MATCH_FLAGS)

Q0_CODE_SELECTION_BEHAVIOR = {
    'item':QtWidgets.QAbstractItemView.SelectItems,
    'rows':QtWidgets.QAbstractItemView.SelectRows,
    'cols':QtWidgets.QAbstractItemView.SelectColumns,
    }
Q0_MNEMONIC_SELECTION_BEHAVIOR = invert(Q0_CODE_SELECTION_BEHAVIOR)

Q0_CODE_SELECTION_MODE = {
    'single':QtWidgets.QAbstractItemView.SingleSelection,
    'contiguous':QtWidgets.QAbstractItemView.ContiguousSelection,
    'extended':QtWidgets.QAbstractItemView.ExtendedSelection,
    'multiple':QtWidgets.QAbstractItemView.MultiSelection,
    'no selection':QtWidgets.QAbstractItemView.NoSelection,
    }
Q0_MNEMONIC_SELECTION_MODE = invert(Q0_CODE_SELECTION_MODE)

Q0_CODE_MOUSE_BUTTON = {
    'nobutton':QtCore.Qt.NoButton,
    'allbuttons':QtCore.Qt.AllButtons,
    'left':QtCore.Qt.LeftButton,
    'right':QtCore.Qt.RightButton,
    'middle':QtCore.Qt.MiddleButton,
    'backward':QtCore.Qt.BackButton,
    'forward':QtCore.Qt.ForwardButton,
    'task':QtCore.Qt.TaskButton,
    }
Q0_MNEMONIC_MOUSE_BUTTON = invert(Q0_CODE_MOUSE_BUTTON)

Q0_CODE_CONTEXT_MENU_POLICY = {
    'no menu':QtCore.Qt.NoContextMenu,
    'prevent':QtCore.Qt.PreventContextMenu,
    'default':QtCore.Qt.DefaultContextMenu,
    'actions':QtCore.Qt.ActionsContextMenu,
    'custom':QtCore.Qt.CustomContextMenu,
    }
Q0_MNEMONIC_CONTEXT_MENU_POLICY = invert(Q0_CODE_CONTEXT_MENU_POLICY)

Q0_CODE_SORT_ORDER = {
    'ascending':QtCore.Qt.AscendingOrder,
    'descending':QtCore.Qt.DescendingOrder,
    }
Q0_MNEMONIC_SORT_ORDER = invert(Q0_CODE_SORT_ORDER)

Q0_CODE_CURSOR_SHAPE = {
    'arrow':QtCore.Qt.ArrowCursor,
    'arrow up':QtCore.Qt.UpArrowCursor,
    'cross':QtCore.Qt.CrossCursor,
    'wait modal':QtCore.Qt.WaitCursor,
    'I beam':QtCore.Qt.IBeamCursor,
    'size ver':QtCore.Qt.SizeVerCursor,
    'size hor':QtCore.Qt.SizeHorCursor,
    'size back diag':QtCore.Qt.SizeBDiagCursor,
    'size fore diag':QtCore.Qt.SizeFDiagCursor,
    'size cross':QtCore.Qt.SizeAllCursor,
    'blank':QtCore.Qt.BlankCursor,
    'split ver':QtCore.Qt.SplitVCursor,
    'split hor':QtCore.Qt.SplitHCursor,
    'hand point':QtCore.Qt.PointingHandCursor,
    'forbidden':QtCore.Qt.ForbiddenCursor,
    'hand open':QtCore.Qt.OpenHandCursor,
    'hand closed':QtCore.Qt.ClosedHandCursor,
    'what':QtCore.Qt.WhatsThisCursor,
    'busy nonmodal':QtCore.Qt.BusyCursor,
    'drag move':QtCore.Qt.DragMoveCursor,
    'drag copy':QtCore.Qt.DragCopyCursor,
    'drag link':QtCore.Qt.DragLinkCursor,
    'custom':QtCore.Qt.BitmapCursor,
    }
Q0_MNEMONIC_CURSOR_SHAPE = invert(Q0_CODE_CURSOR_SHAPE)

Q0_CODE_KEY = {
    'esc':QtCore.Qt.Key_Escape,	 
    'tab':QtCore.Qt.Key_Tab,	 
    'tab reverse':QtCore.Qt.Key_Backtab,	 
    'bs':QtCore.Qt.Key_Backspace,	 
    'ret':QtCore.Qt.Key_Return,	 
    'enter':QtCore.Qt.Key_Enter,
    'ins':QtCore.Qt.Key_Insert,	 
    'del':QtCore.Qt.Key_Delete,	 
    'pause':QtCore.Qt.Key_Pause,
    'print':QtCore.Qt.Key_Print,	 
    'sysreq':QtCore.Qt.Key_SysReq,	 
    'clr':QtCore.Qt.Key_Clear,
    'home':QtCore.Qt.Key_Home,	 
    'end':QtCore.Qt.Key_End,	 
    '←':QtCore.Qt.Key_Left,	 
    '↑':QtCore.Qt.Key_Up,	 
    '→':QtCore.Qt.Key_Right,	 
    '↓':QtCore.Qt.Key_Down,	 
    'pgup':QtCore.Qt.Key_PageUp,	 
    'pgdn':QtCore.Qt.Key_PageDown,	 
    'shift':QtCore.Qt.Key_Shift,	 
    'ctrl':QtCore.Qt.Key_Control,
    'meta':QtCore.Qt.Key_Meta,
    'alt':QtCore.Qt.Key_Alt,	 
    'alt gr':QtCore.Qt.Key_AltGr,
    'caps lock':QtCore.Qt.Key_CapsLock,	 
    'num lock':QtCore.Qt.Key_NumLock,	 
    'scroll lock':QtCore.Qt.Key_ScrollLock,	 
    'f1':QtCore.Qt.Key_F1,	 
    'f2':QtCore.Qt.Key_F2,	 
    'f3':QtCore.Qt.Key_F3,	 
    'f4':QtCore.Qt.Key_F4,	 
    'f5':QtCore.Qt.Key_F5,	 
    'f6':QtCore.Qt.Key_F6,	 
    'f7':QtCore.Qt.Key_F7,	 
    'f8':QtCore.Qt.Key_F8,	 
    'f9':QtCore.Qt.Key_F9,	 
    'f10':QtCore.Qt.Key_F10,	 
    'f11':QtCore.Qt.Key_F11,	 
    'f12':QtCore.Qt.Key_F12,	 
    'f13':QtCore.Qt.Key_F13,	 
    'f14':QtCore.Qt.Key_F14,	 
    'f15':QtCore.Qt.Key_F15,	 
    'f16':QtCore.Qt.Key_F16,	 
    'f17':QtCore.Qt.Key_F17,	 
    'f18':QtCore.Qt.Key_F18,	 
    'f19':QtCore.Qt.Key_F19,	 
    'f20':QtCore.Qt.Key_F20,	 
    'f21':QtCore.Qt.Key_F21,	 
    'f22':QtCore.Qt.Key_F22,	 
    'f23':QtCore.Qt.Key_F23,	 
    'f24':QtCore.Qt.Key_F24,	 
    'f25':QtCore.Qt.Key_F25,	 
    'f26':QtCore.Qt.Key_F26,	 
    'f27':QtCore.Qt.Key_F27,	 
    'f28':QtCore.Qt.Key_F28,	 
    'f29':QtCore.Qt.Key_F29,	 
    'f30':QtCore.Qt.Key_F30,	 
    'f31':QtCore.Qt.Key_F31,	 
    'f32':QtCore.Qt.Key_F32,	 
    'f33':QtCore.Qt.Key_F33,	 
    'f34':QtCore.Qt.Key_F34,	 
    'f35':QtCore.Qt.Key_F35,	 
    'Super_L':QtCore.Qt.Key_Super_L,	 
    'Super_R':QtCore.Qt.Key_Super_R,	 
    'Menu':QtCore.Qt.Key_Menu,	 
    'Hyper_L':QtCore.Qt.Key_Hyper_L,	 
    'Hyper_R':QtCore.Qt.Key_Hyper_R,	 
    'Help':QtCore.Qt.Key_Help,	 
    'Direction_L':QtCore.Qt.Key_Direction_L,	 
    'Direction_R':QtCore.Qt.Key_Direction_R,	 
    'space':QtCore.Qt.Key_Space,	 
    'any':QtCore.Qt.Key_Any,
    '!':QtCore.Qt.Key_Exclam,	 
    '"':QtCore.Qt.Key_QuoteDbl,	 
    '#':QtCore.Qt.Key_NumberSign,	 
    '$':QtCore.Qt.Key_Dollar,	 
    '%':QtCore.Qt.Key_Percent,	 
    '&':QtCore.Qt.Key_Ampersand,	 
    "'":QtCore.Qt.Key_Apostrophe,	 
    '(':QtCore.Qt.Key_ParenLeft,	 
    ')':QtCore.Qt.Key_ParenRight,	 
    '*':QtCore.Qt.Key_Asterisk,	 
    '+':QtCore.Qt.Key_Plus,	 
    ',':QtCore.Qt.Key_Comma,	 
    '-':QtCore.Qt.Key_Minus,	 
    '.':QtCore.Qt.Key_Period,	 
    '/':QtCore.Qt.Key_Slash,	 
    '0':QtCore.Qt.Key_0,	 
    '1':QtCore.Qt.Key_1,	 
    '2':QtCore.Qt.Key_2,	 
    '3':QtCore.Qt.Key_3,	 
    '4':QtCore.Qt.Key_4,	 
    '5':QtCore.Qt.Key_5,	 
    '6':QtCore.Qt.Key_6,	 
    '7':QtCore.Qt.Key_7,	 
    '8':QtCore.Qt.Key_8,	 
    '9':QtCore.Qt.Key_9,	 
    ':':QtCore.Qt.Key_Colon,	 
    ';':QtCore.Qt.Key_Semicolon,	 
    '<':QtCore.Qt.Key_Less,	 
    '=':QtCore.Qt.Key_Equal,	 
    '>':QtCore.Qt.Key_Greater,	 
    '?':QtCore.Qt.Key_Question,	 
    '@':QtCore.Qt.Key_At,	 
    'A':QtCore.Qt.Key_A,	 
    'B':QtCore.Qt.Key_B,	 
    'C':QtCore.Qt.Key_C,	 
    'D':QtCore.Qt.Key_D,	 
    'E':QtCore.Qt.Key_E,	 
    'F':QtCore.Qt.Key_F,	 
    'G':QtCore.Qt.Key_G,	 
    'H':QtCore.Qt.Key_H,	 
    'I':QtCore.Qt.Key_I,	 
    'J':QtCore.Qt.Key_J,	 
    'K':QtCore.Qt.Key_K,	 
    'L':QtCore.Qt.Key_L,	 
    'M':QtCore.Qt.Key_M,	 
    'N':QtCore.Qt.Key_N,	 
    'O':QtCore.Qt.Key_O,	 
    'P':QtCore.Qt.Key_P,	 
    'Q':QtCore.Qt.Key_Q,	 
    'R':QtCore.Qt.Key_R,	 
    'S':QtCore.Qt.Key_S,	 
    'T':QtCore.Qt.Key_T,	 
    'U':QtCore.Qt.Key_U,	 
    'V':QtCore.Qt.Key_V,	 
    'W':QtCore.Qt.Key_W,	 
    'X':QtCore.Qt.Key_X,	 
    'Y':QtCore.Qt.Key_Y,	 
    'Z':QtCore.Qt.Key_Z,	 
    '[':QtCore.Qt.Key_BracketLeft,	 
    'backslash':QtCore.Qt.Key_Backslash,	 
    ']':QtCore.Qt.Key_BracketRight,	 
    '^':QtCore.Qt.Key_AsciiCircum,	 
    '_':QtCore.Qt.Key_Underscore,	 
    '`':QtCore.Qt.Key_QuoteLeft,	 
    '{':QtCore.Qt.Key_BraceLeft,	 
    '|':QtCore.Qt.Key_Bar,	 
    '}':QtCore.Qt.Key_BraceRight,	 
    '~':QtCore.Qt.Key_AsciiTilde,	 
    'nbsp':QtCore.Qt.Key_nobreakspace,	 
    '¡':QtCore.Qt.Key_exclamdown,	 
    '¢':QtCore.Qt.Key_cent,	 
    '£':QtCore.Qt.Key_sterling,	 
    '€':QtCore.Qt.Key_currency,	 
    '¥':QtCore.Qt.Key_yen,	 
    'brokenbar':QtCore.Qt.Key_brokenbar,	 
    'section':QtCore.Qt.Key_section,	 
    'diaeresis':QtCore.Qt.Key_diaeresis,	 
    '©':QtCore.Qt.Key_copyright,	 
    'ordfeminine':QtCore.Qt.Key_ordfeminine,	 
    'guillemotleft':QtCore.Qt.Key_guillemotleft,	 
    '¬':QtCore.Qt.Key_notsign,	 
    'hyphen':QtCore.Qt.Key_hyphen,	 
    '®':QtCore.Qt.Key_registered,	 
    'macron':QtCore.Qt.Key_macron,	 
    '°':QtCore.Qt.Key_degree,	 
    '±':QtCore.Qt.Key_plusminus,	 
    '²':QtCore.Qt.Key_twosuperior,	 
    '³':QtCore.Qt.Key_threesuperior,	 
    'acute':QtCore.Qt.Key_acute,	 
    'µ':QtCore.Qt.Key_mu,	 
    '¶':QtCore.Qt.Key_paragraph,	 
    '·':QtCore.Qt.Key_periodcentered,	 
    'cedilla':QtCore.Qt.Key_cedilla,	 
    '¹':QtCore.Qt.Key_onesuperior,	 
    'masculine':QtCore.Qt.Key_masculine,	 
    'guillemotright':QtCore.Qt.Key_guillemotright,	 
    '¼':QtCore.Qt.Key_onequarter,	 
    '½':QtCore.Qt.Key_onehalf,	 
    '¾':QtCore.Qt.Key_threequarters,	 
    '¿':QtCore.Qt.Key_questiondown,	 
    'Agrave':QtCore.Qt.Key_Agrave,	 
    'Aacute':QtCore.Qt.Key_Aacute,	 
    'Acircumflex':QtCore.Qt.Key_Acircumflex,	 
    'Atilde':QtCore.Qt.Key_Atilde,	 
    'Adiaeresis':QtCore.Qt.Key_Adiaeresis,	 
    'Aring':QtCore.Qt.Key_Aring,	 
    'AE':QtCore.Qt.Key_AE,	 
    'Ccedilla':QtCore.Qt.Key_Ccedilla,	 
    'Egrave':QtCore.Qt.Key_Egrave,	 
    'Eacute':QtCore.Qt.Key_Eacute,	 
    'Ecircumflex':QtCore.Qt.Key_Ecircumflex,	 
    'Ediaeresis':QtCore.Qt.Key_Ediaeresis,	 
    'Igrave':QtCore.Qt.Key_Igrave,	 
    'Iacute':QtCore.Qt.Key_Iacute,	 
    'Icircumflex':QtCore.Qt.Key_Icircumflex,	 
    'Idiaeresis':QtCore.Qt.Key_Idiaeresis,	 
    'ETH':QtCore.Qt.Key_ETH,	 
    'Ntilde':QtCore.Qt.Key_Ntilde,	 
    'Ograve':QtCore.Qt.Key_Ograve,	 
    'Oacute':QtCore.Qt.Key_Oacute,	 
    'Ocircumflex':QtCore.Qt.Key_Ocircumflex,	 
    'Otilde':QtCore.Qt.Key_Otilde,	 
    'Odiaeresis':QtCore.Qt.Key_Odiaeresis,	 
    'multiply':QtCore.Qt.Key_multiply,	 
    'Ooblique':QtCore.Qt.Key_Ooblique,	 
    'Ugrave':QtCore.Qt.Key_Ugrave,	 
    'Uacute':QtCore.Qt.Key_Uacute,	 
    'Ucircumflex':QtCore.Qt.Key_Ucircumflex,	 
    'Udiaeresis':QtCore.Qt.Key_Udiaeresis,	 
    'Yacute':QtCore.Qt.Key_Yacute,	 
    'ð':QtCore.Qt.Key_THORN,	 
    'ssharp':QtCore.Qt.Key_ssharp,	 
    '÷':QtCore.Qt.Key_division,	 
    'ydiaeresis':QtCore.Qt.Key_ydiaeresis,	 
    'Multi_key':QtCore.Qt.Key_Multi_key,	 
    'Codeinput':QtCore.Qt.Key_Codeinput,	 
    'SingleCandidate':QtCore.Qt.Key_SingleCandidate,	 
    'MultipleCandidate':QtCore.Qt.Key_MultipleCandidate,	 
    'PreviousCandidate':QtCore.Qt.Key_PreviousCandidate,	 
    'Mode_switch':QtCore.Qt.Key_Mode_switch,	 
    'Kanji':QtCore.Qt.Key_Kanji,	 
    'Muhenkan':QtCore.Qt.Key_Muhenkan,	 
    'Henkan':QtCore.Qt.Key_Henkan,	 
    'Romaji':QtCore.Qt.Key_Romaji,	 
    'Hiragana':QtCore.Qt.Key_Hiragana,	 
    'Katakana':QtCore.Qt.Key_Katakana,	 
    'Hiragana_Katakana':QtCore.Qt.Key_Hiragana_Katakana,	 
    'Zenkaku':QtCore.Qt.Key_Zenkaku,	 
    'Hankaku':QtCore.Qt.Key_Hankaku,	 
    'Zenkaku_Hankaku':QtCore.Qt.Key_Zenkaku_Hankaku,	 
    'Touroku':QtCore.Qt.Key_Touroku,	 
    'Massyo':QtCore.Qt.Key_Massyo,	 
    'Kana_Lock':QtCore.Qt.Key_Kana_Lock,	 
    'Kana_Shift':QtCore.Qt.Key_Kana_Shift,	 
    'Eisu_Shift':QtCore.Qt.Key_Eisu_Shift,	 
    'Eisu_toggle':QtCore.Qt.Key_Eisu_toggle,	 
    'Hangul':QtCore.Qt.Key_Hangul,	 
    'Hangul_Start':QtCore.Qt.Key_Hangul_Start,	 
    'Hangul_End':QtCore.Qt.Key_Hangul_End,	 
    'Hangul_Hanja':QtCore.Qt.Key_Hangul_Hanja,	 
    'Hangul_Jamo':QtCore.Qt.Key_Hangul_Jamo,	 
    'Hangul_Romaja':QtCore.Qt.Key_Hangul_Romaja,	 
    'Hangul_Jeonja':QtCore.Qt.Key_Hangul_Jeonja,	 
    'Hangul_Banja':QtCore.Qt.Key_Hangul_Banja,	 
    'Hangul_PreHanja':QtCore.Qt.Key_Hangul_PreHanja,	 
    'Hangul_PostHanja':QtCore.Qt.Key_Hangul_PostHanja,	 
    'Hangul_Special':QtCore.Qt.Key_Hangul_Special,	 
    'Dead_Grave':QtCore.Qt.Key_Dead_Grave,	 
    'Dead_Acute':QtCore.Qt.Key_Dead_Acute,	 
    'Dead_Circumflex':QtCore.Qt.Key_Dead_Circumflex,	 
    'Dead_Tilde':QtCore.Qt.Key_Dead_Tilde,	 
    'Dead_Macron':QtCore.Qt.Key_Dead_Macron,	 
    'Dead_Breve':QtCore.Qt.Key_Dead_Breve,	 
    'Dead_Abovedot':QtCore.Qt.Key_Dead_Abovedot,	 
    'Dead_Diaeresis':QtCore.Qt.Key_Dead_Diaeresis,	 
    'Dead_Abovering':QtCore.Qt.Key_Dead_Abovering,	 
    'Dead_Doubleacute':QtCore.Qt.Key_Dead_Doubleacute,	 
    'Dead_Caron':QtCore.Qt.Key_Dead_Caron,	 
    'Dead_Cedilla':QtCore.Qt.Key_Dead_Cedilla,	 
    'Dead_Ogonek':QtCore.Qt.Key_Dead_Ogonek,	 
    'Dead_Iota':QtCore.Qt.Key_Dead_Iota,	 
    'Dead_Voiced_Sound':QtCore.Qt.Key_Dead_Voiced_Sound,	 
    'Dead_Semivoiced_Sound':QtCore.Qt.Key_Dead_Semivoiced_Sound,	 
    'Dead_Belowdot':QtCore.Qt.Key_Dead_Belowdot,	 
    'Dead_Hook':QtCore.Qt.Key_Dead_Hook,	 
    'Dead_Horn':QtCore.Qt.Key_Dead_Horn,	 
    'Dead_Stroke':QtCore.Qt.Key_Dead_Stroke,	 
    'Dead_Abovecomma':QtCore.Qt.Key_Dead_Abovecomma,	 
    'Dead_Abovereversedcomma':QtCore.Qt.Key_Dead_Abovereversedcomma,	 
    'Dead_Doublegrave':QtCore.Qt.Key_Dead_Doublegrave,	 
    'Dead_Belowring':QtCore.Qt.Key_Dead_Belowring,	 
    'Dead_Belowmacron':QtCore.Qt.Key_Dead_Belowmacron,	 
    'Dead_Belowcircumflex':QtCore.Qt.Key_Dead_Belowcircumflex,	 
    'Dead_Belowtilde':QtCore.Qt.Key_Dead_Belowtilde,	 
    'Dead_Belowbreve':QtCore.Qt.Key_Dead_Belowbreve,	 
    'Dead_Belowdiaeresis':QtCore.Qt.Key_Dead_Belowdiaeresis,	 
    'Dead_Invertedbreve':QtCore.Qt.Key_Dead_Invertedbreve,	 
    'Dead_Belowcomma':QtCore.Qt.Key_Dead_Belowcomma,	 
    'Dead_Currency':QtCore.Qt.Key_Dead_Currency,	 
    'Dead_a':QtCore.Qt.Key_Dead_a,	 
    'Dead_A':QtCore.Qt.Key_Dead_A,	 
    'Dead_e':QtCore.Qt.Key_Dead_e,	 
    'Dead_E':QtCore.Qt.Key_Dead_E,	 
    'Dead_i':QtCore.Qt.Key_Dead_i,	 
    'Dead_I':QtCore.Qt.Key_Dead_I,	 
    'Dead_o':QtCore.Qt.Key_Dead_o,	 
    'Dead_O':QtCore.Qt.Key_Dead_O,	 
    'Dead_u':QtCore.Qt.Key_Dead_u,	 
    'Dead_U':QtCore.Qt.Key_Dead_U,	 
    'Dead_Small_Schwa':QtCore.Qt.Key_Dead_Small_Schwa,	 
    'Dead_Capital_Schwa':QtCore.Qt.Key_Dead_Capital_Schwa,	 
    'Dead_Greek':QtCore.Qt.Key_Dead_Greek,	 
    'Dead_Lowline':QtCore.Qt.Key_Dead_Lowline,	 
    'Dead_Aboveverticalline':QtCore.Qt.Key_Dead_Aboveverticalline,	 
    'Dead_Belowverticalline':QtCore.Qt.Key_Dead_Belowverticalline,	 
    'Dead_Longsolidusoverlay':QtCore.Qt.Key_Dead_Longsolidusoverlay,	 
    'Back':QtCore.Qt.Key_Back,	 
    'Forward':QtCore.Qt.Key_Forward,	 
    'Stop':QtCore.Qt.Key_Stop,	 
    'Refresh':QtCore.Qt.Key_Refresh,	 
    'VolumeDown':QtCore.Qt.Key_VolumeDown,	 
    'VolumeMute':QtCore.Qt.Key_VolumeMute,	 
    'VolumeUp':QtCore.Qt.Key_VolumeUp,	 
    'BassBoost':QtCore.Qt.Key_BassBoost,	 
    'BassUp':QtCore.Qt.Key_BassUp,	 
    'BassDown':QtCore.Qt.Key_BassDown,	 
    'TrebleUp':QtCore.Qt.Key_TrebleUp,	 
    'TrebleDown':QtCore.Qt.Key_TrebleDown,	 
    'MediaPlay':QtCore.Qt.Key_MediaPlay,
    'MediaStop':QtCore.Qt.Key_MediaStop,
    'MediaPrevious':QtCore.Qt.Key_MediaPrevious,	 
    'MediaNext':QtCore.Qt.Key_MediaNext,	 
    'MediaRecord':QtCore.Qt.Key_MediaRecord,	 
    'MediaPause':QtCore.Qt.Key_MediaPause,
    'MediaTogglePlayPause':QtCore.Qt.Key_MediaTogglePlayPause,
    'HomePage':QtCore.Qt.Key_HomePage,	 
    'Favorites':QtCore.Qt.Key_Favorites,	 
    'Search':QtCore.Qt.Key_Search,	 
    'Standby':QtCore.Qt.Key_Standby,	 
    'OpenUrl':QtCore.Qt.Key_OpenUrl,	 
    'LaunchMail':QtCore.Qt.Key_LaunchMail,	 
    'LaunchMedia':QtCore.Qt.Key_LaunchMedia,	 
    'Launch0':QtCore.Qt.Key_Launch0,	 
    'Launch1':QtCore.Qt.Key_Launch1,	 
    'Launch2':QtCore.Qt.Key_Launch2,	 
    'Launch3':QtCore.Qt.Key_Launch3,	 
    'Launch4':QtCore.Qt.Key_Launch4,	 
    'Launch5':QtCore.Qt.Key_Launch5,	 
    'Launch6':QtCore.Qt.Key_Launch6,	 
    'Launch7':QtCore.Qt.Key_Launch7,	 
    'Launch8':QtCore.Qt.Key_Launch8,	 
    'Launch9':QtCore.Qt.Key_Launch9,	 
    'LaunchA':QtCore.Qt.Key_LaunchA,	 
    'LaunchB':QtCore.Qt.Key_LaunchB,	 
    'LaunchC':QtCore.Qt.Key_LaunchC,	 
    'LaunchD':QtCore.Qt.Key_LaunchD,	 
    'LaunchE':QtCore.Qt.Key_LaunchE,	 
    'LaunchF':QtCore.Qt.Key_LaunchF,	 
    'LaunchG':QtCore.Qt.Key_LaunchG,	 
    'LaunchH':QtCore.Qt.Key_LaunchH,	 
    'MonBrightnessUp':QtCore.Qt.Key_MonBrightnessUp,	 
    'MonBrightnessDown':QtCore.Qt.Key_MonBrightnessDown,	 
    'KeyboardLightOnOff':QtCore.Qt.Key_KeyboardLightOnOff,	 
    'KeyboardBrightnessUp':QtCore.Qt.Key_KeyboardBrightnessUp,	 
    'KeyboardBrightnessDown':QtCore.Qt.Key_KeyboardBrightnessDown,	 
    'PowerOff':QtCore.Qt.Key_PowerOff,	 
    'WakeUp':QtCore.Qt.Key_WakeUp,	 
    'Eject':QtCore.Qt.Key_Eject,	 
    'ScreenSaver':QtCore.Qt.Key_ScreenSaver,	 
    'WWW':QtCore.Qt.Key_WWW,	 
    'Memo':QtCore.Qt.Key_Memo,	 
    'LightBulb':QtCore.Qt.Key_LightBulb,	 
    'Shop':QtCore.Qt.Key_Shop,	 
    'History':QtCore.Qt.Key_History,	 
    'AddFavorite':QtCore.Qt.Key_AddFavorite,	 
    'HotLinks':QtCore.Qt.Key_HotLinks,	 
    'BrightnessAdjust':QtCore.Qt.Key_BrightnessAdjust,	 
    'Finance':QtCore.Qt.Key_Finance,	 
    'Community':QtCore.Qt.Key_Community,	 
    'AudioRewind':QtCore.Qt.Key_AudioRewind,	 
    'BackForward':QtCore.Qt.Key_BackForward,	 
    'ApplicationLeft':QtCore.Qt.Key_ApplicationLeft,	 
    'ApplicationRight':QtCore.Qt.Key_ApplicationRight,	 
    'Book':QtCore.Qt.Key_Book,	 
    'CD':QtCore.Qt.Key_CD,	 
    'Calculator':QtCore.Qt.Key_Calculator,	 
    'ToDoList':QtCore.Qt.Key_ToDoList,	 
    'ClearGrab':QtCore.Qt.Key_ClearGrab,	 
    'Close':QtCore.Qt.Key_Close,	 
    'Copy':QtCore.Qt.Key_Copy,	 
    'Cut':QtCore.Qt.Key_Cut,	 
    'Display':QtCore.Qt.Key_Display,	 
    'DOS':QtCore.Qt.Key_DOS,	 
    'Documents':QtCore.Qt.Key_Documents,	 
    'Excel':QtCore.Qt.Key_Excel,	 
    'Explorer':QtCore.Qt.Key_Explorer,	 
    'Game':QtCore.Qt.Key_Game,	 
    'Go':QtCore.Qt.Key_Go,	 
    'iTouch':QtCore.Qt.Key_iTouch,	 
    'LogOff':QtCore.Qt.Key_LogOff,	 
    'Market':QtCore.Qt.Key_Market,	 
    'Meeting':QtCore.Qt.Key_Meeting,	 
    'MenuKB':QtCore.Qt.Key_MenuKB,	 
    'MenuPB':QtCore.Qt.Key_MenuPB,	 
    'MySites':QtCore.Qt.Key_MySites,	 
    'News':QtCore.Qt.Key_News,	 
    'OfficeHome':QtCore.Qt.Key_OfficeHome,	 
    'Option':QtCore.Qt.Key_Option,	 
    'Paste':QtCore.Qt.Key_Paste,	 
    'Phone':QtCore.Qt.Key_Phone,	 
    'Calendar':QtCore.Qt.Key_Calendar,	 
    'Reply':QtCore.Qt.Key_Reply,	 
    'Reload':QtCore.Qt.Key_Reload,	 
    'RotateWindows':QtCore.Qt.Key_RotateWindows,	 
    'RotationPB':QtCore.Qt.Key_RotationPB,	 
    'RotationKB':QtCore.Qt.Key_RotationKB,	 
    'Save':QtCore.Qt.Key_Save,	 
    'Send':QtCore.Qt.Key_Send,	 
    'Spell':QtCore.Qt.Key_Spell,	 
    'SplitScreen':QtCore.Qt.Key_SplitScreen,	 
    'Support':QtCore.Qt.Key_Support,	 
    'TaskPane':QtCore.Qt.Key_TaskPane,	 
    'Terminal':QtCore.Qt.Key_Terminal,	 
    'Tools':QtCore.Qt.Key_Tools,	 
    'Travel':QtCore.Qt.Key_Travel,	 
    'Video':QtCore.Qt.Key_Video,	 
    'Word':QtCore.Qt.Key_Word,	 
    'Xfer':QtCore.Qt.Key_Xfer,	 
    'ZoomIn':QtCore.Qt.Key_ZoomIn,	 
    'ZoomOut':QtCore.Qt.Key_ZoomOut,	 
    'Away':QtCore.Qt.Key_Away,	 
    'Messenger':QtCore.Qt.Key_Messenger,	 
    'WebCam':QtCore.Qt.Key_WebCam,	 
    'MailForward':QtCore.Qt.Key_MailForward,	 
    'Pictures':QtCore.Qt.Key_Pictures,	 
    'Music':QtCore.Qt.Key_Music,	 
    'Battery':QtCore.Qt.Key_Battery,	 
    'Bluetooth':QtCore.Qt.Key_Bluetooth,	 
    'WLAN':QtCore.Qt.Key_WLAN,	 
    'UWB':QtCore.Qt.Key_UWB,	 
    'AudioForward':QtCore.Qt.Key_AudioForward,	 
    'AudioRepeat':QtCore.Qt.Key_AudioRepeat,	 
    'AudioRandomPlay':QtCore.Qt.Key_AudioRandomPlay,	 
    'Subtitle':QtCore.Qt.Key_Subtitle,	 
    'AudioCycleTrack':QtCore.Qt.Key_AudioCycleTrack,	 
    'Time':QtCore.Qt.Key_Time,	 
    'Hibernate':QtCore.Qt.Key_Hibernate,	 
    'View':QtCore.Qt.Key_View,	 
    'TopMenu':QtCore.Qt.Key_TopMenu,	 
    'PowerDown':QtCore.Qt.Key_PowerDown,	 
    'Suspend':QtCore.Qt.Key_Suspend,	 
    'ContrastAdjust':QtCore.Qt.Key_ContrastAdjust,	 
    'TouchpadToggle':QtCore.Qt.Key_TouchpadToggle,	 
    'TouchpadOn':QtCore.Qt.Key_TouchpadOn,	 
    'TouchpadOff':QtCore.Qt.Key_TouchpadOff,	 
    'MicMute':QtCore.Qt.Key_MicMute,	 
    'Red':QtCore.Qt.Key_Red,	 
    'Green':QtCore.Qt.Key_Green,	 
    'Yellow':QtCore.Qt.Key_Yellow,	 
    'Blue':QtCore.Qt.Key_Blue,	 
    'ChannelUp':QtCore.Qt.Key_ChannelUp,	 
    'ChannelDown':QtCore.Qt.Key_ChannelDown,	 
    'Guide':QtCore.Qt.Key_Guide,	 
    'Info':QtCore.Qt.Key_Info,	 
    'Settings':QtCore.Qt.Key_Settings,	 
    'MicVolumeUp':QtCore.Qt.Key_MicVolumeUp,	 
    'MicVolumeDown':QtCore.Qt.Key_MicVolumeDown,	 
    'New':QtCore.Qt.Key_New,	 
    'Open':QtCore.Qt.Key_Open,	 
    'Find':QtCore.Qt.Key_Find,	 
    'Undo':QtCore.Qt.Key_Undo,	 
    'Redo':QtCore.Qt.Key_Redo,	 
    'MediaLast':QtCore.Qt.Key_MediaLast,	 
    'unknown':QtCore.Qt.Key_unknown,	 
    'Call':QtCore.Qt.Key_Call,
    'Camera':QtCore.Qt.Key_Camera,
    'CameraFocus':QtCore.Qt.Key_CameraFocus,
    'Context1':QtCore.Qt.Key_Context1,	 
    'Context2':QtCore.Qt.Key_Context2,	 
    'Context3':QtCore.Qt.Key_Context3,	 
    'Context4':QtCore.Qt.Key_Context4,	 
    'Flip':QtCore.Qt.Key_Flip,	 
    'Hangup':QtCore.Qt.Key_Hangup,
    'No':QtCore.Qt.Key_No,	 
    'Select':QtCore.Qt.Key_Select,	 
    'Yes':QtCore.Qt.Key_Yes,	 
    'ToggleCallHangup':QtCore.Qt.Key_ToggleCallHangup,
    'VoiceDial':QtCore.Qt.Key_VoiceDial,	 
    'LastNumberRedial':QtCore.Qt.Key_LastNumberRedial,	 
    'Execute':QtCore.Qt.Key_Execute,	 
    'Printer':QtCore.Qt.Key_Printer,	 
    'Play':QtCore.Qt.Key_Play,	 
    'Sleep':QtCore.Qt.Key_Sleep,	 
    'Zoom':QtCore.Qt.Key_Zoom,	 
    'Exit':QtCore.Qt.Key_Exit,	 
    'Cancel':QtCore.Qt.Key_Cancel,
    }
Q0_MNEMONIC_KEY = invert(Q0_CODE_KEY)

for (key_old, key_new) in [
        ('meta', 'windows'),
        ('meta', 'microsoft'),
        ('clr', 'dead'),
        ('←', 'left'),
        ('→', 'right'),
        ('↑', 'up'),
        ('↓', 'dn'),
        ('↓', 'down'),
        ('€', 'currency'),
    ]:
    Q0_CODE_KEY[key_new] = Q0_CODE_KEY[key_old]
    
Q0_CODE_KEY_MODIFIER = {
    'nomod':QtCore.Qt.NoModifier,
    'shift':QtCore.Qt.ShiftModifier,
    'crtl':QtCore.Qt.ControlModifier,
    'alt':QtCore.Qt.AltModifier,
    'meta':QtCore.Qt.MetaModifier,
    'keypad':QtCore.Qt.KeypadModifier,
    'mode switch':QtCore.Qt.GroupSwitchModifier,
    }
Q0_MNEMONIC_KEY_MODIFIER = invert(Q0_CODE_KEY_MODIFIER)

Q0_CODE_LOCALE_FORMAT = {
    'long':  QtCore.QLocale.LongFormat,
    'short':  QtCore.QLocale.ShortFormat,
    'narrow':  QtCore.QLocale.NarrowFormat,
    }
Q0_MNEMONIC_LOCALE_FORMAT = invert(Q0_CODE_LOCALE_FORMAT)

for (key_old, key_new) in [
        ('meta', 'windows'),
        ('meta', 'microsoft'),
    ]:
    Q0_CODE_KEY_MODIFIER[key_new] = Q0_CODE_KEY_MODIFIER[key_old]


class Q0Application(QtWidgets.QApplication):

    """Application object.

    'For any GUI application using Qt, there is precisely one
    QApplication object.'

    Use:

    app = q0.Q0Application()
    «setup code goes here»
    retcd = app.exec_()
    sys.exit(retcd)


    As with any GUI application, nothing happens during execution of
    the setup code, which instantiates widgets on the screen.  Once
    the setup code is complete, then execution begins and continues
    until the main window is destroyed, but the real work is done by
    exception routines attached the various widgets as event handlers.

    """

    def __init__(self):
        super().__init__(sys.argv)
        return

    def set_window_icon(self, q0_icon):
        result = self.setWindowIcon(q0_icon)
        return result

    def close_all_windows(self):
        self.closeAllWindows()
        return self

    def beep(self):
        super().beep()
        return self

    def connect_clipboard_changed(self, event_changed):
        self.clipboard().dataChanged.connect(event_changed)
        return

    def get_clipboard_text(self):
        result = self.clipboard().text()
        return result

    def exec_(self):
        result = super().exec_()
        return result

    def process_events(self):
        result = super().processEvents()
        return result


class Q0Timer(QtCore.QTimer):

    """Timer object.

    """
    
    def __init__(self, wait_msecs=ZERO, is_single_shot=True, event=None):
        super().__init__()
        if event is None:
            event = self.set_semaphore
        self.timeout.connect(event)
        self.wait_msecs = wait_msecs
        self.setSingleShot(is_single_shot)
        self.semaphore = None
        return

    def start(self):
        super().start(self.wait_msecs)
        self.set_semaphore(is_up=True)
        return self

    def single_shot(self, event=None):
        if event is None:
            event = self.set_semaphore
        self.singleShot(self.wait_msecs, event)
        self.set_semaphore(is_up=True)
        return self

    def stop(self):
        super().stop()
        return self

    def is_active(self):
        result = super().isActive()
        return result

    def set_semaphore(self, is_up=False):
        if is_up:
            pass
        else:
            self.stop()
        self.semaphore = is_up
        return self

    def is_semaphore_up(self):
        return self.semaphore


class Q0Sound(QtMultimedia.QSound):

    """Play an audible *.wav file.

    Don't let the instance go out of scope before the playback is finished.

    """

    def __init__(self, wav_file_name, repetitions=1):
        super().__init__(wav_file_name)
        self.setLoops(repetitions)
        return

    def play(self):
        super().play()
        return self

    def is_finished(self):
        result = self.isFinished()
        return result

    
class Q0MainWindow(QtWidgets.QMainWindow):

    """Main Window object.

    Use:

    app = q0.Q0Application()
    with q0.Q0MainWindow() as main_win:
        «setup code goes here»
    retcd = app.exec_()
    sys.exit(retcd)

    Note that app.exec_() must be called before main_win goes out of
    scope.  This means it should be called in a function where
    main_win is local or global; otherwise, the app will hang without
    displaying anything, producing a difficult to trace bug.  Such is
    the nature of "C" libraries, I guess.

    As with any GUI application, nothing happens during execution of
    the setup code, which instantiates widgets on the screen.  Once
    the setup code is complete, then execution begins and continues
    until the main window is destroyed, but the real work is done by
    exception routines attached to the various widgets as event
    handlers.

    """

    def __init__(self, height=480, width=640, q0_visual='Main Window'):
        super().__init__()
        self.set_min_size(height, width)
        self.set_title(q0_visual)
        return

    def __enter__(self):
        self.q0_open()
        return self

    def q0_open(self):
        return self

    def __exit__(self, *parms):
        self.q0_close()
        return False

    def q0_close(self):
        self.show()
        return self

    def set_min_size(self, height=480, width=640):
        self.setMinimumSize(QtCore.QSize(width, height))
        return self

    def set_title(self, q0_visual):
        self.setWindowTitle(q0_visual)
        return self

    def set_central_widget(self, q0_widget):
        self.setCentralWidget(q0_widget)
        return q0_widget

    def set_menu_bar(self, q0_menu_bar):
        self.setMenuBar(q0_menu_bar)
        result = q0_menu_bar
        return result

    def closeEvent(self, q0_event):
        self.closing(q0_event)
        result = super().closeEvent(q0_event)
        return result

    def closing(self, q0_event):
        return self

    
class Q0DialogModal(QtWidgets.QDialog):

    """Modal Dialog object.

    Use:

    dlg = q0.Q0DialogModal(q0_visual='Choose Account')
    cent_wgt = dlg.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
    dlg.accts = cent_wgt.add_wgt(q0.Q0ComboBox(items))
    dlg.accts.set_pos(ZERO)
    cent_wgt.push('hbox', is_just_right=True)
    button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox())
    button_box.accepted.connect(dlg.accept)
    button_box.rejected.connect(dlg.reject)
    cent_wgt.pop()  # hbox

    """

    def __init__(self, q0_visual='Dialog'):
        super().__init__()
        self.set_title(q0_visual)
        return

    def set_title(self, q0_visual):
        self.setWindowTitle(q0_visual)
        return self

    def set_central_widget(self, q0_widget):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(q0_widget)
        self.setLayout(layout)
        return q0_widget

    def audit(self):

        """Result must be None to stay in the audit loop.

        """
        
        result = "OK"
        return result

    def run_audit_loop(self):
        result = None
        while True:
            if self.exec_():
                result = self.audit()
                if result is None:
                    pass
                else:
                    break
            else:
                break    
        return result

    def set_modal(self, is_modal=True):
        result = self.setModal(is_modal)
        return result


class Q0DialogButtonBox(QtWidgets.QDialogButtonBox):

    """Button box widget group.

    """
    
    def __init__(self, q0_buttons=None, q0_orientation='horizontal'):
        if q0_buttons is None:
            q0_buttons = ['cancel', 'ok']
        buttons = Q0_CODE_DLGBOX_BUTTONS['nobutton']
        for mnemonic in q0_buttons:
            buttons |= Q0_CODE_DLGBOX_BUTTONS[mnemonic]
        super().__init__(buttons)
        self.set_orientation(q0_orientation)
        return

    def add_button(self, q0_button, q0_role='Action'):
        result = q0_button
        self.addButton(result, Q0_CODE_DLGBOX_BUTTON_ROLES[q0_role])
        return result

    def add_qt_standard_button(self, q0_button):
        result = q0_button
        self.addButton(result)
        return result

#    q0_standard_buttons = {
#        'apply': (_('Apply'), 'Apply'),
#        'cancel': (_('Cancel'), 'Reject'),
#        'close': (_('Close'), 'Reject'),
#        'discard': (_('Discard'), 'Destructive'),
#        'help': (_('Help'), 'Help'),
#        'ignore': (_('Ignore'), 'Accept'),
#        'no': (_('No'), 'No'),
#        'notoall': (_('No to All'), 'No'),
#        'ok': (_('OK'), 'Accept'),
#        'open': (_('Open'), 'Accept'),
#        'reset': (_('Reset'), 'Reset'),
#        'restoredefaults': (_('Restore Defaults'), 'Reset'),
#        'retry': (_('Retry'), 'Accept'),
#        'save': (_('Save'), 'Accept'),
#        'saveall': (_('Save All'), 'Accept'),
#        'yes': (_('Yes'), 'Yes'),
#        'yestoall': (_('Yes to All'), 'Yes'),
#        }

#    def add_q0_standard_button(self, q0_button_mnemonic, is_dlgs_default=False, can_handle_ret_ent=True):
#        (q0_visual, q0_role) = self.q0_standard_buttons[q0_button_mnemonic]
#        result = Q0PushButton(q0_visual=q0_visual, is_dlgs_default=is_dlgs_default, can_handle_ret_ent=can_handle_ret_ent)
#        self.add_button(result, q0_role)
#        return result

#    def add_cancel_button(self, is_dlgs_default=False, can_handle_ret_ent=True):
#        result = self.add_q0_standard_button('cancel', is_dlgs_default, can_handle_ret_ent)
#        return result

#    def add_ok_button(self, is_dlgs_default=True, can_handle_ret_ent=True):
#        result = self.add_q0_standard_button('ok', is_dlgs_default, can_handle_ret_ent)
#        return result

    def set_orientation(self, q0_orientation):
        result = self.setOrientation(Q0_CODE_ORIENTATION[q0_orientation])
        return result


class Q0TabWidget(QtWidgets.QTabWidget):

    """This is a tab widget.

    Tab widgets are typically stacked and accessed by clicking on
    their 'tabs.' Doh!

    """
    
    def get_tab_tags_left_to_right(self):
        result = []
        ndx_visual = self.count() - 1
        while ndx_visual >= ZERO:
            tab_visual = self.tabText(ndx_visual)
            result.append(tab_visual)
            ndx_visual -= 1
        result.reverse()
        return result

    def select(self, ndx):
        self.setCurrentIndex(ndx)
        return self

    def get_current_tab_visual(self):
        ndx = self.currentIndex()
        result = self.tabText(ndx)
        return result

    def set_tab_visual(self, ndx, q0_visual):
        self.setTabText(ndx, q0_visual)
        return self

    def add_tab(self, q0_visual, q0_icon=None, q0_tool_tip=NULL, ndx=NA):
        result = Q0Widget()
        ndx = self.insertTab(ndx, result, q0_visual)
        if q0_icon is None:
            pass
        else:
            self.setTabIcon(ndx, q0_icon)
        self.setTabToolTip(ndx, q0_tool_tip)
        self.setCurrentIndex(ndx)
        return result

    def del_tab(self, tab_wgt):
        self.removeTab(self.indexOf(tab_wgt))
        return self


class Q0Widget(QtWidgets.QWidget):

    """Generic Widget with layout.

    Use:

    with q0.Q0MainWindow() as main_win:
        cent_wgt = main_win.set_central_widget(q0.Q0Widget())
        cent_wgt.push(q0_layout='form')
        (lab1, ed1) = cent_wgt.add_row(q0.Q0Label('Label 1'), q0.Q0LineEdit())
        (lab2, ed2) = cent_wgt.add_row(q0.Q0Label('Label 2'), q0.Q0LineEdit())
        cent_wgt.pop()

    """

    def __init__(self, q0_layout='hbox', q0_font=None):
        super().__init__()
        if q0_font is None:
            pass
        else:
            self.setFont(q0_font)
        self.layout_stack = []
        self.push(q0_layout)
        return

    def add_wgt(self, q0_widget, ndx=NA, align=None):
        if align is None:
            self.layout_stack[ZERO].insertWidget(ndx, q0_widget)
        else:
            self.layout_stack[ZERO].insertWidget(ndx, q0_widget, alignment=Q0_CODE_ALIGNMENT[align])
        return q0_widget

    def add_wgt_to_grid(self, q0_widget, row=ZERO, col=ZERO, row_span=1, col_span=1):
        self.layout_stack[ZERO].addWidget(q0_widget, row, col, row_span, col_span)
        return q0_widget

    def add_row(self, q0_label, q0_edit, ndx=NA):

        """Add a row to a form layout.

        It's not terribly obvious that each row has to have the same
        height.

        """
        
        self.layout_stack[ZERO].insertRow(ndx, q0_label, q0_edit)
        return (q0_label, q0_edit)

    def add_tab(self, q0_visual, q0_icon=None, q0_tool_tip=NULL, ndx=NA):

        """For use with TabWidget.

        """
        
        tabs = self.layout_stack[ZERO]
        result = tabs.add_tab(q0_visual, q0_icon, q0_tool_tip, ndx)
        return result

    def add_layer(self, ndx=NA):

        """For use with StackedWidget.

        """
        
        result = Q0Widget()
        tabs = self.layout_stack[ZERO]
        ndx = tabs.insertWidget(ndx, result)
        return result

    def push(self, q0_layout='vbox', q0_visual=NULL, q0_icon=None, is_just_right=False, q0_tool_tip=NULL):

        if self.layout_stack:
            top = self.layout_stack[ZERO]
        else:
            top = self
        if isinstance(top, QtWidgets.QLayout):
            add_layout = top.addLayout
        else:
            add_layout = top.setLayout
        q0_layout_lower = q0_layout.lower()
        if q0_layout_lower in ['grid', 'g']:
            layout = QtWidgets.QGridLayout()
            add_layout(layout)
        elif q0_layout_lower in ['vbox', 'v']:
            layout = QtWidgets.QVBoxLayout()
            add_layout(layout)
            if is_just_right:
                layout.addStretch(1)
        elif q0_layout_lower in ['hbox', 'h']:
            layout = QtWidgets.QHBoxLayout()
            add_layout(layout)
            if is_just_right:
                layout.addStretch(1)
        elif q0_layout_lower in ['form', 'f']:
            layout = QtWidgets.QFormLayout()
            add_layout(layout)
            if is_just_right:
                layout.setLabelAlignment(Q0_CODE_ALIGNMENT['east'])
        elif q0_layout_lower in ['tabs']:
            layout = Q0TabWidget()
            layout.setMovable(True)
#            layout.setTabsClosable(True)
            top.addWidget(layout)
        elif q0_layout_lower in ['stacked']:
            layout = QtWidgets.QStackedWidget()
            top.addWidget(layout)
        elif q0_layout_lower in ['group_box', 'group box', 'groupbox', 'gbox', 'gb']:
            layout = QtWidgets.QGroupBox()
            layout.setTitle(q0_visual)
            top.addWidget(layout)
        else:
            raise NotImplementedError
        self.layout_stack.insert(ZERO, layout)
        return self

    def pop(self, is_just_left=False):
        result = self.layout_stack.pop(ZERO)
        if is_just_left:
            result.addStretch(1)
        return result


class Q0ScrollArea(QtWidgets.QScrollArea):

    """This is a frame that exhibits scrollbars.

    Scrollbars appear when its content exceeds its size.

    *set_wgt* gives the scroll area a child widget.

    """
    
    def set_wgt(self, wgt):
        result = wgt
        self.setWidget(result)
        self.setWidgetResizable(True)
        return result


class Q0Label(QtWidgets.QLabel):

    """Display a text or an image.

    q0_visual may be a str, a Q0String containing rich text (HTML
    or markdown), or a Q0Pixmap.

    """

    def __init__(self, q0_visual=None, q0_font=None):
        super().__init__()
        if q0_font is None:
            pass
        else:
            self.setFont(q0_font)
        if q0_visual:
            self.set_visual(q0_visual)
        return

    def set_visual(self, q0_visual):
        self.setText(q0_visual)
        return self

    def get_visual(self):
        result = self.text()
        return result

    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self

    def set_tool_tip(self, q0_visual):
        self.setToolTip(q0_visual)
        return self

    
class Q0LineEdit(QtWidgets.QLineEdit):

    """A one-line fill-in-the-blank widget.

    """
    
    def __init__(self, q0_default=NULL, q0_echo='normal', has_clear_button=False, q0_font=None):
        super().__init__()
        if q0_font is None:
            pass
        else:
            self.setFont(q0_font)
        self.set_visual(q0_default)
        self.set_echo_mode(q0_echo)
        self.set_clear_button_enabled(has_clear_button)
        return

    def set_enabled(self, is_enabled=True):
        self.setEnabled(is_enabled)
        return self

    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self

    def set_echo_mode(self, q0_echo='normal'):
        q0_echo_lower = q0_echo.lower()
        if q0_echo_lower in ['normal', 'norm']:
            self.setEchoMode(QtWidgets.QLineEdit.Normal)
        elif q0_echo_lower in ['no echo', 'noecho']:
            self.setEchoMode(QtWidgets.QLineEdit.NoEcho)
        elif q0_echo_lower in ['password', 'passwd', 'pass']:
            self.setEchoMode(QtWidgets.QLineEdit.Password)
        elif q0_echo_lower in ['password echo', 'passwd echo', 'pass echo', 'passecho']:
            self.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        else:
            raise NotImplementedError
        return self

    def set_clear_button_enabled(self, has_clear_button=True):
        self.setClearButtonEnabled(has_clear_button)
        return self

    def set_visual(self, q0_visual):
        self.setText(q0_visual)
        return self

    def get_visual(self):
        result = self.text()
        return result

    def set_tool_tip(self, q0_visual):
        self.setToolTip(q0_visual)
        return self

    
class Q0DateEdit(QtWidgets.QDateEdit):

    """A widget for editing dates.

    """
    
    def set_enabled(self, is_enabled=True):
        self.setEnabled(is_enabled)
        return self

    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self

    def set_display_format(self, fmt):
        self.setDisplayFormat(fmt)
        return self

    def enable_calendar_popup(self, enable=True):
        self.setCalendarPopup(enable)
        return self

    def set_visual(self, q0_visual):
        self.setDate(q0_visual)
        return self

    def get_visual(self):
        result = self.date()
        return result

    def set_tool_tip(self, q0_visual):
        self.setToolTip(q0_visual)
        return self

    
class Q0TimeEdit(QtWidgets.QTimeEdit):

    """A widget for entering times.

    """
    
    def set_enabled(self, is_enabled=True):
        self.setEnabled(is_enabled)
        return self

    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self

    def set_display_format(self, fmt):
        self.setDisplayFormat(fmt)
        return self

    def set_visual(self, q0_visual):
        self.setTime(q0_visual)
        return self

    def get_visual(self):
        result = self.time()
        return result

    def set_tool_tip(self, q0_visual):
        self.setToolTip(q0_visual)
        return self

    
class Q0DateTimeEdit(QtWidgets.QDateTimeEdit):

    """A widget for entering date/times.

    """
    
    def set_enabled(self, is_enabled=True):
        self.setEnabled(is_enabled)
        return self

    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self

    def set_display_format(self, fmt):
        self.setDisplayFormat(fmt)
        return self

    def enable_calendar_popup(self, enable=True):
        self.setCalendarPopup(enable)
        return self

    def set_visual(self, q0_visual):
        self.setDateTime(q0_visual)
        return self

    def get_visual(self):
        result = self.dateTime()
        return result

    def set_tool_tip(self, q0_visual):
        self.setToolTip(q0_visual)
        return self

    
class Q0PushButton(QtWidgets.QPushButton):

    """A pushbutton widget.

    """
    
    def __init__(
            self,
            q0_visual=NULL,
            q0_icon=None,
            is_enabled=True,
            event_clicked=None,
            fixed_height=None,
            fixed_width=None,
            is_dlgs_default=False,
            can_handle_ret_ent=False,
            ):
        super().__init__()
        self.set_visual(q0_visual)
        self.set_icon(q0_icon)
        self.set_enabled(is_enabled)
        self.connect_clicked(event_clicked)
        if fixed_height:
            self.setFixedHeight(fixed_height)
        if fixed_width:
            self.setFixedWidth(fixed_width)
        self.set_dlgs_default(is_dlgs_default)
        self.set_handle_ret_ent(can_handle_ret_ent)
        self.drop_mime_type = None
        self.drop_handler = None
        return

    def set_visual(self, q0_visual):
        self.setText(q0_visual)
        return self

    def get_visual(self):
        result = self.text()
        return result

    def set_icon(self, q0_icon):
        if q0_icon is None:
            pass
        else:
            self.setIcon(q0_icon)
        return self

    def set_enabled(self, is_enabled=True):
        self.setEnabled(is_enabled)
        return self

    def connect_clicked(self, event_clicked):
        if event_clicked is None:
            pass
        else:
            self.clicked.connect(event_clicked)
        return self

    def connect_drop(self, collection_mime_types, event_drop):
        self.setAcceptDrops(True)
        self.drop_mime_types = set(collection_mime_types)
        self.drop_handler = event_drop
        return self

    def dragEnterEvent(self, event):
        avail_types = set(event.mimeData().formats())
#        print(f'''
#  avail:  {avail_types}, 
#allowed:  {self.drop_mime_types}, 
# common:  {self.drop_mime_types.intersection(avail_types)}
#''')
        if self.drop_mime_types.intersection(avail_types):
            event.accept()
        else:
            super().dragEnterEvent(event)
            event.ignore()
        return 

    def dropEvent(self, event):
        if self.drop_handler:
            result = self.drop_handler(event)
            if result:
                pass
            else:
                super().dropEvent(event)
        else:
            result = None
        return result

    def set_dlgs_default(self, is_dlgs_default=True):
        self.setDefault(is_dlgs_default)
        return self

    def set_handle_ret_ent(self, can_handle_ret_ent=True):
        self.setAutoDefault(can_handle_ret_ent)
        return self

    def set_tool_tip(self, q0_visual):
        self.setToolTip(q0_visual)
        return self

    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self

    def set_focus(self):
        result = self.setFocus()
        return result


class Q0RadioButton(QtWidgets.QRadioButton):

    """A radio pushbutton widget.

    """
    
    def __init__(self, q0_visual, is_selected=False, is_enabled=True, event_toggled=None):
        super().__init__()
        self.set_visual(q0_visual)
        self.set_checked(is_selected)
        self.set_enabled(is_enabled)
        if event_toggled is None:
            pass
        else:
            self.connect_toggled(event_toggled)
        return
    
    def set_enabled(self, is_enabled=True):
        self.setEnabled(is_enabled)
        return self

    def set_visual(self, q0_visual):
        self.setText(q0_visual)
        return self

    def set_checked(self, is_selected=True):
        self.setChecked(is_selected)
        return self

    def is_checked(self):
        result = self.isChecked()
        return result

    def connect_toggled(self, event_toggled):
        self.toggled.connect(event_toggled)
        return self

    def set_tool_tip(self, q0_visual):
        self.setToolTip(q0_visual)
        return self

    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self


class Q0CheckBox(QtWidgets.QCheckBox):

    """A Checkbox widget.

    """
    
    def __init__(self, q0_visual, is_checked=False, is_enabled=True, is_tri_state=False, event_state_changed=None):
        super().__init__()
        self.set_visual(q0_visual)
        self.set_checked(is_checked)
        self.set_enabled(is_enabled)
        self.set_tri_state(is_tri_state)
        if event_state_changed is None:
            pass
        else:
            self.connect_state_changed(event_state_changed)
        return
    
    def set_enabled(self, is_enabled=True):
        self.setEnabled(is_enabled)
        return self

    def set_tri_state(self, is_tri_state=True):
        self.setTristate(is_tri_state)
        return self

    def set_visual(self, q0_visual):
        self.setText(q0_visual)
        return self

    def set_checked(self, is_checked=True):
        self.setChecked(is_checked)
        return self

    def is_checked(self):
        result = self.isChecked()
        return result

    def set_check_state(self, q0_state):
        q0_state_lower = q0_state.lower()
        if q0_state_lower in ['unchecked']:
            self.setCheckState(QtCore.Qt.Unchecked)
        elif q0_state_lower in ['checked']:
            self.setCheckState(QtCore.Qt.Checked)
        elif q0_state_lower in ['partial', 'neutral', 'both', 'neither', "don't care"]:
            self.setCheckState(QtCore.Qt.PartiallyChecked)
        else:
            raise NotImplementedError
        return self

    def get_state(self):
        result = self.getState()
        return result

    def connect_state_changed(self, event_state_changed):
        self.stateChanged.connect(event_state_changed)
        return self

    def set_tool_tip(self, q0_visual):
        self.setToolTip(q0_visual)
        return self

    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self


class Q0List(QtWidgets.QListWidget):

    """A list widget.

    """

    
    def __init__(
        self,
        height=400,
        width=400,         
        items=None,
        pos=None,
        q0_selection_mode='single',
        ):
        super().__init__()
        self.set_min_size(height, width)
        if items is None:
            pass
        else:
            self.add_items(items)
        if pos is None:
            pass
        else:
            self.set_pos(pos)
        self.set_selection_mode(q0_selection_mode)
        return

    def set_min_size(self, height=480, width=640):
        self.setMinimumSize(QtCore.QSize(width, height))
        return self

    def add_items(self, collection):
        inversion = list(collection)
        inversion.reverse()
        for item in inversion:
            self.add_item(item)
        return self

    def __len__(self):
        return self.count()

    def set_pos(self, pos):
        self.setCurrentRow(pos)
        return self

    def get_pos(self):
        result = self.currentRow()
        return result

    def get_item(self, pos):
        item = self.item(pos)
        if item:
            result = item.text()
        else:
            result = None            
        return result

    def set_item(self, q0_visual, pos):
        self.take_item(pos)
        result = self.add_item(q0_visual, pos)
        return result

    def add_item(self, q0_visual, pos=NA):
        result = self.insertItem(pos, q0_visual)
        return result

    def take_item(self, pos):
        result = self.takeItem(pos)
        return result

    def move_item(self, pos_from, pos_to):
        pos_to = pos_to
        item = self.take_item(pos_from)
        result = self.add_item(item, pos_to)
        return result

    def get_items(self):
        ndx = len(self)
        result = []
        while ndx:
            ndx -= 1
            result.append(self.get_item(ndx))
        result.reverse()
        return result

    def get_selected(self):
        result = self.selectedItems()
        return result

    def set_selection_mode(self, q0_mode):
        self.setSelectionMode(Q0_CODE_SELECTION_MODE[q0_mode])
        return self

#    def selectionChanged(self, q0_selection_new, q0_selection_old):
#        if hasattr(self, 'event_selection_changed'):
#            result = self.event_selection_changed(q0_selection_new, q0_selection_old)
#        if result:
#            pass
#        else:
#            result = super().selectionChanged(q0_selection_new, q0_selection_old)
#        return result

#    def connect_selection_changed(self, event_selection_changed):
#        self.event_selection_changed = event_selection_changed
#        return self

    def connect_row_changed(self, event_row_changed):
        self.currentRowChanged.connect(event_row_changed)
        return self

    def set_item_tool_tip(self, q0_visual, pos=NA):
        item = self.item(pos)
        item.setToolTip(q0_visual)
        return self
            

class Q0ComboBox(QtWidgets.QComboBox):

    """A combobox widget.

    """

    
    def __init__(
        self,
        q0_visual=NULL,
        items=None,
        pos=None,
        is_editable=True,
        min_char_width=ZERO,
        max_visible=10,
        ):
        super().__init__()
        if items is None:
            pass
        else:
            self.add_items(items)
        self.set_visual(q0_visual)
        if pos is None:
            pass
        else:
            self.set_pos(pos)
        self.set_editable(is_editable)
        self.set_min_char_width(min_char_width)
        self.set_max_visible(max_visible)
        return

    def add_items(self, collection):
        inversion = list(collection)
        inversion.reverse()
        for item in inversion:
            if str(item) in ['--', '—']:
                self.add_sep()
            else:
                self.add_item(item)
        return self

    def add_item(self, q0_visual, pos=NA):
        result = self.insertItem(pos, q0_visual)
        return result

    def add_sep(self, pos=NA):
        self.insertSeparator(pos)
        return self

    def set_pos(self, pos):
        self.setCurrentIndex(pos)
        return self

    def get_pos(self):
        result = self.currentIndex()
        return result

    def set_visual(self, q0_visual):
        self.setCurrentText(q0_visual)
        return self

    def get_visual(self):
        result = self.currentText()
        return result

    def set_placeholder(self, q0_visual):

        '''Placeholder text, if any, shows when there is no current position.

        '''
        
        self.setPlaceholderText(q0_visual)
        return self

    def index(self, target, q0_match_flags=None):
        if q0_match_flags:
            pass
        else:
            q0_match_flags = []
        flags = Q0_CODE_MATCH_FLAGS['exact_qvariant']
        for flag in q0_match_flags:
            flags |= Q0_CODE_MATCH_FLAGS[flag.lower()]
        result = self.findText(target, flags)
        return result

    def set_editable(self, is_editable):
        self.setEditable(is_editable)
        return self

    def set_min_char_width(self, min_char_width):
        self.setMinimumContentsLength(min_char_width)
        return self

    def set_max_visible(self, max_visible):
        self.setMaxVisibleItems(max_visible)
        return self

    def clear(self):
        QtWidgets.QComboBox.clear(self)
        return self
    
    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self

    def connect_focus_out(self, focus_event):
        self.focus_event = focus_event
        return self

    def focusOutEvent(self, event_parms):
        if hasattr(self, 'focus_event'):
            result = self.focus_event(event_parms)
        else:
            result = super().focusOutEvent(event_parms)
        return result
    
    def set_tool_tip(self, q0_visual):
        self.setToolTip(q0_visual)
        return self

    def set_item_tool_tip(self, q0_visual, pos=NA):
        self.setItemData(pos, q0_visual, role=Q0_CODE_ITEM_DATA_ROLE['tool tip'])
        return self
    
    
class Q0PlainTextEdit(QtWidgets.QPlainTextEdit):

    """A multi-line text box widget.

    """

    
    def __init__(
            self,
            q0_default=NULL,
            q0_wrap_mode='width',
            is_readonly=False,
            is_tab_handled=False,
            q0_font=None,
            q0_cursor=None,
            ):
        super().__init__()
        if q0_font is None:
            pass
        else:
            self.setFont(q0_font)
        if q0_cursor is None:
            pass
        else:
            self.setCursor(Q0_CODE_CURSOR_SHAPE[q0_cursor.lower()])
        self.set_visual(q0_default)
        self.set_line_wrap(q0_wrap_mode)
        self.set_readonly(is_readonly)
        self.set_tab_handled(is_tab_handled)
        return

    def set_visual(self, q0_visual):
        self.setPlainText(q0_visual)
        self.ensureCursorVisible()
        return self

    def get_visual(self):
        result = self.toPlainText()
        return result

    def set_line_wrap(self, q0_wrap_mode='width'):
        q0_wrap_mode_lower = q0_wrap_mode.lower()
        if q0_wrap_mode_lower in ['width']:
            self.setLineWrapMode(Qt.QPlainTextEdit.WidgetWidth)
        elif q0_wrap_mode_lower in ['nowrap']:
            self.setLineWrapMode(Qt.QPlainTextEdit.NoWrap)
        else:
            raise NotImplementedError
        return self

    def set_readonly(self, is_readonly=True):
        self.setReadOnly(is_readonly)
        return self

    def set_tab_handled(self, is_tab_handled=True):
        self.setTabChangesFocus(is_tab_handled)
        return self
    
    def set_placeholder(self, q0_visual):
        self.setPlaceholderText(q0_visual)
        return self

    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self

    def set_tool_tip(self, q0_visual):
        self.setToolTip(q0_visual)
        return self

    def set_min_size(self, height=480, width=640):
        self.setMinimumSize(QtCore.QSize(width, height))
        return self

    
class Q0TextEdit(QtWidgets.QTextEdit):

    """A multi-line text box widget with super powers.

    """

    
    def __init__(
            self,
            q0_default=NULL,
            is_readonly=False,
            is_tab_handled=False,
            q0_font=None,
            q0_cursor_shape=None,
            ):
        super().__init__()
        if q0_font is None:
            pass
        else:
            self.setFont(q0_font)
        self.cursor_shape_current = None
        if q0_cursor_shape is None:
            self.setMouseTracking(False)
            self.set_cursor_shape('I beam')
        else:
            self.setMouseTracking(True)
            self.set_cursor_shape(q0_cursor_shape)
        self.cursor_shape_default = self.cursor_shape_current
        self.set_visual(q0_default)
        self.set_readonly(is_readonly)
        self.set_tab_handled(is_tab_handled)
        return

    def set_visual(self, q0_visual):
        self.setPlainText(q0_visual)
        self.ensureCursorVisible()
        return self

    def get_visual(self):
        result = self.toPlainText()
        return result

    def set_html(self, q0_visual):
        self.setHtml(q0_visual)
        self.ensureCursorVisible()
        return self

    def get_html(self):
        result = self.toHtml()
        return result

    def set_markdown(self, q0_visual):
        self.setMarkdown(q0_visual)
        self.ensureCursorVisible()
        return self

    def get_markdown(self):
        result = self.toMarkdown()
        return result

    def set_readonly(self, is_readonly=True):
        self.setReadOnly(is_readonly)
        return self

    def set_tab_handled(self, is_tab_handled=True):
        self.setTabChangesFocus(is_tab_handled)
        return self
    
    def set_placeholder(self, q0_visual):
        self.setPlaceholderText(q0_visual)
        return self

    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self

    def set_tool_tip(self, q0_visual):
        self.setToolTip(q0_visual)
        return self

    def set_min_size(self, height=480, width=640):
        self.setMinimumSize(QtCore.QSize(width, height))
        return self

    def set_cursor_shape(self, q0_cursor_shape):
        if q0_cursor_shape == self.cursor_shape_current:
            pass
        else:
            self.viewport().setCursor(Q0_CODE_CURSOR_SHAPE[q0_cursor_shape])
            self.cursor_shape_current = q0_cursor_shape
        return self

    def mouseMoveEvent(self, e):
        result = super().mouseMoveEvent(e)
        anchor = self.anchorAt(e.pos())
        if anchor:
            self.set_cursor_shape('hand point')
        else:
            self.set_cursor_shape(self.cursor_shape_default)
        return result

    def mouseReleaseEvent(self, e):
        result = super().mouseReleaseEvent(e)
        anchor = self.anchorAt(e.pos())
        if anchor:
            self.event_anchor_clicked(anchor)
        return result

    def mousePressEvent(self, e):
        result = super().mousePressEvent(e)
        self.event_mouse_press(e)
        return result

    def event_anchor_clicked(self, link):
        raise NotImplementedError
        return self

    def event_mouse_press(self, e):
        return


class Q0GraphicsView(QtWidgets.QGraphicsView):

    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    """Graphics view widget with controls.

    This is from:

    ekhumoro. "How to Enable Pan and Zoom in a QGraphicsView."  Online
    posting. 19 Feb. 2016. Stack Overflow. 11 June 2021
    <https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview>.

    """

    def __init__(self, parent):
        super().__init__(parent)
        self._zoom = ZERO
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        return

    def has_photo(self):
        result = not self._empty
        return result

    def fit_in_view(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if rect.isNull():
            pass
        else:
            self.setSceneRect(rect)
            if self.has_photo():
                unity = self.transform().mapRect(QtCore.QRectF(ZERO, ZERO, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = ZERO
        return self

    def set_photo(self, q0_pixmap=None):
        self._zoom = ZERO
        if q0_pixmap and not q0_pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(q0_pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fit_in_view()
        return self

    def wheelEvent(self, q0_event):
        if self.has_photo():
            if q0_event.angleDelta().y() > ZERO:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > ZERO:
                self.scale(factor, factor)
            elif self._zoom == ZERO:
                self.fit_in_view()
            else:
                self._zoom = ZERO
        return

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        return self

    def mousePressEvent(self, q0_event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(q0_event.pos()).toPoint())
        result = super().mousePressEvent(q0_event)
        return result


class Q0Pixmap(QtGui.QPixmap):

    """A pixmap.  This IS NOT a widget.

    """
    
    def __init__(self, file_name):
        super().__init__(file_name)
        return


class Q0Font(QtGui.QFont):

    """A font.  This IS NOT a widget.

    """
    
    pass


class Q0FontFixedPitch(Q0Font):

    """A fixed-pitch font.  This IS NOT a widget.

    """
    
    def __init__(self, family='Arial', pointSize=NA, weight=NA, italic=False):
        super().__init__(family, pointSize, weight, italic)
        self.setFixedPitch(True)
        return

    
class Q0Icon(QtGui.QIcon):

    """An icon.  This IS NOT a widget.

    """

    pass


class Q0FileDialog(QtWidgets.QFileDialog):

    """A file open read/write dialog.

    """

    
    def __init__(
            self,
            q0_title=None,
            q0_accept_mode='open',
            q0_file_mode='any',
            q0_view_mode='detail',
            q0_list_dir_mode='hidden',
            q0_options=['no native dialog'],
            name_filters=None,
            default_suffix=None,
            directory=None,
        ):
        super().__init__(caption=q0_title)
        self.set_accept_mode(q0_accept_mode)
        self.set_file_mode(q0_file_mode)
        self.set_view_mode(q0_view_mode)
        self.set_list_dir_mode(q0_list_dir_mode)
        self.set_options(q0_options)
        if name_filters is None:
            name_filters = ['All Files (*.*)']
        self.set_name_filters(name_filters)
        if default_suffix is None:
            pass
        else:
            self.set_default_suffix(default_suffix)
        if directory is None:
            pass
        else:
            self.set_directory(directory)
        return

    def set_accept_mode(self, q0_accept_mode):
        q0_accept_mode_lower = q0_accept_mode.lower()
        if q0_accept_mode_lower in ['open']:
            self.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        elif q0_accept_mode_lower in ['save']:
            self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        else:
            raise NotImplementedError
        return self

    def set_file_mode(self, q0_file_mode):
        self.setFileMode(Q0_CODE_FD_FILE_MODE[q0_file_mode.lower()])
        return self

    def set_view_mode(self, q0_view_mode):
        self.setViewMode(Q0_CODE_FD_VIEW_MODE[q0_view_mode.lower()])
        return self

    def set_list_dir_mode(self, q0_list_dir_mode):
        self.setFilter(Q0_CODE_LIST_DIR_FILTER[q0_list_dir_mode.lower()])
        return self

    def set_name_filters(self, filters):

        """This requires a list.

        """
        
        self.setNameFilters(filters)
        self.selectNameFilter(filters[ZERO])
        return self

    def set_default_suffix(self, default):
        self.setDefaultSuffix(default)
        return self

    def set_directory(self, directory):
        self.setDirectory(directory)
        return self

    def set_options(self, collection):
        options = ZERO
        for q0_option in collection:
            options |= Q0_CODE_FD_OPTIONS[q0_option.lower()]
        self.setOptions(options)
        return self

    def get_selected_files(self):
        if self.exec_():
            result = self.selectedFiles()
        else:
            result = []
        return result

    def set_selected_files(self, collection):
        for fn in collection:
            self.selectFile(fn)
        return self

    def exec_(self):
        result = super().exec_()
        return result


class Q0MessageBox(QtWidgets.QMessageBox):

    """A pop-up messagebox dialog.

    """
    
    def __init__(
            self,
            q0_icon='noicon',
            q0_title=NULL,
            q0_visual=NULL,
            q0_informative_text=NULL,
            q0_detailed_text=NULL,
            ):
        super().__init__()
        self.set_icon(q0_icon)
        self.set_title(q0_title)
        self.set_text(q0_visual)
        self.set_informative_text(q0_informative_text)
        self.set_detailed_text(q0_detailed_text)
        return

    def set_icon(self, q0_icon='noicon'):
        if isinstance(q0_icon, Q0Pixmap):
            self.setIconPixmap(q0_icon)
        elif q0_icon is None:
            pass
        else:
            q0_icon_lower = q0_icon.lower()
            if q0_icon_lower in ['noicon']:
                self.setIcon(QtWidgets.QMessageBox.NoIcon)
            elif q0_icon_lower in ['question']:
                self.setIcon(QtWidgets.QMessageBox.Question)
            elif q0_icon_lower in ['information']:
                self.setIcon(QtWidgets.QMessageBox.Information)
            elif q0_icon_lower in ['warning']:
                self.setIcon(QtWidgets.QMessageBox.Warning)
            elif q0_icon_lower in ['critical']:
                self.setIcon(QtWidgets.QMessageBox.Critical)
            else:
                raise NotImplementedError
        return self

    def set_title(self, q0_title=NULL):
        self.setWindowTitle(q0_title)
        return self

    def set_text(self, q0_visual=NULL):
        self.setText(q0_visual)
        return self

    def set_informative_text(self, q0_informative_text=NULL):
        self.setInformativeText(q0_informative_text)
        return self
 
    def set_detailed_text(self, q0_detailed_text=NULL):        
        self.setDetailedText(q0_detailed_text)
        return self

    def set_standard_buttons(self, collection):
        buttons = Q0_CODE_MSGBOX_BUTTONS['nobutton']
        for q0_button in collection:
            buttons |= Q0_CODE_MSGBOX_BUTTONS[q0_button.lower()]
        self.setStandardButtons(buttons)
        return self

    def set_default_button(self, q0_button):
        self.setDefaultButton(Q0_CODE_MSGBOX_BUTTONS[q0_button.lower()])
        return self

    def set_escape_button(self, q0_button):
        self.setEscapeButton(Q0_CODE_MSGBOX_BUTTONS[q0_button.lower()])
        return self

    def exec_(self):
        result = Q0_MNEMONIC_MSGBOX_BUTTONS.get(super().exec_())
        return result


class Q0Alert(Q0DialogModal):

    """A non-blocking (non-modal, asynchronous) alert box.

    Q0MessageBox is blocking.  Q0Alert is not supposed to be.

    Use:

    alert = Q0Alert(q0_title=_('Opening Browser'), q0_visual=_('Please wait.'))
    alert.open()
    while long_running_event_is_running():
        app.process_events()
        if alert.is_finished:
            break
    else:
        alert.close()

    """

    sleep_msecs = 100

    def __init__(
            self,
            q0_app,
            q0_title=NULL,
            q0_visual=NULL,
            ):
        self.is_finished = False
        self.app = q0_app
        super().__init__(
            q0_visual=q0_title,
            )
        cent_wgt = self.set_central_widget(Q0Widget(q0_layout='vbox'))
        cent_wgt.add_wgt(Q0Label(q0_visual=q0_visual))
        cent_wgt.push('hbox', is_just_right=True)
        button_box = cent_wgt.add_wgt(Q0DialogButtonBox(q0_buttons=['cancel']))
        button_box.rejected.connect(self.reject)
        cent_wgt.pop()  # hbox
        return

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *parms):
        if self.is_finished:
            pass
        else:
            self.close()
        return False

    def open(self):

        """Open the alert box.

        This is a non-blocking call except that it has to block for a
        brief period to allow the message box to be painted.

        """
        result = super().open()
        sleeper = Q0Timer(self.sleep_msecs).single_shot()
        while sleeper.is_semaphore_up():
            self.app.process_events()
        return result

    def reject(self):
        self.is_finished = True
        result = super().reject()
        return result
    

class Q0Menu(QtWidgets.QMenu):

    """A pop-up menu widget.

    Use:

    MAIN_WIN.pop_up_menu.exec(event.globalPos())

    """

    def __init__(self):
        super().__init__()
        self.menu_stack = []
        self.q0_actions = {}
        return

    def get_parent(self):
        if self.menu_stack:
            result = self.menu_stack[ZERO]
        else:
            result = self
        return result

    def add_action(self, q0_action):
        parent = self.get_parent()
        parent.addAction(q0_action)
        result = q0_action
        result.setParent(parent)
        self.q0_actions[result.text()] = result
        return result

    def add_sep(self):
        parent = self.get_parent()
        parent.addSeparator()
        return self

    def push(self, q0_visual, q0_icon=None, has_tool_tips=False):
        parent = self.get_parent()
        menu = parent.addMenu(q0_visual)
        menu.setParent(parent)
        if q0_icon is None:
            pass
        else:
            menu.setIcon(q0_icon)
        menu.setToolTipsVisible(has_tool_tips)
        self.menu_stack.insert(ZERO, menu)
        return self

    def pop(self):
        result = self.menu_stack.pop(ZERO)
        return result


class Q0MenuBar(QtWidgets.QMenuBar):

    """A menu bar widget.

    Use:

    with q0.Q0MainWindow() as main_win:
        menu_bar = main_win.set_menu_bar(q0.Q0MenuBar())
        menu_bar.push(q0_menu='&File')
        menu_bar.add_action(q0.Q0Action('&New', 'Ctrl+N', 'New document.', main_win.event_new))
        menu_bar.add_action(q0.Q0Action('&Open', 'Ctrl+O', 'Open document.', main_win.event_open))
        menu_bar.add_sep()
        menu_bar.add_action(q0.Q0Action('&Exit', 'Ctrl+Q', 'Exit application.', main_win.event_exit))
        menu_bar.pop()

    """

    def __init__(self):
        super().__init__()
        self.menu_stack = []
        self.q0_actions = {}
        return

    def get_parent(self):
        if self.menu_stack:
            result = self.menu_stack[ZERO]
        else:
            result = self
        return result

    def add_action(self, q0_action):
        parent = self.get_parent()
        parent.addAction(q0_action)
        result = q0_action
        result.setParent(parent)
        self.q0_actions[result.text()] = result
        return result

    def add_sep(self):
        parent = self.get_parent()
        parent.addSeparator()
        return self

    def push(self, q0_visual, q0_icon=None, has_tool_tips=False):
        parent = self.get_parent()
        menu = parent.addMenu(q0_visual)
        menu.setParent(parent)
        if q0_icon is None:
            pass
        else:
            menu.setIcon(q0_icon)
        menu.setToolTipsVisible(has_tool_tips)
        self.menu_stack.insert(ZERO, menu)
        return self

    def pop(self):
        result = self.menu_stack.pop(ZERO)
        return result


class Q0Action(QtWidgets.QAction):

    """A menu action widget.

    """

    def __init__(self, q0_visual=NULL, q0_shortcut=NULL, q0_tool_tip=NULL, event=None, q0_icon=None):
        super().__init__(q0_visual)
        self.set_shortcut(q0_shortcut)
        self.set_tool_tip(q0_tool_tip)
        self.triggered.connect(event)
        if q0_icon is None:
            pass
        else:
            self.set_icon(q0_icon)
        return

    def set_enabled(self, is_enabled=True):
        self.setEnabled(is_enabled)
        return self

    def set_icon(self, q0_icon):
        self.setIcon(q0_icon)
        return self

    def set_shortcut(self, q0_shortcut):
        self.setShortcut(q0_shortcut)
        return self

    def set_tool_tip(self, q0_tool_tip):
        self.setToolTip(q0_tool_tip)
        return self

    def connect_triggered(self, event):
        self.triggered.connect(event)
        return self


class _AbstractStructure(object):

    """This points to underlying data structure for an abstract data
    model.

    """

    def __init__(self, obj):
        self.obj = obj
        return

    def __len__(self):
        result = len(self.obj)
        return result


class Q0KeyedStructure(_AbstractStructure):

    """This points to a keyed data structure for an abstract data model
    such as a dict.

    """
    
    def get_val(self, ndx, tag):
        result = self.obj[ndx].get(tag)
        return result

    def set_val(self, ndx, tag, val):
        self.obj[ndx][tag] = val
        return self


class Q0LabeledStructure(_AbstractStructure):

    """This points to a labeled data structure for an abstract data model
    such as attributes of a class.

    """
    
    def get_val(self, ndx, tag):
        result = getattr(self.obj[ndx], tag, None)
        return result

    def set_val(self, ndx, tag, val):
        setattr(self.obj[ndx], tag, val)
        return self


class Q0Fld(object):

    """A text field.

    This is a tag and label to be added to an abstract data model.

    Q0Fld may be subclassed to provide conversions to/from Qt data
    types that have their own style of visual editing.

    """

    def __init__(
            self,
            tag,
            label=NULL,
            q0_help_txt=NULL,
            q0_alignment='nw',
            q0_icon=None,
            q0_size_hint=None,
            q0_font=None,
            q0_foreground_brush=None,
            q0_background_brush=None,
            is_enabled=False,
            ):
        self.tag = tag
        self.label = label
        self.q0_help_txt = q0_help_txt
        self.q0_alignment = q0_alignment
        self.q0_icon = q0_icon
        self.q0_size_hint = q0_size_hint
        self.q0_font = q0_font
        self.q0_foreground_brush = q0_foreground_brush
        self.q0_background_brush = q0_background_brush
        self.is_enabled=is_enabled
        return

    def to_edit(self, val):
        result = val
        return result

    def from_edit(self, val):
        result = val
        return result

    def get_role(self, role, ndx, rec):
        if Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['display', 'user']:
            result = self.get_val(ndx, rec)
        elif Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['edit']:
            result = self.get_as_edit(ndx, rec)
        elif Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['tool tip']:
            result = self.get_as_tooltip(ndx, rec)
        elif Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['what']:
            result = self.get_as_help_txt(ndx, rec)
        elif Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['text alignment']:
            result = self.get_alignment(ndx, rec)
        elif Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['decoration']:
            result = self.get_icon(ndx, rec)
        elif Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['size hint']:
            result = self.get_size_hint(ndx, rec)
        elif Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['font']:
            result = self.get_font(ndx, rec)
        elif Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['foreground']:
            result = self.get_foreground_brush(ndx, rec)
        elif Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['background']:
            result = self.get_background_brush(ndx, rec)
        else:
            result = None
        return result

    def get_val(self, ndx, rec):
        val = rec.get_val(ndx, self.tag)
        if val is None:
            result = None
        else:
            result = self.to_edit(val)
        return result

    def set_val(self, ndx, rec, obj):
        if isinstance(obj, Qt.QVariant):
            val = obj.value()
        else:
            val = obj
        if val is None:
            rec.set_val(ndx, self.tag, None)
        else:
            rec.set_val(ndx, self.tag, self.from_edit(val))
        return self

    def get_as_edit(self, ndx, rec):
        result = self.get_val(ndx, rec)
        return result

    def get_as_tooltip(self, ndx, rec):
        return None

    def get_help_txt(self, ndx, rec):
        result = self.q0_help_txt
        return result

    def get_alignment(self, ndx, rec):
        result = Q0_CODE_ALIGNMENT[self.q0_alignment]
        return result

    def get_icon(self, ndx, rec):
        result = self.q0_icon
        return result

    def get_size_hint(self, ndx, rec):
        result = self.q0_size_hint
        return result

    def get_font(self, ndx, rec):
        result = self.q0_font
        return result

    def get_foreground_brush(self, ndx, rec):
        result = self.q0_foreground_brush
        return result

    def get_background_brush(self, ndx, rec):
        result = self.q0_background_brush
        return result

    def get_wgt(self):
        result = Q0LineEdit()
        self.wgt = result
        return result


class Q0FldDate(Q0Fld):

    """A date field.

    """
    
    def to_edit(self, val):
        result = Qt.QDate(val.year, val.month, val.day)
        return result
    
    def from_edit(self, val):
        result = datetime.date(val.year(), val.month(), val.day())
        return result

    def get_wgt(self):
        result = Q0DateEdit().enable_calendar_popup()
        self.wgt = result
        return result
    

class Q0FldTime(Q0Fld):

    """A time field.

    """
    
    def to_edit(self, val):
        result = Qt.QTime(val.hour, val.minute, val.second)
        return result
    
    def from_edit(self, val):
        result = datetime.time(val.hour(), val.minute(), val.second())
        return result
    
    def get_wgt(self):
        result = Q0TimeEdit()
        self.wgt = result
        return result
    

class Q0FldDateTime(Q0Fld):

    """A date/time field.

    """
    
    def to_edit(self, val):
        result = Qt.QDateTime(val.year, val.month, val.day, val.hour, val.minute, val.second)
        return result
    
    def from_edit(self, val):
        result = datetime.datetime(val.year(), val.month(), val.day(), val.hours(), val.minutes(), val.seconds())
        return result
    
    def get_wgt(self):
        result = Q0DateTimeEdit()
        self.wgt = result
        return result


class Q0FldCurrency(Q0Fld):

    """A dollar-amount field.

    """
    
    def to_edit(self, val):
        try:
            result = locale.currency(float(val), symbol=False, grouping=False)
        except ValueError:
            result = val
        return result

    def from_edit(self, val):
        try:
            result = float(val)
        except ValueError:
            result = val
        return result
    

class Q0FldComboBox(Q0Fld):

    """A code-value field.

    """
    
    def to_edit(self, val):
        result = val
        ndx = self.wgt.index(val)
        self.wgt.set_pos(ndx)
        return result

    def get_wgt(self):
        result = Q0ComboBox()
        self.wgt = result
        return result


class Q0LedgerDelegate(Qt.QStyledItemDelegate):

    """This is a ledger delegate that is font aware.

    """
    
    def paint(self, painter, option, index):
        model = index.model()
        if isinstance(model, Q0LedgerModel):
            new_font = model.data(index, Q0_CODE_ITEM_DATA_ROLE['font'])
            if new_font:
                option.font = new_font
        result = super().paint(painter, option, index)
        return result


class Q0LedgerHeader(Qt.QHeaderView):

    """This is a ledger header.

    This retrieves column headers.

    """

    
    def __init__(self, orientation=Q0_CODE_ORIENTATION['horizontal']):
        super().__init__(orientation)
        self.setStretchLastSection(True)
        self.setSectionResizeMode(Q0_CODE_RESIZE_MODE['interactive'])  # 'resize to contents'])  # 2022 Sep 05
        self.setSectionsClickable(True)
        self.setSectionsMovable(True)
        return

    @property
    def q0_model(self):
        return self.model()
    @q0_model.setter
    def q0_model(self, x):
        self._q0_model = self.setModel(x)

    def get_fld_tags_left_to_right(self):
        result = []
        ndx_visual = self.count() - 1
        while ndx_visual >= ZERO:
            ndx_logical = self.logicalIndex(ndx_visual)
            result.append(self.q0_model.flds[ndx_logical].tag)
            ndx_visual -= 1
        result.reverse()
        return result
    
    
class Q0LedgerView(Qt.QTableView):

    """This is a view of a ledger.

    """

    
    def __init__(self):
        super().__init__()
        self.set_selection_behavior('rows')
        return

    @property
    def q0_model(self):
        return self.model()
    @q0_model.setter
    def q0_model(self, x):
        self.setModel(x)

    @property
    def q0_header(self):
        return self.horizontalHeader()
    @q0_header.setter
    def q0_header(self, x):
        self.setHorizontalHeader(x)

    def set_tab_key_navigation(self, is_enabled=True):
        result = super().setTabKeyNavigation(is_enabled)
        return result

    def set_item_delegate(self, delegate):
        result = super().setItemDelegate(delegate)
        return result

    def set_selection_behavior(self, q0_selection_behavior='item'):
        result = self.setSelectionBehavior(Q0_CODE_SELECTION_BEHAVIOR[q0_selection_behavior])
        return result

    def select_row(self, ndx_row):
        self.selectRow(ndx_row)
        return self

    def mousePressEvent(self, q0_event):
        result = super().mousePressEvent(q0_event)
        ndx = self.q0_model.get_current_index()
        (row, col) = (ndx.row(), ndx.column())
        y = self.rowViewportPosition(row)
        x = self.columnViewportPosition(col)
        self.q0_model.mouse_click(q0_event, row, col, x, y)
        return result

    def mouseDoubleClickEvent(self, q0_event):
        result = super().mouseDoubleClickEvent(q0_event)
        ndx = self.q0_model.get_current_index()
        (row, col) = (ndx.row(), ndx.column())
        y = self.rowViewportPosition(row)
        x = self.columnViewportPosition(col)
        self.q0_model.mouse_double_click(q0_event, row, col, x, y)
        return result

    def set_style_sheet(self, specs):
        self.setStyleSheet(specs)
        return self

    def refresh(self):
        self.viewport().repaint()
        return self

    
class Q0LedgerModel(QtCore.QAbstractTableModel):

    """A ledger model with a keyed structure.

    Use:

    items = []
    structure = q0.Q0KeyedStructure(items)
    items_table = q0.Q0LedgerModel(structure, parent=cent_wgt)
    for (tag, header, fld_type) in [
        ('description', 'Desc', q0.Q0Fld),
        ('long_description', 'Long', q0.Q0Fld),
        ('upc', 'UPC', q0.Q0Fld),
        ('category_code', 'Catagory', q0.Q0Fld),
        ('price', 'Price', q0.Q0Fld),
        ('tax_code', 'Taxable', q0.Q0Fld),
        ('discount_code', 'Discountable', q0.Q0Fld),
        ]:
        fld = fld_type(tag, header)
        items_table.add_fld(fld)
    items_view = cent_wgt.add_wgt(items_table.get_view(q0.Q0LedgerView()))
    items_table.begin_reset_model()
    items.clear()
    for item in doc_rec['items']:
        items.append(item)
    items_table.end_reset_model()

    NOTA BENE: The swindle here is that items must be as persistent as
    as items_table, so it won't do to say, "items = []," which creates
    a new object.  Use "items.clear()," instead.  The fields in items
    need not all exist.  You may fill them and clear them at any time,
    but you may not reassign the items' handle to another structure.

    """

    signal_data_changed = QtCore.pyqtSignal(QtCore.QModelIndex, QtCore.QModelIndex)

    
    def __init__(self, q0_structure, parent, is_editable=True):
        super().__init__(parent)
        self.set_struct(q0_structure)
        self.flds = []
        self.is_editable = is_editable
        return

    def set_struct(self, q0_structure):
        self.struct = q0_structure
        return self

    def begin_reset_model(self):
        result = self.beginResetModel()
        return result

    def end_reset_model(self):
        result = self.endResetModel()
        return result

    def get_view(self):
        result = Q0LedgerView()
        result.q0_model = self
        result.q0_header = Q0LedgerHeader()
        result.q0_header.sectionClicked.connect(self.section_clicked)
        result.setWordWrap(False)  # 2022 Sep 05
        result.setItemDelegate(Q0LedgerDelegate())
        self.q0_view = result
        return result

    def rowCount(self, parent=None):
        result = len(self.struct)
        return result

    def columnCount(self, parent=None):
        result = len(self.flds)
        return result

    def get_current_index(self):
        result = self.q0_view.currentIndex()
        return result

    def get_current_row_col(self):
        index = self.get_current_index()
        result = (index.row(), index.column())
        return result

    def set_current_index(self, q0_index):
        self.q0_view.setCurrentIndex(q0_index)
        return self

    def set_current_row_col(self, row, col):
        q0_index = self.index(row, col)
        self.set_current_index(q0_index)
        return self

    def flags(self, index):
        (row, col) = (index.row(), index.column())
        fld = self.flds[col]
        result = QtCore.Qt.NoItemFlags
        if fld.is_enabled:
            result |= QtCore.Qt.ItemIsSelectable
            result |= QtCore.Qt.ItemIsEnabled
            if self.is_editable:
                result |= QtCore.Qt.ItemIsEditable
        return result            

    def data(self, index, role):
        (row, col) = (index.row(), index.column())
        fld = self.flds[col]
        result = fld.get_role(role, row, self.struct)
        return result

    def setData(self, index, val, role):
        (row, col) = (index.row(), index.column())
        fld = self.flds[col]
        fld.set_val(row, self.struct, val)
        self.signal_data_changed.emit(index, index)
        result = True
        return result

    def headerData(self, section, orientation, role):
        if Q0_MNEMONIC_ORIENTATION[orientation] in ['horizontal']:
            fld = self.flds[section]
            if Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['display']:
                result = fld.label
            elif Q0_MNEMONIC_ITEM_DATA_ROLE[role] in ['text alignment']:
                result = fld.get_alignment(ZERO, self.struct)
            else:
                result = None
        else:
            result = None
        return result

    def layout(self, flds):
        self.flds = flds[:]
        return self
    
#    def add_fld(self, q0_fld):
#        self.flds.append(q0_fld)
#        return self

    def get_fld_ndx(self, tag):
        for (ndx, fld) in enumerate(self.flds):
            if fld.tag == tag:
                result = ndx
                break
        else:
            raise NotImplementedError
        return result

    def section_clicked(self, col):
        return self

    def get_sort_indicator(self, col):
        result = Q0_MNEMONIC_SORT_ORDER.get(self.q0_view.q0_header.sortIndicatorOrder())
        return result

    def get_tag(self, col):
        result = self.flds[col].label
        return result

    def mouse_click(self, event, row, col, x, y):
        return self

    def mouse_double_click(self, event, row, col, x, y):
        return self
     
    def set_style_sheet(self, specs):

        """Don't attempt this until after get_view().

        """
        
        self.q0_view.setStyleSheet(specs)
        return self

   
class Q0LedgerSorted(Q0LedgerModel):

    """A ledger model with sorting capabilities.

    """

    
    def __init__(self, parent, is_editable=True):
        self.rows = []
        q0_structure = Q0KeyedStructure(self.rows)        
        super().__init__(q0_structure, parent, is_editable=is_editable)
        return

    def section_clicked(self, col):
        self.q0_view.setSortingEnabled(True)
        super().section_clicked(col)
        return self

    def add_row(self, row):
        self.rows.append(row)
        return self

    def reset(self, recs):
        self.begin_reset_model()
        self.rows.clear()
        for rec in recs:
            self.add_row(rec)
        self.end_reset_model()
        return self

    def reset_row_tag(self, row, tag):
        if tag in self.flds:
            col = self.get_fld_ndx(tag)
            coord = self.createIndex(row, col)
            self.signal_data_changed.emit(coord, coord)
        return self

    def reset_row(self, row):
        coord_lo = self.createIndex(row, ZERO)
        coord_hi = self.createIndex(row, self.columnCount())
        self.signal_data_changed.emit(coord_lo, coord_hi)
        return self

    def set_current_row_col(self, row, col):
        limit = len(self.rows) - 1
        row = min(row, limit)
        if row < ZERO:
            pass
        else:
            super().set_current_row_col(row, col)
            self.q0_view.select_row(row)
        return self


class Q0RecordModel(Q0LedgerModel):

    """A ledger model with a labeled structure.

    Use:

    batch_rec = Batch()
    batch_mapper = q0.Q0DataWidgetMapper()
    batch_wgts = {}
    structure = q0.Q0LabeledStructure(batch_rec)
    record_model = q0.Q0RecordModel(structure)
    batch_mapper.set_model(record_model)
    for (tag, header, fld_type) in [
        ('batch_date_time', 'Time', q0.Q0FldDateTime),
        ('lo_date', 'Lo Date', q0.Q0FldDate),
        ('hi_date', 'Hi Date', q0.Q0FldDate),
        ('count', 'Count', q0.Q0Fld),
        ('total_amt', 'TOTAL Amt', q0.Q0Fld),
        ('docs_type', 'Type', q0.Q0Fld),
        ]:
        fld = fld_type(tag, header)
        record_model.add_fld(fld)
        (lbl, wgt) = batch_mapper.map_lbl_wgt(fld)
        batch_wgts[tag] = cent_wgt.add_row(lbl, wgt)
    with open(batch_name, 'r') as unit:
        batch_rec.load(unit)
    batch_mapper.to_first_row()
    record_model.rec_to_edit()

    NOTA BENE: The swindle here is that batch_rec must be as
    persistent as batch_mapper, so it won't do to say, "batch_rec =
    Constructor()," which creates a new object.  Use
    "delattr(batch_rec, 'frack')," to get rid of fields instead.  The
    fields in batch_rec need not all exist.  You may fill them and
    clear them at any time, but you may not reassign the batch_rec's
    handle to another structure.

    """

    def __init__(self, q0_structure, parent, is_editable=True):
        struct_type = type(q0_structure)
        table = struct_type([q0_structure.obj])
        super().__init__(table, parent, is_editable=is_editable)
        return
    
    def get_view(self):
        raise NotImplementedError
        return result

#   The following methods are required because Q0RecordModel has no
#   QAbstractItemView and, thus, no QStyledItemDelegate.

    def rec_to_edit(self):
        ndx = len(self.flds) - 1
        while ndx >= ZERO:
            val = self.flds[ndx].get_val(ZERO, self.struct)
            self.flds[ndx].wgt.set_visual(val)
            ndx -= 1
        return self

    def edit_to_rec(self):
        ndx = len(self.flds) - 1
        while ndx >= ZERO:
            val = self.flds[ndx].wgt.get_visual()
            self.flds[ndx].set_val(ZERO, self.struct, val)
            ndx -= 1
        return self


class Q0DataWidgetMapper(QtWidgets.QDataWidgetMapper):

    """Map a data model to a series of widgets.

    """    

    def __init__(self, q0_model=None, q0_submit='auto'):
        super().__init__()
        if q0_submit in ['auto', 'a']:
            self.setSubmitPolicy(QtWidgets.QDataWidgetMapper.AutoSubmit)
        elif q0_submit in ['manual', 'm']:
            self.setSubmitPolicy(QtWidgets.QDataWidgetMapper.ManualSubmit)
        else:
            raise NotImplementedError
        self.set_model(q0_model)
        return

    def set_model(self, q0_model):
        if q0_model is None:
            pass
        else:
            self.setModel(q0_model)
        return self

    def revert(self):
        result = super().revert()
        return result

    def submit(self):
        result = super().submit()
        return result

    def to_row(self, row):
        self.setCurrentIndex(row)
        return self

    def to_first_row(self):
        self.toFirst()
        return self

    def to_last_row(self):
        self.toLast()
        return self

    def to_next_row(self):
        self.toNext()
        return self

    def to_prev_row(self):
        self.toPrevious()
        return self

    def map_wgt(self, fld):
        result = fld.get_wgt()
        fld_ndx = self.model().get_fld_ndx(fld.tag)
        self.addMapping(result, fld_ndx)
        return result

    def map_lbl_wgt(self, fld):
        wgt = self.map_wgt(fld)
        lbl = Q0Label(fld.label)
        lbl.setBuddy(wgt)
        result = (lbl, wgt)
        return result


class ClipboardKind:

    """Clipboard interface.

    """
    
    def __init__(self, app, mime_type='text/x.x.x'):
        self.app_clipboard = app.clipboard()
        self.mime_type = mime_type
        return

    @property
    def contents(self):
        mime = self.app_clipboard.mimeData()
        bytes = mime.data(self.mime_type)
        result = bytes.data().decode()
        return result
    @contents.setter
    def contents(self, x):
        bytes = x.encode() 
        mime = QtCore.QMimeData()
        mime.setData(self.mime_type, bytes)
        self.app_clipboard.setMimeData(mime)

    def clear(self):
        self.app_clipboard.clear()
        return self


def main_line():
    return


locale.setlocale(locale.LC_ALL, '')


if __name__ == "__main__":
    
    """This code is run when this module is executed, not when it is included.

    """

    main_line()


# Fin
