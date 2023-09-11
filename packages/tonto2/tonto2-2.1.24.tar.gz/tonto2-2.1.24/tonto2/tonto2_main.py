#!/usr/bin/python3

# tonto2.py
# ccr . 2023 Jan 24

# ==================================================boilerplate»=====
# *Tonto2* is a rewrite of *tonto* v1.2.
# 
# Copyright 2006—2023 by Chuck Rhode.
# 
# See LICENSE.txt for your rights.
# =================================================«boilerplate======

# I developed the original Tonto in 2006.  It was in daily use for 16
# years.  The old script grew to more than 13.6K lines of *python2*
# code.  I've now broken it up into modules with documentation
# separate.

# This rewrite is necessary because *pygtk* is not currently supported
# in Debian 11 "Buster."  Tonto2 is a *python3* and *PyQt5*
# application.

# The *python3* language and my use of it and its support libraries
# have come a long way in the last decade and a half.  Hopefully
# *tonto2* will be a bit more terse than *tonto*.

# (But no!  As of 2023 Aug 30, the new code is 17.8K lines.)

# This script works best with the Noto Sans font group instead of
# Gnome fonts because Noto uses tabular (fixed-width) digit glyphs by
# default.

# This application is wired for Internationalization.  No
# professional-level translations are attempted although some hacks of
# other languages may be included.  Note that only string literals are
# translated.  Doc strings (except the *tonto2.py* module) and inter
# and intra-lineal code comments are not.

# This application is an *ad hoc* daily-use list maker.  Essentially
# it is a poor-man's relational database management system.  It
# scratches the itches that I'm sensitive to.  I'm not likely to
# broaden its scope.

# Particularly, although *vcard* (*.vcf) and *ical* (*.ics) imports
# and exports seem apropos for the *Tonto2* code base, these are
# supported by external utility scripts.  *Tonto2* is focused on
# *.csv, and other file formats are (for now) outside its scope.
# *.csv is chosen so that these kinds of conversions are feasible.

# One thing that *tonto* obsessed over that did not make it into
# *Tonto2* was automated phone dialing using asynchronous MODEMs.
# These have become much less common (not to say obsolete) in recent
# years.

# Calendar alarms are also mostly obsolete because they are handled
# robustly by scads of cell-phone apps.  For now, though, *Tonto2*
# does implement alarms.

# The range of native relation types is conscientiosly narrow in the
# face of the limitless and more or less legitimate variety that might
# be deemed to exist (in nature).  This pushes the analysis of certain
# uses of *Tonto2* to the periphery where they can be viewed as
# interface problems rather than receive implementation in core
# functionality.  (For instance, it seems to me that generating graphs
# or scatter plots of a relation would be better handled by an
# external script.)  PERT-scheduling float calculations were
# implemented *tonto* but are not attempted in *Tonto2*.

# I don't intend to implement encryption to scramble the contents of
# the native *.csv files.  This is a "knee-jerk ask" for the
# *Passwords* relation types to protect passwords from being scraped
# from the files they're stored in, but I don't believe that OpSec is
# *Tonto2*'s job.  Easy encryption would not be worthwhile, and robust
# encryption would be difficult to design and use correctly.  In fact,
# *Tonto2* tries to be agnostic about how the underlying data files
# are used and endeavors to keep those uses by other apps
# straightforward.  It stores passwords in plain text to minimize the
# difficulty of recovering them.  You are not dependent on a tricky
# encryption scheme and are not subject to the risk of losing your
# encryption keys, which protect your password store.  Be aware that,
# if you use *Tonto2* to store passwords, you have to protect them
# from discovery using other means — perhaps by encrypting/decrypting
# the *.csv files outside of *Tonto2*.  As always, your first and last
# line of defense in protecting your passwords is to keep unauthorized
# people out of your machine.

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1
NOT_AVAIL = "#N/A"
BLANK_VALUES = [NULL, None, NOT_AVAIL]
COLLECTION_SEP = '——'
MARKDN_LINE_END = '<br />'
__version__ = '2.1'

import sys           # Python Standard Library
import os            # Python Standard Library
import locale        # Python Standard Library
import pathlib       # Python Standard Library
import gettext       # Python Standard Library
import subprocess    # Python Standard Library
import re            # Python Standard Library
import datetime      # Python Standard Library
import uuid          # Python Standard Library
import json          # Python Standard Library
import shutil        # Python Standard Library
import webbrowser    # Python Standard Library
import urllib        # Python Standard Library
import configparser  # Python Standard Library
import tempfile      # Python Standard Library
import csv           # Python Standard Library
import dateparser    # *python3-dateparser Debian Package

locale.setlocale(locale.LC_ALL)
path_exec = pathlib.Path(__file__).resolve(strict=True).parent
path_locales = path_exec / 'locales'
translation = gettext.translation('tonto2', localedir=path_locales, fallback=True)
translation.install()

import tonto2.externals.barcodes2 as barcodes2
import tonto2.externals.q0 as q0
import tonto2.externals.tonto2_code_tables as tonto2_code_tables
import tonto2.externals.tonto2_parse_international_addresses as tonto2_parse_international_addresses

DELTA_DAY = datetime.timedelta(days=1)
DELTA_HOUR = datetime.timedelta(hours=1)

MD_SUMMARY = _("""<blockquote>
<b>tonto2.py</b> v{v0} is a personal address-list, calendar, notepad, and so much more.
</blockquote>
""").format(v0=__version__)

MD_GPL_V3 = _("""<blockquote>
<p>Copyright © 2006 Charles Curtis Rhode</p>

<p>This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.</p>

<p>This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.</p>

<p>You should have received a copy of the GNU General Public License
along with this program.  If not, see 
&lt;<a href="https://www.gnu.org/licenses/">https://www.gnu.org/licenses/</a>&gt;.</p>
</blockquote>
""")

MD_CONTACT = _("""<blockquote>
<p>Charles Curtis Rhode,<br>  
<a href=mailto://CRhode@LacusVeris.com?subject=Tonto">CRhode@LacusVeris.com</a>,<br>
1518 N 3rd, Sheboygan, WI 53081</p>
</blockquote>
""")

__doc__ = f"""<big>Tonto2</big>

{MD_SUMMARY}

{MD_GPL_V3}

{MD_CONTACT}
"""


TAG_ACCOUNT = _('Account')
TAG_ACCOUNT_STATUS = _('AccountStatus')
TAG_ADVANCE_ALARM = _('AdvanceAlarm')
TAG_AGENCY_1 = _('Agency1')
TAG_AGENCY_2 = _('Agency2')
TAG_AGENCY_3 = _('Agency3')
TAG_ALARM_SOUND = _('AlarmSound')
TAG_ARTICLE = _('Article')
TAG_ARTICLE_EDITORS = ('ArticleEditors')
TAG_AUTHOR_TYPE = _('AuthorType')
TAG_AUTHOR_1_LAST_NAME = _('Author1LastName')
TAG_AUTHOR_1_FIRST_NAME = _('Author1FirstName')
TAG_AUTHOR_2_LAST_NAME = _('Author2LastName')
TAG_AUTHOR_2_FIRST_NAME = _('Author2FirstName')
TAG_AUTHOR_3_LAST_NAME = _('Author3LastName')
TAG_AUTHOR_3_FIRST_NAME = _('Author3FirstName')
TAG_BACKGROUND_COLOR = _('BackgroundColor')
TAG_CALL_NUMBER = _('CallNumber')
TAG_CATEGORY = _('Category')
TAG_CHALLENGE = _('Challenge')
TAG_CITY = _('City')
TAG_CITY_PUBLISHER = _('CityPublisher')
TAG_COLLECTION_TYPE = _('CollectionType')
TAG_COLLECTION_LINK = _('CollectionLink')
TAG_COMPANY = _('Company')
TAG_CONFERENCE = _('Conference')
TAG_COUNTRY = _('Country')
TAG_DEPT_MAIL_STOP = _('DeptMailStop')
TAG_DISSERTATION = _('Dissertation')
TAG_DISSERTATION_TYPE = _('DissertationType')
TAG_EDITION = _('Edition')
TAG_EMAIL = _('eMail')
TAG_ENTRY_TYPE = _('EntryType')
TAG_EXPIRATION_DATE = _('ExpirationDate')
TAG_FIRST_NAME = _('FirstName')
TAG_FOREGROUND_COLOR = _('ForegroundColor')
TAG_FRAGMENT = _('Fragment')
TAG_GOVERNMENT = _('Government')
TAG_GREETING = _('Greeting')
TAG_IS_OFFSET_IN_MONTH_TYPE_DAYS = _('IsOffsetInMonthTypeDays')
TAG_IS_OFFSET_TYPE_DAYS = _('IsOffsetTypeDays')
TAG_ISSUE = _('Issue')
TAG_KEYWORDS = _('Keywords')
TAG_LAST_NAME = _('LastName')
TAG_LATITUDE = _('Latitude')
TAG_LIBRARY = _('Library')
TAG_LISTING_TYPE = _('ListingType')
TAG_LOCUS = _('Locus')
TAG_LONGITUDE = _('Longitude')
TAG_MANUFACTURER = _('Manufacturer')
TAG_MEDIUM = _('Medium')
TAG_NETWORK = _('Network')
TAG_OFFSET = _('Offset')
TAG_OFFSET_IN_MONTH = _('OffsetInMonth')
TAG_PASSWORD = _('Password')
TAG_PASSWORD_TYPE = _('PasswordType')
TAG_PATH = _('Path')
TAG_PHONE_1 = _('Phone1')
TAG_PHONE_2 = _('Phone2')
TAG_PHONE_3 = _('Phone3')
TAG_PHONE_4 = _('Phone4')
TAG_PHONE_TYPE_1 = _('PhoneType1')
TAG_PHONE_TYPE_2 = _('PhoneType2')
TAG_PHONE_TYPE_3 = _('PhoneType3')
TAG_PHONE_TYPE_4 = _('PhoneType4')
TAG_PAGES = _('Pages')
TAG_PIECES = _('Pieces')
TAG_POLITE_MODE = _('PoliteMode')
TAG_PRIORITY = _('Priority')
TAG_PROJECT = _('Project')
TAG_PROJECT_TYPE = _('ProjectType')
TAG_REMARKS = _('Remarks')
TAG_REPEAT_INTERVAL = _('RepeatInterval')
TAG_REPEAT_LOOP = _('RepeatLoop')
TAG_RESPONSE = _('Response')
TAG_SERIES = _('Series')
TAG_SERIES_FUNCTIONARIES = _('SeriesFunctionaries')
TAG_SERVICE = _('Service')
TAG_SORT_KEY = _('SortKey')
TAG_SPEAK_TITLE = _('SpeakTitle')
TAG_SPONSOR = _('Sponsor')
TAG_STATE = _('State')
TAG_STATUS = _('Status')
TAG_STOP = _('Stop')
TAG_STREET = _('Street')
TAG_TITLE = _('Title')
TAG_UNIQUE_ID = _('UniqueID')
TAG_USER_ID = _('UserID')
TAG_VENDOR = _('Vendor')
TAG_VENUE_CITY = _('VenueCity')
TAG_VOL=_('Volume')
TAG_WEB = _('Web')
TAG_WHEN_ARTICLE_ORIG = _('WhenArticleOrig')
TAG_WHEN_RECORDED = _('WhenRecorded')
TAG_WHEN_PUBLISHED = _('WhenPublished')
TAG_WHEN_WORK_ORIG = _('WhenWorkOrig')
TAG_WORK = _('Work')
TAG_WORK_EDITORS = ('WorkEditors')
TAG_XREF = _('XRef')
TAG_ZIP = _('Zip')
TAG__ACCESSION_DATE = _('_AccessionDate')
TAG__DURATION = _('_Duration')
TAG__HANDLE = _('_Handle')
TAG__START = _('_Start')
TAG__TRAVERSE_DATE = _('_TraverseDate')
TAG__UPDATE_DATE = _('_UpdateDate')
TAG__URI = _('_URI')


def strip_protocol_scheme(uri):

    """Remove protocol (if any) from a URI.

    Return the given URI without the protocol (http://, mail://).

    """
    
    url = urllib.parse.urlparse(str(uri))
    url = list(url)
    url[ZERO] = NULL
    result = urllib.parse.urlunparse(url)
    return result


def raw(markup):

    """Denature any HTML tags.

    Return the given markup string, substituting entity defs for
    control characters.

    """
    
    result = markup
    result = result.replace('&', '&amp;').replace('&amp;amp;', '&amp;')
    result = result.replace('<', '&lt;')
    result = result.replace('>', '&gt;')
    return result


TITLE_SEP = re.compile(r'([-~\s"]+)')
TITLE_UNQUOTE = re.compile(r'^[\'"]*(.+?)[\'"]*$')
UNCASE_WORDS = [
    'a', 
    'about', 
    'above', 
    'across', 
    'after', 
    'against', 
    'along', 
    'among', 
    'an', 
    'and', 
    'around', 
    'as', 
    'at', 
    'before', 
    'behind', 
    'below', 
    'beneath', 
    'beside', 
    'between', 
    'beyond', 
    'but', 
    'by', 
    'despite', 
    'down', 
    'during', 
    'except', 
    'for', 
    'from', 
    'in', 
    'inside', 
    'into', 
    'like', 
    'near', 
    'nor', 
    'of', 
    'off', 
    'on', 
    'onto', 
    'or', 
    'out', 
    'outside', 
    'over', 
    'past', 
    'since', 
    'so', 
    'the', 
    'through', 
    'throughout', 
    'till', 
    'to', 
    'toward', 
    'under', 
    'underneath', 
    'until', 
    'up', 
    'upon', 
    'with', 
    'within', 
    'without', 
    'yet', 
    ]


def initial_cap(word):

    """Capitalize a word.

    This function tries to avoid problems with apostrophes
    in possessives and contractions that plague the string
    method.
        
    """

    return word[:1].upper() + word[1:]


def un_case_word(word):

    """Change a word to all lowercase

    ... except words that are all uppercase

    ... except the first character.

    """
    
    word_lower = word.lower()
    if word_lower in UNCASE_WORDS:
        result = word_lower
    elif word.isupper():
        result = word
    else:
        markup = word_lower.split('>', 1)
        markup[-1] = initial_cap(markup[-1])
        result = '>'.join(markup)
    return result

    
def un_case_phrase(phrase):

    """Change a phrase to all lowercase

    ... while capitalizing words that are not articles or
    prepositions.  Capitalize the first and last words.

    """
    
    words = TITLE_SEP.split(phrase)
    result = []
    result.append(un_case_word(words.pop(ZERO)))
    while words:
        result.append(words.pop(ZERO))
        if words:
            result.append(un_case_word(words.pop(ZERO)))
    ndx = ZERO  # Capitalize first word.
    try:
        while result[ndx] == NULL:
            ndx += 2
    except IndexError:
        ndx = ZERO
    result[ndx] = initial_cap(result[ndx])
    ndx = -1  # Capitalize last word.
    try:
        while result[ndx] == NULL:
            ndx -= 2
    except IndexError:
        ndx = -1
    result[ndx] = initial_cap(result[ndx])
    return NULL.join(result)


def american_title_case(text):

    """Preserve runs of upper-case characters unless text is all
    upper-case to begin with.

    The results of this transformation must be observed closely.  It
    may not always be correct.

    """
    
    if text.isupper():
        text = text.lower()
    return un_case_phrase(text)


def repl_case(valu, targ, repl=None, is_highlighted=False):

    """Search *valu* for *targ* and substitute *repl* with optional
    highlight.

    The result is a tuple: the number of replacements and the string
    with replacments.

    >>> repl_case('Now is the time.', 'The', 'the actual', is_highlighted=True)
    (0, 'Now is the time.')

    >>> repl_case('Now is the time.', 'the', 'the actual', is_highlighted=True)
    (1, 'Now is <b>the actual</b> time.')

    >>> repl_case('Now is the time.', 'the', 'the')
    (1, 'Now is the time.')

    >>> repl_case('Now is the time.', 'the')
    (1, 'Now is the time.')

    >>> repl_case('Now is the time.', 't', '?')
    (2, 'Now is ?he ?ime.')

    >>> repl_case('Now is the time.', 'n', '?')
    (1, '?ow is the time.')

    >>> repl_case('Now is the time.', 'n', 'x')
    (1, 'Xow is the time.')

    >>> repl_case('I became operational at the HAL plant in Urbana, Illinois, on January 12, 1992.  ', 'hal', 'rca')
    (1, 'I became operational at the RCA plant in Urbana, Illinois, on January 12, 1992.  ')

    >>> repl_case('I became operational at the Hal plant in Urbana, Illinois, on January 12, 1992.  ', 'hal', 'rca')
    (1, 'I became operational at the Rca plant in Urbana, Illinois, on January 12, 1992.  ')

    >>> repl_case('I became operational at the hal plant in Urbana, Illinois, on January 12, 1992.  ', 'hal', 'rca')
    (1, 'I became operational at the rca plant in Urbana, Illinois, on January 12, 1992.  ')

    >>> repl_case('I became operational at the HAL plant in Urbana, Illinois, on January 12, 1992.  ', 'hal', 'McGregor')
    (1, 'I became operational at the McGregor plant in Urbana, Illinois, on January 12, 1992.  ')

    >>> repl_case('I became operational at the HAL plant in Urbana, Illinois, on January 12, 1992.  ', NULL, 'McGregor')
    (0, 'I became operational at the HAL plant in Urbana, Illinois, on January 12, 1992.  ')

    """

    if repl is None:
        repl = targ
    result = NULL
    targ_len = len(targ)
    is_targ_caseless = targ.islower()
    is_repl_caseless = repl.islower()
    if is_targ_caseless:
        valu_match = valu.lower()
    else:
        valu_match = valu
    old_pos = ZERO
    count = ZERO
    while True:
        new_pos = valu_match.find(targ, old_pos)
        if (targ_len == ZERO) or (new_pos == NA):
            result += valu[old_pos:]
            break
        else:
            count += 1
            slice_prefix = slice(old_pos, new_pos)
            slice_match = slice(new_pos, new_pos + targ_len)
            result += valu[slice_prefix.start: slice_prefix.stop]
            match = valu[slice_match.start: slice_match.stop]
            if is_targ_caseless and is_repl_caseless and match.istitle():
                repl_match = repl.title()
            elif is_targ_caseless and is_repl_caseless and match.isupper():
                repl_match = repl.upper()
            else:
                repl_match = repl
            if is_highlighted:
                result += f'<b>{repl_match}</b>'
            else:
                result += repl_match
            old_pos = slice_match.stop
    return (count, result)

        
class Error(Exception):

    """Tonto2 base class for errors.

    """
    
    def __init__(self, msg):
        self.msg = msg
        return 

    def __str__(self):
        return self.msg


class ErrorNotNumeric(Error):

    """Tonto2 non-numeric error.

    """
    
    pass


class ErrorNumericRange(Error):

    """Tonto2 numeric-range error.

    """
    
    pass


class ErrorCodeTableLookup(Error):

    """Tonto2 code-table lookup error.

    """
    
    pass


def is_date_instance(dt):

    """Test whether dt is datetime.date.

    It might be datetime.datetime.  Datetime.datetime is an instance
    of datetime.date, so *isinstance* by itself is inconclusive.  We
    want to exclude datetime.datetime.

    """
    
    if isinstance(dt, datetime.datetime):
        result = False
    elif isinstance(dt, datetime.date):
        result = True
    else:
        result = False
    return result


def browser_open_tab(uri=None, can_update_traversed_date=True):

    """Open a new tab with browser.

    This fires up the default browser and updates _TraverseDate.

    """
    
    if uri is None:
        result = False
    else:
        with q0.Q0Alert(
            q0_app=COMMON['APP'],
            q0_title=_('Opening Browser'),
            q0_visual=_('Please wait.'),
            ):
            try:
                if shutil.which(COMMON['CONFIG'].browser):
                    controller = webbrowser.get(using=COMMON['CONFIG'].browser)
                    result = True
                elif COMMON['CONFIG'].browser in BLANK_VALUES:
                    controller = webbrowser.get()
                    result = True
                elif COMMON['CONFIG'].browser in [
                        'most common',
                    ]:
                    controller = webbrowser.get()
                    result = True
                else:
                    result = False
                if result:
                    controller.open(uri, new=2, autoraise=True)
            except webbrowser.Error:
                result = False        
    if result:
        pass
    else:
        q0.Q0MessageBox(
            q0_icon='critical',
            q0_title=_('Error'),
            q0_visual=_("Can't find default browser."),
            ).exec_()

#   Update *_Traversed_Date*.  Staging/Destaging the record needs to
#   get done in the context of calling *browser_open_tab*.

    if can_update_traversed_date:
        tab_current_text = MAIN_WIN.tabs.tab_wgt.get_current_tab_visual()
        tab_current = MAIN_WIN.tabs.get(tab_current_text)
        if tab_current:
            rel = tab_current.rel
            if rel is None:
                pass
            else:
                itm = rel.pages.find(TAG__TRAVERSE_DATE)
                if itm is None:
                    pass
                else:
                    itm.val_comp = datetime.datetime.now()
                    if hasattr(itm, 'edt'):
                        itm.edt.set_visual(itm.val_disp)
    return result


def split_proc_parms(cmd):

    """Split a shell command into an executable processor call and its
    several parameters.

    """
    
    result = []
    while True:
        if shutil.which(cmd):
            result.insert(ZERO, cmd)
            break
        parms = cmd.rsplit(maxsplit=1)
        parms += [None, None]
        (cmd, parm) = parms[:2]
        if parm:
            result.insert(ZERO, parm)
        else:
            result = None
            break
    return result


def announce(txt):

    """Run the voice synthesizer.

    This fires up the default festival-type voice synthesizer to
    pronounce txt.

    """
    
    if COMMON['CONFIG'].festival_type_voice_synth in BLANK_VALUES:
        pass
    else:
        cmd = split_proc_parms(COMMON['CONFIG'].festival_type_voice_synth)
        subprocess.run(
            cmd,
            text=True,
            input=txt,
            )
    return


def generate_qr_image(txt):

    """Run the Quick-Response code generator.

    This fires up the default qrencode-type minecraft image generator
    to encode txt.

    """
    
    if COMMON['CONFIG'].qr_code_generator in BLANK_VALUES:
        result = None
    else:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.png') as unit:
            cmd = split_proc_parms(COMMON["CONFIG"].qr_code_generator.format(unit.name))
            cmd.append(txt)
            proc = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                )
        try:
            proc.check_returncode()
            result = unit.name
            if result.startswith('/'):
                pos = 1
            else:
                pos = ZERO
            result = f'file:///{result[pos:]}'
        except subprocess.CalledProcessError:
            print(f'>  {proc.args}')
            print(proc.stderr)
            proc = None
            result = None
    return result


class RegItem:

    """A Tonto2 entity-register item.

    """
        
    def __init__(self, name, name_i18n, cls, description):
        self.name = name
        self.name_i18n = name_i18n
        self.cls = cls
        self.description = description
        return

    
class Reg(dict):

    """A Tonto2 entity register.

    This is used to look up fld itm classes or rel classes by name,

    """
        
    def add(self, item):
        self[item.name] = item
        return self

    def name_by_type(self):
        result = {}
        for entry in self.values():
            result[entry.cls] = entry.name
        return result

    def type_by_name(self):
        result = {}
        for entry in self.values():
            result[entry.name] = entry.cls
        return result

    def keys_i18n(self):
        result = []
        for item in self.values():
            result.append(item.name_i18n)
        return result

    def lookup_i18n(self, name_i18n):
        for item in self.values():
            if item.name_i18n == name_i18n:
                result = item
                break
        else:
            result = None
        return result


REG_ITMS = Reg()
REG_RELS = Reg()


class EssentialAttribs(list):

    """Not attributes, but a list of attribute names.

    Each attribute name bears a tuple of info items for name
    internationalization, attribute serialization, and graphic
    presentation.

    """
    
    def ammend(self, collection):

        """Change essential attributes.

        Collection is a list of tuples with the same layout as self.
        The tuple[ZERO] is a key.  Collection is appended to self
        except that keys are not duplicated.

        """
        
        for (ndx_new, tuple_new) in enumerate(collection):
            new_name = tuple_new[ZERO]
            for (ndx_old, tuple_old) in enumerate(self):
                old_name = tuple_old[ZERO]
                if new_name == old_name:
                    self[ndx_old] = tuple_new
                    break
            else:
                self.append(tuple_new)
        return self


class TontoObj:

    """A Tonto2 object.

    This is the parent of both Itm and Rel.  It provides common
    properties and serialization and graphic interface methods.

    """
    
    def __init__(self, tag=NULL):
        self.tag = tag
        self.md_desc_long = NULL
        self.essential_attribs = EssentialAttribs()
        self.essential_attribs.ammend([
            ('tag', KeyValSer.put, KeyValSer.get, _('Tag'), q0.Q0LineEdit),
            ('md_desc_long', KeyValSer.put_pgraph, KeyValSer.get, _('Long Description'), q0.Q0TextEdit),
            ])
        return

    def save(self, key_val_ser):
        for (attrib, put, get, label, q0_type) in self.essential_attribs:
            put(key_val_ser, f'  {attrib}', getattr(self, attrib))
        return self

    def load(self, key_val_ser):
        for (attrib, put, get, label, q0_type) in self.essential_attribs:
            setattr(self, attrib, get(key_val_ser, f'  {attrib}'))
        return self

    def clone(self, old_obj):
        for (attrib, put, get, label, q0_type) in self.essential_attribs:
            if attrib in ['fmt_disp']:
                pass
            else:
                x = getattr(old_obj, attrib, None)
                if x is None:
                    pass
                else:
                    setattr(self, attrib, x)
        return self

    @property
    def tag(self):
        return self._tag
    @tag.setter
    def tag(self, x):
        self._tag = x

    @property
    def md_desc_long(self):
        return self._md_desc_long
    @md_desc_long.setter
    def md_desc_long(self, x):
        self._md_desc_long = x

    def conjure_property_edit(self, dlg, form):

        """Populate a form within a dialog with label/edit pairs.

        This is called in the Change-Item dialog.

        Run through the essential attributes.  Create a dictionary of
        widgets within the dialog keyed by attribute name as a
        side-affect.

        """
        
        dlg.property_wgts = {}
        for (attrib, put, get, label, q0_type) in self.essential_attribs:
            if q0_type in [q0.Q0LineEdit]:
                wgt = q0_type(q0_default=str(getattr(self, attrib)))
            elif q0_type in [q0.Q0TextEdit]:
                wgt = q0_type(q0_default=getattr(self, attrib))
            elif q0_type in [q0.Q0CheckBox]:
                wgt = q0_type(q0_visual=NULL)
                wgt.set_checked(getattr(self, attrib))
                if label in ['Locale Formatted']:
                    wgt.connect_state_changed(dlg.event_locale_formatted_changed)
            elif q0_type in [q0.Q0ComboBox]:
                wgt = q0_type(is_editable=False, items=tonto2_code_tables.TAB_BY_NAME.keys())
                wgt.set_visual(self.code_table)
            else:
                raise NotImplementedError
            (lbl, wgt) = form.add_row(q0.Q0Label(label), wgt)
            dlg.property_wgts[attrib] = wgt
        return self

    def digest_property_edit(self, dlg):

        """Recover values for essential attributes from the completed dialog.

        """
        
        def convert(attrib, wgt, conv):
            x = wgt.get_visual()
            if x in BLANK_VALUES:
                result = NOT_AVAIL
            else:
                try:
                    result = conv(x)
                except ValueError:
                    raise ErrorNotNumeric(_('"{v0}" must be numeric or "{v1}".').format(v0=attrib, v1=NOT_AVAIL))
            return result
        
        for (attrib, put, get, label, q0_type) in self.essential_attribs:
            wgt = dlg.property_wgts[attrib]
            if isinstance(wgt, q0.Q0LineEdit):
                if get in [KeyValSer.get]:
                    setattr(self, attrib, wgt.get_visual())
                elif get in [KeyValSer.get_int]:
                    setattr(self, attrib, convert(attrib, wgt, int))
                elif get in [KeyValSer.get_float]:
                    setattr(self, attrib, convert(attrib, wgt, float))
                else:
                    raise NotImplementedError
            elif isinstance(wgt, q0.Q0TextEdit):
                setattr(self, attrib, wgt.get_visual())
            elif isinstance(wgt, q0.Q0CheckBox):
                setattr(self, attrib, wgt.is_checked())
            elif isinstance(wgt, q0.Q0ComboBox):
                setattr(self, attrib, wgt.get_visual())
            else:
                raise NotImplementedError
        return self


class Itm(TontoObj):

    """This is the parent of Tonto2 data items.

    It defines value properties: 

    + default — initial value
    + computational — live value
    + storage — archival value for serialization
    + display — text representation 
    + edit — editable text representation
    + view — markup value
    + sort — lexical-order value

    An Itm may be thought to have a single value, but the value
    properties are separate aspects of that value.  Thus, these
    properties are related.  Setting or getting one sideaffects the
    others.  Itm defines the relationship among the value properties
    for ItmText, but other kinds of Itms have different relationships.

    """
    
    q0_edit_type = q0.Q0LineEdit

    def __init__(self, tag=None):
        super().__init__(tag)
        self.val_default = NOT_AVAIL
        self.val_comp = NOT_AVAIL
        self.is_edit_enabled = True
        self.is_dd_mod_enabled = True
        self.is_locale_formatted = True
        self.fmt_disp = '{}'
        self.fmt_edit = '{}'
        self.essential_attribs.ammend([
            ('val_default', KeyValSer.put, KeyValSer.get, _('Default'), q0.Q0LineEdit),
            ('is_edit_enabled', KeyValSer.put_bool, KeyValSer.get_bool, _('Edit Enabled'), q0.Q0CheckBox),
            ('is_dd_mod_enabled', KeyValSer.put_bool, KeyValSer.get_bool, _('Can Modify'), q0.Q0CheckBox),
            ('is_locale_formatted', KeyValSer.put_bool, KeyValSer.get_bool,_('Locale Formatted'), q0.Q0CheckBox),
            ('fmt_disp', KeyValSer.put, KeyValSer.get, _('Display Format'), q0.Q0LineEdit),
            ('fmt_edit', KeyValSer.put, KeyValSer.get, _('Edit Format'), q0.Q0LineEdit),
            ])
        return

    @property
    def val_default(self):
        return self._val_default
    @val_default.setter
    def val_default(self, x):
        self._val_default = x

    @property
    def val_comp(self):
        return self._val_comp
    @val_comp.setter
    def val_comp(self, x):
        if x in BLANK_VALUES:
            self._val_comp = NOT_AVAIL
            self.has_value = False
        else:
            self._val_comp = x
            self.has_value = True

    @property
    def val_store(self):
        return self.val_comp
    @val_store.setter
    def val_store(self, x):
        self.val_comp = x

    @property
    def is_edit_enabled(self):
        return self._is_edit_enabled
    @is_edit_enabled.setter
    def is_edit_enabled(self, x):
        self._is_edit_enabled = x

    @property
    def is_dd_mod_enabled(self):
        return self._is_dd_mod_enabled
    @is_dd_mod_enabled.setter
    def is_dd_mod_enabled(self, x):
        self._is_dd_mod_enabled = x

    @property
    def is_locale_formatted(self):
        return self._is_locale_formatted
    @is_locale_formatted.setter
    def is_locale_formatted(self, x):
        self._is_locale_formatted = x

    @property
    def fmt_disp(self):
        return self._fmt_disp
    @fmt_disp.setter
    def fmt_disp(self, x):
        self._fmt_disp = x

    @property
    def fmt_edit(self):
        return self._fmt_edit
    @fmt_edit.setter
    def fmt_edit(self, x):
        self._fmt_edit = x

    @property
    def val_disp(self):
        return self.fmt_disp.format(self.val_comp)
    @val_disp.setter
    def val_disp(self, x):
        self.val_comp = x

    @property
    def val_edit(self):
        return self.fmt_edit.format(self.val_comp)
    @val_edit.setter
    def val_edit(self, x):
        self.val_comp = x

    @property
    def val_view(self):
        return self.val_disp

    @property
    def val_sort(self):
        if self.has_value:
            match = TITLE_UNQUOTE.match(self.val_disp)
            if match:
                result = match.group(1)
            else:
                result = self.val_disp
        else:
            result = NOT_AVAIL
        return result

    def conjure_form_entry_extras(self, wgt):

        """Add extra controls for editing an Itm.

        This is an empty hook where descendant Itms hang the code for
        special helper buttons.

        """
        
        return self

    def conjure_form_entry(self, form, align=None):

        """Populate a form with label/edit pairs.

        This is called in the Field-Entry dialog.  It creates a
        self.edt property that is the widget on the form.

        """
        
        wgt = q0.Q0Widget() 
        if self.is_edit_enabled:
            self.edt = wgt.add_wgt(self.q0_edit_type(), align=align)
            self.conjure_form_entry_extras(wgt)
            self.edt.set_visual(self.val_edit)
        else:
            self.edt = wgt.add_wgt(q0.Q0Label(), align=align)
            self.edt.set_visual(self.val_disp)
        (lbl, wgt) = form.add_row(q0.Q0Label(_(self.tag)), wgt)
        lbl.setToolTip(self.md_desc_long)
        return self

    def digest_form_entry(self):

        """Recover the Itm value from the completed form.

        """
        
        def raise_err():
            raise Error(_('''Value "{v0}" 
for field "{v1}" 
is not valid as "{v2}."
''').format(v0=self.edt.get_visual(), v1=self.tag, v2=REG_ITMS.name_by_type()[type(self)]))
        
        if self.is_edit_enabled:
            try:
                self.val_edit = self.edt.get_visual()
            except ValueError:
                raise_err()
            except barcodes2.BarcodeError:
                raise_err()
        return self

    def conjure_property_edit(self, dlg, form):
        super().conjure_property_edit(dlg, form)
        dlg.property_wgts['is_dd_mod_enabled'].set_enabled(False)
        return self

    
class ItmText(Itm):

    """This is a Tonto2 text item.

    """
    
    pass

REG_ITMS.add(RegItem('Text', _('Text'), ItmText, _('**Text** is any sequence of characters.')))


class ItmMarkup(ItmText):

    """This is a Tonto2 markup (HTML) item.

    """
        
    q0_edit_type = q0.Q0TextEdit

REG_ITMS.add(RegItem('Markup', _('Markup'), ItmMarkup, _('**Markup** is **Text**, which may contain XML tags and HTML entities.')))


class ItmMarkdn(ItmMarkup):

    """This is a Tonto2 markdown item.

    """    
    
    q0_edit_type = q0.Q0TextEdit

REG_ITMS.add(RegItem('Markdown', _('Markdown'), ItmMarkdn, _('**Markdown** is **Text**, which may contain mark-down formatting.')))


class ItmLog(ItmMarkdn):

    """This is a Tonto2 log item.

    It has a "Now" button that inserts a time stamp into the edit box.

    """    
    
    q0_edit_type = q0.Q0TextEdit

    def conjure_form_entry_extras(self, wgt):
        wgt.add_wgt(q0.Q0PushButton(
            q0_visual=_('Now'),
            event_clicked=self.event_now,
            ), align='nw')   
        return self

    def event_now(self):
        if isinstance(self.edt, q0.Q0TextEdit):
            self.edt.insertPlainText(ItmDateTime().set_now().val_disp)
        elif isinstance(self.edt, q0.Q0LineEdit):
            self.edt.insert(ItmDateTime().set_now().val_disp)
        else:
            raise NotImplementedError
        return

REG_ITMS.add(RegItem('Log', _('Log'), ItmLog, _('**Log** is **Text**, which may contain time-stamps.')))


class ItmAmericanTitleCase(ItmText):

    """This is a Tonto2 title item.

    It has a "Caps" button that recapitalizes the text in the edit
    box.

    """
    
    
    def conjure_form_entry_extras(self, wgt):
        wgt.add_wgt(q0.Q0PushButton(
            q0_visual=_('Caps'),
            event_clicked=self.event_caps,
            ), align='nw')
        return self

    def event_caps(self):
        self.edt.set_visual(american_title_case(self.edt.get_visual()))
        return

REG_ITMS.add(RegItem(
    'Title Case',
    _('Title Case'),
    ItmAmericanTitleCase,
    _('**Title Case" is **Text** that should obey English capitalization rules.'),
    ))


class ItmCoded(ItmText):

    """This is a Tonto2 coded-value item.

    It is initialized with a code-table name, which is a section label
    in the tonto2_code_tables.ini file.

    """
    
    q0_edit_type = q0.Q0ComboBox

    def __init__(self, tag=None, code_table='YES_NO_MAYBE'):
        super().__init__(tag)
        self.code_table = code_table
        self.essential_attribs.ammend([
            ('code_table', KeyValSer.put, KeyValSer.get, _('Code Table'), q0.Q0ComboBox),
            ])
        return

    @property
    def code_table(self):
        return self._code_table
    @code_table.setter
    def code_table(self, x):
        self._code_table = x
        self.conversion = tonto2_code_tables.TAB_BY_NAME[self._code_table]

    @property
    def val_edit(self):
        return self.fmt_edit.format(self.conversion.comp_to_disp(self.val_comp))
    @val_edit.setter
    def val_edit(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            y = self.conversion.disp_to_comp(x)
            if y in BLANK_VALUES:
                raise ErrorCodeTableLookup(_('Key "{v0}" not found in code table "{v1}."').format(v0=x, v1=self.code_table))
            else:
                self.val_comp = y

    def val_inc(self):
        self.val_comp = self.conversion.inc(self.val_comp)
        return self

    def val_dec(self):
        self.val_comp = self.conversion.dec(self.val_comp)
        return self

    def conjure_form_entry(self, form, align=None):
        wgt = q0.Q0Widget() 
        if self.is_edit_enabled:
            self.edt = wgt.add_wgt(self.q0_edit_type(), align=align)
            for (pos, meaning) in enumerate(self.conversion.collection_disp()):
                self.edt.add_item(q0_visual=meaning, pos=pos)
                code = self.conversion.inverse.get(meaning)
                if code is None:
                    pass
                else:
                    self.edt.set_item_tool_tip(q0_visual=code, pos=pos)
            self.edt.set_visual(self.val_edit)
        else:
            self.edt = wgt.add_wgt(q0.Q0Label(), align=align)
            self.edt.set_visual(self.val_disp)
        (lbl, wgt) = form.add_row(q0.Q0Label(_(self.tag)), wgt)
        lbl.setToolTip(self.md_desc_long)
        return self


REG_ITMS.add(RegItem('Code Table', _('Code Table'), ItmCoded, _('**Code Table** stores a key to a table of values.')))


class ItmSelected(ItmCoded):

    """This is a Tonto2 selection item.

    It, too, is a code-table, but its value is not restricted to keys
    in the table.  The user may fill in the combo-box with a made-up
    value.

    """
    
    @property
    def val_edit(self):
        return self.fmt_edit.format(self.conversion.comp_to_disp(self.val_comp, self.val_comp))
    @val_edit.setter
    def val_edit(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = self.conversion.disp_to_comp(x, x)

REG_ITMS.add(RegItem('Selection', _('Selection'), ItmSelected, _('**Selection** stores a key, which may or may not exist, in a table.')))


class ItmInteger(ItmText):

    """This is a Tonto2 integer-valued item.

    Potentially it may have minimum and maximum values.

    """
        
    def __init__(self, tag=None):
        super().__init__(tag)
        self.val_min = NOT_AVAIL
        self.val_max = NOT_AVAIL
        self.essential_attribs.ammend([
            ('val_default', KeyValSer.put_int, KeyValSer.get_int, _('Default'), q0.Q0LineEdit),
            ('val_min', KeyValSer.put_int, KeyValSer.get_int, _('Minimum Value'), q0.Q0LineEdit), 
            ('val_max', KeyValSer.put_int, KeyValSer.get_int, _('Maximum Value'), q0.Q0LineEdit),
            ])
        return

    @property
    def val_min(self):
        return self._val_min
    @val_min.setter
    def val_min(self, x):
        if x in BLANK_VALUES:
            self._val_min = NOT_AVAIL
        else:
            self._val_min = int(x)

    @property
    def val_max(self):
        return self._val_max
    @val_max.setter
    def val_max(self, x):
        if x in BLANK_VALUES:
            self._val_max = NOT_AVAIL
        else:
            self._val_max = int(x)

    @property
    def val_store(self):
        return str(self.val_comp)
    @val_store.setter
    def val_store(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = int(x)

    @property
    def val_disp(self):
        if False:
#        if self.is_locale_formatted and self.has_value:  # *localize* not avail in Python 3.9.
            result = locale.localize(self.val_comp, grouping=True)
        elif self.has_value:
            result = self.fmt_disp.format(self.val_comp)
        else:
            result = NOT_AVAIL
        return result
    @val_disp.setter
    def val_disp(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = int(locale.delocalize(x))

    @property
    def val_edit(self):
        if False:
#        if self.is_locale_formatted and self.has_value:  # *localize* not avail in Python 3.9.
            result = locale.localize(self.val_comp, grouping=True)
        elif self.has_value:
            result = self.fmt_edit.format(self.val_comp)
        else:
            result = NOT_AVAIL
        return result
    @val_edit.setter
    def val_edit(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = int(locale.delocalize(x))
            if self.val_min in BLANK_VALUES:
                pass
            elif self.val_comp < self.val_min:
                raise ErrorNumericRange(_('Value too small for {v0} item.').format(v0=self.tag))
            else:
                pass
            if self.val_max in BLANK_VALUES:
                pass
            elif self.val_comp > self.val_max:
                raise ErrorNumericRange(_('Value too large for {v0} item.').format(v0=self.tag))
            else:
                pass

REG_ITMS.add(RegItem('Integer', _('Integer'), ItmInteger, _('**Integer** contains a whole number.')))


class ItmFloat(ItmInteger):

    """This is a Tonto2 real-valued item.

    """
        
    def __init__(self, tag=None):
        super().__init__(tag)
        self.essential_attribs.ammend([
            ('val_default', KeyValSer.put_float, KeyValSer.get_float, _('Default'), q0.Q0LineEdit),
            ('val_min', KeyValSer.put_float, KeyValSer.get_float, _('Minimum Value'), q0.Q0LineEdit), 
            ('val_max', KeyValSer.put_float, KeyValSer.get_float, _('Maximum Value'), q0.Q0LineEdit),
            ])
        return

    @property
    def val_min(self):
        return self._val_min
    @val_min.setter
    def val_min(self, x):
        if x in BLANK_VALUES:
            self._val_min = NOT_AVAIL
        else:
            self._val_min = float(x)

    @property
    def val_max(self):
        return self._val_max
    @val_max.setter
    def val_max(self, x):
        if x in BLANK_VALUES:
            self._val_max = NOT_AVAIL
        else:
            self._val_max = float(x)

    @property
    def val_store(self):
        return str(self.val_comp)
    @val_store.setter
    def val_store(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = float(x)

    @property
    def val_disp(self):
        if False:
#        if self.is_locale_formatted and self.has_value:  # *localize* not avail in Python 3.9.
            result = locale.localize(self.val_comp, grouping=True)
        elif self.has_value:
            result = self.fmt_disp.format(self.val_comp)
        else:
            result = NOT_AVAIL
        return result
    @val_disp.setter
    def val_disp(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = float(locale.delocalize(x))

    @property
    def val_edit(self):
        if False:
#        if self.is_locale_formatted and self.has_value:  # *localize* not avail in Python 3.9.
            result = locale.localize(self.val_comp, grouping=True)
        elif self.has_value:
            result = self.fmt_edit.format(self.val_comp)
        else:
            result = NOT_AVAIL
        return result
    @val_edit.setter
    def val_edit(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = float(locale.delocalize(x))
            if self.val_min in BLANK_VALUES:
                pass
            elif self.val_comp < self.val_min:
                raise ErrorNumericRange(_('Value too small for {v0} item.').format(v0=self.tag))
            else:
                pass
            if self.val_max in BLANK_VALUES:
                pass
            elif self.val_comp > self.val_max:
                raise ErrorNumericRange(_('Value too large for {v0} item.').format(v0=self.tag))
            else:
                pass

REG_ITMS.add(RegItem('Float', _('Float'), ItmFloat, _('**Float** contains a floating-point number.')))


class ItmCurrency(ItmFloat):

    """This is a Tonto2 'dollar-valued' item.

    """    
    
    @property
    def val_disp(self):
        if self.is_locale_formatted and self.has_value:
            result = locale.currency(self.val_comp, grouping=True)
        elif self.has_value:
            result = self.fmt_disp.format(self.val_comp)
        else:
            result = NOT_AVAIL
        return result
    @val_disp.setter
    def val_disp(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = float(locale.delocalize(x))

    @property
    def val_edit(self):
        if self.has_value:
            result = self.fmt_edit.format(self.val_comp)
        else:
            result = NOT_AVAIL
        return result
    @val_edit.setter
    def val_edit(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = float(locale.delocalize(x))
            if self.val_min in BLANK_VALUES:
                pass
            elif self.val_comp < self.val_min:
                raise ErrorNumericRange(_('Value too small for {v0} item.').format(v0=self.tag))
            else:
                pass
            if self.val_max in BLANK_VALUES:
                pass
            elif self.val_comp > self.val_max:
                raise ErrorNumericRange(_('Value too large for {v0} item.').format(v0=self.tag))
            else:
                pass

REG_ITMS.add(RegItem('Currency', _('Currency'), ItmCurrency, _('**Currency** contains a floating-point number.')))


class ItmDateTime(Itm):

    """This is a Tonto2 date/time item.

    It has a "Now" button that inserts a time stamp into the edit box.

    """
        
    def __init__(self, tag=None):
        super().__init__(tag)
        self.fmt_disp = "%c"  # "%a %b %e %H:%M:%S %Y"  # locale.nl_langinfo(locale.D_T_FMT)
        self.fmt_store = '%Y-%m-%d %H:%M:%S.%f%z'
        return

    @property
    def val_store(self):
        if self.has_value:
            result = self.val_comp.strftime(self.fmt_store)
        else:
            result = NOT_AVAIL
        return result
    @val_store.setter
    def val_store(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            y = x.strip().replace('/', '-').replace('00:00 AM', '12:00 AM')
            try:
                self.val_comp = datetime.datetime.fromisoformat(y)
            except ValueError:
                self.val_comp = None
            if self.val_comp in BLANK_VALUES:
                try:
                    self.val_comp = dateparser.parse(x)
                except ValueError:
                    self.val_comp = None
            if self.val_comp in BLANK_VALUES:
                try:
                    y = x.strip().replace('-', SPACE).replace(':', '.')
                    self.val_comp = datetime.datetime.strptime(y, '%d %b %Y %H.%M.%S')
                except ValueError:
                    self.val_comp = None
            if self.val_comp in BLANK_VALUES:
                raise ValueError

    @property
    def val_disp(self):
        if self.has_value:
            result = self.val_comp.strftime(self.fmt_disp)
        else:
            result = NOT_AVAIL
        return result
    @val_disp.setter
    def val_disp(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = dateparser.parse(x.strip(), date_formats=[self.fmt_disp])

    @property
    def val_edit(self):
        if self.has_value:
            result = self.val_comp.isoformat(sep=SPACE, timespec='seconds')
        else:
            result = NOT_AVAIL
        return result
    @val_edit.setter
    def val_edit(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            try:
                self.val_comp = datetime.datetime.fromisoformat(x)
            except ValueError:
                self.val_comp = None
            if self.val_comp in BLANK_VALUES:
                self.val_comp = dateparser.parse(x)
    @property
    def val_sort(self):
        return self.val_store

    def set_now(self):
        self.val_comp = datetime.datetime.now()
        return self

    def conjure_form_entry_extras(self, wgt):
        wgt.add_wgt(q0.Q0PushButton(
            q0_visual=_('Now'),
            event_clicked=self.event_now,
            ), align='nw')   
        return self

    def event_now(self):
        new_time_stamp = ItmDateTime().set_now()
        self.edt.set_visual(new_time_stamp.val_edit)
        return

REG_ITMS.add(RegItem('DateTime', _('DateTime'), ItmDateTime, _('**DateTime** contains a calendar date and time of day.')))

    
class ItmDate(ItmDateTime):

    """This is a Tonto2 date item.

    It has a "Today" button that inserts a date stamp into the edit box.

    """
        
    def __init__(self, tag=None):
        super().__init__(tag)
        self.fmt_disp = "%x"  # "%m/%d/%y"  # locale.nl_langinfo(locale.D_FMT)
        self.fmt_store = '%Y/%m/%d'
        return
    
    @property
    def val_store(self):
        if self.has_value:
            result = self.val_comp.strftime(self.fmt_store)
        else:
            result = NOT_AVAIL
        return result
    @val_store.setter
    def val_store(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            y = x.strip().replace('/', '-')
            try:
                self.val_comp = datetime.date.fromisoformat(y)
            except ValueError:
                self.val_comp = None
            if self.val_comp in BLANK_VALUES:
                try:
                    self.val_comp = dateparser.parse(x).date()
                except ValueError:
                    self.val_comp = None
            if self.val_comp in BLANK_VALUES:
                raise ValueError

    @property
    def val_disp(self):
        if self.has_value:
            result = self.val_comp.strftime(self.fmt_disp)
        else:
            result = NOT_AVAIL
        return result
    @val_disp.setter
    def val_disp(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = datetime.datetime.strptime(x.strip(), self.fmt_disp).date()

    @property
    def val_edit(self):
        if self.has_value:
            result = self.val_comp.isoformat()
        else:
            result = NOT_AVAIL
        return result
    @val_edit.setter
    def val_edit(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = datetime.date.fromisoformat(x)

    def set_now(self):
        self.val_comp = datetime.date.today()
        return self

    def conjure_form_entry_extras(self, wgt):
        wgt.add_wgt(q0.Q0PushButton(
            q0_visual=_('Today'),
            event_clicked=self.event_now,
            ), align='nw')
        return self

    def event_now(self):
        new_time_stamp = ItmDate().set_now()
        self.edt.set_visual(new_time_stamp.val_edit)
        return

REG_ITMS.add(RegItem('Date', _('Date'), ItmDate, _('**Date** contains a calendar date.')))


class ItmTime(ItmDateTime):

    """This is a Tonto2 time item.

    It has a "Now" button that inserts a time stamp into the edit box.

    """
        
    def __init__(self, tag=None):
        super().__init__(tag)
        self.fmt_disp = "%X"  # %H:%M:%S"  # locale.nl_langinfo(locale.T_FMT)
        self.fmt_store = '%H:%M:%S%z'
        return
    
    @property
    def val_store(self):
        if self.has_value:
            result = self.val_comp.strftime(self.fmt_store)
        else:
            result = NOT_AVAIL
        return result
    @val_store.setter
    def val_store(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            y = x.strip()
            try:
                self.val_comp = datetime.time.fromisoformat(y)
            except ValueError:
                self.val_comp = None
            if self.val_comp in BLANK_VALUES:
                try:
                    self.val_comp = dateparser.parse(x).time()
                except ValueError:
                    self.val_comp = None
            if self.val_comp in BLANK_VALUES:
                raise ValueError

    @property
    def val_disp(self):
        if self.has_value:
            result = self.val_comp.strftime(self.fmt_disp)
        else:
            result = NOT_AVAIL
        return result
    @val_disp.setter
    def val_disp(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = datetime.datetime.strptime(x.strip(), self.fmt_disp).time()

    @property
    def val_edit(self):
        if self.has_value:
            result = self.val_comp.isoformat(timespec='seconds')
        else:
            result = NOT_AVAIL
        return result
    @val_edit.setter
    def val_edit(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            self.val_comp = datetime.time.fromisoformat(x)

    def set_now(self):
        self.val_comp = datetime.datetime.now().time()
        return self

    def conjure_form_entry_extras(self, wgt):
        wgt.add_wgt(q0.Q0PushButton(
            q0_visual=_('Now'),
            event_clicked=self.event_now,
            ), align='nw')
        return self

    def event_now(self):
        new_time_stamp = ItmTime().set_now()
        self.edt.set_visual(new_time_stamp.val_edit)
        return

REG_ITMS.add(RegItem('Time', _('Time'), ItmTime, _('**Time** contains hours:minutes:seconds.')))


class ItmTimeOffset(ItmText):

    """This is a Tonto2 time-offset item.

    It stores an ±HH:MM text value, but its computational value is
    integer minutes.

    """    
    
    @property
    def val_store(self):
        if self.has_value:
            minutes = self.val_comp
            is_positive = minutes >= ZERO
            if is_positive:
                sign = '+'
            else:
                minutes = -minutes
                sign = '-'
            (hours, minutes) = divmod(minutes, 60)
            result = f'{sign}{hours:02d}:{minutes:02d}'
        else:
            result = NOT_AVAIL
        return result
    @val_store.setter
    def val_store(self, x):
        if x in BLANK_VALUES:
            self.val_comp = NOT_AVAIL
        else:
            if x[:1] in ['+', '-']:
                sign = x[:1]
                x = x[1:]
            else:
                sign = NULL
            is_negative = sign in ['-']
            x = x.split(':')
            x.append('0')
            hours = int(x[ZERO])
            minutes = int(x[1])
            self.val_comp = hours * 60 + minutes
            if is_negative:
                self.val_comp = -self.val_comp

    @property
    def val_disp(self):
        result = self.val_store
        return result
    @val_disp.setter
    def val_disp(self, x):
        self.val_store = x

    @property
    def val_edit(self):
        result = self.val_store
        return result
    @val_edit.setter
    def val_edit(self, x):
        self.val_store = x

REG_ITMS.add(RegItem('Time Offset', _('Time Offset'), ItmTimeOffset, _('**Time Offset** holds the hours:minutes between events.')))


class ItmLocalFile(ItmText):

    """This is a Tonto2 filename item.

    It has a Search button that opens a file-dialog box.

    """    
    
    px_bombsight = 36
    name_filters = None
    
    @property
    def val_local(self):
        return self._val_local
    
    def conjure_form_entry_extras(self, wgt):
        spyglass = wgt.add_wgt(q0.Q0PushButton(
            q0_visual='\N{TELEPHONE RECORDER}',
            fixed_height=self.px_bombsight, fixed_width=self.px_bombsight,
            ), align='nw')
        spyglass.set_style_sheet(f'font-size: {self.px_bombsight}px')
        spyglass.set_tool_tip(_('Click to use file-search dialog.'))
        spyglass.connect_clicked(event_clicked=self.event_search)
        return self

    def event_search(self):
        dlg = q0.Q0FileDialog(
            q0_title=_('Local File'),
            q0_accept_mode='open',
            q0_view_mode='detail',
            q0_list_dir_mode='hidden',
            q0_options=['no native dialog'],
            name_filters=self.name_filters,
            default_suffix=None,
            directory=None,
            )
        old_file_name = self.edt.get_visual()
        if old_file_name in BLANK_VALUES:
            pass
        else:
            old_path = pathlib.Path(old_file_name)
            old_dir = strip_protocol_scheme(old_path.parent)
            old_fn = old_path.name
            dlg.set_directory(str(old_dir))
            dlg.set_selected_files([old_fn])
        new_file_names = dlg.get_selected_files()
        if new_file_names:
            new_path = pathlib.Path(new_file_names[ZERO])
            self.edt.set_visual(new_path.as_uri())
        return 

REG_ITMS.add(RegItem('Local File', _('Local File'), ItmLocalFile, _('''**Local File**
contains a Uniform Reference Identifier (URI) to a file on the local
machine.''')))


class ItmSoundFile(ItmLocalFile):

    """This is a Tonto2 sound-filename item.

    Not only does it come with a search button, it comes with a play
    button, too.

    """
    
    name_filters = ["*.wav"]

    def conjure_form_entry_extras(self, wgt):
        super().conjure_form_entry_extras(wgt)
        wgt.add_wgt(q0.Q0PushButton(
            q0_visual=_('Play'),
            event_clicked=self.event_play,
            ), align='nw')
        return self

    def event_play(self):
        file_name = self.edt.get_visual()
        if file_name in BLANK_VALUES:
            pass
        else:
            path = strip_protocol_scheme(file_name)
            tone = q0.Q0Sound(path)
            tone.play()
            while not tone.isFinished():
                COMMON['APP'].process_events()
        return

REG_ITMS.add(RegItem(
    'Sound File',
    _('Sound File'),
    ItmSoundFile,
    _('**Sound File** contains a  Uniform Reference Identifier (URI) to an audio file on the local machine.'),
    ))


class ItmURI(ItmText):

    """This is a Tonto2 URL item.

    It has both a drag-and-drop target and an open button.  The open
    button opens a new tab in the default browser for the URL.

    """
    
    px_bombsight = 36
    mime_types = {
        '_NETSCAPE_URL': (True, 'utf-8'),
        'text/x-moz-url': (True, 'utf-16'),
        'text/uri-list': (False, 'utf-8'),
        'text/plain': (False, 'utf-8'), 
        }

    def conjure_form_entry_extras(self, wgt):
        bombsight = wgt.add_wgt(q0.Q0PushButton(
            q0_visual='\N{POSITION INDICATOR}',
            fixed_height=self.px_bombsight, fixed_width=self.px_bombsight,
            ), align='nw')
        bombsight.set_style_sheet(f'font-size: {self.px_bombsight}px')
        bombsight.set_tool_tip(_('Drag from browser search bar or from link.  Drop here.'))
        bombsight.connect_drop(collection_mime_types=self.mime_types.keys(), event_drop=self.event_drag_and_drop)
        wgt.add_wgt(q0.Q0PushButton(
            q0_visual=_('Open'),
            event_clicked=self.event_open,
            ), align='nw')
        return self

    def event_open(self):
        link = self.edt.get_visual()  # self.val_comp
        if link in BLANK_VALUES:
            pass
        else:
            browser_open_tab(uri=link)
        return

    def event_drag_and_drop(self, event):
        debug = False
        allowable = self.mime_types.items()
        available = event.mimeData().formats()
        if debug:
            print(f'avail:  {available}')
        uri = None
        title = None
        for (mime, (has_title, encoding)) in allowable:
            if debug:
                print(f'allow:  {mime}')
            if mime in available:
                text = event.mimeData().data(mime).data().decode(encoding)
                lines = text.splitlines()
                if lines:
                    uri = lines.pop(ZERO)
                    if debug:
                        print(f'  uri:  {uri}')
                    if lines and has_title:
                        title = lines.pop(ZERO)
                        if debug:
                            print(f'title:  {title}')
                if debug:
                    pass
                else:
                    break
        if uri:
            self.edt.set_visual(uri)
        if title:
            tab_current_text = MAIN_WIN.tabs.tab_wgt.get_current_tab_visual()
            tab_current = MAIN_WIN.tabs.get(tab_current_text)
            if tab_current:
                rel = tab_current.rel
                if rel is None:
                    pass
                else:
                    itm = rel.pages.find(TAG_TITLE)
                    if itm is None:
                        pass
                    else:
                        itm.edt.set_visual(title)
                    itm = rel.pages.find(TAG_ARTICLE)
                    if itm is None:
                        pass
                    else:
                        itm.edt.set_visual(f'"{title}"')
                    itm = rel.pages.find(TAG__TRAVERSE_DATE)
                    if itm is None:
                        pass
                    else:
                        itm.val_comp = datetime.datetime.now()
                        itm.edt.set_visual(itm.val_disp)
        return

REG_ITMS.add(RegItem('URI', _('URI'), ItmURI, _('**URI** contains a  Uniform Reference Identifier (URI).')))


class ItmImg(ItmURI):

    """This is a Tonto2 image item.

    It is a URL but is viewed as an image.

    """
    
    @property
    def val_view(self):
        if self.val_disp in BLANK_VALUES:
            result = NULL
        else:
            result =  f'<img src="{self.val_disp}" />'
        return result

REG_ITMS.add(RegItem('Image', _('Image'), ItmImg, _('''**Image** contains a
Uniform Reference Identifier (URI).  Its visualization is the image
itself.''')))


class ItmQrCode(ItmText):

    """This is a Tonto2 Quick-Response (QR code) item.

    It is viewed as an image.  The image is created in a temporary
    file by the default *qrencode* utility.

    """
    
    @property
    def val_view(self):
        if self.val_disp in BLANK_VALUES:
            result = NULL
        else:
            img = generate_qr_image(self.val_disp)
            if img is None:
                result = self.val_disp
            else:
                result =  f'<img src="{img}" />'
        return result

REG_ITMS.add(RegItem('QR Code', _('QR Code'), ItmQrCode, _('''**QR Code** contains text.  Its visualization is a Quick-Response
Code (Minecraft Stamp) encoding of the text.''')))


class ItmUPCA(ItmText):

    """This is a Tonto2 UPC item.

    It is specially encoded to be viewed with a UPC font.

    """    
    
    @property
    def val_comp(self):
        return self._val_comp
    @val_comp.setter
    def val_comp(self, x):
        if x in BLANK_VALUES:
            self._val_comp = NOT_AVAIL
            self.has_value = False
        else:
            barcodes2.BarcodeUPCA().set_and_audit(x)  # Invite error.
            self._val_comp = x
            self.has_value = True

    @property
    def val_view(self):
        if self.val_disp in BLANK_VALUES:
            result = NULL
        else:
            result = f'<span style="font-size:48pt;">{barcodes2.BarcodeUPCA().set_and_audit(self.val_disp).get_markup()}</span>'
        return result

REG_ITMS.add(RegItem('UPCA', _('UPCA'), ItmUPCA, _('**UPCA** contains a Universal Product Code.  Its visualization is a bar code.')))


class ItmEAN13(ItmText):

    """This is a Tonto2 EAN item.

    It is specially encoded to be viewed with an EAN font.

    """    
    
    @property
    def val_comp(self):
        return self._val_comp
    @val_comp.setter
    def val_comp(self, x):
        if x in BLANK_VALUES:
            self._val_comp = NOT_AVAIL
            self.has_value = False
        else:
            barcodes2.BarcodeEAN13().set_and_audit(x)  # Invite error.
            self._val_comp = x
            self.has_value = True

    @property
    def val_view(self):
        if self.val_disp in BLANK_VALUES:
            result = NULL
        else:
            result =  f'<span style="font-size:48pt;">{barcodes2.EAN13().set_and_audit(self.val_disp).get_markup()}</span>'
        return result

REG_ITMS.add(RegItem('EAN13', _('EAN13'), ItmEAN13, _('**EAN13** contains a European Article Number.  Its visualization is a bar code.')))


class ItmCode39(ItmText):

    """This is a Tonto2 Code 3 of 9 item.

    It is specially encoded to be viewed with a code39 font.

    """    
    
    @property
    def val_comp(self):
        return self._val_comp
    @val_comp.setter
    def val_comp(self, x):
        if x in BLANK_VALUES:
            self._val_comp = NOT_AVAIL
            self.has_value = False
        else:
            barcodes2.Barcode39().set_and_audit(x)  # Invite error.
            self._val_comp = x
            self.has_value = True

    @property
    def val_view(self):
        if self.val_disp in BLANK_VALUES:
            result = NULL
        else:
            result =  f'<span style="font-size:21pt;">{barcodes2.Barcode39().set_and_audit(self.val_disp).get_markup()}</span>'
        return result

REG_ITMS.add(RegItem('Code39', _('Code39'), ItmCode39, _('''**Code39** contains "3 of 9" text.  Text is limited to uppercase ASCII, the
digits, SPACE, hyphen, period, dollar-sign, forward slash, plus, and
percent-sign.  Its visualization is a bar code.''')))


class ItmCode39X(ItmText):

    """This is a Tonto2 Code 3 of 9 extended item.

    It is specially encoded to be viewed with a code39x font.

    """    
    
    @property
    def val_comp(self):
        return self._val_comp
    @val_comp.setter
    def val_comp(self, x):
        if x in BLANK_VALUES:
            self._val_comp = NOT_AVAIL
            self.has_value = False
        else:
            barcodes2.Barcode39X().set_and_audit(x)  # Invite error.
            self._val_comp = x
            self.has_value = True

    @property
    def val_view(self):
        if self.val_disp in BLANK_VALUES:
            result = NULL
        else:
            result =  f'<span style="font-size:21pt;">{barcodes2.Barcode39X().set_and_audit(self.val_disp).get_markup()}</span>'
        return result

REG_ITMS.add(RegItem('Code39X', _('Code39X'), ItmCode39X, _('''**Code39X** contains "3 of 9" extended text.  Text is limited to
upper and lowercase ASCII, the digits, SPACE, and some punctuation.
Its visualization is a bar code.''')))


class ItmCode128(ItmText):

    """This is a Tonto2 Code 128 item.

    It is specially encoded to be viewed with a code128 font.

    """    
    
    @property
    def val_comp(self):
        return self._val_comp
    @val_comp.setter
    def val_comp(self, x):
        if x in BLANK_VALUES:
            self._val_comp = NOT_AVAIL
            self.has_value = False
        else:
            barcodes2.Barcode128().set_and_audit(x)  # Invite error.
            self._val_comp = x
            self.has_value = True

    @property
    def val_view(self):
        if self.val_disp in BLANK_VALUES:
            result = NULL
        else:
            result =  f'<span style="font-size:21pt;">{barcodes2.Barcode128().set_and_audit(self.val_disp).get_markup()}</span>'
        return result

REG_ITMS.add(RegItem('Code128', _('Code128'), ItmCode128, _('''**Code128** contains "code128" text.  Text is limited to the ASCII
character set.  Its visualization is a bar code.''')))


class ItmUID(ItmText):

    """This is a Tonto2 unique-id item.

    It's default value is 'guaranteed' to be unique according to
    RFC4122.

    """
        
    @property
    def val_comp(self):
        return self._val_comp
    @val_comp.setter
    def val_comp(self, x):
        if x in BLANK_VALUES:
            self._val_comp = str(uuid.uuid4())
            self.has_value = True
        else:
            self._val_comp = x
            self.has_value = True

REG_ITMS.add(RegItem('UID', _('UID'), ItmUID, _('''**UID** contains a "Unique Identifier."  It's a long string generated with enough randomness in it so that it is never going to come up again.  It may be used as a key when other data identifiers are not unique.''')))


ITM_CLASS_NAME = REG_ITMS.name_by_type()
ITM_NAME_CLASS = REG_ITMS.type_by_name()


class KeyValSer:

    """Key/Value serialization.

    This is initialized with a path and mode.  Like the *open*
    built-in, it is a context manager.

    The put method is good on instances opened in 'w' mode.  It
    requires a key and a value and stores both in the next record.

    The get method is good on instances opened in 'r' mode.  It
    requires the key and verifies it against the next record.

    """    
    
    recode = {}

    def  __init__(self, path, mode='r', is_version_required=True, asserted_versions=None):
        if asserted_versions:
            pass
        else:
            asserted_versions = [__version__]
        self.path = pathlib.Path(path).expanduser()
        self.is_read_only = mode in ['r', 'R']
        self.is_write_enabled = mode in ['w', 'W']
        assert self.is_read_only != self.is_write_enabled
        self.unit = open(path, mode)
        if is_version_required:
            if self.is_write_enabled:
                self.put('Tonto Version', __version__)
            else:
                version = self.get('Tonto Version')
                try:
                    assert version in asserted_versions
                except AssertionError:
                    print(_('''
"{v0}" was written at version "{v1}", 
but version "{v2}" is required to read it.
''').format(v0=self.path, v1=version, v2=asserted_versions))
                    raise
        return

    def close(self):
        self.unit.close()
        return self

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()
        return False

    def put(self, key, val):
        self.unit.write(f'{key}={val}\n')
        return self

    def get(self, key):
        line = self.unit.readline()[:-1]
        group = line.split('=', 1)
        key = self.recode.get(key, key)
        if key == group[ZERO]:
            pass
        else:
            raise Error(_('In "{v0}," expected "{v1}."  Received "{v2}."').format(v0=self.path, v1=key, v2=group[ZERO]))
        result = group[1]
        return result

    def put_int(self, key, val):
        self.put(key, str(val))
        return self

    def get_int(self, key):
        result = self.get(key)
        if result == NOT_AVAIL:
            pass
        else:
            result = int(result)
        return result

    def put_float(self, key, val):
        self.put(key, str(val))
        return self

    def get_float(self, key):
        result = self.get(key)
        if result == NOT_AVAIL:
            pass
        else:
            result = float(result)
        return result

    def put_bool(self, key, val):
        if val == NOT_AVAIL:
            text == NOT_AVAIL
        elif val:
            text = 'T'
        else:
            text = 'F'
        self.put(key, text)
        return self

    def get_bool(self, key):
        result = self.get(key)
        if result == NOT_AVAIL:
            pass
        else:
            result = result in ['T', 'True']
        return result

    def put_tuple(self, key, val):
        if val == NOT_AVAIL:
            text = NOT_AVAIL
        else:
            for elt in val:
                assert not ';' in elt
            text = ';'.join(val)
        self.put(key, text)
        return self

    def get_tuple(self, key):
        result = self.get(key)
        if result == NOT_AVAIL:
            pass
        else:
            result = result.split(';')
        return result

    def put_pgraph(self, key, val):
        collection = val.splitlines()
        self.put(key, SPACE.join(collection))
        return self

class Pages(list):

    """A list of lists of items.

    A relation owns an instance of this.

    Pages is the outside list.  Items on a page is the inside list.

    """

    def get_next_itm(self):
        for (ndx_page, page) in enumerate(self):
            for (ndx_itm, itm) in enumerate(page):
                yield (itm, ndx_page, ndx_itm)
        return

    def get_tag_collection(self, include_seps=False):
        result = []
        for (ndx_page, page) in enumerate(self):
            for (ndx_itm, itm) in enumerate(page):
                result.append(itm.tag)
            if include_seps:
                result.append(COLLECTION_SEP)
        if include_seps:
            result = result[:NA]  # Spike trailing sep.
        return result

    def conjure_itm_by_tag(self):
        result = {}
        for (itm, ndx_page, ndx_itm) in self.get_next_itm():
            result[itm.tag] = itm
        return result

    def conjure_tag_by_itm(self):
        result = {}
        for (itm, ndx_page, ndx_itm) in self.get_next_itm():
            result[itm] = itm.tag
        return result

    def find_tuple(self, tag):
        for result in self.get_next_itm():
            (itm, ndx_page, ndx_itm) = result
            if itm.tag == tag:
                break
        else:
            result = None
        return result

    def find(self, tag):
        itm_with_indexes = self.find_tuple(tag)
        if itm_with_indexes:
            (itm, ndx_page, ndx_itm) = itm_with_indexes
            result = itm
        else:
            result = None
        return result

    def save(self, key_val_ser, class_names=ITM_CLASS_NAME):
        count = ZERO
        for page in self:
            if page:
                count += 1
        key_val_ser.put_int('pages', count)
        for page in self:
            if page:
                key_val_ser.put_int('itms', len(page))
                for itm in page:
                    key_val_ser.put(' itm_type', class_names[type(itm)])
                    itm.save(key_val_ser)
        return self

    def load(self, key_val_ser):
        super().clear()
        page_count = key_val_ser.get_int('pages')
        ndx_page = ZERO
        while page_count:
            itm_count = key_val_ser.get_int('itms')
            ndx_itm = ZERO
            while itm_count:
                cls = ITM_NAME_CLASS[key_val_ser.get(' itm_type')]
                itm = cls()
                itm.load(key_val_ser)
                self.add(itm, ndx_page=ndx_page, ndx_itm=ndx_itm)
                itm_count -= 1
                ndx_itm += 1
            page_count -= 1
            ndx_page += 1
        return self

    def add(self, itm, ndx_page=None, ndx_itm=None):
        if self.find_tuple(itm.tag) is None:
            pass
        else:
            raise Error(_('"{v0}" already exists.').format(v0=name))
        if ndx_page is None:
            ndx_page = -1
        try:
            page = self[ndx_page:][ZERO]
        except IndexError:
            page = []
            self.insert(ndx_page, page)
        if ndx_itm is None:
            ndx_itm = len(page)
        page.insert(ndx_itm, itm)
        return self

    def deep_copy(self, old_pages):
        self.extend([page[:] for page in old_pages])
        return self

    def transform(self, new_itms, plan):
        page = []
        for tag in plan:
            if tag in [COLLECTION_SEP]:
                self.append(page)
                page = []
            else:
                page.append(new_itms[tag])
        self.append(page)
        return self

    def conjure_list(self, width=200):
        result = q0.Q0List(width=width)
        tags = self.get_tag_collection(include_seps=True)
        itms = self.conjure_itm_by_tag()
        for (pos, tag) in enumerate(tags):
            result.add_item(q0_visual=tag, pos=pos)
            if tag in [COLLECTION_SEP]:
                pass
            else:
                result.set_item_tool_tip(q0_visual=itms[tag].md_desc_long, pos=pos)
        return result

    def clear(self):
        super().clear()
        self.insert(ZERO, [])
        return self

    
class RecsStorage(list):

    """Repository of csv records.

    A relation owns an instance of this.

    """    
    
    def save(self, writer):
        for rec in self:
            d = {key:val for (key, val) in rec.items() if not key in BLANK_VALUES}
            writer.writerow(d) 
        return self

    def load(self, reader):
        self.clear()
        self.extend(reader)
        return self

    def transform(self, rel, old_tags, new_itms, plan):
        for (row, old_rec) in enumerate(self):
            new_rec = {}
            for new_tag in plan:
                if new_tag in [COLLECTION_SEP]:
                    pass
                else:
                    itm = new_itms[new_tag]
                    old_tag = old_tags[itm]
                    new_rec[new_tag] = old_rec.get(old_tag, itm.val_default)
            self[row] = new_rec
        return self

    def ndx_inc(self, ndx):
        result = ndx
        result += 1
        if result >= len(self):
            result = ZERO
            fault = True
        else:
            fault = False
        return (fault, result)

    def ndx_dec(self, ndx):
        result = ndx
        result -= 1
        if result < ZERO:
            result = len(self) - 1
            fault = True
        else:
            fault = False
        return (fault, result)


class Rel(TontoObj):

    """A Tonto2 relation.

    This is the parent of each of Tonto2's repertoire of relations.

    It provides serialization methods.

    One csv record at a time may be staged in a dictionary owned by
    self and keyed by field names.  The dictionary values are display
    values for the storage values in the record for the items on the
    relation's pages.  Each item on each page is touched while staging
    a record.  The setter for the storage value for each item is used
    and then the getter for the display value, so the item's
    formatting logic is obeyed.

    *icon* is not used ... yet.

    """    
    
    def __init__(self, tag=None):
        super().__init__(tag)
        self.rel_is_dirty = False
        self.rec_is_dirty = False
        self.icon = None
        self.pages = Pages().clear()
        self.display_tags = []
        self.recs = RecsStorage()
        self.ndx_rec = None
        return

    def save(self, key_val_ser, classes_itm=ITM_CLASS_NAME):
        super().save(key_val_ser)
        key_val_ser.put('  icon', self.icon)
        key_val_ser.put_tuple('display_tags', [tag for tag in self.display_tags if tag not in BLANK_VALUES])
        self.pages.save(key_val_ser, class_names=classes_itm)
        return self

    def save_recs(self, unit):
        writer = csv.DictWriter(unit, fieldnames=self.pages.get_tag_collection(), extrasaction='ignore')
        writer.writeheader()
        self.recs.save(writer)
        self.rel_is_dirty = False
        return self

    def load(self, key_val_ser, pages_factory=Pages):
        super().load(key_val_ser)
        self.icon = key_val_ser.get('  icon')
        self.display_tags = key_val_ser.get_tuple('display_tags')
        self.pages = pages_factory().load(key_val_ser)
        return self

    def load_recs(self, unit, fieldnames=None):
        reader = csv.DictReader(unit, fieldnames=fieldnames)
        self.recs = RecsStorage().load(reader)
        self.rel_is_dirty = False
        self.scan_recs_for_changes()
        return self

    def new_rec(self, ndx_rec):
        result = {}
        for (col, ndx_page, ndx_itm) in self.pages.get_next_itm():
            col.val_store = col.val_default
            self.destage_col(result, col)
        self.recs.insert(ndx_rec, result)
        self.rel_is_dirty = True
        self.scan_rec_for_changes(ndx_rec)
        return result
            
    def stage_col(self, rec, col):
        try:
            col.val_store = rec.get(col.tag, col.val_default)
        except ValueError:
            print(
                _('Relation {v0} rec[{v1}]["{v2}"]={v3}, but this is not valid.  Using default={v4}.').format(
                v0=self.tag,
                v1=self.ndx_rec,
                v2=col.tag,
                v3=repr(rec.get(col.tag)),
                v4=repr(col.val_default)),
                )
            col.val_store = col.val_default
        return self

    def stage_rec(self, ndx_rec):

        """Move one record at a time from storage to structure.

        This returns a dictionary of display values.

        """

        self.ndx_rec = ndx_rec
        result = {}
        try:
            rec = self.recs[self.ndx_rec]
        except IndexError:
            rec = self.new_rec(self.ndx_rec)
        for (col, ndx_page, ndx_itm) in self.pages.get_next_itm():
            self.stage_col(rec, col)
            result[col.tag] = col.val_disp            
        self.rec_is_dirty = False
        return result

    def destage_col(self, rec, col, is_dirty=True):
        if rec.get(col.tag) == col.val_store:
            pass
        else:
            rec[col.tag] = col.val_store
            self.rec_is_dirty = is_dirty
        return self

    def destage_rec(self, ndx_rec, update_timestamp=True):

        """Move one record at a time from structure to storage.

        This returns a dictionary of display values.

        """
        
        result = {}
        rec = self.recs[ndx_rec]
        for (col, ndx_page, ndx_itm) in self.pages.get_next_itm():  # Filter through tags that sideaffect _Update_Date.
            if col.tag in [TAG__ACCESSION_DATE, TAG__UPDATE_DATE, TAG__TRAVERSE_DATE]:
                pass
            else:
                self.destage_col(rec, col)
                result[col.tag] = col.val_disp            
        if update_timestamp:
            accession_date = self.pages.find(TAG__ACCESSION_DATE)
            update_date = self.pages.find(TAG__UPDATE_DATE)
            if accession_date and accession_date.val_store in BLANK_VALUES:
                accession_date.val_comp = datetime.datetime.now()
                self.rec_is_dirty = True
            if update_date and self.rec_is_dirty:
                update_date.val_comp = datetime.datetime.now()
        for (col, ndx_page, ndx_itm) in self.pages.get_next_itm():  # Filter through tags that don't sideaffect _Update_Date.
            if col.tag in [TAG__ACCESSION_DATE, TAG__UPDATE_DATE, TAG__TRAVERSE_DATE]:
                self.destage_col(rec, col)
                result[col.tag] = col.val_disp            
        if self.rec_is_dirty:
            self.rel_is_dirty = True
            self.scan_rec_for_changes(ndx_rec)
        self.rec_is_dirty = False
        return result

    def sort(self, tag, is_descending=False):

        """Sort self's records on the 'col' item.

        Each record is staged and the col's sort value is invoked.
        Old ordering is preserved for value collisions.

        """
        
        col = self.pages.find(tag)
        size = len(self.recs)
        collection = []
        for (ndx, rec) in enumerate(self.recs):
            self.stage_rec(ndx)
            if col is None:
                val = NULL
            else:
                val = col.val_sort
            if is_descending:
                uniq = size - ndx
            else:
                uniq = ndx
            key = f'{val}{uniq:09d}'
            collection.append([key.casefold(), rec])
        collection.sort()
        if is_descending:
            collection.reverse()
        self.recs = RecsStorage()
        for (key, rec) in collection:
            self.recs.append(rec)
        self.rel_is_dirty = True
        return self

    @property
    def pages(self):
        return self._pages
    @pages.setter
    def pages(self, x):
        self._pages = Pages().deep_copy(x)

    @property
    def display_tags(self):
        return self._display_tags
    @display_tags.setter
    def display_tags(self, x):
        if x is None:
            self._display_tags = self.pages.get_tag_collection()
        else:
            self._display_tags = x[:]
            
    @property
    def icon(self):
        return self._icon
    @icon.setter
    def icon(self, x):
        if x in BLANK_VALUES:
            self._icon = None
        else:
            self._icon = os.path.expandvars(pathlib.Path(x).expanduser())

    def transform(self, old_tags, plan):
        new_itms = self.pages.conjure_itm_by_tag()
        self.pages = Pages().transform(
            new_itms=new_itms,
            plan=plan,
            )
        if self.recs:
            self.recs.transform(
                rel=self,
                old_tags=old_tags,
                new_itms=new_itms,
                plan=plan,
                )
        old_display_tags = self.display_tags
        recode_tags = {}
        for new_tag in plan:
            if new_tag in [COLLECTION_SEP]:
                pass
            else:
                itm = new_itms[new_tag]
                old_tag = old_tags[itm]
                if old_tag in old_display_tags:
                    recode_tags[old_tag] = new_tag
        new_display_tags = []
        for old_tag in old_display_tags:
            if old_tag in recode_tags:
                new_display_tags.append(recode_tags[old_tag])
        self.display_tags = new_display_tags
        self.rel_is_dirty = True
        self.scan_recs_for_changes()
        return self

    def get_tags_displayed_and_hidden(self):
        all_tags = self.pages.get_tag_collection()
        displayed = self.display_tags[:]
        hidden = []
        for (ndx, tag) in enumerate(all_tags):
            if tag in displayed:
                pass
            else:
                hidden.append(tag)
        return (displayed, hidden)

    def view_as_text(self):

        """Return markup text for the staged record.  

        This uses the view value of the items.

        This method is overridden in Rel descendants.

        """
        
        result = []
        result.append('<table>')
        itm_by_tag = self.pages.conjure_itm_by_tag()
        for itm in itm_by_tag.values():
            result.append(f'<tr><td align=right><i>{itm.tag}:&nbsp;&nbsp;</i></td><td>{itm.val_view}</td></tr>')
        result.append('</table>')    
        return '\n'.join(result)

    def scan_rec_for_changes(self, rec):
        return self

    def scan_recs_for_changes(self):

        """This is a hook.

        RelCalendar hangs code here to rebuild Alarms.

        """
        
        for (ndx_rec, rec) in enumerate(self.recs):
            self.scan_rec_for_changes(ndx_rec)
        return self

    def conjure_pages(self):

        """This is a hook.

        Rel descendants use it to fill predefined pages.

        """
        
        return self
    

class RelUserDef(Rel):

    """Tonto2 User-Defined Relation.

    This has no predefined pages.

    """
    
    def __init__(self):
        super().__init__(tag=_('User'))
        self.md_desc_long = _('User Defined')
        return

REG_RELS.add(RegItem(
    'User Defined',
    _('User Defined'),
    RelUserDef,
    _('**User Defined** files may have any columns you wish.'),
    ))


class RelCalendar(Rel):

    """Tonto2 Calendar Relation.

    """
    
    def __init__(self):
        super().__init__(tag=_('Calendar'))
        self.md_desc_long = _('Personal Appointment Calendar and To-Do List')
        return

    def initialize_holidays(self):        
        self.load_recs(HOLIDAYS.splitlines())
        return

    def conjure_pages(self):
        page = ZERO
        if True:
            itm = ItmText(TAG_PROJECT)
            itm.md_desc_long = _('''Distinguishes appointments and to-do events by the **{v0}** they
belong to, if any.''').format(v0=TAG_PROJECT)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_TITLE)
            itm.md_desc_long = _('''Each event may have a **{v0}**.  This is what shows on the
calendar layout.  Brevity is essential.''').format(v0=TAG_TITLE)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG__HANDLE)
            itm.md_desc_long = _('''In addition to **{v0}**, a event may have a short **{v1}**.
Dependent events may refer this this.''').format(v0=TAG_TITLE, v1=TAG__HANDLE)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_PRIORITY)
            itm.md_desc_long = _('''**{v0}** is an indication of the relative importance of this
event.  It may be anything.  Events that represent "red-letter" days
should have **{v1}** zero so that they sort first on a given
day.  On the monthly calendar, the **{v2}** of a day
is the **{v3}** of the most important event.  The
**{v4}** comes from the least important event.''').format(
                v0=TAG_PRIORITY,
                v1=TAG_PRIORITY,
                v2=TAG_FOREGROUND_COLOR,
                v3=TAG_FOREGROUND_COLOR,
                v4=TAG_BACKGROUND_COLOR,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_STATUS)
            itm.md_desc_long = _('''**{v0}** may be *{v1}*,
but it could be anything.''').format(
                v0=TAG_STATUS,
                v1=tonto2_code_tables.TAB_BY_NAME['EVENT_STATUS'].codes,
                )
            itm.code_table = 'EVENT_STATUS'
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmLog(TAG_REMARKS)
            itm.md_desc_long = _('''**{v0}** is any markdown text.  The other **Calendar** items
cover "when" well enough.  Specify "who, what, where, why, and how
much" here.''').format(v0=TAG_REMARKS)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmCoded(TAG_FOREGROUND_COLOR)
            itm.code_table = 'COLORS'
            itm.md_desc_long = _('''When this task appears on the monthly calendar, set day of the
month digits to this **{v0}**.  Normally, this is reserved
for tasks that represent "red-letter" days.''').format(v0=TAG_FOREGROUND_COLOR)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmCoded(TAG_BACKGROUND_COLOR)
            itm.code_table = 'COLORS'
            itm.md_desc_long = _('''When this task appears on the monthly calendar, set the cell for
the day to this **{v0}**.''').format(v0=TAG_BACKGROUND_COLOR)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmUID(TAG_UNIQUE_ID)
            itm.md_desc_long = _('''**{v0}** is Unique Identifier (UID), if any, that may help spot duplicates.  When swapping records with other devices, a copy of the same record that was exported may be imported again later.  The UID is a durable item in each record that should be the same in both copies even though other items may have changed in both copies.  It will not be obvious which copy is authoritative, but identifying potential conflicts is the first step to resolving duplicates.''').format(v0=TAG_UNIQUE_ID)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmDateTime(TAG__START)
            itm.md_desc_long = _('''**{v0}** is the scheduled date and time.''').format(v0=TAG__START)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmFloat(TAG__DURATION)
            itm.md_desc_long = _('''The event takes **{v0}** hours.''').format(v0=TAG__DURATION)
            itm.val_default = 1
            itm.is_dd_mod_enabled = False 
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmInteger(TAG_ADVANCE_ALARM)
#            itm.val_default = ZERO  # Not a good idea.  Default should be no alarm, i.e. #N/A.
            itm.md_desc_long = _('''A pop-up alarm is scheduled **{v0}** 
minutes before **{v1}**.  There is no alarm if this is set to
NOT_AVAIL.  This is preparation time in minutes.  If **{v2}**
is positive, the alarm rings several minutes in advance of the scheduled
event.  To schedule a time-limit alarm during an event, set **{v3}**
to a negative value.''').format(v0=TAG_ADVANCE_ALARM, v1=TAG__START, v2=TAG_ADVANCE_ALARM, v3=TAG_ADVANCE_ALARM)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSoundFile(TAG_ALARM_SOUND)
            itm.md_desc_long = _('''The **{v0}** is a file path.''').format(v0=TAG_ALARM_SOUND)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmCoded(TAG_SPEAK_TITLE)
            itm.md_desc_long = _('''During an alarm, announce the event **{v0}**.''').format(v0=TAG_TITLE)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmInteger(TAG_REPEAT_INTERVAL)
            itm.md_desc_long = _('''The alarm repeats every **{v0}** seconds.''').format(v0=TAG_REPEAT_INTERVAL)
            itm.val_default = 8
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmInteger(TAG_REPEAT_LOOP)
            itm.md_desc_long = _('''The alarm repeats **{v0}** times.''').format(v0=TAG_REPEAT_LOOP)
            itm.val_default = 10
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmInteger(TAG_OFFSET)
            itm.md_desc_long = _('''**{v0}** causes the event to be rescheduled.  It is a number of days or monnths.
See **{v1}**.  If this is non-positive, then the event is non-recurring.''').format(v0=TAG_OFFSET, v1=TAG_IS_OFFSET_TYPE_DAYS)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmCoded(TAG_IS_OFFSET_TYPE_DAYS)
            itm.md_desc_long = _('''**{v0}** is *Yes*, if **{v1}** is a number of days.  If
**{v2}** is *No*, **{v3}** is a number of months.''').format(
                v0=TAG_IS_OFFSET_TYPE_DAYS,
                v1=TAG_OFFSET,
                v2=TAG_IS_OFFSET_TYPE_DAYS,
                v3=TAG_OFFSET,
                )
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmInteger(TAG_OFFSET_IN_MONTH)
            itm.md_desc_long = _('''**{v0}** goes with **{v1}**=*No*.  It may be
a day or a week number.  See **{v2}**.  It may be -1
to reschedule the event on the last day of the month or in the last
week.  If **{v3}** is not specified, the event is
rescheduled on the same day of the month as it was originally.''').format(
                v0=TAG_OFFSET_IN_MONTH,
                v1=TAG_IS_OFFSET_TYPE_DAYS,
                v2=TAG_IS_OFFSET_IN_MONTH_TYPE_DAYS,
                v3=TAG_OFFSET_IN_MONTH,
                )
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmCoded(TAG_IS_OFFSET_IN_MONTH_TYPE_DAYS)
            itm.md_desc_long = _('''**{v0}** is *Yes*, if **{v1}** is a
number of days.  If **{v2}** is *No*,
**{v3}** is a number of weeks, and event will be on the
same day of the week as **{v4}**.''').format(
                v0=TAG_IS_OFFSET_IN_MONTH_TYPE_DAYS,
                v1=TAG_OFFSET_IN_MONTH,
                v2=TAG_IS_OFFSET_IN_MONTH_TYPE_DAYS,
                v3=TAG_OFFSET_IN_MONTH, v4=TAG__START,
                )
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDate(TAG_STOP)
            itm.md_desc_long = _('''The task will not be rescheduled beyond the *Stop* date, if any.''')
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmDateTime(TAG__ACCESSION_DATE)
            itm.is_edit_enabled = False
            itm.md_desc_long = _('''**{v0}** cannot be changed manually because it
automatically keeps track of when the entry was made.''').format(v0=TAG__ACCESSION_DATE)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDateTime(TAG__UPDATE_DATE)
            itm.md_desc_long = _('''**{v0}** cannot be changed manually because it automatically
keeps track of when the entry was last changed.''').format(v0=TAG__UPDATE_DATE)
            itm.is_dd_mod_enabled = False
            itm.is_edit_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_KEYWORDS)
            itm.md_desc_long = _('''**{v0}** is a list of word forms that you want to remember this
entry by, so that you can search by them.  You may wish to separate
them with semicolons.''').format(v0=TAG_KEYWORDS)
            self.pages.add(itm, ndx_page=page)
        self.display_tags = [
            TAG_PROJECT,
            TAG__HANDLE,
            TAG_PRIORITY,
            TAG__START,
            ]
        return self

    def scan_rec_for_changes(self, ndx_rec):
        super().scan_rec_for_changes(ndx_rec)
        self.stage_rec(ndx_rec)
        alarm = Alarm(parent_rel=self).create_from_rec()
        COMMON['ALARMS'].schedule(alarm)
        return self

    def scan_recs_for_changes(self):
        COMMON['ALARMS'].clear()
        super().scan_recs_for_changes()
        return self
    
    def view_as_text(self):
        result = []
        itms = self.pages.conjure_itm_by_tag()
        val_disp = {}
        for (tag_en, tag) in [
                ('project', TAG_PROJECT),
                ('title', TAG_TITLE),
                ('handle', TAG__HANDLE),
                ('priority', TAG_PRIORITY),
                ('status', TAG_STATUS),
                ('remarks', TAG_REMARKS),
                ('foreground', TAG_FOREGROUND_COLOR),
                ('background', TAG_BACKGROUND_COLOR),
                ('time_start', TAG__START),
                ('duration_hrs', TAG__DURATION),
                ('advance_mins', TAG_ADVANCE_ALARM),
                ('audio', TAG_ALARM_SOUND),
                ('repeat_secs', TAG_REPEAT_INTERVAL),
                ('repeat_count', TAG_REPEAT_LOOP),
                ('ofs', TAG_OFFSET),
                ('ofs_in_mo', TAG_OFFSET_IN_MONTH),
                ('time_stop', TAG_STOP),
                ('accession_date', TAG__ACCESSION_DATE),
                ('update_date', TAG__UPDATE_DATE),
                ('keywords', TAG_KEYWORDS),
                ]:
            itm = itms.get(tag)
            if itm:
                val_disp[tag_en] = itms[tag].val_view
                del itms[tag]
            else:
                val_disp[tag_en] = NOT_AVAIL
        for (tag_en, tag) in [
                ('can_speak', TAG_SPEAK_TITLE),
                ('is_ofs_days', TAG_IS_OFFSET_TYPE_DAYS),
                ('is_ofs_in_mo_days', TAG_IS_OFFSET_IN_MONTH_TYPE_DAYS),
                ]:
            itm = itms.get(tag)
            if itm:
                val_disp[tag_en] = itms[tag].val_comp in ['Y']
                del itms[tag]
            else:
                val_disp[tag_en] = False
        if val_disp["foreground"] in BLANK_VALUES:
            val_disp["foreground"] = 'black'
        result.append(f'<font color={val_disp["foreground"]}><big><b>{val_disp["title"]}</b></big></font>')
        result.append('<table>')
        result.append(_('<tr><td align=right><i>Project:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["project"]))
        result.append(_('<tr><td align=right><i>Handle:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["handle"]))
        result.append(_('<tr><td align=right><i>Priority:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["priority"]))
        result.append(_('<tr><td align=right><i>Status:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["status"]))
        result.append(_('<tr><td align=right><i>Time_Start:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["time_start"]))
        result.append(_('<tr><td align=right><i>Duration (hours):&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(
            v0=val_disp["duration_hrs"],
            ))
        result.append(_('<tr><td align=right><i>Advance Alarm (minutes):&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(
            v0=val_disp["advance_mins"],
            ))
        result.append(_('<tr><td align=right><i>Alarm Sound:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["audio"]))
        result.append(_('<tr><td align=right><i>Can Speak Title:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(
            v0=val_disp["can_speak"],
            ))
        result.append(_('<tr><td align=right><i>Repeat (seconds):&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(
            v0=val_disp["repeat_secs"],
            ))
        result.append(_('<tr><td align=right><i>Repetitions:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["repeat_count"]))
        result.append(_('<tr><td align=right><i>Keywords:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["keywords"]))
        result.append('</table>')
        result.append(MARKDN_LINE_END)
        result.append(MARKDN_LINE_END)
        result.append(f'{val_disp["remarks"]}{MARKDN_LINE_END}')
        result.append(MARKDN_LINE_END)
        if val_disp["ofs"] in BLANK_VALUES:
            pass
        else:
            result.append(_('Repeat every'))
            if val_disp["is_ofs_days"]:
                if val_disp["ofs"] == '1':
                    result.append(_('day'))
                else:
                    result.append(_('{v0} days').format(v0=val_disp["ofs"]))
            else:
                if val_disp["ofs"] == '1':
                    result.append(_('month'))
                else:
                    result.append(_('{v0} months').format(v0=val_disp["ofs"]))
                if val_disp["ofs_in_mo"] in BLANK_VALUES:
                    pass
                else:
                    if val_disp["is_ofs_in_mo_days"]:
                        result.append(_('on day {v0} of the month').format(v0=val_disp["ofs_in_mo"]))
                    else:
                        result.append(_('in week {v0} of the month').format(v0=val_disp["ofs_in_mo"]))
            if val_disp["time_stop"] in BLANK_VALUES:
                result.append(_('forever.'))
            else:
                result.append(_('until {v0}.').format(v0=val_disp["time_stop"]))
            alarm = Alarm(parent_rel=self).create_from_rec()
            alarm.gen_time()
            itm_alert = ItmDateTime()
            itm_alert.val_comp = alarm.time_next_alert
            result.append(_('Next occurrence {v0}.{v1}').format(v0=itm_alert.val_view, v1=MARKDN_LINE_END))
            result.append(MARKDN_LINE_END)
        result.append('<font size=-1><tt><table>')
        result.append(_('<tr><td align=right><i>Created:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["accession_date"]))
        result.append(_('<tr><td align=right><i>Updated:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["update_date"]))
        result.append('</table></tt></font>')
        result.append(MARKDN_LINE_END)
        result.append('<table>')
        for itm in itms.values():
            result.append(f'<tr><td align=right><i>{itm.tag}:&nbsp;&nbsp;</i></td><td>{itm.val_view}</td></tr>')
        result.append('</table>')    
        return '\n'.join(result)
    
REG_RELS.add(RegItem(
    'Calendar',
    _('Calendar'),
    RelCalendar,
    ('**Calendar** is an appointments and to-do list.'),
    ))


class RelPasswords(Rel):

    """Tonto2 Passwords Relation.
    
    """
    
    def __init__(self):
        super().__init__(tag=_('Passwords'))
        self.md_desc_long = _('Repository of Passwords and User IDs Used in Other Applications')
        return

    def conjure_pages(self):
        page = ZERO
        if True:
            itm = ItmText(TAG_VENDOR)
            itm.md_desc_long = _('''**{v0}** is the manufacturer, publisher or provider of a
*Service* that demands a password.''').format(v0=TAG_VENDOR)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_SERVICE)
            itm.md_desc_long = _('''**{v0}** is the segment of a **{v1}**\'s product that demands
the following **{v2}**. For example, and Internet Service Provider
(ISP) may require separate passwords for eMail and for FTP.''').format(v0=TAG_SERVICE, v1=TAG_VENDOR, v2=TAG_PASSWORD)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmURI(TAG_WEB)
            itm.md_desc_long = _('''**{v0}** is the URI of the **{v1}**\'s Account-Maintenance Web
page (if any) where you would go to change your **User ID**,
**{v2}** or **{v3}**.''').format(v0=TAG_WEB, v1=TAG_VENDOR, v2=TAG_PASSWORD, v3=TAG_ACCOUNT)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmURI(TAG_EMAIL)
            itm.md_desc_long = _('''**{v0}** is the electronic mail address (if any) where you expect
to receive correspondence about your **User ID** or **{v1}**.  Many
people use several addresses with different **{v2}**s.  When one of
your **{v3}** addresses changes, you can then find **{v4}**s you
need to notify.  When you receive eMail from an unexpected source, you
can hopefully trace it to the **{v5}** who leaked the address.''').format(
                v0=TAG_EMAIL,
                v1=TAG_ACCOUNT,
                v2=TAG_VENDOR,
                v3=TAG_EMAIL,
                v4=TAG_VENDOR,
                v5=TAG_VENDOR,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_USER_ID)
            itm.md_desc_long = _('''**{v0}** is your identity while using the **{v1}**.  The
**{v2}** combines your **{v3}** with your **{v4}** to verify
that you are who you say you are before allowing you to use the
**{v5}**.''').format(v0=TAG_USER_ID, v1=TAG_SERVICE, v2=TAG_VENDOR, v3=TAG_USER_ID, v4=TAG_PASSWORD, v5=TAG_SERVICE)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_PASSWORD_TYPE)
            itm.md_desc_long = _('''**{v0}** tells how to use the following **{v1}**.
Usually, it is *{v2}*, but it
could be anything.''').format(v0=TAG_PASSWORD_TYPE, v1=TAG_PASSWORD, v2=tonto2_code_tables.TAB_BY_NAME['PASSD_TYPE'].codes)
            itm.code_table = 'PASSWD_TYPE'
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_PASSWORD)
            itm.md_desc_long = _('''**{v0}** is a secret code or pass phrase demanded by the
**{v1}**.  Here it is stored in all its plaintext, unhashed glory
so you can read it easily in case you forget it.  Further, you don't
have to remember a hash code and provide that to do so.  Obviously
this file needs to be kept away from prying eyes.  Your operating
environment may provide the means to protect this file from
unauthorized access or even to encrypt it, but these techniques are
far beyond the scope of *Tonto2*.  Consider saving this file on
removable media and storing it in a safe place.''').format(v0=TAG_PASSWORD, v1=TAG_SERVICE)
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmText(TAG_ACCOUNT)
            itm.md_desc_long = _('''**{v0}** is the identity of your client (if any).  The
**{v1}** bills the **{v2}** for his service.  Usually, though,
you and the client are the same, and you get the bill directly.  In
this case, your **{v3}** is good enough, and you don't have to
provide a separate **{v4}** Number.''').format(v0=TAG_ACCOUNT, v1=TAG_VENDOR, v2=TAG_ACCOUNT, v3=TAG_USER_ID, v4=TAG_ACCOUNT)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_PROJECT_TYPE)
            itm.md_desc_long = _('''**{v0}** tells how to use the following **{v1}** ID.
Usually, a **{v2}** is a refinement of **{v3}**, but it could be
called anything.''').format(v0=TAG_PROJECT_TYPE, v1=TAG_PROJECT, v2=TAG_PROJECT, v3=TAG_ACCOUNT)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_PROJECT)
            itm.md_desc_long = _('''**{v0}** is any subdivision of **{v1}** Number.  Perhaps you
are working on multiple **{v2}**s for a client and billing him for
the time you spend online.  Perhaps he wants his Internet bill
itemized by **{v3}**.''').format(v0=TAG_PROJECT, v1=TAG_ACCOUNT, v2=TAG_PROJECT, v3=TAG_PROJECT)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_CHALLENGE)
            itm.md_desc_long = _('''In the days before two-factor authentication (2FA), it was
customary to challenge a client to provide additional information to
confirm identity.  This often took the form of a question that only
the client could answer, such as *What is your mother's maiden name?
What is your cat\'s birthday?  What is your favorite color?* The login
scheme was constrained by the client's pre-arranged choice of a
**{v0}** question, which he provided during registration with a
**{v1}** and which can be recorded here.  Alternatively, this item
may record the type of any other piece of identifying information
beside **{v2}**, **{v3}**, **{v4}**, and **{v5}** that a
login scheme may require.''').format(v0=TAG_CHALLENGE, v1=TAG_VENDOR, v2=TAG_USER_ID, v3=TAG_PASSWORD, v4=TAG_ACCOUNT, v5=TAG_PROJECT)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_RESPONSE)
            itm.md_desc_long = _('''**{v0}** is the pre-arranged, correct answer to the
**{v1}** question or any other additional piece of identifying
information that a login scheme may require beyond **{v2}**,
**{v3}**, **{v4}**, or **{v5}**.''').format(
                v0=TAG_RESPONSE,
                v1=TAG_CHALLENGE,
                v2=TAG_USER_ID,
                v3=TAG_PASSWORD,
                v4=TAG_ACCOUNT,
                v5=TAG_PROJECT,
                )
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmDateTime(TAG__ACCESSION_DATE)
            itm.md_desc_long = _('''**{v0}** cannot be changed manually because it
automatically keeps track of when the entry was made.''').format(v0=TAG__ACCESSION_DATE)
            itm.is_dd_mod_enabled = False
            itm.is_edit_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDateTime(TAG__UPDATE_DATE)
            itm.md_desc_long = _('''**{v0}** cannot be changed manually because it automatically
keeps track of when the entry was last changed.''').format(v0=TAG__UPDATE_DATE)
            itm.is_dd_mod_enabled = False
            itm.is_edit_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDate(TAG_EXPIRATION_DATE)
            itm.md_desc_long = _('''**Expiration Date**, if any, keeps track of when the **{v0}**
must be renewed.''').format(v0=TAG_PASSWORD)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_ACCOUNT_STATUS)
            itm.md_desc_long = _('''**Account Status** may be *{v0}*
but it could be anything.''').format(v0=tonto2_code_tables.TAB_BY_NAME['ACCT_STATUS'].codes)
            itm.code_table = 'ACCT_STATUS'
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_KEYWORDS)
            itm.md_desc_long = _('''**{v0}** is a list of word forms that you want to remember this
entry by, so that you can search by them.  You may wish to separate
them with semicolons.''').format(v0=TAG_KEYWORDS)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmLog(TAG_REMARKS)
            itm.md_desc_long = _('''**{v0}** is any free-form text that applies to the **{v1}**,
**{v2}**, or **{v3}**.''').format(v0=TAG_REMARKS, v1=TAG_USER_ID, v2=TAG_PASSWORD, v3=TAG_ACCOUNT)
            self.pages.add(itm, ndx_page=page)
        self.display_tags = [
            TAG_VENDOR,
            TAG_SERVICE,
            TAG_USER_ID,
            ]
        return self

REG_RELS.add(RegItem(
    'Passwords', 
    _('Passwords'),
    RelPasswords,
    _('**Passwords** is a repository of passwords and user IDs used in other applications.'),
    ))


class Rel3x5Cards(Rel):

    """Tonto2 3x5 Note-Card Relation.

    """
        
    def __init__(self):
        super().__init__(tag=_('3x5Cards'))
        self.md_desc_long = _('3x5 Note-Card File')
        return

    def conjure_pages(self):
        page = ZERO
        if True:
            itm = ItmText(TAG_CATEGORY)
            itm.md_desc_long = _('''Each card in the list belongs in a **{v0}**, but **{v1}**
may be anything.''').format(v0=TAG_CATEGORY, v1=TAG_CATEGORY)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_TITLE)
            itm.md_desc_long = _('''Each card may have a **{v0}**.''').format(v0=TAG_TITLE)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmURI(TAG__URI)
            itm.md_desc_long = _('''A card may have a Uniform Reference Identifier (URI) for a
World-Wide Web page, if any, that the card describes or that is the
authority for the card.''')
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDateTime(TAG__TRAVERSE_DATE)
            itm.md_desc_long = _('''The **{v0}** cannot be changed manually.  Instead, it is
updated automatically whenever a traversal of the **{v1}** link is
made.''').format(v0=TAG__TRAVERSE_DATE, v1=TAG__URI)
            itm.is_dd_mod_enabled = False
            itm.is_edit_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmLog(TAG_REMARKS)
            itm.md_desc_long = _('''**{v0}** is any free-form text.''').format(v0=TAG_REMARKS)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDateTime(TAG__ACCESSION_DATE)
            itm.md_desc_long = _('''**{v0}** cannot be changed manually because it
automatically keeps track of when the entry was made.''').format(v0=TAG__ACCESSION_DATE)
            itm.is_dd_mod_enabled = False
            itm.is_edit_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDateTime(TAG__UPDATE_DATE)
            itm.md_desc_long = _('''**{v0}** cannot be changed manually because it automatically
keeps track of when the entry was last changed.''').format(v0=TAG__UPDATE_DATE)
            itm.is_dd_mod_enabled = False
            itm.is_edit_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_KEYWORDS)
            itm.md_desc_long = _('''**{v0}** is a list of word forms that you want to remember this
entry by, so that you can search by them.  You may wish to separate
them with semicolons.''').format(v0=TAG_KEYWORDS)
            self.pages.add(itm, ndx_page=page)
        self.display_tags = [
            TAG_CATEGORY,
            TAG__UPDATE_DATE,
            TAG_TITLE,
            ]
        return self

    def view_as_text(self):
        result = []
        itms = self.pages.conjure_itm_by_tag()
        val_disp = {}
        for (tag_en, tag) in [
                ('title', TAG_TITLE),
                ('category', TAG_CATEGORY),
                ('uri', TAG__URI),
                ('keywords', TAG_KEYWORDS),
                ('remarks', TAG_REMARKS),
                ('accession_date', TAG__ACCESSION_DATE),
                ('update_date', TAG__UPDATE_DATE),
                ('traversed_date', TAG__TRAVERSE_DATE),
                ]:
            itm = itms.get(tag)
            if itm:
                val_disp[tag_en] = itms[tag].val_view
                del itms[tag]
            else:
                val_disp[tag_en] = NOT_AVAIL
        result.append(f'<big><b>{val_disp["title"]}</b></big>')
        result.append('<table>')
        result.append(_('<tr><td align=right><i>Category:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["category"]))
        result.append(_('''<tr><td align=right><i>URI:&nbsp;&nbsp;</i></td>
<td><a href="{v0}">{v1}</a></td></tr>
''').format(v0=val_disp["uri"], v1=val_disp["uri"]))
        result.append(_('<tr><td align=right><i>Keywords:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["keywords"]))
        result.append('</table>')
        result.append(MARKDN_LINE_END)
        result.append(MARKDN_LINE_END)
        result.append(f'{val_disp["remarks"]}')
        result.append(MARKDN_LINE_END)
        result.append('<font size=-1><tt><table>')
        result.append(_('<tr><td align=right><i>Created:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["accession_date"]))
        result.append(_('<tr><td align=right><i>Updated:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["update_date"]))
        result.append(_('<tr><td align=right><i>Traversed:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val_disp["traversed_date"]))
        result.append('</table></tt></font>')
        result.append(MARKDN_LINE_END)
        result.append('<table>')
        for itm in itms.values():
            result.append(f'<tr><td align=right><i>{itm.tag}:&nbsp;&nbsp;</i></td><td>{itm.val_view}</td></tr>')
        result.append('</table>')    
        return '\n'.join(result)
    
REG_RELS.add(RegItem(
    '3x5Cards',
    _('3x5Cards'),
    Rel3x5Cards,
    _('''**A *3x5 Note-Card File* emulates a shoebox full of notes scribbled
on individual scraps of paper.  It is a list of similar records.  Each
note may have a Uniform Resource Identifier (URI) and serve as a
browser bookmark or an HTML favorite.'''), 
))


class RelAddressList(Rel):

    """Tonto2 Address-List Relation.

    """    
    
    def __init__(self):
        super().__init__(tag=_('Addresses'))
        self.md_desc_long = _('Address and Phone List')
        return

    def conjure_pages(self):
        page = ZERO
        if True:
            itm = ItmSelected(TAG_LISTING_TYPE)
            itm.md_desc_long = _('''**{v0}** tells how to use the following address.''').format(v0=TAG_LISTING_TYPE)
            itm.code_table = 'LISTING_TYPE'
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_GREETING)
            itm.md_desc_long = _('''**{v0}** is the polite title by which a person is addressed
(after the word *Dear*) within a letter — formally *Mr.* or *Ms.* and
his **{v1}** — informally his **{v2}** or nickname only.
When writing to an unknown person within a **{v3}**, it may be
*Sirs*, *Sir*, or *Madam*. This will be useful if you export your
address list to a word processor for generating form letters;
otherwise, you may leave it blank.''').format(v0=TAG_GREETING, v1=TAG_LAST_NAME, v2=TAG_FIRST_NAME, v3=TAG_COMPANY)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_POLITE_MODE)
            itm.md_desc_long = _('''**{v0}** is the method of polite address written before the
person\'s full name on an envelope.''').format(v0=TAG_POLITE_MODE)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_FIRST_NAME)
            itm.md_desc_long = _('''**{v0}** is all a person's names except his surname. You may
include first and middle, first and middle initial, or first only.
Families are a special case.  **{v1}** may be a couple like
*Dick and Jane*. On the other hand, **{v2}** may be just the
head of household.  Then you can append *Family* to the **{v3}**.''').format(
                v0=TAG_FIRST_NAME,
                v1=TAG_FIRST_NAME,
                v2=TAG_FIRST_NAME,
                v3=TAG_LAST_NAME,
                )
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_LAST_NAME)
            itm.md_desc_long = _('''**{v0}** is a person\'s surname.  When you sort the list, you
may wish to use this as a key along with **{v1}**.''').format(v0=TAG_LAST_NAME, v1=TAG_COMPANY)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_TITLE)
            itm.md_desc_long = _('''**{v0}** may be a professional degree such as *MD*, but it is
commonly the name of the position the person holds within a
**{v1}**.  Try to include it when writing to a **{v2}** so your
mail will be directed appropriately even if the person no longer works
there.''').format(v0=TAG_TITLE, v1=TAG_COMPANY, v2=TAG_COMPANY)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmText(TAG_COMPANY)
            itm.md_desc_long = _('''**{v0}** is the name of the business where the person works.
Try to include it when writing to the person at his office.  When
writing to an unknown person at a **{v1}**, omit the person\'s
names but include his **{v2}** if possible.  When writing to a person
at home, omit the **{v3}**.''').format(v0=TAG_COMPANY, v1=TAG_COMPANY, v2=TAG_TITLE, v3=TAG_COMPANY)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_DEPT_MAIL_STOP)
            itm.md_desc_long = _('''**{v0}** is required by organizations large enough to
occupy several buildings within a campus.  Usually it is a building
and room number.''').format(v0=TAG_DEPT_MAIL_STOP)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_LOCUS)
            itm.md_desc_long = _('''**{v0}** may be an additional organizational identifier
such as the name of a university when the name of the department where
the person works occupies the **{v1}** slot.''').format(v0=TAG_LOCUS, v1=TAG_COMPANY)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_STREET)
            itm.md_desc_long = _('''**{v0}** is the last line of the address before **{v1}**.
According to postal regulation and custom, the mailman is required to
look only one line above the **{v2}** and no higher.  Any lines above
that are purely decorative so far as the Post Office is concerned, and
interpretation of such extraneous routing information is up to clerks
and secretaries within the destination organization, not the postal
service.''').format(v0=TAG_STREET, v1=TAG_CITY, v2=TAG_CITY)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_CITY)
            itm.md_desc_long = _('''**{v0}** is the name of the destination Post Office.''').format(v0=TAG_CITY)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_STATE)
            itm.md_desc_long = _('''**{v0}** is the postal-service approved, two-character state code.
There are approved codes for United States possessions and
protectorates and Canadian provinces and territories.  Other countries
have their own district codes that may or may not be two
characters.''').format(v0=TAG_STATE)
            itm.is_dd_mod_enabled = False
            itm.code_table = 'STATES'
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_ZIP)
            itm.md_desc_long = _('''**{v0}** is a postal-service routing code.  In the United States
this may be five or nine digits or more.  In Canada it is two groups
of three alphanumeric characters.  Other countries have their own
schemes.  When printing mail, you may wish to sort on this key.''').format(v0=TAG_ZIP)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_COUNTRY)
            itm.md_desc_long = _('''**{v0}** is the destination nation.  It is usually left blank on
domestic mail.''').format(v0=TAG_COUNTRY)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmFloat(TAG_LATITUDE)
            itm.md_desc_long = _('''**{v0}** is in decimal degrees, if known.''').format(v0=TAG_LATITUDE)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmFloat(TAG_LONGITUDE)
            itm.md_desc_long = _('''**{v0}** is in decimal degrees, if known.''').format(v0=TAG_LONGITUDE)
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmSelected(TAG_PHONE_TYPE_1)
            itm.md_desc_long = _('''**{v0}** tells how to use the following **{v1}** number.
Usually, it is *{v2}* depending
on what type of device it connects with and whether it is for personal
or business use, but it could be anything.''').format(
                v0=TAG_PHONE_TYPE_1,
                v1=TAG_PHONE_1,
                v2=tonto2_code_tables.TAB_BY_NAME['PHONE_TYPE'].codes,
                )
            itm.is_dd_mod_enabled = False
            itm.code_table = 'PHONE_TYPE'
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_PHONE_1)
            itm.md_desc_long = _('''**{v0}** is the number to dial.  It may be any length and may
include hyphens and parentheses for readability.  It should include
leading long-distance and foreign access codes and trailing PBX
extensions.''').format(v0=TAG_PHONE_1)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_PHONE_TYPE_2)
            itm.md_desc_long = _('''**{v0}** tells how to use the following **{v1}** number.
Usually, it is *{v2}* depending
on what type of device it connects with and whether it is for personal
or business use, but it could be anything.''').format(
                v0=TAG_PHONE_TYPE_2,
                v1=TAG_PHONE_2,
                v2=tonto2_code_tables.TAB_BY_NAME['PHONE_TYPE'].codes,
                )
            itm.is_dd_mod_enabled = False
            itm.code_table = 'PHONE_TYPE'
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_PHONE_2)
            itm.md_desc_long = _('''**{v0}** is the number to dial.  It may be any length and may
include hyphens and parentheses for readability.  It should include
leading long-distance and foreign access codes and trailing PBX
extensions.''').format(v0=TAG_PHONE_2)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_PHONE_TYPE_3)
            itm.md_desc_long = _('''**{v0}** tells how to use the following **{v1}** number.
Usually, it is *{v2}* depending
on what type of device it connects with and whether it is for personal
or business use, but it could be anything.''').format(
                v0=TAG_PHONE_TYPE_3,
                v1=TAG_PHONE_3,
                v2=tonto2_code_tables.TAB_BY_NAME['PHONE_TYPE'].codes,
                )
            itm.is_dd_mod_enabled = False
            itm.code_table = 'PHONE_TYPE'
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_PHONE_3)
            itm.md_desc_long = _('''**{v0}** is the number to dial.  It may be any length and may
include hyphens and parentheses for readability.  It should include
leading long-distance and foreign access codes and trailing PBX
extensions.''').format(v0=TAG_PHONE_3)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_PHONE_TYPE_4)
            itm.md_desc_long = _('''**{v0}** tells how to use the following **{v1}** number.
Usually, it is *{v2}* depending
on what type of device it connects with and whether it is for personal
or business use, but it could be anything.''').format(
                v0=TAG_PHONE_TYPE_4,
                v1=TAG_PHONE_4,
                v2=tonto2_code_tables.TAB_BY_NAME['PHONE_TYPE'].codes,
                )
            itm.is_dd_mod_enabled = False
            itm.code_table = 'PHONE_TYPE'
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_PHONE_4)
            itm.md_desc_long = _('''**{v0}** is the number to dial.  It may be any length and may
include hyphens and parentheses for readability.  It should include
leading long-distance and foreign access codes and trailing PBX
extensions.''').format(v0=TAG_PHONE_4)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmURI(TAG_EMAIL)
            itm.md_desc_long = _('''**{v0}** is the URI of the person\'s electronic mail address
including the *mailto://* protocol scheme, if he has one.  ''').format(v0=TAG_EMAIL)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmURI(TAG__URI)
            itm.md_desc_long = _('''**{v0}** is the  Uniform Reference Identifier (URI) including the *http://*
protocol scheme of the person's World-Wide Web site, if any.''').format(v0=TAG__URI)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmUID(TAG_UNIQUE_ID)
            itm.md_desc_long = _('''**{v0}** is Unique Identifier (UID), if any, that may help spot duplicates.  When swapping records with other devices, a copy of the same record that was exported may be imported again later.  The UID is a durable item in each record that should be the same in both copies even though other items may have changed in both copies.  It will not be obvious which copy is authoritative, but identifying potential conflicts is the first step to resolving duplicates.''').format(v0=TAG_UNIQUE_ID)
            itm.is_dd_mod_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDateTime(TAG__ACCESSION_DATE)
            itm.md_desc_long = _('''**{v0}** cannot be changed manually because it
automatically keeps track of when the entry was made.''').format(v0=TAG__ACCESSION_DATE)
            itm.is_dd_mod_enabled = False
            itm.is_edit_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDateTime(TAG__UPDATE_DATE)
            itm.md_desc_long = _('''**{v0}** cannot be changed manually because it automatically
keeps track of when the entry was last changed.''').format(v0=TAG__UPDATE_DATE)
            itm.is_dd_mod_enabled = False
            itm.is_edit_enabled = False
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_KEYWORDS)
            itm.md_desc_long = _('''**{v0}** is a list of word forms that you want to remember this
entry by, so that you can search by them.  You may wish to separate
them with semicolons.''').format(v0=TAG_KEYWORDS)
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmLog(TAG_REMARKS)
            itm.md_desc_long = _('''**{v0}** is any free-form text that applies to the address.''').format(v0=TAG_REMARKS)
            self.pages.add(itm, ndx_page=page)
        self.display_tags = [
            TAG_LAST_NAME,
            TAG_FIRST_NAME,
            TAG_COMPANY,
            TAG_PHONE_1,
            ]
        return self

    disp_tags = {
        'listing_type': TAG_LISTING_TYPE,  # √
        'greeting': TAG_GREETING,  # √
        'polite_mode': TAG_POLITE_MODE,  # √
        'first_name': TAG_FIRST_NAME,  # √
        'last_name': TAG_LAST_NAME,  # √
        'title': TAG_TITLE,  # √
        'company': TAG_COMPANY,  # √
        'dept_mail_stop': TAG_DEPT_MAIL_STOP,  # √
        'locus': TAG_LOCUS,  # √
        'street': TAG_STREET,  # √
        'city': TAG_CITY,  # √
        'state': TAG_STATE,  # √
        'zipcode': TAG_ZIP,  # √
        'country': TAG_COUNTRY,  # √
        'latitude': TAG_LATITUDE,  # √ 
        'longitude': TAG_LONGITUDE,  # √ 
        'phone_type_1': TAG_PHONE_TYPE_1,  # √
        'phone_1': TAG_PHONE_1,  # √
        'phone_type_2': TAG_PHONE_TYPE_2,  # √
        'phone_2': TAG_PHONE_2,  # √
        'phone_type_3': TAG_PHONE_TYPE_3,  # √
        'phone_3': TAG_PHONE_3,  # √
        'phone_type_4': TAG_PHONE_TYPE_4,  # √
        'phone_4': TAG_PHONE_4,  # √
        'email': TAG_EMAIL,  # √
        'uri': TAG__URI,  # √
        'accession_date': TAG__ACCESSION_DATE,  # √
        'update_date': TAG__UPDATE_DATE,  # √
        'keywords': TAG_KEYWORDS,  # √
        'remarks': TAG_REMARKS,  # √
        }

    disp_tags_adr = [
        'polite_mode',
        'first_name',
        'last_name',
        'title',
        'company',
        'dept_mail_stop',
        'locus',
        'street',
        'city',
        'state',
        'zipcode',
        'country',
        ]

    def view_as_text(self, is_from_rec=True):
        result = []
        itms = self.pages.conjure_itm_by_tag()
        val_disp = {}
        for (tag_en, tag) in self.disp_tags.items():
            itm = itms.get(tag)
            if itm:
                if is_from_rec:
                    val_disp[tag_en] = itms[tag].val_view
                else:
                    val_disp[tag_en] = itms[tag].edt.get_visual()
                del itms[tag]
            else:
                val_disp[tag_en] = NOT_AVAIL
        result.append(_('<i>Listing Type:  </i>{v0}.{v1}').format(v0=val_disp["listing_type"], v1=MARKDN_LINE_END))
        result.append(MARKDN_LINE_END)
        if val_disp['greeting'] in BLANK_VALUES:
            pass
        else:
            result.append(_('Dear {v0}:{v1}').format(v0=val_disp["greeting"], v1=MARKDN_LINE_END))
            result.append(MARKDN_LINE_END)
        parms = {tag_en: val_disp[tag_en] for tag_en in self.disp_tags_adr}
        adr = tonto2_parse_international_addresses.new_adr(**parms)
        result.append(f'{adr.view_as_text()}{MARKDN_LINE_END}')
        result.append(MARKDN_LINE_END)
        lat_lon = [
            val_disp[key]
            for key in ('latitude', 'longitude')
            if not val_disp[key] in BLANK_VALUES
            ]
        if lat_lon:
            lat_lon = ', '.join(lat_lon)
            result.append(_('<i>Lat/Lon:  </i>{v0}.{v1}').format(v0=lat_lon, v1=MARKDN_LINE_END))
            result.append(MARKDN_LINE_END)
        phones = []
        for ndx in ['1', '2', '3', '4']:
            phone_key = f'phone_{ndx}'
            type_key = f'phone_type_{ndx}'
            phone = []
            if val_disp[phone_key] in BLANK_VALUES:
                pass
            else:
                hit = val_disp[phone_key]
                digits = tonto2_parse_international_addresses.extract_digits(hit)
                if hit.startswith('+'):
                    digits = '+' + digits
                phone.append(f'<a href="tel:{digits}">{hit}</a>')
                if val_disp[type_key] in BLANK_VALUES:
                    pass
                else:
                    phone.append(f'({val_disp[type_key]})')
            if phone:
                phone = SPACE.join(phone)
                phones.append(phone)
        if phones:
            if len(phones) > 1:
                label = _('Phones')
            else:
                label = _('Phone')
            phones = ', '.join(phones)
            result.append(f'<i>{label}:  </i>{phones}.{MARKDN_LINE_END}')
            result.append(MARKDN_LINE_END)
        if val_disp['email'] in BLANK_VALUES:
            pass
        else:
            result.append(_('<i>eMail:  </i><a href="mailto://{v0}">{v1}</a>{v2}').format(
                v0=val_disp["email"],
                v1=val_disp["email"],
                v2=MARKDN_LINE_END,
                ))
            result.append(MARKDN_LINE_END)
        if val_disp['uri'] in BLANK_VALUES:
            pass
        else:
            result.append(_('<i>Web:  </i><a href="{v0}">{v1}</a>{v2}').format(
                v0=val_disp["uri"],
                v1=val_disp["uri"],
                v2=MARKDN_LINE_END,
                ))
            result.append(MARKDN_LINE_END)
        if val_disp['keywords'] in BLANK_VALUES:
            pass
        else:
            result.append(_('<i>Keywords:  </i>{v0}{v1}').format(
                v0=val_disp["keywords"],
                v1=MARKDN_LINE_END,
                ))
            result.append(MARKDN_LINE_END)
        if val_disp['remarks'] in BLANK_VALUES:
            pass
        else:
            result.append(f'{val_disp["remarks"]}{MARKDN_LINE_END}')
            result.append(MARKDN_LINE_END)
        result.append(_('<font size=-1><tt><i>Created:  </i>{v0}</tt></font>{v1}').format(
            v0=val_disp["accession_date"],
            v1=MARKDN_LINE_END,
            ))
        result.append(_('<font size=-1><tt><i>Updated:  </i>{v0}</tt></font>{v1}').format(
            v0=val_disp["update_date"],
            v1=MARKDN_LINE_END,
            ))
        result.append(MARKDN_LINE_END)
        for itm in itms.values():
            result.append(f'<i>{itm.tag}:  </i>{itm.val_view}{MARKDN_LINE_END}')
        result.append(MARKDN_LINE_END)
        result = NULL.join(result)
        return result

                
    def free_form_entry(self, txt):
        result = txt
        itm = self.pages.conjure_itm_by_tag()
        (adr, result) = tonto2_parse_international_addresses.parse_adr(result)
        for tag_en in self.disp_tags_adr:
            tag = self.disp_tags[tag_en]
            val = getattr(adr, tag_en)
            if val in BLANK_VALUES:
                pass
            else:
                itm[tag].edt.set_visual(val)
        (lat_lon, result) = tonto2_parse_international_addresses.parse_lat_lon(result)
        if lat_lon:
            (val_lat, val_lon) = lat_lon[ZERO]
            tag = self.disp_tags['latitude']
            itm[tag].edt.set_visual(str(val_lat))
            tag = self.disp_tags['longitude']
            itm[tag].edt.set_visual(str(val_lon))
        (phones, result) = tonto2_parse_international_addresses.parse_phones(result)
        for (ndx, val_phone) in enumerate(phones):
            tag = self.disp_tags.get(f'phone_{ndx + 1}')
            if tag:
                itm[tag].edt.set_visual(val_phone)
        (links, result) = tonto2_parse_international_addresses.parse_uri(result)
        val_uri = None
        val_email = None
        for val_link in links:
            if '@' in val_link:
                if val_email:
                    pass
                else:
                    val_email = val_link
            else:
                if val_uri:
                    pass
                else:
                    val_uri = val_link
        if val_email:
            tag = self.disp_tags['email']
            itm[tag].edt.set_visual(val_email)
        if val_uri:
            tag = self.disp_tags['uri']
            itm[tag].edt.set_visual(val_uri)
        return result
    
REG_RELS.add(RegItem(
    'Address List',
    _('Address List'),
    RelAddressList,
    _('''An **Address List** has predefined items such as city, state, zip,
and phone number.'''), 
))


class RelBibliography(Rel):

    """Tonto2 Bibliography Relation.

    """    
    
    mla_fmt = '%d %b %Y'
    
    def __init__(self):
        super().__init__(tag=_('Bibliography'))
        self.md_desc_long = _('List of Works Cited')
        return

    def conjure_pages(self):
        date_squib = '''Dates are **99 Mon. 9999** or **Mon. 9999** or **9999**.  Dates may
be hyphenated to express a date range.  Do not duplicate the trailing
portions of the beginning date that it has in common with the ending
date.  If expressing a range of years, do not duplicate the leading
century of the ending date that it has in common with the beginning
date.'''
        page = ZERO
        if True:
            itm = ItmText(TAG_PROJECT)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''This file may combine bibliographies from several research
**{v0}**s.  This field distiguishes each entry by the **{v0}** that
generated it.''').format(
                v0=TAG_PROJECT,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_LIBRARY)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is the name of the collection where you found the
reference.  Specify this so you can remember and relocate the
source.''').format(
                v0=TAG_LIBRARY,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_CALL_NUMBER)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""**{v0}** is the **{v1}**'s catalog number for the source.""").format(
                v0=TAG_CALL_NUMBER,
                v1=TAG_LIBRARY,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_SORT_KEY)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""**{v0}** is not part of the bibliographic reference but orders the
references in the **List of Works Cited.** It may be left empty to be
filled later.  When filled, it ought to be unique because other
entries may cross-reference it.  Generally it is not long but contains
enough of the author's **{v1}** followed by enough of the title
to be unique.  Omit leading words like **A** and **The** to sort
titles correctly.""").format(
                v0=TAG_SORT_KEY,
                v1=TAG_AUTHOR_1_LAST_NAME,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmCoded(TAG_ENTRY_TYPE)
            itm.code_table = 'BIBLIO_ENTRY_TYPE'
            itm.val_default = 'Book'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** tells what kind of **{v1}** this entry refers to.''').format(
                v0=TAG_ENTRY_TYPE,
                v1=TAG_WORK,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_ARTICLE)
            itm.val_default = '""'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is the significant minor portion (if any) of a larger
**{v1}** from which the reference is drawn.  It may be an article (but
not a periodical), a TV episode (but not a program), a track (but not
an album), or a Web page (but not a site).  A subtitle may be included
after a colon.

Normally, this must be enclosed in quotes.  Exceptions are a(n)
**{v0}** that was published independently, which is enclosed in
&lt;u&gt;&lt;/u&gt; or a review (The title begins with **Rev. of**
followed by the underlined **{v1}** followed by a comma and a space
followed by the **{v1}** **{v2}**.).''').format(
                v0=TAG_ARTICLE,
                v1=TAG_WORK,
                v2=TAG_WORK_EDITORS,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_FRAGMENT)
            itm.code_table = 'BIBLIO_FRAGMENT_TYPE'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** specifies that the **{v1}** is a specific part of the
larger **{v2}** whether or not it has its own title.''').format(
                v0=TAG_FRAGMENT,
                v1=TAG_ARTICLE,
                v2=TAG_WORK,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmURI(TAG__URI)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is the URL of a World-Wide Web page, if any,
that is the reference source.

If the source is a Usenet news group, precede the name of the group
with **news:**.''').format(
                v0=TAG__URI,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_PATH)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** may be **Path:** followed by a sequence of hypertext links
(separated by semicolons) to follow (if any) from the **{v1}** URL.

Alternatively, it may be **Keyword:** follwed by a single word used to
access the source from a subscription service.''').format(
                v0=TAG_PATH,
                v1=TAG__URI,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDateTime(TAG__TRAVERSE_DATE)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is the date that the **{v1}** page was referenced.''').format(
                v0=TAG__TRAVERSE_DATE,
                v1=TAG__URI,
                )
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmSelected(TAG_GOVERNMENT)
            itm.code_table = 'BIBLIO_GOVERNMENT'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''For government publications, spell out the issuing
**{v0}**.''').format(
                v0=TAG_GOVERNMENT,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_AGENCY_1)
            itm.code_table = 'BIBLIO_AGENCY_1'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''For government publications, provide short names for the various
levels of issuing agencies, starting with the most inclusive
**{v0}**.''').format(
                v0=TAG_AGENCY_1,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_AGENCY_2)
            itm.code_table = 'BIBLIO_AGENCY_2'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''For government publications, provide a short name for the issuing
**{v0}**.''').format(
                v0=TAG_AGENCY_2,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_AGENCY_3)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''For government publications, provide a short name for the issuing
**{v0}**.''').format(
                v0=TAG_AGENCY_3,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_AUTHOR_TYPE)
            itm.code_table = 'BIBLIO_AUTHOR_FUNCTION'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is the principal function of the author.''').format(
                v0=TAG_AUTHOR_TYPE,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_AUTHOR_1_LAST_NAME)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""This is the author's **{v0}**.  If the author is an organization,
use the corporate name, omit the leading article (**A, An,
The**) if any, and leave **{v1}** empty.""").format(
                v0=TAG_AUTHOR_1_LAST_NAME,
                v1=TAG_AUTHOR_1_FIRST_NAME,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_AUTHOR_1_FIRST_NAME)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""This is the author's **{v0}**.  Famous classical authors don't
always have a first name.

Suffixes to the name (**Jr.**) appear after a comma after the **{v0}**.

If the work was published under a pseudonym, you may enclose the
author's actual name in square brackets after his **{v0}**.""").format(
                v0=TAG_AUTHOR_1_FIRST_NAME,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_AUTHOR_2_LAST_NAME)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""This is the second author's **{v0}**.  If there
are more than three, this should be **et al.**""").format(
                v0=TAG_AUTHOR_2_LAST_NAME,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_AUTHOR_2_FIRST_NAME)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""This is the author's **{v0}**.""").format(
                v0=TAG_AUTHOR_2_FIRST_NAME,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_AUTHOR_3_LAST_NAME)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""This is the third author's **{v0}**.""").format(
                v0=TAG_AUTHOR_3_LAST_NAME,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_AUTHOR_3_FIRST_NAME)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""This is the author's **{v0}**.""").format(
                v0=TAG_AUTHOR_3_FIRST_NAME,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_ARTICLE_EDITORS)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""This is the first and last names of the editor(s) of the **{v0}**,
if any.  Prefix the name with an abbreviation of the editor's
function: (**{v1}**).  Editors that have the same function must be
joined by the conjuction **and** (or by commas and the
conjuction if there are more than two).  Periods must separate editors
that have different functions.""").format(
                v0=TAG_ARTICLE,
                v1=tonto2_code_tables.TAB_BY_NAME['BIBLIO_EDITOR_FUNCTION'].codes,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_WHEN_ARTICLE_ORIG)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''If significant, **{v0}** may specify the year that the
**{v1}** was originally published.''').format(
                v0=TAG_WHEN_ARTICLE_ORIG,
                v1=TAG_ARTICLE,
                )
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmText(TAG_XREF)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""A **{v0}** to a collective work (anthology) with its own entry is
the collective **{v1}**'s editor's last name (with leading initial or
first name or trailing **{v1}** title if required to make the
reference unique).  The collective work must be alphabetized under the
editor's last name.""").format( 
                v0=TAG_XREF,
                v1=TAG_WORK,
               )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_WORK)
            itm.val_default = '<u></u>'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is the large source from which the reference is drawn.  It
may be a short name of a periodical (but not an article), a TV program
(but not an episode), an album (but not a track), or a Web site (but
not a page).  A subtitle may be included after a colon.

Normally, this must be enclosed in &lt;u&gt;&lt;/u&gt;, but there are
exceptions: a musical composition identified by form, number, and key
(not generally underlined unless you refer to its score); **Home
page**; a course of study (followed by a period and a space followed
by **Course home page**); an academic department (followed by a period
and a space followed by **Dept. home page**); a trial case; a law or
statute; a patent; an unpublished work; a journal published in more
than one series **2nd ser.** or **3rd ser.** follows the underlined
short name.); a local newspaper (City in square brackets follows the
underlined name of the paper unless the name already includes the
city.).''').format(
                v0=TAG_WORK,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_CONFERENCE)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''If this entry is from the proceedings of a conference, this is a
short title of the **{v0}**, its date, and its location.  Be sure to
provide only the parts that are left out of the title of the
conference proceedings.

If this entry is a legislative document, this is the convention number
and legislature name, session, and document number.''').format(
                v0=TAG_CONFERENCE,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_WORK_EDITORS)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""This is the first and last names of the editor(s) of the **{v0}**,
if any.  Prefix the name with an abbreviation of the editor's function
(**{v1}**). An exception is **gen. ed.** that follows a comma after
the name.

Editors that have the same function must be joined by the conjuction
**and** (or by commas and the conjuction if there are more than two).
Periods must separate editors that have different functions.  Omit
this altogether for standard reference works.""").format(
                v0=TAG_WORK,
                v1=tonto2_code_tables.TAB_BY_NAME['BIBLIO_EDITOR_FUNCTION'].codes,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_WHEN_WORK_ORIG)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''If significant, **{v0}** may specify the year that the **{v1}** was
originally published.''').format(
                v0=TAG_WHEN_WORK_ORIG,
                v1=TAG_WORK,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_EDITION)
            itm.code_table = 'BIBLIO_EDITION'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** designates a revision of a book, a version of a Web page,
or a morning or afternoon edition of a newspaper.

If the same **{v0}** of a newpaper contains duplicate page numbers in
separate sections, add a comma and a space followed by **sec.**
followed by the section number.''').format(
                v0=TAG_EDITION,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_VOL)
            itm.code_table = 'BIBLIO_VOLUME'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''For a multivolume work, **{v0}** tells which portion the reference
is from.  If refering to more than one volume, provide the number of
volumes.

For a journal, it indicates what date range the pages are in.

This does not apply to other periodicals.

Omit this for encyclopedias and dictionaries.''').format(
                v0=TAG_VOL,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_ISSUE)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** number must appear in addition to **{v1}** only if a
journal is not continuously paginated.''').format(
                v0=TAG_ISSUE,
                v1=TAG_VOL,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_DISSERTATION_TYPE)
            itm.code_table = 'BIBLIO_DISSERTATION_TYPE'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is the type of paper.''').format(
                v0=TAG_DISSERTATION_TYPE,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_DISSERTATION)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is the name of the degree-granting university followed by
a comma and a space followed by the year of the **{v0}**.''').format(
                v0=TAG_DISSERTATION,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_SERIES)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''If the **{v0}** is part of a published **{v1}**, this is the short
**{v1}** name followed by the number of the **{v0}** in the **{v1}**.

If the **{v0}** is part of a **{v1}** of performances, this is the
short **{v1}** name or the name of the group that is performing.

If the group is listed as author, **{v1}** may be **Concert.**

If the **{v0}** is supplied by a subscription service, **{v1}** may be
the name of the service.''').format(
                v0=TAG_WORK,
                v1=TAG_SERIES,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_SERIES_FUNCTIONARIES)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''This is the first and last names of those who serve as
functionaries of the **{v0}**, if any.  Prefix the name with an
abbreviation of the function (**{v1}**).''').format(
                v0=TAG_SERIES,
                v1=tonto2_code_tables.TAB_BY_NAME['BIBLIO_EDITOR_FUNCTION'].codes,
                )
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmAmericanTitleCase(TAG_CITY_PUBLISHER)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""**{v0}** for print sources is a short city name followed by a colon
and a space followed by a short company name.

If the city or publisher is known but not in the source, place the
name in square brackets.

If the city or publisher is controversial, place **?** in the brackets
after the name.

If the city is unknown, use **N.p.** before the colon.

If the publisher is unknown, use **n.p.** after the colon.  The colon
and publisher may be omitted for **{v1}**s published before 1900.

A publisher's imprint may precede a hyphen before the
publisher's name.

Omit this altogether for standard reference works.

Semicolons must separate multiple **{v0}**s.""").format(
                v0=TAG_CITY_PUBLISHER,
                v1=TAG_WORK,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_MEDIUM)
            itm.code_table = 'BIBLIO_MEDIUM'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** for recordings is the kind of recording.  Also it may
indicate a peculiar kind of printed material.  For software or data,
**Rel.** precedes a version or release number.''').format(
                v0=TAG_MEDIUM,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_PIECES)
            itm.code_table = 'BIBLIO_PIECES'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''If more than one, specify the number of **{v0}** of a medium that
comprise the **{v1}** or the number of the piece used.''').format(
                v0=TAG_PIECES,
                v1=TAG_WORK,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_MANUFACTURER)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** for recordings is the short name of the publisher.''').format(
                v0=TAG_MANUFACTURER,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_NETWORK)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** for a broadcast performance is a short network name.''').format(
                v0=TAG_NETWORK,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_VENUE_CITY)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""**{v0}** for broadcast performances is a TV or radio station's call
letters followed by a comma and a space followed by a short city name.
Place the broadcast date in **{v1}**.

For live performances and exhibitions, it is a venue followed by a
comma and a space followed by a short city name if the city is not
already part of the venu name.  Place the performance date in
**{v1}**.""").format(
                v0=TAG_VENUE_CITY,
                v1=TAG_WHEN_PUBLISHED,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmAmericanTitleCase(TAG_SPONSOR)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** for electronic sources is a short organization name.''').format(
                v0=TAG_SPONSOR,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_WHEN_RECORDED)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''If significant, **{v0}** may specify the date of a recording.
Proceed this with **Rec.** for audio recordings.  

{v1}''').format(
                v0=TAG_WHEN_RECORDED,
                v1=date_squib,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_WHEN_PUBLISHED)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is a date.

Give only the year for a book or continuously paginated journal.

If the date is known but not in the source, place the date in square
brackets.

If the date is approximate, place **c.** in the brackets before the
date.

If the date is controversial, place **?** in the brackets after the
date.

If the date is unknown, place **n.d.** in this field.

{v2}''').format(
                v0=TAG_WHEN_PUBLISHED,
                v1=TAG_WORK,
                v2=date_squib,
                )
            self.pages.add(itm, ndx_page=page)
        page += 1
        if True:
            itm = ItmText('Pages')
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is the number of the page on which an **{v1}** begins, a
hyphen, and the number of the page on which the **{v1}** ends.
Suppress the portion of the ending page that is the same as the
beginning page except the last two digits.

If the page numbers are not consecutive, follow the beginning page
with a **+** and omit the ending page.

Commas separate page ranges for each installment of a serialized
**{v1}** by the same author under the same title.  When a subsequent
installment crosses into a different **{v2}** of a journal, set off
the **{v2}** by a semicolon.  Follow it by the **Publication Date** in
parens followed by a colon and a space followed by the page range for
that installment.

If the **{v3}** is not paginated, use **N.pag.**.

If referring to an item in an abstracts journal, insert **item**
before the number.

If referring to an article on microfiche, use, for example, **fiche 1,
grids A8-11.**

If referring to an article in a loose-leaf collection, insert **Art.**
before the number.

Omit this for entries that are not **{v1}**s if the **{v3}** <u>is</u>
paginated.

Omit this for encyclopedias and dictionaries.''').format(
                v0=TAG_PAGES,
                v1=TAG_ARTICLE,
                v2=TAG_VOL,
                v3=TAG_WORK,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmSelected(TAG_COLLECTION_TYPE)
            itm.code_table = 'BIBLIO_COLLECTION_TYPE'
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _("""Some kinds of entries depend on links to others.  **{v0}**
specifies the kind of link.  **{v1}** specifies the linked entry.

An article reprinted in a more recent collection (**Rpt. in**) depends
on an anthology.  An article reprinted under a new name (**Rpt. of**)
depends on the original.  A translation (**Trans. of**) depends on an
original.  A named volume (**Vol. x of**) includes its own publisher
info but depends on an entry for the complete work, which specifies
the number of **{v2}**s and their inclusive dates.  A published letter
(**Letter [item number] of**) entitled 'To [Recipient]' depends on a
collective work.  Its **{v3}** should contain the date of the letter.
A special issue of a journal (**Spec. issue of**) depends on an entry
for the journal publication info.

Other entries (**Link to **) depend on collective works: abstracts;
articles in loose-leaf, microforms, or online collections; photos of
paintings or sculpture (which should cite the exhibition of the
original and link to the collective work that is the source of the
photo).""").format(
                v0=TAG_COLLECTION_TYPE,
                v1=TAG_COLLECTION_LINK,
                v2=TAG_VOL,
                v3=TAG_WHEN_PUBLISHED,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_COLLECTION_LINK)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is the **{v1}** of a separate entry for a **{v2}**, which
should have no author information.  Be sure that **{v2}** has a
different **{v3}** so that it is not itself included in the **List of
Works Cited** with this entry.''').format(
                v0=TAG_COLLECTION_LINK,
                v1=TAG_SORT_KEY,
                v2=TAG_WORK,
                v3=TAG_PROJECT,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmMarkdn(TAG_REMARKS)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is an annotation to a bibliographic entry.

Use **{v0}** to denote that a(n) **{v1}** in a periodical is part of a
**{v2}**. For example: **Pt. 2 of a series, Series Title Not
Underlined, begun 9 Sep. 1999.**

Use it to denote that the entry is a **Transcript** of a performance.

Use it to record the catalog number and location of a manuscript.  For
example: **Ms 91. Dean and Chapter Lib., Lincoln, Eng.**%s''').format(
                v0=TAG_REMARKS,
                v1=TAG_ARTICLE,
                v2=TAG_SERIES,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDateTime(TAG__ACCESSION_DATE)
            itm.is_edit_enabled = False
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** cannot be changed manually because it
automatically keeps track of when the entry was made.''').format(
                v0=TAG__ACCESSION_DATE,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmDateTime(TAG__UPDATE_DATE)
            itm.is_edit_enabled = False
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** cannot be changed manually because it automatically
keeps track of when the entry was last changed.''').format(
                v0=TAG__UPDATE_DATE,
                )
            self.pages.add(itm, ndx_page=page)
        if True:
            itm = ItmText(TAG_KEYWORDS)
            itm.is_dd_mod_enabled = False
            itm.md_desc_long = _('''**{v0}** is a list of word forms that do not exactly occur in any
of the other parts of this entry but that you want to remember this
citation by.  You can search by **Keyword** to find this entry.  You
may wish to separate **{v0}** with semicolons.''').format(
                v0=TAG_KEYWORDS,    
                )
            self.pages.add(itm, ndx_page=page)
        self.display_tags = [
            TAG_PROJECT,
            TAG_SORT_KEY,
            TAG_KEYWORDS,
            ]
        return self

    def view_as_biblio(self):

        def sub_all(text, targ, repl=NULL):
            while True:
                result = targ.sub(repl, text)
                if result == text:
                    break
                else:
                    text = result
            return result

        def conjure_names():
            result = []
            names = []
            names.append([itms[TAG_AUTHOR_1_LAST_NAME].val_disp, itms[TAG_AUTHOR_1_FIRST_NAME].val_disp])
            names.append([itms[TAG_AUTHOR_2_FIRST_NAME].val_disp, itms[TAG_AUTHOR_2_LAST_NAME].val_disp])
            names.append([itms[TAG_AUTHOR_3_FIRST_NAME].val_disp, itms[TAG_AUTHOR_3_LAST_NAME].val_disp])
            if names[1][1] in ['et al', 'et al.']:
                result.append(f'''
                    {names[ZERO][ZERO]}, {names[ZERO][1]},
                    et al.
                    ''')
            elif names[ZERO][ZERO] in BLANK_VALUES:
                pass
            elif names[1][1] in BLANK_VALUES:
                result.append(f'''
                    {names[ZERO][ZERO]}, {names[ZERO][1]}
                    ''')
            elif names[2][1] in BLANK_VALUES:
                result.append(f'''
                    {names[ZERO][ZERO]}, {names[ZERO][1]}, and
                    {names[1][ZERO]} {names[1][1]}
                    ''')
            else:
                result.append(f'''
                    {names[ZERO][ZERO]}, {names[ZERO][1]},
                    {names[1][ZERO]} {names[1][1]}, and
                    {names[2][ZERO]} {names[2][1]}
                    ''')
            if itms[TAG_AUTHOR_TYPE].val_disp in ['by', 'By']:
                pass
            else:
                result.append(f''', {itms[TAG_AUTHOR_TYPE].val_disp}''')
                result.append('''. 
                    ''')
            result.append(f'''
                {itms[TAG_GOVERNMENT].val_disp}.
                {itms[TAG_AGENCY_1].val_disp}.
                {itms[TAG_AGENCY_2].val_disp}.
                {itms[TAG_AGENCY_3].val_disp}.
                ''')
            return result

        def conjure_article():
            result = []
            result.append(f'''{itms[TAG_ARTICLE].val_disp}.
                ''')
            result.append(f'''{itms[TAG_WHEN_ARTICLE_ORIG].val_disp}.
                ''')
            result.append(f'''{itms[TAG_ARTICLE_EDITORS].val_disp}.
                ''')
            result.append(f'''{itms[TAG_FRAGMENT].val_disp}.
                ''')
            return result

        def conjure_journal():
            result = []
            result.append(f'''{itms[TAG_WORK].val_disp}
                ''')
            result.append(f'''{itms[TAG_VOL].val_disp}
                ''')
            issue = itms[TAG_ISSUE]
            if issue.has_value:
                result.append(f'''.{issue.val_disp}
                    ''')  
            result.append(f'''({itms[TAG_WHEN_PUBLISHED].val_disp}):
                ''')
            result.append(f'''{itms[TAG_PAGES].val_disp}.
                ''')
            return result

        def conjure_newsmag():
            result = []
            result.append(f'''{itms[TAG_WORK].val_disp}
                ''')
            result.append(f'''{itms[TAG_VOL].val_disp}
                ''')
            issue = itms[TAG_ISSUE]
            if issue.has_value:
                result.append(f'''.{issue.val_disp}
                    ''')  
            result.append(f'''{itms[TAG_WHEN_PUBLISHED].val_disp}
                ''')
            edition = itms[TAG_EDITION]
            if edition.has_value:
                result.append(f''', {edition.val_disp}.
                    ''')
            pages = itms[TAG_PAGES]
            if pages.has_value:
                result.append(f''': {pages.val_disp}.
                    ''')
            return result

        def conjure_performance():
            result = []
            result.append(f'''{itms[TAG_WORK].val_disp}.
                ''')
            result.append(f'''{itms[TAG_WORK_EDITORS].val_disp}.
                ''')
            result.append(f'''{itms[TAG_EDITION].val_disp}.
                ''')
            result.append(f'''{itms[TAG_WHEN_WORK_ORIG].val_disp}.
                ''')
            result.append(f'''{itms[TAG_SERIES].val_disp}.
                ''')
            result.append(f'''{itms[TAG_SERIES_FUNCTIONARIES].val_disp}.
                ''')
            result.append(f'''{itms[TAG_SPONSOR].val_disp}.
                ''')
            result.append(f'''{itms[TAG_CONFERENCE].val_disp}.
                ''')
            result.append(f'''{itms[TAG_NETWORK].val_disp}.
                ''')
            result.append(f'''{itms[TAG_VENUE_CITY].val_disp}.
                ''')
            result.append(f'''{itms[TAG_WHEN_RECORDED].val_disp}.
                ''')
            result.append(f'''{itms[TAG_MEDIUM].val_disp}.
                ''')
            result.append(f'''{itms[TAG_PIECES].val_disp}.
                ''')
            mfg = itms[TAG_MANUFACTURER]
            if mfg.has_value:
                result.append(f'''{mfg.val_disp},
                    ''')
            result.append(f'''{itms[TAG_WHEN_PUBLISHED].val_disp}
                ''')
            pages = itms[TAG_PAGES]
            if pages.has_value:
                result.append(f''': {pages.val_disp}.
                    ''')
            return result

        def conjure_book():
            result = []
            result.append(f'''{itms[TAG_WORK].val_disp}.
                ''')
            work_editors = itms[TAG_WORK_EDITORS].val_disp
            if work_editors.startswith('By '):
                result.append(f'''{work_editors}.
                    ''')
            result.append(f'''{itms[TAG_WHEN_WORK_ORIG].val_disp}.
                ''')
            if work_editors.startswith('By '):
                pass
            else:
                result.append(f'''{work_editors}.
                    ''')
            result.append(f'''{itms[TAG_EDITION].val_disp}.
                ''')
            result.append(f'''{itms[TAG_VOL].val_disp}.
                ''')
            result.append(f'''{itms[TAG_ISSUE].val_disp}.
                ''')
            result.append(f'''{itms[TAG_DISSERTATION_TYPE].val_disp}
                {itms[TAG_DISSERTATION].val_disp}.
                ''')
            result.append(f'''{itms[TAG_MEDIUM].val_disp}.
                ''')
            result.append(f'''{itms[TAG_PIECES].val_disp}.
                ''')
            result.append(f'''{itms[TAG_CONFERENCE].val_disp}.
                ''')
            result.append(f'''{itms[TAG_NETWORK].val_disp}.
                ''')
            result.append(f'''{itms[TAG_VENUE_CITY].val_disp}.
                ''')
            publisher = itms[TAG_CITY_PUBLISHER]
            if publisher.has_value:
                result.append(f'''{publisher.val_disp},
                    ''')
            result.append(f'''{itms[TAG_WHEN_PUBLISHED].val_disp}. 
                ''')
            result.append(f'''{itms[TAG_SERIES].val_disp}.
                ''')
            result.append(f'''{itms[TAG_SERIES_FUNCTIONARIES].val_disp}.
                ''')
            result.append(f'''{itms[TAG_WHEN_RECORDED].val_disp}.
                ''')
            result.append(f'''{itms[TAG_MANUFACTURER].val_disp}.
                ''')
            result.append(f'''{itms[TAG_SPONSOR].val_disp}.
                ''')
            result.append(f'''{itms[TAG_XREF].val_disp}
                {itms[TAG_PAGES].val_disp}.
                ''')
            return result

        def conjure_access():
            result = []
            result.append(f'''{itms[TAG_REMARKS].val_disp}.
                ''')
            access_time_stamp = itms[TAG__TRAVERSE_DATE].val_comp
            access_link = itms[TAG__URI].val_comp
            if (access_time_stamp in BLANK_VALUES) or (access_link in BLANK_VALUES):
                pass
            else:
                result.append(f'''{access_time_stamp.strftime(self.mla_fmt)}
                    &lt;<a href="{access_link}">{access_link}</a>&gt;.
                    ''')
            result.append(f'''{itms[TAG_PATH].val_disp}.
                ''')
            return result

        def conjure_collection():
            result = []
            result.append(f'''{itms[TAG_COLLECTION_TYPE].val_disp}
                ''')
            collection_link = itms[TAG_COLLECTION_LINK].val_disp
            save_ndx_rec = self.ndx_rec
            for (ndx_rec, rec) in enumerate(self.recs):
                sort_key = rec.get(TAG_SORT_KEY)
                if sort_key in BLANK_VALUES:
                    pass
                elif sort_key == collection_link:
                    self.stage_rec(ndx_rec)
                    result.append(self.view_as_biblio())
                    break
            self.stage_rec(save_ndx_rec)
            return result
        
        itms = self.pages.conjure_itm_by_tag()
        entry_type = itms[TAG_ENTRY_TYPE].val_disp
        result = []
        result.extend(conjure_names())
        result.extend(conjure_article())
        if entry_type in ['Journal']:
            result.extend(conjure_journal())
        elif entry_type in ['NewsMag']:
            result.extend(conjure_newsmag())
        elif entry_type in ['Performance']:
            result.extend(conjure_performance())
        else:
            result.extend(conjure_book())
        result.extend(conjure_access())
        result.extend(conjure_collection())
        result = NULL.join(result)
        flags = re.DOTALL | re.MULTILINE
        for (targ, repl) in [
                (re.compile(r'#N/A', flags), NULL),
                (re.compile(r'"{2}\.', flags), NULL),
                (re.compile(r"'{2}\.", flags), NULL),
                (re.compile(r'<u></u>', flags), NULL),
                (re.compile(r'([!?])\.', flags), r'\1'),
                (re.compile(r'\s+\,', flags), ','),
                (re.compile(r'\s+\.', flags), '.'),
                (re.compile(r'\s+\:', flags), ':'),
                (re.compile(r'[.,]\.', flags), '.'),
                (re.compile(r'\.+', flags), '.'),
                (re.compile(r'(["\'])([.,?!])', flags), r'\2\1'),
                (re.compile(r'\s+', flags), SPACE),
                (re.compile(r'^\.', flags), NULL),
                ]:
            result = sub_all(result, targ, repl)
            result = result.strip()
        return result

    def view_as_text(self):
        result = []
        itms = self.pages.conjure_itm_by_tag()
        result.append('<table>')
        for tag in [
                TAG_PROJECT,
                TAG_LIBRARY,
                TAG_CALL_NUMBER,
                TAG_SORT_KEY,
                TAG_ENTRY_TYPE,
                ]:
            val = itms.get(tag, None)
            if val:
                val = val.val_disp
            else:
                val = NOT_AVAIL
            result.append(_('<tr><td align=right><i>{v1}:&nbsp;&nbsp;</i></td><td>{v0}</td></tr>').format(v0=val, v1=tag))
            itms.pop(tag, None)
        result.append('</table>')
        result.append('<p>')
        biblio_entry = self.view_as_biblio()
        result.append(biblio_entry)
        result.append('</p>')
        for tag in [
                TAG_GOVERNMENT,
                TAG_AGENCY_1,
                TAG_AGENCY_2,
                TAG_AGENCY_3,
                TAG_AUTHOR_1_FIRST_NAME,
                TAG_AUTHOR_2_FIRST_NAME,
                TAG_AUTHOR_3_FIRST_NAME,
                TAG_AUTHOR_1_LAST_NAME,
                TAG_AUTHOR_2_LAST_NAME,
                TAG_AUTHOR_3_LAST_NAME,
                TAG_AUTHOR_TYPE,
                TAG_ARTICLE,
                TAG_WHEN_ARTICLE_ORIG,
                TAG_ARTICLE_EDITORS,
                TAG_FRAGMENT,
                TAG_WORK,
                TAG_WORK_EDITORS,
                TAG_WHEN_WORK_ORIG,
                TAG_EDITION,
                TAG_VOL,
                TAG_ISSUE,
                TAG_DISSERTATION_TYPE,
                TAG_DISSERTATION,
                TAG_MEDIUM,
                TAG_PIECES,
                TAG_CITY_PUBLISHER,
                TAG_WHEN_PUBLISHED,
                TAG_CONFERENCE,
                TAG_SERIES,
                TAG_SERIES_FUNCTIONARIES,
                TAG_WHEN_RECORDED,
                TAG_MANUFACTURER,
                TAG_NETWORK,
                TAG_VENUE_CITY,
                TAG_SPONSOR,
                TAG_XREF,
                TAG_PAGES,
                TAG_REMARKS,
                TAG__TRAVERSE_DATE,
                TAG__URI,
                TAG_PATH,
                TAG_COLLECTION_TYPE,
                TAG_COLLECTION_LINK,
                ]:
            itms.pop(tag, None)
        result.append(MARKDN_LINE_END)
        result.append('<table>')
        for itm in itms.values():

            result.append(f'<tr><td align=right><i>{itm.tag}:&nbsp;&nbsp;</i></td><td>{itm.val_view}</td></tr>')
        result.append('</table>')    
        return '\n'.join(result)
        
REG_RELS.add(RegItem(
    'Bibliography',
    _('Bibliography'),
    RelBibliography,
    _('''A **Bibliography** provides a framework for formatting Works Cited
entries according to the Modern Language Association (MLA) Handbook,
6th Ed. (2003).'''), 
))


REL_CLASS_NAME = REG_RELS.name_by_type()
REL_NAME_CLASS = REG_RELS.type_by_name()


def coerce_suffix(file_name, suffix):

    """Force a path suffix to be *.dd or *.csv.

    """
    
    result = pathlib.Path(file_name).expanduser()
    suffix_old = result.suffix
    if suffix_old in ['.dd', '.csv']:
        result = result.with_suffix(suffix)
    else:
        result = pathlib.Path(str(result) + suffix)
    return result


class Config:

    """Load/Save the tonto.ini file.

    """
    
    fn = 'tonto.ini'
    ini_path = tonto2_code_tables.get_xdg_config_home()
    ini_path = pathlib.Path(ini_path, 'Tonto2', fn)
    default_ledger_font = 'noto sans semicondensed'
    default_icon_file = '/usr/share/icons/Adwaita/256x256/legacy/dialog-information.png'
    default_alert_wav = NOT_AVAIL
    default_festival_type_voice_synth = NOT_AVAIL
    default_qr_code_generator = NOT_AVAIL
    default_browser = 'most common'
    default_week_first_day = 7

    def __init__(self):
        self.tabs = []
        self.geometry_byt = NULL.encode()
        self.state_byt = NULL.encode()
        self.ledger_font = self.default_ledger_font
        self.icon_file = self.default_icon_file
        self.alert_wav = self.default_alert_wav
        self.festival_type_voice_synth = self.default_festival_type_voice_synth
        self.qr_code_generator = self.default_qr_code_generator
        self.browser = self.default_browser
        self.week_first_day = self.default_week_first_day
        self.current_tab_visual = NOT_AVAIL
        return

    def load(self):

        def load_globals():

            def expand_vars(path):
                path = pathlib.Path(path)
                result = os.path.expandvars(path.expanduser())
                return result
            
            self.geometry_hex = self.ini[sect].get('geometry', NULL)
            self.state_hex = self.ini[sect].get('state', NULL)
            self.ledger_font = expand_vars(self.ini[sect].get('ledger_font', self.default_ledger_font))
            if self.ledger_font in BLANK_VALUES:
                self.ledger_font = self.default_ledger_font
            self.icon_file = expand_vars(self.ini[sect].get('icon_file', self.default_icon_file))
            if self.icon_file in BLANK_VALUES or (not pathlib.Path(self.icon_file).exists()):
                self.icon_file = self.default_icon_file
            self.alert_wav = expand_vars(self.ini[sect].get('alert_wav', self.default_alert_wav)) 
            if self.alert_wav in BLANK_VALUES or (not pathlib.Path(self.alert_wav).exists()):
                self.alert_wav = self.default_alert_wav

            self.festival_type_voice_synth = expand_vars(self.ini[sect].get(
                'festival_type_voice_synth',
                self.default_festival_type_voice_synth,
                ))
            if self.festival_type_voice_synth in BLANK_VALUES:
                self.festival_type_voice_synth = self.default_festival_type_voice_synth
            else:
                if split_proc_parms(self.festival_type_voice_synth):
                    pass
                else:
                    self.festival_type_voice_synth = self.default_festival_type_voice_synth

            self.qr_code_generator = expand_vars(self.ini[sect].get(
                'qr_code_generator',
                self.default_qr_code_generator,
                ))
            if self.qr_code_generator in BLANK_VALUES:
                self.qr_code_generator = self.default_qr_code_generator
            else:
                if split_proc_parms(self.qr_code_generator):
                    pass
                else:
                    self.qr_code_generator = self.default_qr_code_generator

            self.browser = expand_vars(self.ini[sect].get('browser', self.default_browser))
            if self.browser in BLANK_VALUES:
                self.browser = self.default_browser
            else:
                self.register_default_browser(self.browser)
            self.current_tab_visual = self.ini[sect].get('current_tab_visual', NOT_AVAIL)
            self.week_first_day = self.ini[sect].getint('week_first_day', self.default_week_first_day)
            return
        
        self.ini = configparser.ConfigParser()
        if self.ini_path.exists():
            with open(self.ini_path) as unit:
                self.ini.read_file(unit)
                self.tabs.clear()
        for sect in self.ini.sections():
            if sect in ['DEFAULT']:
                pass
            elif sect in ['GLOBAL']:
                load_globals()
            else:
                try:
                    tab_dd_path = self.load_file(sect)
                except Error as e:
                    print(f'{e!s}')
                    tab_dd_path = None
                if tab_dd_path:
                    try:
                        tab_ndx_current_row = self.ini.getint(sect, 'row', fallback=ZERO)
                    except ValueError:
                        tab_ndx_current_row = ZERO
                    entry = (sect, tab_dd_path, tab_ndx_current_row)
                    self.tabs.append(entry)
        return self

    def load_file(self, sect):
        tab_file = self.ini[sect].get('file', None)
        if tab_file:
            tab_dd_path = coerce_suffix(tab_file, '.dd')
            if tab_dd_path.exists():
                pass
            else:
                raise Error(_('From "{v0}," file "{v1}" does not exist.').format(v0=self.ini_path, v1=tab_dd_path))
            tab_csv_path = coerce_suffix(tab_file, '.csv')
            if tab_csv_path.exists():
                pass
            else:
                raise Error(_('From "{v0}," file "{v1}" does not exist.').format(v0=self.ini_path, v1=tab_csv_path))
        else:
            raise Error(_('From "{v0}," there is no "file" on tab "{v1}."').format(v0=self.ini_path, v1=sect))
        return tab_dd_path

    def save(self):
        self.ini = configparser.ConfigParser()
        self.ini['GLOBAL'] = {}
        self.ini['GLOBAL']['geometry'] = self.geometry_hex
        self.ini['GLOBAL']['state'] = self.state_hex
        self.ini['GLOBAL']['ledger_font'] = self.ledger_font
        self.ini['GLOBAL']['icon_file'] = self.icon_file
        self.ini['GLOBAL']['alert_wav'] = self.alert_wav
        self.ini['GLOBAL']['festival_type_voice_synth'] = self.festival_type_voice_synth
        self.ini['GLOBAL']['qr_code_generator'] = self.qr_code_generator
        self.ini['GLOBAL']['browser'] = self.browser
        self.ini['GLOBAL']['current_tab_visual'] = MAIN_WIN.tabs.tab_wgt.get_current_tab_visual()
        self.ini['GLOBAL']['week_first_day'] = str(self.week_first_day)
        for (sect, tab_dd_path, tab_ndx_current_row) in self.tabs:
            self.ini[sect] = {}
            self.ini[sect]['file'] = str(tab_dd_path)
            self.ini[sect]['row'] = str(tab_ndx_current_row)
        self.ini_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ini_path, 'w') as unit:
            self.ini.write(unit)
        return self

    @property
    def geometry_hex(self):
        return self._geometry
    @geometry_hex.setter
    def geometry_hex(self, x):
        self._geometry = x

    @property
    def geometry_byt(self):
        return bytes.fromhex(self._geometry)
    @geometry_byt.setter
    def geometry_byt(self, x):
        self._geometry = bytes(x).hex()

    @property
    def state_hex(self):
        return self._state
    @state_hex.setter
    def state_hex(self, x):
        self._state = x

    @property
    def state_byt(self):
        return bytes.fromhex(self._state)
    @state_byt.setter
    def state_byt(self, x):
        self._state = bytes(x).hex()

    def register_default_browser(self, name=None):
        if name in BLANK_VALUES:
            pass
        elif name in [
                'most common',
                ]:
            pass
        elif name in [
                'mozilla',
                'firefox',
                'netscape',
                'galeon',
                'epiphany',
                'skipstone',
                'fkmclient',
                'konqueror',
                'kfm',
                'mosaic',
                'opera',
                'grail',
                'links',
                'elinks',
                'lynx',
                'w3m',
                'windows-default',
                'macosx',
                'safari',
                'google-chrome',
                'chrome',
                'chromium',
                'chromium-browser',
                ]:
            pass
        else:
            webbrowser.register(
                name, None,
                instance=webbrowser.GenericBrowser(name),
                )
        return self


class Ledger(q0.Q0LedgerSorted):

    """Adaptation of q0 Sorted Ledger.

    This provides methods for sorting and for detecting the
    double-click shortcut.

    """    
    
    def section_clicked(self, ndx_col):
        super().section_clicked(ndx_col)
        order = self.get_sort_indicator(ndx_col)
        is_descending = order in ['descending']
        tag = self.get_tag(ndx_col)
        if tag in BLANK_VALUES:
            pass
        else:
            self.tab.rel.sort(tag, is_descending)
            self.tab.reset()
        return self

    def mouse_click(self, event, ndx_row, ndx_col, x, y):
        if q0.Q0_MNEMONIC_MOUSE_BUTTON[event.button()] in ['right']:
            MAIN_WIN.menu_popup.exec_(event.globalPos())
        elif (q0.Q0_MNEMONIC_MOUSE_BUTTON[event.button()] in ['left']) and (ndx_col is ZERO):
            self.tab.toggle_mark(ndx_row)
        return self

    def mouse_double_click(self, event, ndx_row, ndx_col, x, y):
        MAIN_WIN.event_field_entry()
        return self


class RowMark(ItmCoded):

    """This is a special item.

    It is displayed at the left edge of every record on the ledger
    widget, but it is a control.  It is not stored.

    """
        
    def __init__(self, code_table='BALLOT_BOX'):
        super().__init__(tag=NULL, code_table=code_table)
        return

    
class Tab:

    """A Main Window Tab.

    This owns the ledger widget and the relation.  It invokes
    serialization for the relation.

    """    
    
    def __init__(self, tag, path, ndx_current_row=ZERO):
        self.tag = tag
        self.path_dd = coerce_suffix(path, '.dd')
        self.path_csv = coerce_suffix(path, '.csv')
        self.ndx_current_row = ndx_current_row
        self.wgt = None
        self.rel = None
        return

    def load_rel(self):
        with KeyValSer(self.path_dd) as unit_dd:
            rel_type = unit_dd.get(' rel_type')
            rel_cls = REL_NAME_CLASS[rel_type]
            self.rel = rel_cls()
            self.rel.load(unit_dd)
        with open(self.path_csv) as unit_csv:
            self.rel.load_recs(unit_csv)
        return self

    def save_rel(self, tags=None):
        self.rel.tag = self.tag
        if tags:
            self.rel.display_tags = tags
        else:
            self.rel.display_tags = [tag for tag in self.ledger.q0_view.q0_header.get_fld_tags_left_to_right() if tag not in BLANK_VALUES]
        with KeyValSer(self.path_dd, 'w') as unit_dd:
            rel_type = REL_CLASS_NAME[type(self.rel)]
            unit_dd.put(' rel_type', rel_type)
            self.rel.save(unit_dd)
        if self.rel.rel_is_dirty:
            with open(self.path_csv, 'w') as unit_csv:
                self.rel.save_recs(unit_csv)
        return self

    def ledger_fill(self):
        self.ledger = Ledger(self.wgt, is_editable=False)
        self.ledger.tab = self
        self.ledger_layout()
        self.wgt.add_wgt(self.ledger.get_view())
        self.reset()
        return self

    def ledger_layout(self):

        def fld(tag):

            """Among other things this function invokes the ledger font.

            The default font for Gnome 3 on Debian Linux 11 "Bullseye"
            is Cantarell.  Although this font possesses tabular digit
            glyphs, they are not default.  The default is proportional
            digits, which is not suitable for the Q0LedgerView widget.

            We suggest [Noto Sans
            Semicondensed](https://en.wikipedia.org/wiki/Noto_fonts),
            instead.  It's a free font (**No**t **To**fu) bundled with
            LibreOffice whose creation was funded by Google.

            Indeed there appears to be no QFont style option (yet)
            corresponding to CSS "font-variant-numeric:tabular-nums"
            to request tabular digits from fonts that default to
            proportional digits.

            """
            
            result = q0.Q0Fld(
                tag=tag,
                label=tag,
                is_enabled=True,
                q0_font=q0.Q0Font(COMMON['CONFIG'].ledger_font, 11),
                )
            return result
        
        flds = [fld(tag) for tag in self.rel.display_tags]
        fld_mark = q0.Q0Fld(
            tag=NULL,
            label=NULL,
            is_enabled=True,
            q0_font=q0.Q0Font(COMMON['CONFIG'].ledger_font, 16),
            )
        flds.insert(ZERO, fld_mark)
        self.ledger.layout(flds)
        return self

    def reset(self):
        store = self.rel.pages.conjure_itm_by_tag()
        store[NULL] = RowMark()
        self.ledger.begin_reset_model()
        self.ledger.rows.clear()
        for (ndx, row) in enumerate(self.rel.recs):
            row_disp = self.rel.stage_rec(ndx)
            for tag in [NULL]:
                store[tag].val_comp = 'X'
                row_disp[tag] = store[tag].val_edit
            self.ledger.add_row(row_disp)
        self.ledger.end_reset_model()
        return self

    def toggle_mark(self, ndx_row):
        row_mark = RowMark()
        row_mark.val_edit = self.ledger.rows[ndx_row][NULL]
        row_mark.val_inc()
        self.ledger.rows[ndx_row][NULL] = row_mark.val_edit
        self.ledger.reset_row_tag(ndx_row, NULL)
        return self

    def set_mark(self, ndx_row, val=True):
        row_mark = RowMark()
        if val:
            row_mark.val_comp = 'T'
        else:
            row_mark.val_comp = 'F'
        self.ledger.rows[ndx_row][NULL] = row_mark.val_edit
        self.ledger.reset_row_tag(ndx_row, NULL)
        return self

    def has_mark(self, ndx_row):
        row_mark = RowMark()
        row_mark.val_edit = self.ledger.rows[ndx_row][NULL]
        result = row_mark.val_comp in ['T']
        return result


class TabList(dict):

    """The list of Main Window Tabs.

    This provides serialization.

    """    
    
    def load(self, cent_wgt):
        cent_wgt.push(q0_layout='tabs')
        for (tag, path, ndx_current_row) in COMMON['CONFIG'].tabs:
            tab = Tab(tag, path, ndx_current_row)
            tab.load_rel()
            tab.wgt = cent_wgt.add_tab(q0_visual=tag)
            tab.ledger_fill()
            self[tag] = tab
        self.tab_wgt = cent_wgt.pop()  # tabs
        return self

    def save(self):
        COMMON['CONFIG'].tabs.clear()
        for tag in self.tab_wgt.get_tab_tags_left_to_right():
            tab = self[tag]
            entry = (tab.tag, tab.path_dd, tab.ndx_current_row)
            COMMON['CONFIG'].tabs.append(entry)
            tab.save_rel()
        return self

    def check_dups(self, tag_target=None, path_target=None):
        result = None
        for key in self.tab_wgt.get_tab_tags_left_to_right():
            if key in BLANK_VALUES:
                pass
            else:
                tab = self[key]
                if tag_target == tab.tag:
                    result = _('There is an open tab with tag "{v0}."').format(v0=tag_target)
                    break
                if path_target == tab.path_dd:
                    result = _('There is an open relation using "{v0}."').format(v0=path_target)
                    break
        return result


class MainWindow(q0.Q0MainWindow):

    """The Main Window.

    This inherits context-manager methods.

    """
        
    def __init__(self):
        super().__init__(q0_visual='Tonto2')
        self.restoreGeometry(COMMON['CONFIG'].geometry_byt)
        self.restoreState(COMMON['CONFIG'].state_byt)
        self.main_wgts = {}
        return

    def build_menu_bar(self):
        self.menu_bar = self.set_menu_bar(q0.Q0MenuBar())
        menu_bar = self.menu_bar

        menu_bar.push(_('File'), has_tool_tips=True)

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('New...'),
            q0_shortcut='Ctrl+N',
            q0_tool_tip = _('Create a tab from a new file.'),
            event=self.event_new,
            ))
        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Open...'),
            q0_shortcut='Ctrl+O',
            q0_tool_tip = _('Create a tab from an existing file.'),
            event=self.event_open,
            ))
        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Close'),
            q0_shortcut='Ctrl+W',
            q0_tool_tip = _('Remove a tab.'),
            event=self.event_close,
            ))
        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Checkpoint'),
            q0_shortcut='Ctrl+S',
            q0_tool_tip = _('Save changes.'),
            event=self.event_checkpoint,
            ))

        menu_bar.add_sep()

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Revert'),
            q0_shortcut='Ctrl+Z',
            q0_tool_tip=_('Discard changes.'),
            event=self.event_revert,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Extend...'),
            q0_tool_tip=_('''Append a *.csv file.  This is not a "join".  This appends records
from the merged file.  Items (fields, columns) in the merged file that
are not in the current relation are appended as text items.'''),
            event=self.event_merge,
            ))

        menu_bar.add_sep()

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Add/Change/Remove Fields...'),
            q0_tool_tip=_('Change what data is kept.'),
            event=self.event_add_change_remove_items,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Rename...'),
            q0_tool_tip=_('Change the visual label on the tab.'),
            event=self.event_rename,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Choose Display Columns...'),
            q0_tool_tip=_('Change appearance of the list'),
            event=self.event_choose_display_columns,
            ))

        menu_bar.add_sep()
        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Quit'),
            q0_shortcut='Ctrl+Q',
            q0_tool_tip = _('Save changes and exit.'),
            event=self.event_quit,
            ))

        menu_bar.pop()
        menu_bar.push(_('Edit'), has_tool_tips=True)

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Search/Replace...'),
            q0_shortcut='Ctrl+F',
            q0_tool_tip=_('Find words (and change them).'),
            event=self.event_search_replace,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Go to Row...'),
            q0_tool_tip=_('Choose a line number.'),
            event=self.event_go_to_row,
            ))

        menu_bar.add_sep()

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Insert Before Row'),
            q0_shortcut='Ctrl+I',
            q0_tool_tip=_('Create a blank line above.'),
            event=self.event_insert_before_row,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Insert After Row'),
            q0_shortcut='Shift+Ctrl+I',
            q0_tool_tip=_('Create a blank line below.'),
            event=self.event_insert_after_row,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Insert at Top'),
            q0_tool_tip=_('Create a blank line at the beginning.'),
            event=self.event_insert_at_top,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Insert at Bottom'),
            q0_tool_tip=_('Create a blank line at the end.'),
            event=self.event_insert_at_bottom,
            ))

        menu_bar.add_sep()
        
        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Free-Form Entry'),
            q0_tool_tip=_('Paste-in a blob of text.'),
            event=self.event_free_form_entry,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Field Entry'),
            q0_tool_tip=_('Fill-in blanks.'),
            event=self.event_field_entry,
            ))

        menu_bar.add_sep()

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Cut Row'),
            q0_shortcut='Ctrl+X',
            q0_tool_tip=_('Remove row to clipboard.'),
            event=self.event_cut_row,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Copy Row'),
            q0_shortcut='Ctrl+C',
            q0_tool_tip=_('Copy row to clipboard.'),
            event=self.event_copy_row,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Paste Before'),
            q0_shortcut='Ctrl+V',
            q0_tool_tip=_('Insert row(s) from clipboard above current line.'),
            event=self.event_paste_before_row,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Paste After'),
            q0_shortcut='Shift+Ctrl+V',
            q0_tool_tip=_('Insert row(s) from clipboard below current line.'),
            event=self.event_paste_after_row,
            ))

        menu_edit = menu_bar.pop()
        menu_edit.aboutToShow.connect(self.event_show_menu_edit)
        menu_bar.push(_('View'), has_tool_tips=True)

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('View as Text'),
            q0_tool_tip=_('Show contents of selected row as blob of text.'),
            event=self.event_display_as_text,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Traverse Link'),
            q0_tool_tip=_('Open web page in browser.'),
            event=self.event_traverse_link,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('View Calendar Month'),
            q0_tool_tip=_('Show contents of selected tab as a monthly calendar.'),
            event=self.event_calendar_month,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('View Alarms'),
            q0_tool_tip=_('Show alarms set to go off today.'),
            event=self.event_alarms,
            ))

        self.menu_view = menu_bar.pop()
        self.menu_view.aboutToShow.connect(self.event_show_menu_view)
        menu_bar.push(_('Mark'), has_tool_tips=True)

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Toggle Row Mark'),
            q0_tool_tip=_('Checked vs unchecked.'),
            event=self.event_mark_toggle,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Mark All Rows'),
            q0_tool_tip=_('Check all.'),
            event=self.event_mark_all,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Toggle All Rows'),
            q0_tool_tip=_('Reverse all checkmarks.'),
            event=self.event_mark_toggle_all,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Cut Marked Rows'),
            q0_tool_tip=_('Remove checked rows to clipboard.'),
            event=self.event_cut_marked_rows,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Copy Marked Rows'),
            q0_tool_tip=_('Copy checked rows to clipboard.'),
            event=self.event_copy_marked_rows,
            ))

        menu_bar.pop()
        menu_bar.push(_('Help'), has_tool_tips=True)

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('Contents'),
            q0_shortcut='Ctrl+H',
            q0_tool_tip=_('Browse *Tonto* manual'),
            event=self.event_contents,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('GNU General Public License'),
            q0_tool_tip=_('View statement of copying permission.'),
            event=self.event_gpl,
            ))

        menu_bar.add_action(q0.Q0Action(
            q0_visual=_('About'),
            q0_tool_tip=_('Show version number.'),
            event=self.event_about,
            ))
        
        return self

    def build_menu_popup(self):
        self.menu_popup = q0.Q0Menu()

        self.menu_popup.add_action(q0.Q0Action(
            q0_visual=_('View as Text'),
            q0_tool_tip=_('Show contents of selected row as blob of text.'),
            event=self.event_display_as_text,
            ))

        self.menu_popup.add_action(q0.Q0Action(
            q0_visual=_('Traverse Link'),
            q0_tool_tip=_('Open web page in browser.'),
            event=self.event_traverse_link,
            ))

        self.menu_popup.add_sep()
        
        self.menu_popup.add_action(q0.Q0Action(
            q0_visual=_('Insert Before Row'),
            q0_tool_tip=_('Create a blank line above.'),
            event=self.event_insert_before_row,
            ))

        self.menu_popup.add_action(q0.Q0Action(
            q0_visual=_('Insert After Row'),
            q0_tool_tip=_('Create a blank line below.'),
            event=self.event_insert_after_row,
            ))

        self.menu_popup.add_action(q0.Q0Action(
            q0_visual=_('Insert at Top'),
            q0_tool_tip=_('Create a blank line at the beginning.'),
            event=self.event_insert_at_top,
            ))

        self.menu_popup.add_action(q0.Q0Action(
            q0_visual=_('Insert at Bottom'),
            q0_tool_tip=_('Create a blank line at the end.'),
            event=self.event_insert_at_bottom,
            ))

        self.menu_popup.aboutToShow.connect(self.event_show_menu_popup)

        return self

    def closing(self, q0_event):
        self.tabs.save()
        COMMON['CONFIG'].geometry_byt = self.saveGeometry()
        COMMON['CONFIG'].state_byt = self.saveState()
        COMMON['CONFIG'].current_tab_visual = self.tabs.tab_wgt.get_current_tab_visual()
        return super().closing(q0_event)

    def event_quit(self):
        self.close()
        return

    def event_new(self):
        dlg = DlgNewRel(tab_list=self.tabs)
        if dlg.run_audit_loop():
            tag = dlg.edt_name.get_visual()
            name_i18n = dlg.q0_cls.get_visual()
            path = dlg.path
            tab = Tab(tag=tag, path=path)
            tab.rel = REG_RELS.lookup_i18n(name_i18n).cls().conjure_pages()
            if isinstance(tab.rel, RelCalendar):
                tab.rel.initialize_holidays()
            tab.rel.rel_is_dirty = True
            self.tabs[tag] = tab
            tabs_wgt = self.tabs.tab_wgt
            tab.wgt = tabs_wgt.add_tab(q0_visual=tag)
            tab.ledger_fill()
        return
    
    def event_open(self):
        dlg = q0.Q0FileDialog(
            q0_title='Open',
            q0_file_mode='exists',
            name_filters=['Tonto Data Definition (*.dd)'],
            )
        file_names = dlg.get_selected_files()
        if file_names:
            path = pathlib.Path(file_names[ZERO])
            tab = Tab(NULL, path)
            try:
                tab.load_rel()
            except AssertionError:
                q0.Q0MessageBox(
                    q0_icon='critical',
                    q0_title=_('Error'),
                    q0_visual=_('Path "{v0}" has wrong version.'.format(v0=path)),
                    ).exec_()
            if tab.rel:
                tab.tag = tab.rel.tag
                msg = self.tabs.check_dups(tag_target=tab.tag, path_target=tab.path_dd)
                if msg:
                    q0.Q0MessageBox(
                        q0_icon='critical',
                        q0_title=_('Error'),
                        q0_visual=msg,
                    ).exec_()
                else:
                    tab.wgt = self.tabs.tab_wgt.add_tab(q0_visual=tab.tag)
                    tab.ledger_fill()
                    self.tabs[tab.tag] = tab
        return
    
    def event_close(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            tab_current.save_rel()
            self.tabs.tab_wgt.del_tab(tab_current.wgt)
        return

    def event_checkpoint(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            tab_current.save_rel()
        return

    def event_revert(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            tab_current.load_rel()
            tab_current.reset()
        return

    def event_merge(self):

        def conjure_extended_rel(rel_old, path_dd, path_csv):
            result = Rel()
            if path_dd.exists():
                try:
                    with KeyValSer(path_dd) as unit:
                        dummy = unit.get(' rel_type')
                        result = result.load(unit)
                except AssertionError:  # Version mismatch, probably.
                    pass
            with open(path_csv) as unit:
                reader = csv.DictReader(unit)
                result.recs = RecsStorage().load(reader)
                result.pages.append([])
                ndx_page = len(result.pages) - 1
                for tag in reader.fieldnames:
                    itm = result.pages.find(tag)
                    if itm:
                        pass
                    else:
                        itm = ItmText(tag)
                        ndx_itm = len(result.pages[ndx_page])
                        result.pages[ndx_page].insert(ndx_itm, itm)
            return result

        def merge_dd(rel_old, rel_ext):
            rel_old.pages.append([])
            ndx_page = len(rel_old.pages) - 1
            for (itm_ext, ndx_page, ndx_itm) in rel_ext.pages.get_next_itm():
                tag = itm_ext.tag
                itm_old = rel_old.pages.find(tag)
                if itm_old:
                    pass
                else:
                    cls = type(itm_ext)
                    itm_new = cls().clone(itm_ext)
                    ndx_itm = len(rel_old.pages[ndx_page])
                    rel_old.pages[ndx_page].insert(ndx_itm, itm_new)
            return

        def merge_csv(rel_old, rel_ext):
            for (ndx_old, rec) in enumerate(rel_old.recs):
                rel_old.stage_rec(ndx_old)
                rel_old.destage_rec(ndx_old, update_timestamp=False)
            for (ndx_ext, rec) in enumerate(rel_ext.recs):
                rel_ext.stage_rec(ndx_ext)
                ndx_old = len(rel_old.recs)
                rel_old.new_rec(ndx_old)
                for (itm_ext, ndx_page, ndx_itm) in rel_ext.pages.get_next_itm():
                    tag = itm_ext.tag
                    itm_old = rel_old.pages.find(tag)
                    try:
                        itm_old.val_store = itm_ext.val_store
                    except ValueError:
                        print(
                            _('Relation {v0} rec[{v1}]["{v2}"]={v3}, but this is not valid.  Using default={v4}.').format(
                                v0=rel_old.tag,
                                v1=ndx_ext,
                                v2=tag,
                                v3=repr(itm_ext.val_store),
                                v4=repr(itm_old.val_default),
                                )
                            ) 
                        itm_old.val_store = itm_old.val_default
                rel_old.destage_rec(ndx_old)
            return 
        
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            rel_old = tab_current.rel
            dlg = q0.Q0FileDialog(
                q0_title='CSV File',
                q0_file_mode='exists',
                name_filters=['Tonto Data Definition (*.csv)'],
                )
            file_names = dlg.get_selected_files()
            if file_names:
                path = pathlib.Path(file_names[ZERO])
                path_dd = coerce_suffix(path, '.dd')
                path_csv = coerce_suffix(path, '.csv')
                rel_ext = conjure_extended_rel(rel_old, path_dd, path_csv)
                merge_dd(rel_old, rel_ext)
                merge_csv(rel_old, rel_ext)
                rel_old.rel_is_dirty = True
                tab_current.reset()
        return

    def event_rename(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            new_tag = DlgRename(tab_current=tab_current, tab_list=self.tabs).run_audit_loop()
            if new_tag:
                tab_current.tag = new_tag
                del self.tabs[tab_current_text]
                self.tabs[new_tag] = tab_current
                wgt = self.tabs.tab_wgt
                all_tags = wgt.get_tab_tags_left_to_right()
                ndx = all_tags.index(tab_current_text)
                wgt.set_tab_visual(ndx, new_tag)
        return

    def event_add_change_remove_items(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            DlgChgItms(tab=tab_current, ndx_row=ndx_row, ndx_col=ndx_col).run_audit_loop()
        return

    def event_choose_display_columns(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            DlgChooseDisplayCols(tab=tab_current, ndx_row=ndx_row, ndx_col=ndx_col).run_audit_loop()
        return

    def event_show_menu_edit(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            has_clipboard = not (COMMON['RECS_CUT'].contents in BLANK_VALUES)
            has_free_form_entry = hasattr(tab_current.rel, 'free_form_entry')
            action = self.menu_bar.q0_actions[_('Paste Before')]
            if has_clipboard:
                action.set_enabled(True)
            else:
                action.set_enabled(False)
            action = self.menu_bar.q0_actions[_('Paste After')]
            if has_clipboard:
                action.set_enabled(True)
            else:
                action.set_enabled(False)
            action = self.menu_bar.q0_actions[_('Free-Form Entry')]
            if has_free_form_entry:
                action.set_enabled(True)
            else:
                action.set_enabled(False)
        return

    def event_search_replace(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            dlg = DlgSearchReplace(tab=tab_current)
            dlg.run_audit_loop()
        return

    def event_go_to_row(self):
        ndx_row = DlgSkipToRow().run_audit_loop()
        if ndx_row is None:
            pass
        else:
            tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
            tab_current = self.tabs.get(tab_current_text)
            if tab_current:
                tab_current.ledger.set_current_row_col(ndx_row - 1, ZERO)
        return

    def event_insert_before_row(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            tab_current.rel.new_rec(ndx_row)
            tab_current.reset()
            tab_current.ledger.set_current_row_col(ndx_row, ndx_col)
        return

    def event_insert_after_row(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            tab_current.rel.new_rec(ndx_row + 1)
            tab_current.reset()
            tab_current.ledger.set_current_row_col(ndx_row + 1, ndx_col)
        return

    def event_insert_at_top(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            tab_current.rel.new_rec(ZERO)
            tab_current.reset()
            tab_current.ledger.set_current_row_col(ZERO, ZERO)
        return

    def event_insert_at_bottom(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            pos = len(tab_current.rel.recs)
            tab_current.rel.new_rec(pos)
            tab_current.reset()
            tab_current.ledger.set_current_row_col(pos, ZERO)
        return

    def event_free_form_entry(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            tab_current.rel.stage_rec(ndx_row)
            response = DlgFreeformEntry(rel=tab_current.rel).run_audit_loop()
            if response:
                row_disp = tab_current.rel.destage_rec(ndx_row)
                tab_current.ledger.rows[ndx_row] = row_disp
                row_mark = RowMark()
                row_mark.val_comp = 'X'
                tab_current.ledger.rows[ndx_row][NULL] = row_mark.val_edit
                tab_current.ledger.reset_row(ndx_row)
                tab_current.ledger.set_current_row_col(ndx_row, ndx_col)
        return

    def event_field_entry(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            tab_current.rel.stage_rec(ndx_row)
            response = DlgFieldEntry(rel=tab_current.rel).run_audit_loop()
            if response:
                row_disp = tab_current.rel.destage_rec(ndx_row)
                tab_current.ledger.rows[ndx_row] = row_disp
                row_mark = RowMark()
                row_mark.val_comp = 'X'
                tab_current.ledger.rows[ndx_row][NULL] = row_mark.val_edit
                tab_current.ledger.reset_row(ndx_row)
                tab_current.ledger.set_current_row_col(ndx_row, ndx_col)
        return

    def event_cut_row(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            rec = tab_current.rel.recs.pop(ndx_row)
            x = json.dumps([rec])
            COMMON['RECS_CUT'].contents = x
            tab_current.reset()
            tab_current.ledger.set_current_row_col(ndx_row, ndx_col)
            tab_current.rel.rel_is_dirty = True
        return

    def event_copy_row(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            rec = tab_current.rel.recs[ndx_row]
            x = json.dumps([rec])
            COMMON['RECS_CUT'].contents = x
        return

    def event_paste_before_row(self):
        x = COMMON['RECS_CUT'].contents
        recs = json.loads(x)
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            for (pos, rec) in enumerate(recs):
                tab_current.rel.recs.insert(ndx_row + pos, rec)
                tab_current.reset()
                tab_current.ledger.set_current_row_col(ndx_row + 1 + pos, ndx_col)
                tab_current.rel.rel_is_dirty = True
        return

    def event_paste_after_row(self):
        x = COMMON['RECS_CUT'].contents
        recs = json.loads(x)
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            for (pos, rec) in enumerate(recs):
                tab_current.rel.recs.insert(ndx_row + 1 + pos, rec)
                tab_current.reset()
                tab_current.ledger.set_current_row_col(ndx_row, ndx_col)
                tab_current.rel.rel_is_dirty = True
        return

    def event_display_as_text(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            if ndx_row < ZERO:
                pass
            else:
                tab_current.rel.stage_rec(ndx_row)
                DlgViewText(rel=tab_current.rel).run_audit_loop()
                row_disp = tab_current.rel.destage_rec(ndx_row)  # Save _Traversed_Date.
                tab_current.ledger.rows[ndx_row] = row_disp
                row_mark = RowMark()
                row_mark.val_comp = 'X'
                tab_current.ledger.rows[ndx_row][NULL] = row_mark.val_edit
                tab_current.ledger.reset_row(ndx_row)
                tab_current.ledger.set_current_row_col(ndx_row, ndx_col)
        return

    def event_traverse_link(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            itm_uri = tab_current.rel.pages.find(TAG__URI)
            if itm_uri:
                (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
                tab_current.rel.stage_rec(ndx_row)
                link = itm_uri.val_comp
                if link in BLANK_VALUES:
                    pass
                else:
                    browser_open_tab(uri=itm_uri.val_comp)
                    tab_current.rel.destage_rec(ndx_row)
        return

    def event_calendar_month(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        self.alarms = Alarms()
        if tab_current:
            for (ndx_rec, rec) in enumerate(tab_current.rel.recs):
                tab_current.rel.stage_rec(ndx_rec)
                alarm = Alarm(parent_rel=tab_current.rel).create_from_rec()
                self.alarms.append(alarm)
        self.call_calendar_month()
        return

    def call_calendar_month(self, date=datetime.date.today()):
        DlgCalendarMonth(date).run_audit_loop()
        return

    def event_alarms(self):
        COMMON['ALARMS'].sort()
        l0 = len(COMMON['ALARMS'])
        if l0 is ZERO:
            a0 = _('There are no events scheduled.')
        elif l0 == 1: 
            a0 = _('There is one scheduled event:')
        else:
            a0 = _('There are {v0} scheduled events:').format(v0=l0)
        q0.Q0MessageBox(
            q0_icon='information',
            q0_title=_('Events'),
            q0_visual=a0,
            q0_informative_text=str(COMMON['ALARMS']),
            ).exec_()
        return

    def event_show_menu_view(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            has_uri = tab_current.rel.pages.find(TAG__URI)
            is_calendar = isinstance(tab_current.rel, RelCalendar)
            action = self.menu_bar.q0_actions[_('Traverse Link')]
            if has_uri:
                action.set_enabled(True)
            else:
                action.set_enabled(False)
            action = self.menu_bar.q0_actions[_('View Calendar Month')]
            if is_calendar:
                action.set_enabled(True)
            else:
                action.set_enabled(False)
            action = self.menu_bar.q0_actions[_('View Alarms')]
            action.set_enabled(True)
        return

    def event_mark_toggle(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            (ndx_row, ndx_col) = tab_current.ledger.get_current_row_col()
            tab_current.toggle_mark(ndx_row)
        return

    def event_mark_all(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            tab_current.ledger.begin_reset_model()
            for (ndx_row, row) in enumerate(tab_current.ledger.rows):
                tab_current.set_mark(ndx_row)
            tab_current.ledger.end_reset_model()
        return

    def event_mark_toggle_all(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            tab_current.ledger.begin_reset_model()
            for (ndx_row, row) in enumerate(tab_current.ledger.rows):
                tab_current.toggle_mark(ndx_row)
            tab_current.ledger.end_reset_model()
        return

    def event_cut_marked_rows(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            manifest = []
            collection = []
            if tab_current:
                for (ndx_row, row) in enumerate(tab_current.ledger.rows):
                    if tab_current.has_mark(ndx_row):
                        manifest.append(ndx_row)
            manifest.reverse()
            for ndx_row in manifest:
                rec = tab_current.rel.recs.pop(ndx_row)
                collection.append(rec)
            collection.reverse()
            x = json.dumps(collection)
            COMMON['RECS_CUT'].contents = x
            tab_current.reset()
            tab_current.ledger.set_current_row_col(ZERO, ZERO)
            tab_current.rel.rel_is_dirty = True
        return

    def event_copy_marked_rows(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            manifest = []
            collection = []
            if tab_current:
                for (ndx_row, row) in enumerate(tab_current.ledger.rows):
                    if tab_current.has_mark(ndx_row):
                        manifest.append(ndx_row)
            manifest.reverse()
            for ndx_row in manifest:
                rec = tab_current.rel.recs[ndx_row]
                collection.append(rec)
            collection.reverse()
            x = json.dumps(collection)
            COMMON['RECS_CUT'].contents = x
        return

    def event_contents(self):
        browser_open_tab(f'https://lacusveris.com/Tonto2/Docs/en/', can_update_traversed_date=False)
        return

    def event_gpl(self):
        q0.Q0MessageBox(
            q0_icon='information',
            q0_title=_('Gnu General Public License'),
            q0_informative_text=__doc__,
            ).exec_()
        return

    def event_about(self):
        q0.Q0MessageBox(
            q0_icon='information',
            q0_title=_('About'),
            q0_informative_text=MD_SUMMARY + MD_CONTACT,
            ).exec_()
        return

    def event_show_menu_popup(self):
        tab_current_text = self.tabs.tab_wgt.get_current_tab_visual()
        tab_current = self.tabs.get(tab_current_text)
        if tab_current:
            has_uri = tab_current.rel.pages.find(TAG__URI)
            action = self.menu_popup.q0_actions[_('Traverse Link')]
            if has_uri:
                action.set_enabled(True)
            else:
                action.set_enabled(False)
        return


class DlgRename(q0.Q0DialogModal):

    """Dialog to rename the selected tab.

    """    
    
    def __init__(self, tab_current, tab_list, q0_visual=_('Rename Tab')):
        super().__init__(q0_visual=q0_visual)
        self.tabs = tab_list
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.push(q0_layout='form')
        (lbl_row, self.edt_name) = cent_wgt.add_row(q0.Q0Label(_('Name')), q0.Q0LineEdit())
        self.edt_name.set_visual(tab_current.tag)
        cent_wgt.pop()  # form
        cent_wgt.push(q0_layout='hbox', is_just_right=True)
        button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox())
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        cent_wgt.pop()  # hbox
        return

    def audit(self):
        result = self.edt_name.get_visual()
        if result in BLANK_VALUES:
            result = None
        if result:
            pass
        else:
            q0.Q0MessageBox(
                q0_icon='critical',
                q0_title=_('Error'),
                q0_visual=_('Please provide a new name for the tab.'),
                ).exec_()
        msg = self.tabs.check_dups(tag_target=result)
        if msg:
            q0.Q0MessageBox(
                q0_icon='critical',
                q0_title=_('Error'),
                q0_visual=msg,
                ).exec_()
            result=None
        return result

    
class DlgNewRel(q0.Q0DialogModal):

    """Dialog to create a new tab from scratch.

    """    
    
    def __init__(self, tab_list, q0_visual=_('New Tab')):
        super().__init__(q0_visual=q0_visual)
        self.tabs = tab_list
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.push(q0_layout='form', is_just_right=True)
        (lbl_row, self.edt_name) = cent_wgt.add_row(q0.Q0Label(_('Name')), q0.Q0LineEdit())
        (lbl, self.q0_cls) = cent_wgt.add_row(q0.Q0Label(_('Type')), q0.Q0ComboBox(is_editable=False))
        q0_list_classes = list(REG_RELS.values())
        for (pos, rel) in enumerate(q0_list_classes):
            self.q0_cls.add_item(q0_visual=rel.name_i18n, pos=pos)
            self.q0_cls.set_item_tool_tip(rel.description, pos=pos)
        cent_wgt.pop()  # form
        cent_wgt.push(q0_layout='hbox', is_just_right=True)
        button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox())
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        cent_wgt.pop()  # hbox
        return

    def audit(self):
        tag = super().audit()
        if tag:
            result = True
        else:
            result = None
        if result:
            dlg = q0.Q0FileDialog(
                q0_title='New',
                q0_file_mode='any',
                name_filters=['Tonto Data Definition (*.dd)'],
                )
            file_names = dlg.get_selected_files()
            if file_names:
                self.path = pathlib.Path(file_names[ZERO])
                path_dd = coerce_suffix(self.path, '.dd')
                path_csv = coerce_suffix(self.path, '.csv')
                if path_dd.exists():
                    q0.Q0MessageBox(
                        q0_icon='critical',
                        q0_title=_('Error'),
                        q0_visual=_('Path "{v0}" already exists.').format(v0=path_dd),
                        ).exec_()
                    self.path = None
                elif path_csv.exists():
                    q0.Q0MessageBox(
                        q0_icon='critical',
                        q0_title=_('Error'),
                        q0_visual=_('Path "{v0}" already exists.').format(v0=path_csv),
                        ).exec_()
                    self.path = None
                else:
                    pass    
            else:
                self.path = None
        if self.path:
            result = True
        else:
            result = None
        return result

    
class DlgSkipToRow(q0.Q0DialogModal):

    """Dialog to skip to a record number on the selected tab.

    """    
    
    def __init__(self):
        super().__init__(q0_visual=_('Skip to Row'))
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.push(q0_layout='form')
        (lbl_row, self.edt_row) = cent_wgt.add_row(q0.Q0Label(_('Row Number')), q0.Q0LineEdit())
        cent_wgt.pop()  # form
        cent_wgt.push(q0_layout='hbox', is_just_right=True)
        button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox())
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        cent_wgt.pop()  # hbox
        return

    def audit(self):
        try:
            result = int(self.edt_row.get_visual())
        except ValueError:
            result = None
        if (result in [None]) or (result <= ZERO):
            q0.Q0MessageBox(
                q0_icon='critical',
                q0_title=_('Error'),
                q0_visual=_('Row Number must be a positive integer.'),
                ).exec_()
            result = None
        return result        


class DlgFieldEntry(q0.Q0DialogModal):

    """Field-Entry Dialog.

    """    
    
    def __init__(self, rel):
        self.rel = rel
        super().__init__(q0_visual=self.rel.tag)
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.push(q0_layout='stacked')
        self.count_pages = len(self.rel.pages)
        for (ndx_page, page) in enumerate(self.rel.pages):
            self.stack_page(cent_wgt, page, ndx_page + 1, self.count_pages)
        self.page_layers = cent_wgt.pop()  # stacked
        return

    def stack_page(self, cent_wgt, page, ndx_page, count_pages):
        layer = cent_wgt.add_layer()
        layer.push(q0_layout='vbox')
        layer.push(q0_layout='form', is_just_right=True)
        for itm in page:
            itm.conjure_form_entry(layer, align='top')
        layer.pop()  # form
        layer.push(q0_layout='hbox', is_just_right=True)
        layer.add_wgt(q0.Q0Label(_('Page {v0} of {v1}').format(v0=ndx_page, v1=count_pages),q0_font=q0.Q0Font(COMMON['CONFIG'].ledger_font, 11)))
        button_box = layer.add_wgt(q0.Q0DialogButtonBox(q0_buttons=[]))
        btn = button_box.add_button(q0.Q0PushButton(_('← Previous'), event_clicked=self.prev))
        btn = button_box.add_button(q0.Q0PushButton(_('Next →'), event_clicked=self.next))
        btn = button_box.add_qt_standard_button(q0.Q0_CODE_DLGBOX_BUTTONS['cancel'])
        btn = button_box.add_qt_standard_button(q0.Q0_CODE_DLGBOX_BUTTONS['ok'])
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layer.pop()  # hbox
        layer.pop()  # vbox
        return self

    def audit(self):
        for (itm, ndx_page, ndx_itm) in self.rel.pages.get_next_itm():
            self.page_layers.setCurrentIndex(ndx_page)
            try:
                itm.digest_form_entry()
            except Error as e:
                q0.Q0MessageBox(
                    q0_icon='critical',
                    q0_title=_('Error'),
                    q0_visual=str(e),
                    ).exec_()
                result = None
                break
        else:
            result = True
        return result

    def prev(self):
        ndx = self.page_layers.currentIndex()
        ndx -= 1
        if ndx < ZERO:
            ndx = self.count_pages - 1
        self.page_layers.setCurrentIndex(ndx)
        return self

    def next(self):
        ndx = self.page_layers.currentIndex()
        ndx += 1
        if ndx >= self.count_pages:
            ndx = ZERO
        self.page_layers.setCurrentIndex(ndx)
        return self


class DlgFreeformEntry(q0.Q0DialogModal):

    """Free-Form-Entry Dialog.
    
    """
        
    def __init__(self, rel):
        self.rel = rel
        super().__init__(q0_visual=self.rel.tag)
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.push(q0_layout='hbox')
        self.txt = cent_wgt.add_wgt(q0.Q0TextEdit(q0_default=_('Type, paste, or drag free-form text here.')), align='nw')
        self.txt.set_min_size(height=400, width=300)
        cent_wgt.push(q0_layout='vbox')
        cent_wgt.add_wgt(q0.Q0PushButton(q0_visual=_('Parse →'), event_clicked=self.event_parse), align='nw')
        cent_wgt.add_wgt(q0.Q0PushButton(q0_visual=_('← View'), event_clicked=self.event_view), align='nw')
        cent_wgt.pop(is_just_left=True)  # vbox
        scrolling_area = cent_wgt.add_wgt(q0.Q0ScrollArea())
        container = q0.Q0Widget(q0_layout='vbox')
        scrolling_area.set_wgt(container)
        container.push(q0_layout='form', is_just_right=True)
        for (itm, ndx_page, ndx_itm) in self.rel.pages.get_next_itm():
            itm.conjure_form_entry(container, align='top')
        container.pop()  # form
        cent_wgt.pop()  # hbox
        button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox())
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        return

    def audit(self):
        for (itm, ndx_page, ndx_itm) in self.rel.pages.get_next_itm():
            try:
                itm.digest_form_entry()
            except Error as e:
                q0.Q0MessageBox(
                    q0_icon='critical',
                    q0_title=_('Error'),
                    q0_visual=str(e),
                    ).exec_()
                result = None
                break
        else:
            result = True
        return result

    def event_parse(self):
        txt_side_effect = self.rel.free_form_entry(txt=self.txt.get_visual())
        self.txt.set_html(txt_side_effect)
        return

    def event_view(self):
        txt_side_effect = self.rel.view_as_text(is_from_rec=False)
        self.txt.insertHtml(txt_side_effect)
        return


class DlgCalendarMonth(q0.Q0DialogModal):

    """Calendar-Month Dialog.

    """    
    
    day_names = [
        _('Mon'),  # locale.nl_langinfo(locale.ABDAY_2),
        _('Tue'),  # locale.nl_langinfo(locale.ABDAY_3),
        _('Wed'),  # locale.nl_langinfo(locale.ABDAY_4),
        _('Thu'),  # locale.nl_langinfo(locale.ABDAY_5),
        _('Fri'),  # locale.nl_langinfo(locale.ABDAY_6),
        _('Sat'),  # locale.nl_langinfo(locale.ABDAY_7),
        _('Sun'),  # locale.nl_langinfo(locale.ABDAY_1),
        ]
    mo_names = [
        _('Jan'),  # locale.nl_langinfo(locale.ABMON_1),
        _('Feb'),  # locale.nl_langinfo(locale.ABMON_2),
        _('Mar'),  # locale.nl_langinfo(locale.ABMON_3),
        _('Apr'),  # locale.nl_langinfo(locale.ABMON_4),
        _('May'),  # locale.nl_langinfo(locale.ABMON_5),
        _('Jun'),  # locale.nl_langinfo(locale.ABMON_6),
        _('Jul'),  # locale.nl_langinfo(locale.ABMON_7),
        _('Aug'),  # locale.nl_langinfo(locale.ABMON_8),
        _('Sep'),  # locale.nl_langinfo(locale.ABMON_9),
        _('Oct'),  # locale.nl_langinfo(locale.ABMON_10),
        _('Nov'),  # locale.nl_langinfo(locale.ABMON_11),
        _('Dec'),  # locale.nl_langinfo(locale.ABMON_12),
        ]

    def __init__(self, date_seed):
        super().__init__(q0_visual=_('Calendar'))
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.push('hbox')
        cent_wgt.add_wgt(q0.Q0PushButton(q0_visual=_('← Year'), event_clicked=self.event_prev_yr))
        cent_wgt.add_wgt(q0.Q0PushButton(q0_visual=_('← Month'), event_clicked=self.event_prev_mo))
        self.cal_mo_yr = cent_wgt.add_wgt(q0.Q0Label(), align='x')
        self.set_cal_mo_yr(date_seed)
        cent_wgt.add_wgt(q0.Q0PushButton(q0_visual=_('Month →'), event_clicked=self.event_next_mo))
        cent_wgt.add_wgt(q0.Q0PushButton(q0_visual=_('Year →'), event_clicked=self.event_next_yr))
        cent_wgt.pop()  # hbox
        cent_wgt.push('grid')
        (self.day_beg, self.day_end) = (self.get_mo_beg(date_seed), self.get_mo_end(date_seed))
        day_lo = self.get_wk_beg(self.day_beg)
        day_hi = self.get_wk_end(self.day_end)
        self.alarms_by_date = MAIN_WIN.alarms.collect_dates(date_range=[day_lo, day_hi])
        dow = ZERO
        wom = 1
        date = day_lo
        day_name = []
        while True:
            if date < self.day_beg or date > self.day_end:
                background_color = 'gray'
            else:
                background_color = 'lightgray'
            if date.isoweekday() == 7:
                foreground_color = 'red'
            else:
                foreground_color = 'black'
            if wom in [1]:
                day_name.append(self.day_names[date.isoweekday() - 1])
            btn = cent_wgt.add_wgt_to_grid(TextEditCalendarCell(is_readonly=True), col=dow, row=wom)
            btn.alarms = self.alarms_by_date.get(date, Alarms())
            (markup, background_color) = self.get_cell_visual(foreground_color, background_color, date)
            btn.set_html(markup)
            btn.set_min_size(height=100, width=100)
            if date == datetime.date.today():
                background_color = 'gold'
            btn.set_style_sheet(f'text-align:left; background-color:{background_color}')
            date = self.bump_day(date)
            dow += 1
            if dow > 6:
                dow = ZERO
                wom += 1
                if wom > 6:
                    break
        for (dow, day_abbreviation) in enumerate(day_name):
            wgt = q0.Q0Widget()
            markup = f'<font color=gray>{day_abbreviation}</font>'
            lbl = wgt.add_wgt(q0.Q0Label(q0_visual=markup), align='*')
            cent_wgt.add_wgt_to_grid(wgt, col=dow, row=ZERO)
        cent_wgt.pop()  # grid
        cent_wgt.push('vbox', is_just_right=True)
        button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox(q0_buttons = ['ok']))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        cent_wgt.pop()  # vbox
        return

    def audit(self):
        result = True
        return result

    def get_cell_visual(self, foreground_color, background_color, date):

        def get_foreground(alarm, foreground_color):
            if alarm.parent_rec:
                result = alarm.parent_rec.get(TAG_FOREGROUND_COLOR)
                if result in BLANK_VALUES:
                    result = foreground_color
            else:
                result = foreground_color
            return result

        def get_background(alarm, background_color):
            if alarm.parent_rec:
                result = alarm.parent_rec.get(TAG_BACKGROUND_COLOR)
                if result in BLANK_VALUES:
                    result = background_color
            else:
                result = background_color
            return result

        def get_handle(alarm):
            if alarm.parent_rec:
                result = alarm.parent_rec.get(TAG__HANDLE)
                if result in BLANK_VALUES:
                    result = None
            else:
                result = None
            return result

        alarms = self.alarms_by_date.get(date, Alarms())
        alarms.sort_by_priority()
        if alarms:
            foreground_color = get_foreground(alarms[ZERO], foreground_color)
            background_color = get_background(alarms[-1], background_color)
        markup = []
        markup.append(f'<font color={foreground_color} size=+2>')
        markup.append(str(date.day))
        markup.append('</font>')
        alarms.sort_by_time()
        for alarm in alarms:
            handle = get_handle(alarm)
            if handle:
                markup.append(MARKDN_LINE_END)
                markup.append(handle)
        result = (NULL.join(markup), background_color)
        return result

    def set_cal_mo_yr(self, date):
        mo_name = self.mo_names[date.month - 1]
        markup = _('<center>{v0} of {v1}</center>').format(v0=mo_name, v1=date.year)
        self.cal_mo_yr.set_visual(markup)
        return self

    def event_prev_mo(self):
        self.reject()
        date = self.bump_day(self.day_beg, inc=-1)
        MAIN_WIN.call_calendar_month(date)
        return

    def event_next_mo(self):
        self.reject()
        date = self.bump_day(self.day_end, inc=1)
        MAIN_WIN.call_calendar_month(date)
        return

    def event_prev_yr(self):
        self.reject()
        date = self.bump_yr(self.day_beg, inc=-1)
        MAIN_WIN.call_calendar_month(date)
        return

    def event_next_yr(self):
        self.reject()
        date = self.bump_yr(self.day_beg, inc=1)
        MAIN_WIN.call_calendar_month(date)
        return

    def bump_day(self, date, inc=1):
        result = date + datetime.timedelta(days=inc)
        return result

    def get_mo_beg(self, date):
        (yyyy, mm, dd) = (date.year, date.month, date.day)
        result = datetime.date(yyyy, mm, 1)
        return result

    def get_mo_end(self, date):
        (this_yyyy, this_mm, this_dd) = (date.year, date.month, date.day)
        result = datetime.date(this_yyyy, this_mm, 28)
        while True:
            next_date = self.bump_day(result)
            if this_mm == next_date.month:
                result = next_date
            else:
                break
        return result

    def get_mo_prev(self, mo_beg):
        mo_end = bump_day(mo_beg, inc=-1)
        mo_beg = get_mo_beg(mo_end)
        result = (mo_beg, mo_end)
        return result

    def get_mo_next(self, mo_end):
        mo_beg = bump_day(mo_end, inc=1)
        mo_end = get_mo_end(mo_beg)
        result = (mo_beg, mo_end)
        return result

    def bump_yr(self, date, inc=1):
        (this_yyyy, this_mm, this_dd) = (date.year, date.month, date.day)
        result = datetime.date(this_yyyy + inc, this_mm, this_dd)  # Theoretically, as used in this script, date will never be 29 Feb.
        return result

    def get_wk_beg(self, date):
        day_1 = COMMON['CONFIG'].week_first_day
        result = date
        while result.isoweekday() != day_1:
            result = self.bump_day(result, inc=-1)
        return result

    def get_wk_end(self, date):
        day_7 = (COMMON['CONFIG'].week_first_day + 5) % 7 + 1
        result = date
        while result.isoweekday() != day_7:
            result = self.bump_day(result, inc=1)
        return result
    
    
class DlgChgItms(q0.Q0DialogModal):

    """Add/Change/Remove Fields Dialog.

    """    
    
    def __init__(self, tab, ndx_row, ndx_col):
        self.tab = tab
        self.ndx_row = ndx_row
        self.ndx_col = ndx_col
        super().__init__(q0_visual=self.tab.rel.tag)
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.add_wgt(q0.Q0Label(q0_visual=_('Field Tags')))
        cent_wgt.push('hbox')
        self.old_tags = self.tab.rel.pages.conjure_tag_by_itm()
        self.q0_list_itms = cent_wgt.add_wgt(self.tab.rel.pages.conjure_list())
        self.q0_list_itms.connect_row_changed(self.event_itm_selected_changed)
        cent_wgt.push('vbox')
        self.btns = {}
        for (q0_visual, event_clicked) in [
            (_('← Insert Before'), self.event_insert_before_itm),
            (_('← Insert After'), self.event_insert_after_itm),
            (_('→ Remove'), self.event_remove_itm),
            (_('Change Kind...'), self.event_change_type_itm),
            (_('Edit Field...'), self.event_edit_itm),
            (_('← Sep Before'), self.event_sep_before_itm),
            (_('← Sep After'), self.event_sep_after_itm),
            (_('↑ Move Up'), self.event_move_itm_up),
            (_('↓ Move Dn'), self.event_move_itm_dn),
            ]:
            btn = cent_wgt.add_wgt(q0.Q0PushButton(
                q0_visual=q0_visual,
                event_clicked=event_clicked,
                ))
            btn.set_style_sheet('text-align:left')
            self.btns[q0_visual] = btn
        self.event_itm_selected_changed()
        cent_wgt.push('vbox', is_just_right=True)
        button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox(q0_buttons = ['ok']))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        cent_wgt.pop()  # vbox
        cent_wgt.pop()  # vbox
        cent_wgt.pop()  # hbox
        return

    def run_audit_loop(self):

        """Always succeed.

        Because DlgChgItm, invoked by event_edit_itm, has side effects
        and may be called several times, it is not possible to restore
        the state of the relation in case the user wants to back out.
        In other words, we can't back out.

        This is supposed to ensure that any change to the relation is
        committed and displayed as-is.

        """
        
        self.exec_()
        return self.audit()
    
    def audit(self):
        self.tab.rel.transform(old_tags=self.old_tags, plan=self.q0_list_itms.get_items())
        self.tab.ledger_layout()
        self.tab.reset()
        self.tab.ledger.set_current_row_col(self.ndx_row, self.ndx_col)
        result = True
        return result

    def event_itm_selected_changed(self):
        pos = self.q0_list_itms.get_pos()
        tag = self.q0_list_itms.get_item(pos)
        itm = self.tab.rel.pages.find(tag)
        if itm and itm.is_dd_mod_enabled:
            self.btns[_('→ Remove')].set_enabled(True)
            self.btns[_('Change Kind...')].set_enabled(True)
            self.btns[_('Edit Field...')].set_enabled(True)
        else:
            if tag in [COLLECTION_SEP]:
                self.btns[_('→ Remove')].set_enabled(True)
            else:
                self.btns[_('→ Remove')].set_enabled(False)
            self.btns[_('Change Kind...')].set_enabled(False)
            self.btns[_('Edit Field...')].set_enabled(False)
        return

    def event_insert_before_itm(self):
        collection = self.q0_list_itms.get_items()
        ndx = self.q0_list_itms.get_pos()
        old_tag = self.q0_list_itms.get_item(ndx)
        if old_tag:
            n_tuple = self.tab.rel.pages.find_tuple(old_tag)
            if n_tuple:
                (old_itm, ndx_page, ndx_itm) = n_tuple
            else:
                (old_itm, ndx_page, ndx_itm) = (None, NA, NA)
        else:
            (old_itm, ndx_page, ndx_itm) = (None, NA, NA)
        unique = ZERO
        while True:
            new_tag = _('«new_{v0}»').format(v0=unique)
            if new_tag in collection:
                unique += 1
            else:
                break
        new_itm = ItmText(new_tag)
        self.tab.rel.pages[ndx_page].insert(ndx, new_itm)
        self.old_tags[new_itm] = new_tag
        self.q0_list_itms.add_item(new_tag, ndx)
        self.q0_list_itms.set_pos(ndx)
        return
    
    def event_insert_after_itm(self):
        collection = self.q0_list_itms.get_items()
        ndx = self.q0_list_itms.get_pos()
        old_tag = self.q0_list_itms.get_item(ndx)
        if old_tag:
            n_tuple = self.tab.rel.pages.find_tuple(old_tag)
            if n_tuple:
                (old_itm, ndx_page, ndx_itm) = n_tuple
            else:
                (old_itm, ndx_page, ndx_itm) = (None, NA, NA)
        else:
            (old_itm, ndx_page, ndx_itm) = (None, NA, NA)
        unique = ZERO
        while True:
            new_tag = _('«new_{v0}»').format(v0=unique)
            if new_tag in collection:
                unique += 1
            else:
                break
        new_itm = ItmText(new_tag)
        self.tab.rel.pages[ndx_page].insert(ndx + 1, new_itm)
        self.old_tags[new_itm] = new_tag
        self.q0_list_itms.add_item(new_tag, ndx + 1)
        self.q0_list_itms.set_pos(ndx + 1)
        return
    
    def event_remove_itm(self):
        ndx = self.q0_list_itms.get_pos()
        self.q0_list_itms.take_item(ndx)
        self.q0_list_itms.set_pos(ndx)
        return

    def event_change_type_itm(self):
        ndx = self.q0_list_itms.get_pos()
        tag = self.q0_list_itms.get_item(ndx)
        (old_itm, ndx_page, ndx_itm) = self.tab.rel.pages.find_tuple(tag)
        response = DlgChgTyp(ndx=ndx, itm=old_itm).run_audit_loop()
        if response:
            new_itm = response.cls()
            new_itm.clone(old_itm)
            self.tab.rel.pages[ndx_page][ndx_itm] = new_itm
            self.old_tags[new_itm] = self.old_tags[old_itm]
        return
    
    def event_edit_itm(self):
        ndx = self.q0_list_itms.get_pos()
        tag = self.q0_list_itms.get_item(ndx)
        itm = self.tab.rel.pages.find(tag)
        response = DlgChgItm(q0_list_itms=self.q0_list_itms, ndx=ndx, itm=itm).run_audit_loop()
        if response:
            self.q0_list_itms.set_item(itm.tag, ndx)
            self.q0_list_itms.set_pos(ndx)
        return
    
    def event_sep_before_itm(self):
        ndx = self.q0_list_itms.get_pos()
        self.q0_list_itms.add_item(COLLECTION_SEP, ndx)
        self.q0_list_itms.set_pos(ndx)
        return
    
    def event_sep_after_itm(self):
        ndx = self.q0_list_itms.get_pos()
        self.q0_list_itms.add_item(COLLECTION_SEP, ndx + 1)
        self.q0_list_itms.set_pos(ndx + 1)
        return
    
    def event_move_itm_up(self):
        ndx = self.q0_list_itms.get_pos()
        if ndx <= ZERO:
            self.q0_list_itms.set_pos(ZERO)
        else:
            self.q0_list_itms.move_item(ndx, ndx - 1)
            self.q0_list_itms.set_pos(ndx - 1)
        return

    def event_move_itm_dn(self):
        ndx = self.q0_list_itms.get_pos()
        size = len(self.q0_list_itms) - 1
        if ndx >= size:
            self.q0_list_itms.set_pos(size)
        else:
            self.q0_list_itms.move_item(ndx, ndx + 1)
            self.q0_list_itms.set_pos(ndx + 1)
        return
    

class DlgChgItm(q0.Q0DialogModal):

    """Edit-Field Dialog.

    """    
    
    def __init__(self, q0_list_itms, ndx, itm):
        self.q0_list_itms = q0_list_itms
        self.ndx = ndx
        self.itm = itm
        super().__init__(q0_visual='Field Edit')
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.push(q0_layout='form', is_just_right=True)
        self.itm.conjure_property_edit(dlg=self, form=cent_wgt)
        self.event_locale_formatted_changed()
        cent_wgt.pop()  # form
        cent_wgt.push(q0_layout='hbox', is_just_right=True)
        button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox())
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        cent_wgt.pop()  # hbox
        return
    
    def audit(self):
        result = True
        try:
            self.itm.digest_property_edit(dlg=self)
        except ErrorNotNumeric as e:
            q0.Q0MessageBox(
                q0_icon='critical',
                q0_title=_('Error'),
                q0_visual=str(e),
                ).exec_()
            result = None
            
        collection = self.q0_list_itms.get_items()
        del collection[self.ndx]
        if self.itm.tag in collection:
            q0.Q0MessageBox(
                q0_icon='critical',
                q0_title=_('Error'),
                q0_visual=_('Tag "{v0}" is duplicated in the relation.').format(v0=self.itm.tag),
                ).exec_()
            result = None
        return result

    def event_locale_formatted_changed(self):
        if self.property_wgts['is_locale_formatted'].is_checked():
            self.property_wgts['fmt_disp'].set_enabled(False)
            self.property_wgts['fmt_edit'].set_enabled(False)
        else:
            self.property_wgts['fmt_disp'].set_enabled(True)
            self.property_wgts['fmt_edit'].set_enabled(True)
        return

    
class DlgChgTyp(q0.Q0DialogModal):

    """Change-Kind Dialog.

    """    
    
    def __init__(self, ndx, itm):
        self.ndx = ndx
        self.itm = itm
        super().__init__(q0_visual=_('Change Kind'))
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.add_wgt(q0.Q0Label(q0_visual=_('WARNING:  The new type may choke on old stored data.')))
        cent_wgt.push('form')
        (lbl, self.q0_cls) = cent_wgt.add_row(q0.Q0Label(_('Type')), q0.Q0ComboBox(is_editable=False))
        q0_list_classes = list(REG_ITMS.values())
        for (pos, rel) in enumerate(q0_list_classes):
            self.q0_cls.add_item(q0_visual=rel.name_i18n, pos=pos)
            self.q0_cls.set_item_tool_tip(rel.description, pos=pos)
        old_key = ITM_CLASS_NAME[type(self.itm)]
        old_name_i18n = REG_ITMS[old_key].name_i18n
        self.q0_cls.set_visual(old_name_i18n)
        cent_wgt.pop()  # form
        button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox())
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        return
    
    def audit(self):
        result = REG_ITMS.lookup_i18n(self.q0_cls.get_visual())
        return result


class DlgChooseDisplayCols(q0.Q0DialogModal):

    """Choose-Display-Columns Dialog.

    """    
    
    def __init__(self, tab, ndx_row, ndx_col):
        self.tab = tab
        self.ndx_row = ndx_row
        self.ndx_col = ndx_col
        super().__init__(q0_visual=self.tab.rel.tag)
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.push('hbox')
        cent_wgt.push('vbox')
        cent_wgt.add_wgt(q0.Q0Label(q0_visual=_('Displayed Tags')))
        (displayed_list, hidden_list) = self.tab.rel.get_tags_displayed_and_hidden()
        self.q0_disp_itms = cent_wgt.add_wgt(q0.Q0List(items=displayed_list, width=200))
        self.q0_disp_itms.connect_row_changed(self.event_itm_selected_changed)
        cent_wgt.pop()  # vbox
        cent_wgt.push('vbox')
        cent_wgt.add_wgt(q0.Q0Label(q0_visual=NULL))
        self.btns = {}
        for (q0_visual, event_clicked) in [
            (_('← Insert Before'), self.event_insert_before_itm),
            (_('← Insert After'), self.event_insert_after_itm),
            (_('→ Remove'), self.event_remove_itm),
            (_('↑ Move Up'), self.event_move_itm_up),
            (_('↓ Move Dn'), self.event_move_itm_dn),
            ]:
            btn = cent_wgt.add_wgt(q0.Q0PushButton(
                q0_visual=q0_visual,
                event_clicked=event_clicked,
                ))
            btn.set_style_sheet('text-align:left')
            self.btns[q0_visual] = btn
        cent_wgt.pop(is_just_left=True)  # vbox
        cent_wgt.push('vbox')
        cent_wgt.add_wgt(q0.Q0Label(q0_visual=_('Hidden Tags')))
        self.q0_hide_itms = cent_wgt.add_wgt(q0.Q0List(items=hidden_list, width=200))
        self.q0_hide_itms.connect_row_changed(self.event_itm_selected_changed)
        cent_wgt.pop()  # vbox
        cent_wgt.pop()  # hbox
        button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox())
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.event_itm_selected_changed()
        return

    def audit(self):
        self.tab.rel.display_tags = self.q0_disp_itms.get_items()
        self.tab.ledger_layout()
        self.tab.reset()
        self.tab.ledger.set_current_row_col(self.ndx_row, self.ndx_col)
        self.tab.rel.rel_is_dirty = True
        return True

    def event_itm_selected_changed(self):
        disp_pos = self.q0_disp_itms.get_pos()
        hide_pos = self.q0_hide_itms.get_pos()
        if hide_pos is NA:
            self.btns[_('← Insert Before')].set_enabled(False)
            self.btns[_('← Insert After')].set_enabled(False)
        else:
            self.btns[_('← Insert Before')].set_enabled(True)
            self.btns[_('← Insert After')].set_enabled(True)
        if disp_pos is NA:
            self.btns[_('→ Remove')].set_enabled(False) 
            self.btns[_('↑ Move Up')].set_enabled(False)
            self.btns[_('↓ Move Dn')].set_enabled(False)
        else:
            self.btns[_('→ Remove')].set_enabled(True)
            self.btns[_('↑ Move Up')].set_enabled(True)
            self.btns[_('↓ Move Dn')].set_enabled(True)
        return

    def event_insert_before_itm(self):
        disp_pos = self.q0_disp_itms.get_pos()
        hide_pos = self.q0_hide_itms.get_pos()
        if disp_pos in [NA]:
            disp_pos = ZERO
        itm = self.q0_hide_itms.take_item(hide_pos)
        self.q0_disp_itms.add_item(itm, disp_pos)
        self.q0_hide_itms.set_pos(hide_pos)
        self.q0_disp_itms.set_pos(disp_pos)
        return
    
    def event_insert_after_itm(self):
        disp_pos = self.q0_disp_itms.get_pos()
        hide_pos = self.q0_hide_itms.get_pos()
        if disp_pos in [NA]:
            disp_pos = len(self.q0_disp_itms)
        itm = self.q0_hide_itms.take_item(hide_pos)
        self.q0_disp_itms.add_item(itm, disp_pos + 1)
        self.q0_hide_itms.set_pos(hide_pos)
        self.q0_disp_itms.set_pos(disp_pos + 1)
        return
    
    def event_remove_itm(self):
        disp_pos = self.q0_disp_itms.get_pos()
        hide_pos = ZERO
        itm = self.q0_disp_itms.take_item(disp_pos)
        self.q0_hide_itms.add_item(itm, hide_pos)
        self.q0_hide_itms.set_pos(hide_pos)
        self.q0_disp_itms.set_pos(disp_pos)
        return
    
    def event_move_itm_up(self):
        disp_pos = self.q0_disp_itms.get_pos()
        if disp_pos <= ZERO:
            self.q0_disp_itms.set_pos(ZERO)
        else:
            self.q0_disp_itms.move_item(disp_pos, disp_pos - 1)
            self.q0_disp_itms.set_pos(disp_pos - 1)
        return
    
    def event_move_itm_dn(self):
        disp_pos = self.q0_disp_itms.get_pos()
        size = len(self.q0_disp_itms) - 1
        if disp_pos >= size:
            self.q0_disp_itms.set_pos(size)
        else:
            self.q0_disp_itms.move_item(disp_pos, disp_pos + 1)
            self.q0_disp_itms.set_pos(disp_pos + 1)
        return

class DlgSearchReplace(q0.Q0DialogModal):

    """Search/Replace Dialog.

    """    
    
    btn_width = 100

    def __init__(self, tab):

        def conjure_target():
            wgt = q0.Q0Widget()
            self.wgt_target = wgt.add_wgt(q0.Q0LineEdit())
            self.wgt_target.set_tool_tip(_('*Target* is a string of characters to search for.'))
            bbx = wgt.add_wgt(q0.Q0DialogButtonBox(q0_buttons=[]))
            btn = q0.Q0PushButton(
                _(' ← Previous'),
                event_clicked=self.event_prev,
                fixed_width=self.btn_width,
                )
            btn.set_tool_tip(_('Find the previous row with a field that contans the *Target* string.'))
            btn.set_style_sheet('text-align:left')
            bbx.add_button(btn)
            self.btn_next = q0.Q0PushButton(
                _(' Next →'),
                event_clicked=self.event_next,
                fixed_width=self.btn_width,
                )
            self.btn_next.set_tool_tip(_('Find the next row with a field that contans the *Target* string.'))
            self.btn_next.set_style_sheet('text-align:left')
            bbx.add_button(self.btn_next)
            (lbl, wgt) = cent_wgt.add_row(q0.Q0Label(_('Target')), wgt)
            return

        def conjure_found():
            wgt = q0.Q0Widget()
            self.wgt_found = wgt.add_wgt(q0.Q0TextEdit(is_readonly=True))
            self.wgt_found.set_style_sheet('background-color: lightgray')
            bbx = wgt.add_wgt(q0.Q0DialogButtonBox(q0_buttons=[], q0_orientation='vertical'))
            btn = q0.Q0PushButton(
                _(' Toggle'),
                event_clicked=self.event_mark,
                fixed_width=self.btn_width,
                )
            btn.set_tool_tip(_('Flip the mark on the current row.'))
            btn.set_style_sheet('text-align:left')
            bbx.add_button(btn)
            btn.set_enabled(False)
            self.btn_mark = btn
            btn = q0.Q0PushButton(
                _(' Mark → Go'),
                event_clicked=self.event_mark_and_go,
                fixed_width=self.btn_width,
                )
            btn.set_tool_tip(_('Set the mark on the current row and then search for the next matching row.'))
            btn.set_style_sheet('text-align:left')
            bbx.add_button(btn)
            btn.set_enabled(False)
            self.btn_mark_and_go = btn
            btn = q0.Q0PushButton(
                _(' Mark All'),
                event_clicked=self.event_mark_all,
                fixed_width=self.btn_width,
                )
            btn.set_tool_tip(_('Find all matching rows and set their marks.'))
            btn.set_style_sheet('text-align:left')
            bbx.add_button(btn)
            btn = q0.Q0PushButton(
                _(' Skip Field'),
                event_clicked=self.event_skip_field,
                fixed_width=self.btn_width,
                )
            btn.set_tool_tip(_('Ignore this column.'))
            btn.set_style_sheet('text-align:left')
            bbx.add_button(btn)
            btn.set_enabled(False)
            self.btn_skip = btn
            wgt.pop(is_just_left=True)
            (lbl, wgt) = cent_wgt.add_row(q0.Q0Label(_('Found')), wgt)
            return

        def conjure_replacement():
            wgt = q0.Q0Widget()
            self.wgt_replacement = wgt.add_wgt(q0.Q0LineEdit())
            self.wgt_replacement.set_tool_tip(_('*Replacement* is a string of characters that will substitute for the *Target*.'))
            (lbl, wgt) = cent_wgt.add_row(q0.Q0Label(_('Replacement')), wgt)
            return

        def conjure_preview():
            wgt = q0.Q0Widget()
            self.wgt_preview = wgt.add_wgt(q0.Q0TextEdit(is_readonly=True))
            self.wgt_preview.set_style_sheet('background-color: lightgray')
            bbx = wgt.add_wgt(q0.Q0DialogButtonBox(q0_buttons=[], q0_orientation='vertical'))
            btn = q0.Q0PushButton(
                _(' Update'),
                event_clicked=self.event_update,
                fixed_width=self.btn_width,
                )
            btn.set_tool_tip(_('Replace the current field in the current row.'))
            btn.set_style_sheet('text-align:left')
            bbx.add_button(btn)
            btn.set_enabled(False)
            self.btn_update = btn
            btn = q0.Q0PushButton(
                _(' Update → Go'),
                event_clicked=self.event_update_and_go,
                fixed_width=self.btn_width,
                )
            btn.set_tool_tip(_('Replace the current field in the current row and then search for the next matching field.'))
            btn.set_style_sheet('text-align:left')
            bbx.add_button(btn)
            btn.set_enabled(False)
            self.btn_update_and_go = btn
            btn = q0.Q0PushButton(
                _(' Update All'),
                event_clicked=self.event_update_all,
                fixed_width=self.btn_width,
                )
            btn.set_tool_tip(_('Find all matching fields in all rows and replace them.'))
            btn.set_style_sheet('text-align:left')
            bbx.add_button(btn)
            wgt.pop(is_just_left=True)
            (lbl, wgt) = cent_wgt.add_row(q0.Q0Label(_('Preview')), wgt)
            return

        self.tab = tab
        self.tags = self.tab.rel.pages.get_tag_collection()
        self.init_starting_pos()
        super().__init__(q0_visual=self.tab.rel.tag)
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.push(q0_layout='form', is_just_right=True)
        conjure_target()
        conjure_found()
        conjure_replacement()
        conjure_preview()
        cent_wgt.pop()  # form
        button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox(q0_buttons = ['ok']))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.btn_next.set_dlgs_default()
        return

    def run_audit_loop(self):

        """Always succeed.

        Because this dialog may affect many rows in the relation, it
        is not possible to restore the state of the relation in case
        the user wants to back out.  In other words, we can't back
        out.

        This is supposed to ensure that any changes to the relation
        are committed and displayed as-is.

        """
        
        self.exec_()
        return self.audit()
    
    def audit(self):
        result = True
        return result

    def init_starting_pos(self):
        (self.ndx_starting_rec, ndx_col) = self.tab.ledger.get_current_row_col()
        if self.ndx_starting_rec == NA:
            self.ndx_starting_rec = ZERO
        self.ndx_starting_tag = ZERO
        self.ndx_current_rec = self.ndx_starting_rec
        self.ndx_current_tag = self.ndx_starting_tag
        self.col = self.tab.rel.pages.find(self.tags[self.ndx_current_tag])
        return self

    def bump_row(self, f_next):
        (result, self.ndx_current_rec) = f_next(self.tab.rel.recs, self.ndx_current_rec)
        return result

    def bump_col(self, delta=1):
        size = len(self.tags)
        self.ndx_current_tag += delta
        if self.ndx_current_tag >= size:
            self.ndx_current_tag = ZERO
        elif self.ndx_current_tag < ZERO:
            self.ndx_current_tag = size - 1
        result = (self.ndx_current_tag == self.ndx_starting_tag)
        self.col = self.tab.rel.pages.find(self.tags[self.ndx_current_tag])
        return result

    def bump_row_within_col(self, is_inc=True):
        if is_inc:
            f_next = RecsStorage.ndx_inc
            delta = 1
        else:
            f_next = RecsStorage.ndx_dec
            delta = -1
        if self.bump_row(f_next=f_next):
            self.bump_col(delta=delta)
        result = (self.ndx_current_rec == self.ndx_starting_rec) and (self.ndx_current_tag == self.ndx_starting_tag)
        return result

    def conjure_search_disp(self, txt):
        result = _('''{v0} N⁰ {v1}:
<font color=indianred size=-1>«{v2}»</font>
{v3}
<font color=indianred size=-1>«/{v4}»</font>
''').format(v0=self.tab.rel.tag, v1=self.ndx_current_rec + 1, v2=self.col.tag, v3=txt, v4=self.col.tag)
        return result

    def preview(self, targ, valu):
        repl = self.wgt_replacement.get_visual()
        (count, valu_disp) = repl_case(valu, targ, repl, is_highlighted=True)
        self.wgt_preview.set_markdown(self.conjure_search_disp(valu_disp))
        self.btn_mark.set_enabled(True)
        self.btn_mark_and_go.set_enabled(True)
        self.btn_skip.set_enabled(True)
        self.btn_update.set_enabled(True)
        self.btn_update_and_go.set_enabled(True)
        return self

    def match(self):
        self.tab.rel.stage_rec(self.ndx_current_rec)
        targ = self.wgt_target.get_visual()
        valu = self.col.val_disp
        (count, valu_disp) = repl_case(valu, targ, is_highlighted=True)
        if count:
            result = True
            self.tab.ledger.set_current_row_col(self.ndx_current_rec, ZERO)
            self.wgt_found.set_markdown(self.conjure_search_disp(valu_disp))
            self.preview(targ=targ, valu=valu)
        else:
            result = False
            self.btn_mark.set_enabled(False)
            self.btn_mark_and_go.set_enabled(False)
            self.btn_skip.set_enabled(False)
            self.btn_update.set_enabled(False)
            self.btn_update_and_go.set_enabled(False)
        return result

    def prev(self, is_inc=False):
        self.next(is_inc=is_inc)
        return self

    def next(self, is_inc=True):
        while True:
            if self.bump_row_within_col(is_inc):
                q0.Q0MessageBox(
                    q0_icon='information',
                    q0_title=_('Exhaustion'),
                    q0_visual=_('All rows and fields have been searched.'),
                    ).exec_()
                break
            if self.match():
                break
        return self

    def toggle(self, val_comp=None):
        return self

    def event_prev(self):
        with q0.Q0Alert(
            q0_app=COMMON['APP'],
            q0_title=_('Working'),
            q0_visual=_('Please wait.'),
            ):
            self.prev()
        return

    def event_next(self):
        with q0.Q0Alert(
            q0_app=COMMON['APP'],
            q0_title=_('Working'),
            q0_visual=_('Please wait.'),
            ):
            self.next()
        return

    def event_mark(self):
        self.tab.toggle_mark(self.ndx_current_rec)
        self.tab.ledger.q0_view.refresh()
        return

    def event_mark_and_go(self):
        self.tab.set_mark(self.ndx_current_rec)
        self.tab.ledger.q0_view.refresh()
        self.event_next()
        return

    def event_mark_all(self):
        count = ZERO
        with q0.Q0Alert(
            q0_app=COMMON['APP'],
            q0_title=_('Working'),
            q0_visual=_('Please wait.'),
            ):
            while True:
                if self.match():
                    if self.tab.has_mark(self.ndx_current_rec):
                        pass
                    else:
                        count += 1
                    self.tab.set_mark(self.ndx_current_rec)
                    self.tab.ledger.q0_view.refresh()
                if self.bump_row_within_col():
                    break
        q0.Q0MessageBox(
                q0_icon='information',
                q0_title=_('Exhaustion'),
                q0_visual=_('All rows have been searched.  {v0} rows marked.').format(v0=count),
            ).exec_()
        return

    def event_skip_field(self):
        self.bump_col(delta=1)
        self.event_next()
        return

    def event_update(self):
        targ = self.wgt_target.get_visual()
        valu = self.col.val_disp
        repl = self.wgt_replacement.get_visual()
        (count, valu_disp) = repl_case(valu, targ, repl, is_highlighted=True)
        self.wgt_preview.set_markdown(self.conjure_search_disp(valu_disp))
        (count, valu_disp) = repl_case(valu, targ, repl)
        self.col.val_disp = valu_disp
        self.tab.rel.destage_rec(self.ndx_current_rec)
        self.tab.ledger.rows[self.ndx_current_rec][self.col.tag] = self.col.val_disp
        self.tab.ledger.reset_row_tag(self.ndx_current_rec, self.col.tag)
        self.tab.ledger.q0_view.refresh()
        return

    def event_update_and_go(self):
        self.event_update()
        self.event_next()
        return

    def event_update_all(self):
        count = ZERO
        with q0.Q0Alert(
            q0_app=COMMON['APP'],
            q0_title=_('Working'),
            q0_visual=_('Please wait.'),
            ):
            while True:
                if self.match():
                    self.event_update()
                    count += 1
                if self.bump_row_within_col():
                    break
        q0.Q0MessageBox(
                q0_icon='information',
                q0_title=_('Exhaustion'),
                q0_visual=_('All rows have been searched.  {v0} rows updated.').format(v0=count),
            ).exec_()
        return


class TextEditWithLinks(q0.Q0TextEdit):

    """Adaptation of q0 Text Edit.

    This supplies a hook to open a browser tab when a displayed markup
    anchor is clicked.

    """    
    
    def event_anchor_clicked(self, link):
        browser_open_tab(uri=link)
        return True


class TextEditCalendarCell(q0.Q0TextEdit):

    """Yet another adaptation of q0 Text Edit.

    This supplies a mouse-press hook to display the alarms set for a
    particular cell (day) on the calendar grid.

    """
    
    def event_mouse_press(self, event):
        self.alarms.sort_by_time()
        l0 = len(self.alarms)
        if l0 is ZERO:
            a0 = _('There are no events scheduled.')
        elif l0 == 1: 
            a0 = _('There is one scheduled event:')
        else:
            a0 = _('There are {v0} scheduled events:').format(v0=l0)
        q0.Q0MessageBox(
            q0_icon='information',
            q0_title=_('Events'),
            q0_visual=a0,
            q0_informative_text=str(self.alarms),
            ).exec_()
        return 


class DlgViewText(q0.Q0DialogModal):

    """View-as-Text Dialog.

    In the event handler for the Preview button, a temporary file is
    created, which is opened in the browser.  For security, this file
    is deleted within self.sleep_msecs.

    """    
    
    btn_width = 100
    sleep_msecs = 30000

    def __init__(self, rel):
        self.rel = rel
        super().__init__(q0_visual='View Formatted Text')
        cent_wgt = self.set_central_widget(q0.Q0Widget(q0_layout='vbox'))
        cent_wgt.push(q0_layout='hbox')
        self.wgt_view = cent_wgt.add_wgt(TextEditWithLinks(is_readonly=True, q0_cursor_shape='arrow'))
        self.wgt_view.set_min_size()
        itm_background = self.rel.pages.find(TAG_BACKGROUND_COLOR)
        if itm_background:
            if itm_background.val_store in BLANK_VALUES:
                self.wgt_view.set_style_sheet('background-color: lightgray')
            else:
                self.wgt_view.set_style_sheet(f'background-color: {itm_background.val_store}')
        else:
            self.wgt_view.set_style_sheet('background-color: lightgray')
        bbx = cent_wgt.add_wgt(q0.Q0DialogButtonBox(q0_buttons=[], q0_orientation='vertical'))
        btn = q0.Q0PushButton(
            _(' Plain'),
            event_clicked=self.event_view_plain,
            fixed_width=self.btn_width,
            )
        btn.set_tool_tip(_('Render data as text.'))
        btn.set_style_sheet('text-align:left')
        bbx.add_button(btn)
        btn = q0.Q0PushButton(
            _(' Raw'),
            event_clicked=self.event_view_raw,
            fixed_width=self.btn_width,
            )
        btn.set_tool_tip(_('Render raw data.'))
        btn.set_style_sheet('text-align:left')
        bbx.add_button(btn)
        btn = q0.Q0PushButton(
            _(' Uppercase'),
            event_clicked=self.event_view_uppercase,
            fixed_width=self.btn_width,
            )
        btn.set_tool_tip(_('Render data as uppercase.'))
        btn.set_style_sheet('text-align:left')
        bbx.add_button(btn)
        btn = q0.Q0PushButton(
            _(' Markup'),
            event_clicked=self.event_view_markup,
            fixed_width=self.btn_width,
            )
        btn.set_tool_tip(_('Render data as markup.'))
        btn.set_style_sheet('text-align:left')
        bbx.add_button(btn)
        btn = q0.Q0PushButton(
            _(' Markdown'),
            event_clicked=self.event_view_markdn,
            fixed_width=self.btn_width,
            )
        btn.set_tool_tip(_('Render data as markdown.'))
        btn.set_style_sheet('text-align:left')
        bbx.add_button(btn)
        btn = q0.Q0PushButton(
            _(' Preview'),
            event_clicked=self.event_view_preview,
            fixed_width=self.btn_width,
            )
        btn.set_tool_tip(_('Render data in browser.'))
        btn.set_style_sheet('text-align:left')
        bbx.add_button(btn)
        cent_wgt.pop()  # hbox
        button_box = cent_wgt.add_wgt(q0.Q0DialogButtonBox(q0_buttons = ['cancel']))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.event_view_plain()
        return

    def event_view_plain(self):
        txt = self.rel.view_as_text()
        self.wgt_view.set_html(txt)
        return

    def event_view_uppercase(self):
        txt = self.wgt_view.get_html()
        self.wgt_view.set_html(txt.upper())
        return

    def event_view_raw(self):
        txt = self.rel.view_as_text()
        self.wgt_view.set_html(raw(txt))
        return

    def event_view_markup(self):
        txt = self.wgt_view.get_html()
        self.wgt_view.set_visual(txt)
        return

    def event_view_markdn(self):
        txt = self.wgt_view.get_markdown()
        self.wgt_view.set_visual(txt)
        return

    def event_view_preview(self):
        txt = self.wgt_view.get_html()
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".html") as unit:
            unit.write(txt)
            tmp_name = unit.name
        browser_open_tab(f'file://{tmp_name}', can_update_traversed_date=False)
        if self.sleep_msecs:
            sleeper = q0.Q0Timer(self.sleep_msecs).single_shot()
            while sleeper.is_semaphore_up():
                COMMON['APP'].process_events()
            os.unlink(tmp_name)
        return

class Alarm:

    """A calendar event.

    >>> now = datetime.datetime(2023,6,5,10,0)
    >>> d230202t0900 = datetime.datetime(2023,2,2,9,0)
    >>> d220701t0000 = datetime.datetime(2022,7,1,0,0)
    >>> d230702t0900 = datetime.datetime(2023,7,2,9,0)
    >>> d230704t0900 = datetime.datetime(2023,7,4,9,0)
    >>> d050619t0000 = datetime.datetime(2005,6,19,0,0)
    >>> d050117t0000 = datetime.datetime(2005,1,17,0,0)
    >>> test_past = Alarm(now).new(
    ...     time_start=d230202t0900,
    ...     )
    >>> test_future = Alarm(now).new(
    ...     time_start=d230702t0900,
    ...     )
    >>> test_adv = Alarm(now).new(
    ...     time_start=d230702t0900, 
    ...     mins_adv=30,
    ...     )
    >>> test_bump_mos = Alarm(now).new(
    ...     time_start=d230702t0900, 
    ...     ofs=1,
    ...     )
    >>> test_stop = Alarm(now).new(
    ...     time_start=d230702t0900, 
    ...     ofs=1, 
    ...     is_ofs_days='Y', 
    ...     time_stop=d230704t0900,
    ...     )
    >>> test_wom_beg = Alarm(now).new(
    ...     time_start=d230702t0900,  
    ...     ofs=1,   
    ...     ofs_in_mo=1,
    ...     )
    >>> test_wom_end = Alarm(now).new(
    ...     time_start=d230702t0900,  
    ...     ofs=1,   
    ...     ofs_in_mo=-1,
    ...     )
    >>> test_dom_beg = Alarm(now).new(
    ...     time_start=d230702t0900,  
    ...     ofs=1,   
    ...     ofs_in_mo=1,  
    ...     is_ofs_in_mo_days='Y',
    ...     )
    >>> test_dom_end = Alarm(now).new(
    ...     time_start=d230702t0900,  
    ...     ofs=1,   
    ...     ofs_in_mo=-1,  
    ...     is_ofs_in_mo_days='Y',
    ...     )
    >>> test_fathers_day = Alarm(now).new(
    ...     time_start=d050619t0000,
    ...     ofs=12,
    ...     ofs_in_mo=3,
    ...     )
    >>> test_4th_july = Alarm(now).new(
    ...     time_start=d220701t0000,
    ...     ofs=12,
    ...     ofs_in_mo=4,
    ...     is_ofs_in_mo_days='Y',
    ...     )
    >>> test_mlk_day = Alarm(now).new(
    ...     time_start=d050117t0000,
    ...     ofs=12,
    ...     ofs_in_mo=3,
    ...     )
    >>> test_past.gen_time().time_next_alert

    >>> test_future.gen_time().time_next_alert
    datetime.datetime(2023, 7, 2, 9, 0)
    >>> test_future.gen_time().time_next_alert

    >>> test_adv.gen_time().time_next_alert
    datetime.datetime(2023, 7, 2, 8, 30)
    >>> test_adv.gen_time().time_next_alert

    >>> test_bump_mos.gen_time().time_next_alert  # 1
    datetime.datetime(2023, 7, 2, 9, 0)
    >>> test_bump_mos.gen_time().time_next_alert  # 2
    datetime.datetime(2023, 8, 2, 9, 0)
    >>> test_stop.gen_time().time_next_alert  # 1
    datetime.datetime(2023, 7, 2, 9, 0)
    >>> test_stop.gen_time().time_next_alert  # 2
    datetime.datetime(2023, 7, 3, 9, 0)
    >>> test_stop.gen_time().time_next_alert  # 3
    datetime.datetime(2023, 7, 4, 9, 0)
    >>> test_stop.gen_time().time_next_alert  # 4

    >>> test_wom_beg.gen_time().time_next_alert  # 1
    datetime.datetime(2023, 7, 2, 9, 0)
    >>> test_wom_beg.gen_time().time_next_alert  # 2
    datetime.datetime(2023, 8, 6, 9, 0)
    >>> test_wom_beg.gen_time().time_next_alert  # 3
    datetime.datetime(2023, 9, 3, 9, 0)
    >>> test_wom_end.gen_time().time_next_alert  # 1
    datetime.datetime(2023, 7, 2, 9, 0)
    >>> test_wom_end.gen_time().time_next_alert  # 2
    datetime.datetime(2023, 8, 27, 9, 0)
    >>> test_wom_end.gen_time().time_next_alert  # 3
    datetime.datetime(2023, 9, 24, 9, 0)
    >>> test_dom_beg.gen_time().time_next_alert  # 1
    datetime.datetime(2023, 7, 2, 9, 0)
    >>> test_dom_beg.gen_time().time_next_alert  # 2
    datetime.datetime(2023, 8, 1, 9, 0)
    >>> test_dom_beg.gen_time().time_next_alert  # 3
    datetime.datetime(2023, 9, 1, 9, 0)
    >>> test_dom_end.gen_time().time_next_alert  # 1
    datetime.datetime(2023, 7, 2, 9, 0)
    >>> test_dom_end.gen_time().time_next_alert  # 2
    datetime.datetime(2023, 8, 31, 9, 0)
    >>> test_dom_end.gen_time().time_next_alert  # 3
    datetime.datetime(2023, 9, 30, 9, 0)
    >>> test_dom_end.gen_time().time_next_alert  # 4
    datetime.datetime(2023, 10, 31, 9, 0)
    >>> test_fathers_day.gen_time().time_next_alert  # 1
    datetime.datetime(2023, 6, 18, 0, 0)
    >>> test_fathers_day.gen_time().time_next_alert  # 2
    datetime.datetime(2024, 6, 16, 0, 0)
    >>> test_4th_july.gen_time().time_next_alert  # 1
    datetime.datetime(2023, 7, 4, 0, 0)
    >>> test_4th_july.gen_time().time_next_alert  # 2
    datetime.datetime(2024, 7, 4, 0, 0)
    >>> test_mlk_day.gen_time().time_next_alert # 1
    datetime.datetime(2024, 1, 15, 0, 0)
    >>> test_mlk_day.gen_time().time_next_alert # 2
    datetime.datetime(2025, 1, 20, 0, 0)

    """

    essential_attribs = [
        ('title', TAG_TITLE, None),
        ('time_start', TAG__START, None), 
        ('mins_adv', TAG_ADVANCE_ALARM, ZERO),
        ('tone', TAG_ALARM_SOUND, None),
        ('can_speak_title', TAG_SPEAK_TITLE, False),
        ('count_repeat', TAG_REPEAT_LOOP, 1),
        ('secs_repeat', TAG_REPEAT_INTERVAL, 3.5),
        ('ofs', TAG_OFFSET, ZERO),
        ('is_ofs_days', TAG_IS_OFFSET_TYPE_DAYS, "N"),
        ('ofs_in_mo', TAG_OFFSET_IN_MONTH, ZERO),
        ('is_ofs_in_mo_days', TAG_IS_OFFSET_IN_MONTH_TYPE_DAYS, "N"),
        ('time_stop', TAG_STOP, None),            
        ]

    # *mins_adv*: There is no alarm if this is set to NOT_AVAIL.  This
    # is preparation time in minutes.  If *mins_adv* is positive, the
    # alarm rings several minutes in advance of the scheduled event.
    # To schedule a time-limit alarm during an event, set *mins_adv*
    # to a negative value.

    # *time_start*: This is the date/time of the alarm when first
    # *scheduled.

    # *time_stop*: Alarms will not be scheduled after the *time_stop*
    # date/time.

    # *ofs*: If this is not positive, then the alarm is non-recurring.

    # *is_ofs_days*: If True, then *ofs* is days; otherwise, it is
    # *months.

    # *ofs_in_mo*: Event will be on the same day of the month as
    # *time_start* if this is ZERO or NOT_AVAIL.  If this is positive,
    # it is an offset from the beginning of the month.  If this is
    # negtive, it is an offset from the end of the month.

    # *is_ofs_in_mo_days*: If True, then *ofs_in_mo* is days.  If
    # False, it is weeks, and event will be on the same day of the
    # week as *time_start*.

    def recode_offsets(self):
        self.is_audible = not self.mins_adv in BLANK_VALUES
        if self.is_audible:
            self.mins_adv_diff = datetime.timedelta(minutes=self.mins_adv)
        else:
            self.mins_adv_diff = datetime.timedelta(seconds=ZERO)
        self.is_recurring = (not self.ofs in BLANK_VALUES) and (self.ofs > ZERO)
        self.is_ofs_days = self.is_ofs_days in ['Y']
        if (not self.ofs in BLANK_VALUES):
            if self.is_ofs_days:
                self.ofs_days = self.ofs
                self.ofs_mos = ZERO
            else:
                self.ofs_days = ZERO
                self.ofs_mos = self.ofs
        else:
            self.ofs_days = ZERO
            self.ofs_mos = ZERO
        del self.ofs
        self.is_ofs_in_mo_days = self.is_ofs_in_mo_days in ['Y']
        if (self.ofs_in_mo in BLANK_VALUES) or (self.ofs_in_mo is ZERO):
            self.is_ofs_from_beg = False
            self.is_ofs_from_end = False
            self.ofs_in_mo_days = None
            self.ofs_in_mo_weeks = None
        else:
            self.is_ofs_from_beg = self.ofs_in_mo > ZERO
            self.is_ofs_from_end = not self.is_ofs_from_beg
            if self.is_ofs_in_mo_days:
                self.ofs_in_mo_days = self.ofs_in_mo
                self.ofs_in_mo_weeks = ZERO
            else:
                self.ofs_in_mo_days = ZERO
                self.ofs_in_mo_weeks = self.ofs_in_mo
        del self.ofs_in_mo
        return self

    def __init__(self, parent_rel=None, today=None):
        if parent_rel:
            self.parent_rel = parent_rel
            self.parent_rec = self.parent_rel.recs[self.parent_rel.ndx_rec]
        else:
            self.parent_rel = None
            self.parent_rec = None
        self.gen_time_restart(today)
        self.time_next_alert = None
        return 

    def create_from_rec(self):
        for (attrib, tag, default) in self.essential_attribs:
            itm = self.parent_rel.pages.find(tag)
            if itm:
                if itm.val_comp in BLANK_VALUES:
                    setattr(self, attrib, default)
                else:
                    setattr(self, attrib, itm.val_comp)
            else:
                setattr(self, attrib, default)
        self.recode_offsets()
        return self

    def new(self, **parms):
        for (attrib, tag, default) in self.essential_attribs:
            setattr(self, attrib, parms.get(attrib, default))
        self.recode_offsets()
        return self

    def gen_time_restart(self, today):
        if today:
            pass
        else:
            today = datetime.date.today()
        self._iter = self.gen_time_iter(today)
        return self

    def gen_time(self):
        try:
            self.time_next_alert = next(self._iter)
        except StopIteration:
            self.time_next_alert = None
        return self

    def gen_time_iter(self, today):

        def bump_days(result):
            count = self.ofs_days
            while count:
                result += DELTA_DAY
                count -= 1
            return result

        def bump_mos(result):
            yr_old = result.year
            mo_old = result.month
            day_old = result.day
            time_old = result.time()
            mo_old -= 1
            (yr_ofs, mo_new) = divmod(mo_old + self.ofs_mos, 12)
            mo_new += 1
            yr_old += yr_ofs
            while True:
                try:
                    result = datetime.datetime.combine(datetime.date(yr_old, mo_new, day_old), time_old)
                except ValueError:
                    result = None
                if result:
                    break
                else:
                    day_old -= 1
            return result

        def find_mo_beg(result):
            yr_old = result.year
            mo_old = result.month
            day_old = 1
            time_old = result.time()
            result = datetime.datetime.combine(datetime.date(yr_old, mo_old, day_old), time_old)
            return result        

        def find_mo_end(result):
            yr_old = result.year
            mo_old = result.month
            day_old = 32
            time_old = result.time()
            while True:
                try:
                    result = datetime.datetime.combine(datetime.date(yr_old, mo_old, day_old), time_old)
                except ValueError:
                    result = None
                if result:
                    break
                day_old -= 1
            return result        

        def ofs_days_in_mo(result, delta_days):
            diff = datetime.timedelta(days=self.ofs_in_mo_days - delta_days)
            result += diff
            return result

        def ofs_weeks_in_mo(result, delta_days):
            diff = datetime.timedelta(days=(self.ofs_in_mo_weeks - delta_days) * 7)
            result += diff
            if delta_days:
                diff = datetime.timedelta(days=delta_days)
                while result.weekday() != self.d0w:
                    result += diff
            return result

        result = self.time_start
        if result:
            result -= self.mins_adv_diff  # test_adv
            self.d0w = result.weekday()
            while True:
                if is_date_instance(self.time_stop):
                    if result.date() > self.time_stop:  # test_stop
                        break
                elif isinstance(self.time_stop, datetime.datetime):
                    if result > self.time_stop:  # test_stop
                        break
                if result.date() >= today:  # test_past  # test_future
                    yield result
                result_prev = result
                if self.is_recurring:
                    result = bump_days(result)
                    result = bump_mos(result)  # test_bump_mos
                    if self.is_ofs_from_beg:
                        result = find_mo_beg(result)
                        if self.is_ofs_in_mo_days:
                            result = ofs_days_in_mo(result, 1)  # test_dom_beg
                        else:
                            result = ofs_weeks_in_mo(result, 1)  # test_wom_beg
                    if self.is_ofs_from_end:
                        result = find_mo_end(result)
                        if self.is_ofs_in_mo_days:
                            result = ofs_days_in_mo(result, -1)  # test_dom_end
                        else:
                            result = ofs_weeks_in_mo(result, -1)  # test_wom_end
                if result == result_prev:
                    break
        return

    def event_ring(self):
        if self.is_audible:
            self.alert()
        self.gen_time()
        return

    def alert(self):

        def beep(msg, count_repeat, secs_repeat, secs_delay):
            while not msg.is_finished:
                count = count_repeat
                while count:
                    COMMON['APP'].beep()
                    sleeper = q0.Q0Timer(secs_delay * 1000).single_shot()
                    while sleeper.is_semaphore_up():
                        COMMON['APP'].process_events()
                    count -= 1
                if self.title in BLANK_VALUES:
                    pass
                elif self.can_speak_title in ['Y']:
                    announce(self.title)
                sleeper = q0.Q0Timer(secs_repeat * 1000).single_shot()
                while (not msg.is_finished) and sleeper.is_semaphore_up():
                    COMMON['APP'].process_events()
            return

        def wav(msg, wav_file_name, count_repeat, secs_repeat):
            tone = q0.Q0Sound(wav_file_name, count_repeat)
            while not msg.is_finished:
                tone.play()
                while not tone.isFinished():
                    COMMON['APP'].process_events()
                if self.title in BLANK_VALUES:
                    pass
                elif self.can_speak_title in ['Y']:
                    announce(self.title)
                sleeper = q0.Q0Timer(secs_repeat * 1000).single_shot()
                while (not msg.is_finished) and sleeper.is_semaphore_up():
                    COMMON['APP'].process_events()
            return

        fld = ItmDateTime()
        fld.val_comp = self.time_next_alert
        msg = q0.Q0Alert(q0_app=COMMON['APP'], q0_title=_('Alarm'), q0_visual=str(self))
        msg.open()
        if self.tone in BLANK_VALUES:
            if COMMON['CONFIG'].alert_wav in BLANK_VALUES:
                method = beep
                parms = {
                    'msg': msg,
                    'count_repeat': 5,
                    'secs_repeat': 3.5 - 5 * 0.280,
                    'secs_delay': 0.280,
                    }
            else:
                method = wav
                parms = {
                    'msg': msg,
                    'wav_file_name': COMMON['CONFIG'].alert_wav,
                    'count_repeat': 1,
                    'secs_repeat': 3.5,
                    }
        else:
            method = wav
            parms = {
                'msg': msg,
                'wav_file_name': strip_protocol_scheme(self.tone),
                'count_repeat': self.count_repeat,
                'secs_repeat': self.secs_repeat,
                }
        method(**parms)
        return self

    def __str__(self):
        fld = ItmDateTime()
        fld.val_comp = self.time_next_alert
        txt_time = fld.val_disp.replace(SPACE, '&nbsp;')
        txt_title = self.title.replace(SPACE, '&nbsp;')
        result = f'<td><tt>{txt_time}</tt></td><td><b>{txt_title}</b></td>'
        return result

    def __lt__(self, other):

        """Compare alarms by alert time.

        """
        
        if None in [self.time_next_alert, other.time_next_alert]:
            result = NotImplemented
        else:
            result = self.time_next_alert < other.time_next_alert
        return result


class Alarms(list):

    """A list of events.

    """    
    
    def start(self):
        self.awaken = q0.Q0Timer(wait_msecs=30000, is_single_shot=False, event=self.event_audit).start()
        return self

    def event_audit(self):
        t0 = datetime.datetime.now()
        m1 = datetime.timedelta(minutes=1)
        t1 = t0 + m1
        collection = []
        for (ndx, alarm) in enumerate(self):
            if t0 <= alarm.time_next_alert <= t1:
                alarm.event_ring()
                if alarm.time_next_alert:
                    pass
                else:
                    collection.append(ndx)
        collection.reverse()
        for ndx in collection:
            del self[ndx]
        return self

    def elim_dups(self, alarm_new):
        collection = []
        for (ndx, alarm_old) in enumerate(self):
            if alarm_new.parent_rec == alarm_old.parent_rec:
                collection.append(ndx)
        collection.reverse()
        for ndx in collection:
            del self[ndx]
        return self

    def schedule(self, alarm):
        alarm.gen_time()
        if alarm.time_next_alert:
            self.elim_dups(alarm)
            self.append(alarm)
        return self

    def collect_dates(self, date_range):
        (date_lo, date_hi) = date_range
        result = {}
        for alarm in self:
            alarm.gen_time_restart(date_lo)
            while True:
                alarm.gen_time()
                date_time = alarm.time_next_alert
                if date_time:
                    date = date_time.date()
                    if date <= date_hi:
                        collection = result.setdefault(date, Alarms())
                        collection.append(alarm)
                    else:
                        break
                else:
                    break
        return result

    def sort_by_time(self):

        def get_time(alarm):
            result = alarm.time_next_alert
            return result

        self.sort(key=get_time)
        return self

    def sort_by_priority(self):

        def get_priority(alarm):
            if alarm.parent_rec:
                result = alarm.parent_rec.get(TAG_PRIORITY)
                if result in BLANK_VALUES:
                    result = None
            else:
                result = None    
            return result

        self.sort(key=get_priority)
        return self

    def __str__(self):
        result = []
        result.append('<table>')
        for (ndx, alarm) in enumerate(self):
            result.append('<tr>')
            result.append(str(alarm))
            result.append('</tr>')
        result.append('</table>')
        return '\n'.join(result)


def main_line():

    """Main loop.

    """    
    
    global MAIN_WIN
    
    with MainWindow() as MAIN_WIN:
        MAIN_WIN.build_menu_bar()
        MAIN_WIN.build_menu_popup()
        cent_wgt = MAIN_WIN.set_central_widget(q0.Q0Widget())
        MAIN_WIN.tabs = TabList().load(cent_wgt)
        open_tabs = MAIN_WIN.tabs.tab_wgt.get_tab_tags_left_to_right()
        try:
            ndx = open_tabs.index(COMMON['CONFIG'].current_tab_visual)
        except ValueError:
            ndx = NA
        if ndx == NA:
            pass
        else:
            MAIN_WIN.tabs.tab_wgt.select(ndx)
    result = COMMON['APP'].exec_()  # Start the q0 application event loop.
    return result


HOLIDAYS = """Project,Title,_Handle,Priority,Status,Remarks,ForegroundColor,BackgroundColor,_Start,_Duration,AdvanceAlarm,AlarmSound,SpeakTitle,RepeatInterval,RepeatLoop,Offset,IsOffsetTypeDays,OffsetInMonth,IsOffsetInMonthTypeDays,Stop,_AccessionDate,_UpdateDate,Keywords
~Holidays,New Year's Day,New Year's Day,0,Inactive,#N/A,red,#N/A,2005-01-01 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,1,Y,#N/A,2006-02-17 14:21:00.000000,2023-06-26 15:15:31.544893,#N/A
~Holidays,ML King Day,ML King Day,0,Inactive,#N/A,red,#N/A,2005-01-17 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,3,N,#N/A,2006-02-24 17:40:00.000000,2023-06-25 15:54:29.243175,#N/A
~Holidays,Valentine's Day,Valentine's Day,0,Inactive,#N/A,#N/A,#N/A,2005-02-14 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,14,Y,#N/A,2006-02-25 13:16:00.000000,2023-06-26 15:16:34.651726,#N/A
~Holidays,Presidents' Day,Presidents' Day,0,Inactive,#N/A,red,#N/A,2005-02-21 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,3,N,#N/A,2006-02-25 13:49:00.000000,2023-06-26 19:28:01.148720,#N/A
~Holidays,St Patrick's Day,St Patrick's Day,0,Inactive,#N/A,#N/A,#N/A,2005-03-17 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,17,Y,#N/A,2006-02-25 13:53:00.000000,2023-06-25 15:49:27.491024,#N/A
~Holidays,April Fool's Day,April Fool's Day,0,Inactive,#N/A,#N/A,#N/A,2005-04-01 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,1,Y,#N/A,2006-02-25 13:53:00.000000,2023-06-26 15:33:04.416442,#N/A
~Holidays,Mothers' Day,Mothers' Day,0,Inactive,#N/A,#N/A,#N/A,2005-05-08 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,2,N,#N/A,2006-02-25 13:53:00.000000,2023-06-26 15:45:35.703261,#N/A
~Holidays,Memorial Day,Memorial Day,0,Inactive,#N/A,red,#N/A,2005-05-30 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,-1,N,#N/A,2006-02-25 13:53:00.000000,2023-06-25 15:59:12.665689,#N/A
~Holidays,Fathers' Day,Fathers' Day,0,Inactive,#N/A,#N/A,#N/A,2005-06-19 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,3,N,#N/A,2006-02-25 13:53:00.000000,2023-06-26 15:46:34.956701,#N/A
~Holidays,Independence Day,Independence Day,9,Inactive,#N/A,red,#N/A,2005-07-04 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,4,Y,#N/A,2006-02-25 13:53:00.000000,2023-06-26 15:46:49.577339,#N/A
~Holidays,Labor Day,Labor Day,0,Inactive,#N/A,red,#N/A,2005-09-05 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,1,N,#N/A,2006-02-25 13:53:00.000000,2023-06-26 15:47:14.693758,#N/A
~Holidays,Columbus Day,Columbus Day,0,Inactive,#N/A,red,#N/A,2005-10-10 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,2,N,#N/A,2006-02-25 13:53:00.000000,2023-06-26 15:47:40.030763,#N/A
~Holidays,Halloween,Halloween,0,Inactive,#N/A,#N/A,#N/A,2005-10-31 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,31,Y,#N/A,2006-02-25 13:53:00.000000,2023-06-26 15:47:52.937082,#N/A
~Holidays,Veterans' Day,Veterans' Day,0,Inactive,#N/A,red,#N/A,2005-11-11 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,11,Y,#N/A,2006-02-25 13:53:00.000000,2023-06-26 15:48:08.682416,#N/A
~Holidays,Thanksgiving,Thanksgiving,0,Inactive,#N/A,red,#N/A,2005-11-24 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,4,N,#N/A,2006-02-25 13:53:00.000000,2023-06-26 15:48:32.030216,#N/A
~Holidays,Christmas,Christmas,0,Inactive,#N/A,red,#N/A,2005-12-25 00:00:00.000000,#N/A,#N/A,#N/A,#N/A,#N/A,#N/A,12,N,25,Y,#N/A,2006-02-25 13:53:00.000000,2023-06-26 16:05:01.533939,#N/A"""        


def entry_point():

    global COMMON

    COMMON = {}
    if False:
        import doctest
        doctest.testmod()
        raise NotImplementedError
    print(__doc__, file=sys.stdout)
    COMMON['CONFIG'] = Config().load()
    COMMON['APP'] = q0.Q0Application()
    COMMON['APP'].set_window_icon(q0.Q0Icon(COMMON['CONFIG'].icon_file))
    COMMON['ALARMS'] = Alarms().start()
    COMMON['RECS_CUT'] = q0.ClipboardKind(COMMON['APP'], mime_type='x.tonto_recs+json')
    retcd = main_line()
    if retcd:
        pass
    else:
        COMMON['CONFIG'].save()
    sys.exit(retcd)


if __name__ == "__main__":
    entry_point()

    
# Fin
