#!/usr/bin/python3

# tonto2_parse_international_addresses.py
# ccr . 2023 Jun 28

# ==================================================boilerplate»=====
# *Tonto2* is a rewrite of *tonto* v1.2.
# 
# Copyright 2006—2023 by Chuck Rhode.
# 
# See LICENSE.txt for your rights.
# =================================================«boilerplate======

"""Recognize and parse mailing addresses of various countries.

This code is sketchy.  It follows the examples in:

+ https://en.wikipedia.org/wiki/Address

It relies mostly on anglicized country names.

This is not A-I.  It cannot and will not be successful with all or
even very many legitimate addresses, and it has the propensity to
throw false positives.  Given the correct country, it can probably
recognize postal codes in the trailing portions of most address
blocks.  Please be aware that it is bone-headed about expecting the
top line to be a first-name-last-name sequence.  If it cannot find a
country name in the text provided, it uses USA parsing rules.

This module provides classes for recognizing telephone numbers and
latitude/longitude strings as well capturing URIs for eMail and other
network addresses.

"""

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1
NOT_AVAIL = '#N/A'
BLANK_VALUES = [NULL, None, NOT_AVAIL]
MARKDN_LINE_END = '<br />'

import re
import tonto2.externals.tonto2_code_tables as tonto2_code_tables

    
PAT_LEFT_MARGIN = re.compile(r'^[\s>+\.]*', re.DOTALL)


def extract_digits(txt):

    """Return a string of the digits in txt.

    This is used to parse telephone numbers.

    """

    result = [c for c in txt if c.isdecimal()]
    return NULL.join(result)


def find_country(txt):

    """Extract a country name from txt.

    """

    txt_upper = txt.upper()
    targets = tonto2_code_tables.TAB_BY_NAME['COUNTRIES'].meanings + list(ADR_BY_COUNTRY.keys())
    for disp in targets:
        ndx = disp.find('\t') + 1
        result = disp[ndx:]
        if result.upper() in txt_upper:
            break
    else:
        result = NULL
    return result


def parse_adr(txt_in):

    """Parse an address according to its detected country.

    """

    target = find_country(txt_in)
    adr_cls = ADR_BY_COUNTRY.get(target, Adr)
    adr = adr_cls()
    txt_out = adr.parse(txt_in)
    result = (adr, txt_out)
    return result


def new_adr(**parms):

    """Assemble an address from its parts.

    """

    target = parms.get('country', NOT_AVAIL)
    adr_cls = ADR_BY_COUNTRY.get(target, Adr)
    result = adr_cls(**parms)
    return result


class Adr():

    """Base address class.

    """
    
    country = NOT_AVAIL
    are_lines_inverted = False
    rex_state = r'[A-Z]{2}'
    rex_zip = r'\d{5}(:?-\d{4})?'
    rex_city_state_zip = rf'^([^\n,]+),\s+({rex_state})\s+({rex_zip})$'
    grp_city = 1
    grp_state = 2
    grp_zip = 3
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (', ', 'state'),
        (SPACE * 2, 'zipcode'),
        ('|', 'country'),
        ]
    

    def __init__(self, **parms):
        self.pat_city_state_zip = re.compile(self.rex_city_state_zip, re.MULTILINE | re.DOTALL)
        self.city = NOT_AVAIL
        self.state = NOT_AVAIL
        self.zipcode = NOT_AVAIL
        self.street = NOT_AVAIL
        self.locus = NOT_AVAIL
        self.dept_mail_stop = NOT_AVAIL
        self.company = NOT_AVAIL
        self.polite_mode = NOT_AVAIL
        self.first_name = NOT_AVAIL
        self.last_name = NOT_AVAIL
        self.title = NOT_AVAIL
        for (key, val) in parms.items():
            setattr(self, key, val)
        return

    def strip_margins(self, lines):
        result = []
        for line in lines:
            line = PAT_LEFT_MARGIN.sub(NULL, line.strip())
            result.append(line)
        return result

    def parse(self, txt):
        lines = self.strip_margins(txt.splitlines())
        txt = '\n'.join(lines)
        result = txt
        pgraphs = txt.split('\n\n')
        for (ndx_pgraph, pgraph) in enumerate(pgraphs):
            match = self.pat_city_state_zip.search(pgraph)
            if match:
                if self.grp_city:
                    self.city = match.group(self.grp_city)
                if self.grp_state:
                    self.state = match.group(self.grp_state)
                if self.grp_zip:
                    self.zipcode = match.group(self.grp_zip)
                self.parse_top_lines(pgraph, pos_match=(match.start(), match.end()))
                pgraph = f'<font color=gray>{pgraph}</font>'
                pgraphs[ndx_pgraph] = pgraph.replace('\n', MARKDN_LINE_END)
                result = MARKDN_LINE_END.join(pgraphs)
                break
        return result

    def parse_top_lines(self, pgraph, pos_match):
        significance = ['street', 'locus', 'dept_mail_stop', 'company']
        count_max = len(significance)
        (pos_lo, pos_hi) = pos_match
        if self.are_lines_inverted:
            bottom = pgraph[pos_hi:].strip()
            lines = bottom.splitlines()
        else:
            top = pgraph[:pos_lo].strip()
            lines = top.splitlines()
            lines.reverse()
        for (ndx_line, line) in enumerate(lines[:-1]):
            try:
                setattr(self, significance[ndx_line], line)
            except IndexError:
                pass
        if lines:
            top_line = lines[-1]
            (top_line, self.title) = (top_line.split(',', 1) + [NOT_AVAIL])[:2]
            self.title = self.title.strip()
            (polite_mode, remainder) = ([NOT_AVAIL] + top_line.split('.', 1))[-2:]
            if len(polite_mode) < 5:
                if polite_mode in BLANK_VALUES:
                    pass
                else:
                    self.polite_mode = f'{polite_mode}.'
                top_line = remainder
            words = top_line.split()
            if words:
                self.last_name = words[-1]
                self.first_name = SPACE.join(words[:-1])
        return self

    def __str__(self):
        result = []
        for (delim, tag) in self.tmpl:
            attrib = getattr(self, tag, tag)
            if attrib in BLANK_VALUES:
                pass
            else:
                if delim:
                    if result:
                        if result[-1] in ['|']:
                            pass
                        else:
                            result.append(delim)
                result.append(attrib)
        return NULL.join(result)

    def view_as_text(self):
        result = str(self).replace('|', MARKDN_LINE_END)
        return result


class AdrArgentina(Adr):

    """
    >>> adr = AdrArgentina()
    >>> txt = adr.parse('''
    ...
    ... Luis Escala
    ... Piedras 623
    ... Piso 2, depto 4
    ... C1070AAM, Capital Federal
    ... 
    ... ''')
    >>> adr.last_name
    'Escala'
    >>> adr.city
    'Capital Federal'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    'C1070AAM'
    >>> str(adr)
    'Luis Escala|Piedras 623|Piso 2, depto 4|C1070AAM, Capital Federal|Argentina'
    """

    country = 'Argentina'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'[A-Z]\d{4}[A-Z]{3}'
    rex_city_state_zip = rf'^({rex_zip}),\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (', ', 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrAustralia(Adr):

    """
    >>> adr = AdrAustralia()
    >>> txt = adr.parse('''
    ...
    ... Ms. H Williams
    ... Finance and Accounting
    ... Australia Post
    ... 219–241 Cleveland St
    ... STRAWBERRY HILLS  NSW  1427 
    ... 
    ... ''')
    >>> adr.polite_mode
    'Ms.'
    >>> adr.last_name
    'Williams'
    >>> adr.city
    'STRAWBERRY HILLS'
    >>> adr.state
    'NSW'
    >>> adr.zipcode
    '1427'
    >>> str(adr)
    'Ms. H Williams|Finance and Accounting|Australia Post|219–241 Cleveland St|STRAWBERRY HILLS  NSW  1427|Australia'
    """

    country = 'Australia'
    are_lines_inverted = False
    rex_state = r'[A-Z]{2,3}'
    rex_zip = r'\d{4}'
    rex_city_state_zip = rf'^([^\n]+?)\s+({rex_state})\s+({rex_zip})$'
    grp_city = 1
    grp_state = 2
    grp_zip = 3
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE * 2, 'state'),
        (SPACE * 2, 'zipcode'),
        ('|', 'country'),
        ]


class AdrAustria(Adr):

    """
    >>> adr = AdrAustria()
    >>> txt = adr.parse('''
    ... 
    ... Hans Schmidt
    ... Firma ABC
    ... Kundendienst
    ... Hauptstr. 5
    ... 1234 Musterstadt
    ... 
    ... ''')
    >>> adr.last_name
    'Schmidt'
    >>> adr.city
    'Musterstadt'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '1234'
    >>> str(adr)
    'Hans Schmidt|Firma ABC|Kundendienst|Hauptstr. 5|1234 Musterstadt|Austria'
    """

    country = 'Austria'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{4}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrBangladesh(Adr):

    """
    >>> adr = AdrBangladesh()
    >>> txt = adr.parse('''
    ...
    ... Sheikh Mujibur Rahman
    ... Dhanmondi. 32
    ... Dhaka-1209
    ... Bangladesh 
    ... 
    ... ''')
    >>> adr.last_name
    'Rahman'
    >>> adr.city
    'Dhaka'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '1209'
    >>> str(adr)
    'Sheikh Mujibur Rahman|Dhanmondi. 32|Dhaka-1209|Bangladesh'
    """

    country = 'Bangladesh'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{4}'
    rex_city_state_zip = rf'^([^\n-]+)-({rex_zip})$'
    grp_city = 1
    grp_state = None
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('-', 'zipcode'),
        ('|', 'country'),
        ]


class AdrBelgium(Adr):

    """
    >>> adr = AdrBelgium()
    >>> txt = adr.parse('''
    ...
    ... M. Alain Dupont
    ... Directeur Service Clients
    ... Acme SA
    ... Bloc A - étage 4
    ... Rue du Vivier 7C bte 5
    ... 1000 Bruxelles
    ... BELGIQUE
    ... 
    ... ''')
    >>> adr.polite_mode
    'M.'
    >>> adr.last_name
    'Dupont'
    >>> adr.city
    'Bruxelles'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '1000'
    >>> str(adr)
    'M. Alain Dupont|Directeur Service Clients|Acme SA|Bloc A - étage 4|Rue du Vivier 7C bte 5|1000 Bruxelles|Belgique'
    """

    country = "Belgique"
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{4}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]

    
class AdrBrazil(Adr):

    """
    >>> adr = AdrBrazil()
    >>> txt = adr.parse('''
    ...
    ... Carlos Rossi
    ... Avenida João Jorge, 112, ap. 31
    ... Vila Industrial
    ... Campinas - SP
    ... 13035-680
    ... 
    ... ''')
    >>> adr.last_name
    'Rossi'
    >>> adr.city
    'Campinas'
    >>> adr.state
    'SP'
    >>> adr.zipcode
    '13035-680'
    >>> str(adr)
    'Carlos Rossi|Avenida João Jorge, 112, ap. 31|Vila Industrial|Campinas - SP|13035-680|Brazil'
    """

    country = "Brazil"
    are_lines_inverted = False
    rex_state = r'[A-Z]{2}'
    rex_zip = r'\d{5}-\d{3}'
    rex_city_state_zip = rf'^([^\n]+?)\s+-\s+({rex_state})\s+({rex_zip})$'
    grp_city = 1
    grp_state = 2
    grp_zip = 3
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (' - ', 'state'),
        ('|', 'zipcode'),
        ('|', 'country'),
        ]


class AdrCanada(Adr):

    """
    >>> adr = AdrCanada()
    >>> txt = adr.parse('''
    ... 
    ... Monsieur Jean-Pierre Lamarre
    ... 101–3485, rue de la Montagne
    ... Montréal (Québec)  H3G 2A6
    ... 
    ... ''')
    >>> adr.last_name
    'Lamarre'
    >>> adr.city
    'Montréal'
    >>> adr.state
    '(Québec)'
    >>> adr.zipcode
    'H3G 2A6'
    >>> str(adr)
    'Monsieur Jean-Pierre Lamarre|101–3485, rue de la Montagne|Montréal (Québec)  H3G 2A6|Canada'
    """

    country = 'Canada'
    are_lines_inverted = False
    rex_state = r'(?:[A-Z]{2})|(?:\([^\)]+\))'
    rex_zip = r'[A-Z]\d[A-Z]\s\d[A-Z]\d'
    rex_city_state_zip = rf'^([^\n]+?)\s+({rex_state})\s+({rex_zip})$'
    grp_city = 1
    grp_state = 2
    grp_zip = 3
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        (SPACE * 2, 'zipcode'),
        ('|', 'country'),
        ]


class AdrChina(Adr):

    """
    >>> adr = AdrChina()
    >>> txt = adr.parse('''
    ... 
    ... P.R. China 528400
    ... Beijing City, Dongcheng District, Mingdu Road, Hengda Garden, 7th Building, Room 702
    ... To: Mr. Xiaoming Zhang 
    ... 
    ... ''')
    >>> adr.last_name
    'Zhang'
    >>> adr.city
    'Beijing City'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '528400'
    >>> str(adr)
    'P.R. China 528400|Beijing City, Dongcheng District, Mingdu Road, Hengda Garden, 7th Building, Room 702|To: Mr. Xiaoming Zhang'
    """

    country = 'P.R. China'
    are_lines_inverted = True
    rex_state = None
    rex_zip = r'\d{6}'
    rex_city_state_zip = rf'^P.R. China\s+({rex_zip})\s+([^,]+?),'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'country'),
        (SPACE, 'zipcode'),
        ('|', 'city'),
        (SPACE, 'state'),
        (', ', 'street'),
        ('|', 'locus'),
        ('|', 'dept_mail_stop'),
        ('|', 'company'),
        (None, '|'),
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ]


class AdrCroatia(Adr):

    """
    >>> adr = AdrCroatia()
    >>> txt = adr.parse('''
    ... 
    ... Hrvoje Horvat
    ... Soblinec
    ... 1. kat, stan 2
    ... Soblinečka ulica 1
    ... 10360 SESVETE
    ... CROATIA
    ... 
    ... ''')
    >>> adr.last_name
    'Horvat'
    >>> adr.city
    'SESVETE'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '10360'
    >>> str(adr)
    'Hrvoje Horvat|Soblinec|1. kat, stan 2|Soblinečka ulica 1|10360 SESVETE|Croatia'
    """

    country = 'Croatia'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrDenmark(Adr):

    """
    >>> adr = AdrDenmark()
    >>> txt = adr.parse('''
    ... 
    ... Stig Jensen
    ... Solvej 5, 4. t.v.
    ... 5250 Odense SV
    ... 
    ... ''')
    >>> adr.last_name
    'Jensen'
    >>> adr.city
    'Odense'
    >>> adr.state
    'SV'
    >>> adr.zipcode
    '5250'
    >>> str(adr)
    'Stig Jensen|Solvej 5, 4. t.v.|5250 Odense SV|Denmark'
    """

    country = 'Denmark'
    are_lines_inverted = False
    rex_state = '[A-Z]{2}'
    rex_zip = '\d{4}'
    rex_city_state_zip = rf'^({rex_zip})\s+(.+?)\s+({rex_state})$'
    grp_city = 2
    grp_state = 3
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrEstonia(Adr):

    """
    >>> adr = AdrEstonia()
    >>> txt = adr.parse('''
    ... 
    ... Kati Kask
    ... Aia tn 1–23
    ... 10615 Tallinn
    ... ESTONIA
    ... 
    ... ''')
    >>> adr.last_name
    'Kask'
    >>> adr.city
    'Tallinn'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '10615'
    >>> str(adr)
    'Kati Kask|Aia tn 1–23|10615 Tallinn|Estonia'
    """

    country = 'Estonia'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrFinland(Adr):

    """
    >>> adr = AdrFinland()
    >>> txt = adr.parse('''
    ... 
    ... Eduskunta
    ... Matti Mallikainen
    ... Mannerheimintie 30 as. 1
    ... 00100 HELSINKI
    ... Finland
    ... 
    ... ''')
    >>> adr.last_name
    'Eduskunta'
    >>> adr.city
    'HELSINKI'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '00100'
    >>> str(adr)
    'Eduskunta|Matti Mallikainen|Mannerheimintie 30 as. 1|00100 HELSINKI|Finland'
    """

    country = 'Finland'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]

    
class AdrFrance(Adr):

    """
    >>> adr = AdrFrance()
    >>> txt = adr.parse('''
    ... 
    ... Entreprise ABC
    ... M. Frank Bender
    ... 12 rue de la Montagne
    ... 01234 EXAMPLEVILLE
    ... 
    ... ''')
    >>> adr.last_name
    'ABC'
    >>> adr.city
    'EXAMPLEVILLE'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '01234'
    >>> str(adr)
    'Entreprise ABC|M. Frank Bender|12 rue de la Montagne|01234 EXAMPLEVILLE|France'
    """

    country = 'France'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrGermany(Adr):

    """
    >>> adr = AdrGermany()
    >>> txt = adr.parse('''
    ... 
    ... Firma ABC
    ... Kundendienst
    ... Hauptstr. 5
    ... 01234 Musterstadt
    ... 
    ... ''')
    >>> adr.last_name
    'ABC'
    >>> adr.city
    'Musterstadt'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '01234'
    >>> str(adr)
    'Firma ABC|Kundendienst|Hauptstr. 5|01234 Musterstadt|Germany'
    """

    country = 'Germany'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrGreece(Adr):

    """
    >>> adr = AdrGreece()
    >>> txt = adr.parse('''
    ... 
    ... P. Pavlou
    ... Doiranis 25
    ... 653 02  KAVALA
    ... 
    ... ''')
    >>> adr.polite_mode
    'P.'
    >>> adr.last_name
    'Pavlou'
    >>> adr.city
    'KAVALA'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '653 02'
    >>> str(adr)
    'P. Pavlou|Doiranis 25|653 02  KAVALA|Gréce'
    """

    country = 'Gréce'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{3}\s\d{2}'
    rex_city_state_zip = rf'^(?:GR-)?({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE * 2, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrIceland(Adr):

    """
    >>> adr = AdrIceland()
    >>> txt = adr.parse('''
    ... 
    ... Agnes Gísladóttir
    ... Holtsflöt 4
    ... íbúð 202 (flat 202)
    ... 300 Akranes
    ... 
    ... ''')
    >>> adr.last_name
    'Gísladóttir'
    >>> adr.city
    'Akranes'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '300'
    >>> str(adr)
    'Agnes Gísladóttir|Holtsflöt 4|íbúð 202 (flat 202)|300 Akranes|Iceland'
    """

    country = 'Iceland'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{3}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrIndia(Adr):

    """
    >>> adr = AdrIndia()
    >>> txt = adr.parse('''
    ... 
    ... Dr. Ashok Padhye
    ... General Physician
    ... A-205, Natasha Apartments
    ... 2, Inner Ring Road
    ... Domlur
    ... BANGALORE - 560071
    ... Karnataka 
    ... 
    ... ''')
    >>> adr.polite_mode
    'Dr.'
    >>> adr.last_name
    'Padhye'
    >>> adr.city
    'BANGALORE'
    >>> adr.state
    'Karnataka'
    >>> adr.zipcode
    '560071'
    >>> str(adr)
    'Dr. Ashok Padhye|General Physician|A-205, Natasha Apartments|2, Inner Ring Road|Domlur|BANGALORE - 560071|Karnataka|India'
    """

    country = 'India'
    are_lines_inverted = False
    rex_state = r'[^\n]+?'
    rex_zip = r'\d{6}'
    rex_city_state_zip = rf'^(?:([^\n]+?)\s+-\s+)?({rex_zip})\s+({rex_state})$'
    grp_city = 1
    grp_state = 3
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (' - ', 'zipcode'),
        ('|', 'state'),
        ('|', 'country'),
        ]


class AdrIraq(Adr):

    """
    >>> adr = AdrIraq()
    >>> txt = adr.parse('''
    ... 
    ... Ali Hassan
    ... Al-Mansour
    ... Mahla 609
    ... Zuqaq 8
    ... House no. 12
    ... Baghdad
    ... 10013
    ... Iraq
    ... 
    ... ''')
    >>> adr.last_name
    'Hassan'
    >>> adr.city
    '#N/A'
    >>> adr.state
    'Baghdad'
    >>> adr.zipcode
    '10013'
    >>> str(adr)
    'Ali Hassan|Al-Mansour|Mahla 609|Zuqaq 8|House no. 12|Baghdad|10013|Iraq'
    """

    country = 'Iraq'
    are_lines_inverted = False
    rex_state = r'[^\n]+?'
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_state})\s+({rex_zip})$'
    grp_city = None
    grp_state = 1
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'zipcode'),
        ('|', 'country'),
        ]


class AdrIreland(Adr):

    """
    >>> adr = AdrIreland()
    >>> txt = adr.parse('''
    ... 
    ... Lissadell House
    ... Lissadell
    ... Ballinfull
    ... Co. Sligo
    ... F91 ED70 
    ... 
    ... ''')
    >>> adr.last_name
    'House'
    >>> adr.city
    'Ballinfull'
    >>> adr.state
    'Co. Sligo'
    >>> adr.zipcode
    'F91 ED70'
    >>> str(adr)
    'Lissadell House|Lissadell|Ballinfull|Co. Sligo|F91 ED70|Ireland'
    """

    country = 'Ireland'
    are_lines_inverted = False
    rex_state = r'[^\n]+?'
    rex_zip = r'\w{3}\s+\w{4}'
    rex_city_state_zip = rf'^([^\n]+?)\s+({rex_state})\s+({rex_zip})$'
    grp_city = 1
    grp_state = 2
    grp_zip = 3
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        ('|', 'state'),
        ('|', 'zipcode'),
        ('|', 'country'),
        ]


class AdrIsrael(Adr):

    """
    >>> adr = AdrIsrael()
    >>> txt = adr.parse('''
    ... 
    ... Yisrael Yisraeli
    ... 1B/20 HaDoar
    ... 9414219 Tel Aviv, ISRAEL
    ... 
    ... ''')
    >>> adr.last_name
    'Yisraeli'
    >>> adr.city
    'Tel Aviv'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '9414219'
    >>> str(adr)
    'Yisrael Yisraeli|1B/20 HaDoar|9414219 Tel Aviv, Israel'
    """

    country = 'Israel'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{7}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)(?:, ISRAEL)?$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        (', ', 'country'),
        ]


class AdrItaly(Adr):

    """
    >>> adr = AdrItaly()
    >>> txt = adr.parse('''
    ... 
    ... Claudio Verdi
    ... via Roma 35
    ... 81055 Santa Maria Capua Vetere CE
    ... 
    ... ''')
    >>> adr.last_name
    'Verdi'
    >>> adr.city
    'Santa Maria Capua Vetere'
    >>> adr.state
    'CE'
    >>> adr.zipcode
    '81055'
    >>> str(adr)
    'Claudio Verdi|via Roma 35|81055 Santa Maria Capua Vetere CE|Italy'
    """

    country = 'Italy'
    are_lines_inverted = False
    rex_state = r'[A-Z]{2}'
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)\s+({rex_state})$'
    grp_city = 2
    grp_state = 3
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrJapan(Adr):

    """
    >>> adr = AdrJapan()
    >>> txt = adr.parse('''
    ... 
    ... Ms. Hanako Tanaka
    ... 3rd Fl. Rm. B
    ... 4-3-2 Hakusan
    ... Bunkyō-ku, Tōkyō 112-0001
    ... (Japan) 
    ... 
    ... ''')
    >>> adr.last_name
    'Tanaka'
    >>> adr.city
    'Bunkyō-ku'
    >>> adr.state
    'Tōkyō'
    >>> adr.zipcode
    '112-0001'
    >>> str(adr)
    'Ms. Hanako Tanaka|3rd Fl. Rm. B|4-3-2 Hakusan|Bunkyō-ku, Tōkyō 112-0001|(Japan)'
    """

    country = '(Japan)'
    are_lines_inverted = False
    rex_state = r'[^\s]+?'
    rex_zip = r'\d{3}-\d{4}'
    rex_city_state_zip = rf'^([^\n,]+),\s+({rex_state})\s+({rex_zip})$'
    grp_city = 1
    grp_state = 2
    grp_zip = 3
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (', ', 'state'),
        (SPACE, 'zipcode'),
        ('|', 'country'),
        ]


class AdrLatvia(Adr):

    """
    >>> adr = AdrLatvia()
    >>> txt = adr.parse('''
    ... 
    ... Andris Lapa
    ... Liepu iela 1
    ... Ērberģe
    ... Mazzalves pag.
    ... Neretas nov.
    ... LV-5133
    ... 
    ... ''')
    >>> adr.last_name
    'Lapa'
    >>> adr.city
    'Neretas nov.'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    'LV-5133'
    >>> str(adr)
    'Andris Lapa|Liepu iela 1|Ērberģe|Mazzalves pag.|Neretas nov.|LV-5133|Latvia'
    """

    country = 'Latvia'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'[A-Z]{2}-\d{4}'
    rex_city_state_zip = rf'^([^\n]+?)\s+({rex_zip})$'
    grp_city = 1
    grp_state = None
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'zipcode'),
        ('|', 'country'),
        ]


class AdrMalaysia(Adr):

    """
    >>> adr = AdrMalaysia()
    >>> txt = adr.parse('''
    ... 
    ... Dato' S.M. Nasrudin
    ... Managing Director
    ... Capital Shipping Bhd.
    ... Lot 323, 1st Floor, Bintang Commercial Centre
    ... 29 Jalan Sekilau
    ... 81300 JOHOR BAHRU
    ... JOHOR
    ... MALAYSIA
    ... 
    ... ''')
    >>> adr.last_name
    'Nasrudin'
    >>> adr.company
    'Managing Director'
    >>> adr.city
    'JOHOR BAHRU'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '81300'
    >>> str(adr)
    "Dato' S.M. Nasrudin|Managing Director|Capital Shipping Bhd.|Lot 323, 1st Floor, Bintang Commercial Centre|29 Jalan Sekilau|81300 JOHOR BAHRU|Malaysia"
    """

    country = 'Malaysia'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrMexico(Adr):

    """
    >>> adr = AdrMexico()
    >>> txt = adr.parse('''
    ... 
    ... Ing. Juan Rodríguez Altamirano
    ... Farmacéutica Altamirano
    ... Av. Durango No. 264 Int. 1
    ... Col. Primer Cuadro
    ... 81200 Los Mochis, Ahome, Sin. 
    ... 
    ... ''')
    >>> adr.last_name
    'Altamirano'
    >>> adr.dept_mail_stop
    'Farmacéutica Altamirano'
    >>> adr.city
    'Los Mochis, Ahome'
    >>> adr.state
    'Sin.'
    >>> adr.zipcode
    '81200'
    >>> str(adr)
    'Ing. Juan Rodríguez Altamirano|Farmacéutica Altamirano|Av. Durango No. 264 Int. 1|Col. Primer Cuadro|81200 Los Mochis, Ahome, Sin.|México'
    """

    country = 'México'
    are_lines_inverted = False
    rex_state = r'\w+\.'
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_zip})\s+(.+?),\s+({rex_state})$'
    grp_city = 2
    grp_state = 3
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (', ', 'state'),
        ('|', 'country'),
        ]


class AdrNorway(Adr):

    """
    >>> adr = AdrNorway()
    >>> txt = adr.parse('''
    ... 
    ... Kari Normann
    ... Storgata 81A
    ... 6415 Molde 
    ... 
    ... ''')
    >>> adr.last_name
    'Normann'
    >>> adr.city
    'Molde'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '6415'
    >>> str(adr)
    'Kari Normann|Storgata 81A|6415 Molde|Norway'
    """

    country = 'Norway'
    are_lines_inverted = False
    rex_state = None
    rex_zip = '\d{4}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrPakistan(Adr):

    """
    >>> adr = AdrPakistan()
    >>> txt = adr.parse('''
    ... 
    ... Muhammad Abdullah Umar
    ... 15, M. A. Jinnah Road
    ... Kharadar, Saddar
    ... Karachi
    ... Karachi District
    ... 457700
    ... Sindh 
    ... 
    ... ''')
    >>> adr.last_name
    'Umar'
    >>> adr.city
    'Karachi District'
    >>> adr.state
    'Sindh'
    >>> adr.zipcode
    '457700'
    >>> str(adr)
    'Muhammad Abdullah Umar|15, M. A. Jinnah Road|Kharadar, Saddar|Karachi|Karachi District|457700|Sindh|Pakistan'
    """

    country = 'Pakistan'
    are_lines_inverted = False
    rex_state = r'[^\n]+?'
    rex_zip = '\d{6}'
    rex_city_state_zip = rf'^([^\n]+?)\s+({rex_zip})\s+({rex_state})$'
    grp_city = 1
    grp_state = 3
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        ('|', 'city'),
        ('|', 'zipcode'),
        ('|', 'state'),
        ('|', 'country'),
        ]


class AdrPhilippines(Adr):

    """
    >>> adr = AdrPhilippines()
    >>> txt = adr.parse('''
    ... 
    ... Mr. Juan Maliksi
    ... 121 Epifanio Delos Santos Ave., Wack-wack Greenhills, Mandaluyong
    ... 1550 METRO MANILA 
    ... 
    ... ''')
    >>> adr.last_name
    'Maliksi'
    >>> adr.city
    'METRO MANILA'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '1550'
    >>> str(adr)
    'Mr. Juan Maliksi|121 Epifanio Delos Santos Ave., Wack-wack Greenhills, Mandaluyong|1550 METRO MANILA|Philippines'
    """

    country = 'Philippines'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{4}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrPoland(Adr):

    """
    >>> adr = AdrPoland()
    >>> txt = adr.parse('''
    ... 
    ... Jan Kowalski
    ... ul. Wiejska 4/6
    ... 00-902 WARSZAWA
    ... POLAND (POLSKA) 
    ... 
    ... ''')
    >>> adr.last_name
    'Kowalski'
    >>> adr.city
    'WARSZAWA'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '00-902'
    >>> str(adr)
    'Jan Kowalski|ul. Wiejska 4/6|00-902 WARSZAWA|Poland (Polska)'
    """

    country = 'Poland (Polska)'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{2}-\d{3}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrPortugal(Adr):

    """
    >>> adr = AdrPortugal()
    >>> txt = adr.parse('''
    ... 
    ... José Saramago
    ... Rua da Liberdade, 34, 2º Esq.
    ... 4000-000 Porto
    ... Portugal 
    ... 
    ... ''')
    >>> adr.last_name
    'Saramago'
    >>> adr.city
    'Porto'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '4000-000'
    >>> str(adr)
    'José Saramago|Rua da Liberdade, 34, 2º Esq.|4000-000 Porto|Portugal'
    """

    country = 'Portugal'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{4}-\d{3}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrRussia(Adr):

    """
    >>> adr = AdrRussia()
    >>> txt = adr.parse('''
    ... 
    ... Гусев Иван Сергеевич
    ... ул. Победы, д. 20, кв. 29
    ... пос. Октябрьский
    ... Борский р-н
    ... Нижегородская обл.
    ... 606480
    ... Russia, Россия 
    ... 
    ... ''')
    >>> adr.last_name
    'Сергеевич'
    >>> adr.city
    '#N/A'
    >>> adr.state
    'Нижегородская обл.'
    >>> adr.zipcode
    '606480'
    >>> str(adr)
    'Гусев Иван Сергеевич|ул. Победы, д. 20, кв. 29|пос. Октябрьский|Борский р-н|Нижегородская обл.|606480|Russia, Россия'
    """

    country = 'Russia, Россия'
    are_lines_inverted = False
    rex_state = r'[^\n]+?'
    rex_zip = r'\d{6}'
    rex_city_state_zip = rf'^({rex_state})\s+({rex_zip})$'
    grp_city = None
    grp_state = 1
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'zipcode'),
        ('|', 'country'),
        ]


class AdrSaudiArabia(Adr):

    """
    >>> adr = AdrSaudiArabia()
    >>> txt = adr.parse('''
    ... 
    ... Mohammed Ali Al-Ahmed
    ... 8228 Imam Ali Road – Alsalam Neighbourhood
    ... Riyadh 12345-6789
    ... Kingdom of Saudi Arabia 
    ... 
    ... ''')
    >>> adr.last_name
    'Al-Ahmed'
    >>> adr.city
    'Riyadh'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '12345-6789'
    >>> str(adr)
    'Mohammed Ali Al-Ahmed|8228 Imam Ali Road – Alsalam Neighbourhood|Riyadh 12345-6789|Kingdom of Saudi Arabia'
    """

    country = 'Kingdom of Saudi Arabia'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{5}-\d{4}'
    rex_city_state_zip = rf'^([^\n]+?)\s+({rex_zip})$'
    grp_city = 1
    grp_state = None
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        (SPACE, 'zipcode'),
        ('|', 'country'),
        ]


class AdrSerbia(Adr):

    """
    >>> adr = AdrSerbia()
    >>> txt = adr.parse('''
    ... 
    ... Petar Petrović
    ... Krunska 5
    ... 11000 Beograd
    ... 
    ... ''')
    >>> adr.last_name
    'Petrović'
    >>> adr.city
    'Beograd'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '11000'
    >>> str(adr)
    'Petar Petrović|Krunska 5|11000 Beograd|Serbia'
    """

    country = 'Serbia'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrSingapore(Adr):

    """
    >>> adr = AdrSingapore()
    >>> txt = adr.parse('''
    ... 
    ... Mr. M. Rajendran
    ... Blk 35 Mandalay Road
    ... # 13–37 Mandalay Towers
    ... SINGAPORE 308215
    ... SINGAPORE 
    ... 
    ... ''')
    >>> adr.polite_mode
    'Mr.'
    >>> adr.last_name
    'Rajendran'
    >>> adr.city
    'SINGAPORE'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '308215'
    >>> str(adr)
    'Mr. M. Rajendran|Blk 35 Mandalay Road|# 13–37 Mandalay Towers|SINGAPORE 308215|Singapore'
    """

    country = 'Singapore'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{6}'
    rex_city_state_zip = rf'^([^\n]+?)\s+({rex_zip})$'
    grp_city = 1
    grp_state = None
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        (SPACE, 'zipcode'),
        ('|', 'country'),
        ]


class AdrSlovakia(Adr):

    """
    >>> adr = AdrSlovakia()
    >>> txt = adr.parse('''
    ... 
    ... Jozef Vymyslený
    ... Firma s.r.o.
    ... Nezábudková 3084/25
    ... 84545 Bratislava
    ... Slovensko 
    ... 
    ... ''')
    >>> adr.last_name
    'Vymyslený'
    >>> adr.city
    'Bratislava'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '84545'
    >>> str(adr)
    'Jozef Vymyslený|Firma s.r.o.|Nezábudková 3084/25|84545 Bratislava|Slovensko'
    """

    country = 'Slovensko'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrSouthKorea(Adr):

    """
    >>> adr = AdrSouthKorea()
    >>> txt = adr.parse('''
    ... 
    ... Mr. Gil-dong Hong
    ... Apt. 102–304
    ... Sajik-ro-9-gil 23
    ... Jongno-gu, Seoul 30174
    ... (South Korea) 
    ... 
    ... ''')
    >>> adr.last_name
    'Hong'
    >>> adr.city
    'Jongno-gu'
    >>> adr.state
    'Seoul'
    >>> adr.zipcode
    '30174'
    >>> str(adr)
    'Mr. Gil-dong Hong|Apt. 102–304|Sajik-ro-9-gil 23|Jongno-gu, Seoul 30174|(South Korea)'
    """

    country = '(South Korea)'
    are_lines_inverted = False
    rex_state = r'.+?'
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^([^\n,]+),\s+({rex_state})\s+({rex_zip})$'
    grp_city = 1
    grp_state = 2
    grp_zip = 3
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (', ', 'state'),
        (SPACE, 'zipcode'),
        ('|', 'country'),
        ]


class AdrSpain(Adr):

    """
    >>> adr = AdrSpain()
    >>> txt = adr.parse('''
    ... 
    ... Dña. Antonia Fernandez Garcia
    ... Av. de las Delicias, 14, 1º Dcha.
    ... 29001 Madrid
    ... Madrid 
    ... 
    ... ''')
    >>> adr.polite_mode
    'Dña.'
    >>> adr.last_name
    'Garcia'
    >>> adr.city
    'Madrid'
    >>> adr.state
    'Madrid'
    >>> adr.zipcode
    '29001'
    >>> str(adr)
    'Dña. Antonia Fernandez Garcia|Av. de las Delicias, 14, 1º Dcha.|29001 Madrid|Madrid|Spain'
    """

    country = 'Spain'
    are_lines_inverted = False
    rex_state = r'[^\n]+?'
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)\n({rex_state})$'
    grp_city = 2
    grp_state = 3
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        ('|', 'state'),
        ('|', 'country'),
        ]


class AdrSriLanka(Adr):

    """
    >>> adr = AdrSriLanka()
    >>> txt = adr.parse('''
    ... 
    ... Mr. A. L. Perera
    ... 201 Silkhouse Street
    ... KANDY
    ... 20000
    ... SRI LANKA 
    ... 
    ... ''')
    >>> adr.last_name
    'Perera'
    >>> adr.city
    'KANDY'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '20000'
    >>> str(adr)
    'Mr. A. L. Perera|201 Silkhouse Street|KANDY|20000|Sri Lanka'
    """

    country = 'Sri Lanka'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^([^\n]+?)\s+({rex_zip})$'
    grp_city = 1
    grp_state = None
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'zipcode'),
        ('|', 'country'),
        ]


class AdrSweden(Adr):

    """
    >>> adr = AdrSweden()
    >>> txt = adr.parse('''
    ... 
    ... Anna Björklund
    ... Storgatan 1
    ... 112 01 Stockholm
    ... SWEDEN 
    ... 
    ... ''')
    >>> adr.last_name
    'Björklund'
    >>> adr.city
    'Stockholm'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    '112 01'
    >>> str(adr)
    'Anna Björklund|Storgatan 1|112 01 Stockholm|Sweden'
    """

    country = 'Sweden'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\d{3}\s\d{2}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)$'
    grp_city = 2
    grp_state = None
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrSwitzerland(Adr):

    """
    >>> adr = AdrSwitzerland()
    >>> txt = adr.parse('''
    ... 
    ... Herrn
    ... Rudolf Weber
    ... Marktplatz 1
    ... 4051 Basel
    ... Switzerland 
    ... 
    ... ''')
    >>> adr.last_name
    'Herrn'
    >>> adr.city
    'Basel'
    >>> adr.state

    >>> adr.zipcode
    '4051'
    >>> str(adr)
    'Herrn|Rudolf Weber|Marktplatz 1|4051 Basel|Switzerland'
    """

    country = 'Switzerland'
    are_lines_inverted = False
    rex_state = r'[A-Z]{2}'
    rex_zip = r'\d{4}'
    rex_city_state_zip = rf'^({rex_zip})\s+([^\n]+?)\s*({rex_state})?$'
    grp_city = 2
    grp_state = 3
    grp_zip = 1
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'zipcode'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'country'),
        ]


class AdrThailand(Adr):

    """
    >>> adr = AdrThailand()
    >>> txt = adr.parse('''
    ... 
    ... Mr. Siam Rakchart
    ... 238/54 Phaithong Village
    ... Bang Yai, Bang Yai
    ... Nonthaburi
    ... 11140
    ... Thailand
    ... 
    ... ''')
    >>> adr.last_name
    'Rakchart'
    >>> adr.city
    '#N/A'
    >>> adr.state
    'Nonthaburi'
    >>> adr.zipcode
    '11140'
    >>> str(adr)
    'Mr. Siam Rakchart|238/54 Phaithong Village|Bang Yai, Bang Yai|Nonthaburi|11140|Thailand'
    """

    country = 'Thailand'
    are_lines_inverted = False
    rex_state = r'[^\n]+?'
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^({rex_state})\s+({rex_zip})$'
    grp_city = None
    grp_state = 1
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'zipcode'),
        ('|', 'country'),
        ]


class AdrUkraine(Adr):

    """
    >>> adr = AdrUkraine()
    >>> txt = adr.parse('''
    ... 
    ... Петренко Іван Леонідович
    ... вул. Шевченка, буд. 17
    ... м. Біла Церква
    ... Київська обл.
    ... 09117
    ... Україна (UKRAINE) 
    ... 
    ... ''')
    >>> adr.last_name
    'Леонідович'
    >>> adr.city
    '#N/A'
    >>> adr.state
    'Київська обл.'
    >>> adr.zipcode
    '09117'
    >>> str(adr)
    'Петренко Іван Леонідович|вул. Шевченка, буд. 17|м. Біла Церква|Київська обл.|09117|Україна (UKRAINE)'
    """

    country = 'Україна (UKRAINE)'
    are_lines_inverted = False
    rex_state = r'[^\n]+?'
    rex_zip = r'\d{5}'
    rex_city_state_zip = rf'^([^\n]+?)\s+({rex_zip})$'
    grp_city = None
    grp_state = 1
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'zipcode'),
        ('|', 'country'),
        ]


class AdrUK(Adr):

    """
    >>> adr = AdrUK()
    >>> txt = adr.parse('''
    ... 
    ... Mr A Smith
    ... 3a High Street
    ... Hedge End
    ... SOUTHAMPTON
    ... SO31 4NG 
    ... 
    ... ''')
    >>> adr.last_name
    'Smith'
    >>> adr.city
    'SOUTHAMPTON'
    >>> adr.state
    '#N/A'
    >>> adr.zipcode
    'SO31 4NG'
    >>> str(adr)
    'Mr A Smith|3a High Street|Hedge End|SOUTHAMPTON|SO31 4NG|United Kingdom'
    """

    country = 'United Kingdom'
    are_lines_inverted = False
    rex_state = None
    rex_zip = r'\w{2,4}\s\w{3}'
    rex_city_state_zip = rf'^([^\n]+?)\s+({rex_zip})$'
    grp_city = 1
    grp_state = None
    grp_zip = 2
    tmpl = [
        (None, 'polite_mode'),
        (SPACE, 'first_name'),
        (SPACE, 'last_name'),
        (', ', 'title'),
        ('|', 'company'),
        ('|', 'dept_mail_stop'),
        ('|', 'locus'),
        ('|', 'street'),
        (None, '|'),
        (SPACE, 'city'),
        (SPACE, 'state'),
        ('|', 'zipcode'),
        ('|', 'country'),
        ]


class AdrUS(Adr):

    """
    >>> adr = AdrUS()
    >>> txt = adr.parse('''
    ... 
    ... Jeremy Martinson, Jr.
    ... 455 Larkspur Dr. Apt 23
    ... Baviera, CA  92908
    ... 
    ... ''')
    >>> adr.last_name
    'Martinson'
    >>> adr.city
    'Baviera'
    >>> adr.state
    'CA'
    >>> adr.zipcode
    '92908'
    >>> str(adr)
    'Jeremy Martinson, Jr.|455 Larkspur Dr. Apt 23|Baviera, CA  92908|USA'
    """

    country = 'USA'
    
    pass


def parse_phones(txt_in):

    """Parse phone numbers.

    """

    phones = Phones()
    txt_out = phones.parse(txt_in)
    result = (phones, txt_out)
    return result


class Phones(list):

    """(Possibly) match prospective telephone numbers.

    This is sketchy.  It follows the discussion at:

    + https://stackoverflow.com/questions/2113908/what-regular-expression-will-match-valid-international-phone-numbers

    This is not A-I.  It cannot and will not be successful with all or
    even very many legitimate telephone numbers, and it has the
    propensity to throw false positives.

    >>> phones = Phones()
    >>> txt = phones.parse('''
    ... 
    ... > (0123) 123 456 1       GB
    ... > 555-555-5555           US
    ... > 0049 1555 532-3455     DE
    ... > 123 456 7890           US
    ... > 0761 12 34 56          DE
    ... > +49 123 1-234-567-8901 DE
    ... > +61-234-567-89-01      IN
    ... > +46-234 5678901        GB
    ... > +1 (234) 56 89 901     US
    ... > +1 (234) 56-89 901     US
    ... > +46.234.567.8901       GB
    ... > +1/234/567/8901        US
    ... > 999-99-9999            SocSec
    ... > 089.123456, 120.123456 Lat/Lon
    ... > 12345-1234             Zipcode
    ... > 2023-07-03 10:58       Date
    ... 
    ... ''')
    >>> str(phones)
    "['(0123) 123 456 1', '555-555-5555', '0049 1555 532-3455', '123 456 7890', '0761 12 34 56', '+49 123 1-234-567-8901', '+61-234-567-89-01', '+46-234 5678901', '+1 (234) 56 89 901', '+1 (234) 56-89 901', '+46.234.567.8901', '+1/234/567/8901']"
    """
    
    pat_i18n_phone = re.compile(r'\+?[\(\s\.\:\-\/\d\)]+')

    def parse(self, txt):
        result = txt
        lines = result.splitlines()
        for (line_ndx, line) in enumerate(lines):
            matches = []
            for match in self.pat_i18n_phone.finditer(line):
                matches.append(match)
            matches.reverse()
            for (ndx, match_phones) in enumerate(matches):
                pos_beg = match_phones.start()
                pos_end = match_phones.end()
                hit = match_phones.group(ZERO)
                digits = extract_digits(hit)
                if 10 <= len(digits) <= 16:
                    if ':' in hit:
                        pass
                    else:
                        self.append(hit.strip())
                        line = f'{line[:pos_beg]}<font color=gray>{hit}</font>{line[pos_end:]}'
            lines[line_ndx] = line
        return MARKDN_LINE_END.join(lines)


def parse_lat_lon(txt_in):

    """Parse latitude/longitude.

    """

    lat_lon = LatLon()
    txt_out = lat_lon.parse(txt_in)
    result = (lat_lon, txt_out)
    return result


class LatLon(list):

    """Match latitude/longitude.

    >>> lat_lon_list = LatLon()
    >>> txt = lat_lon_list.parse('''
    ... 
    ... > (0123) 123 456 1       GB
    ... > 555-555-5555           US
    ... > 0049 1555 532-3455     DE
    ... > 123 456 7890           US
    ... > 0761 12 34 56          DE
    ... > +49 123 1-234-567-8901 DE
    ... > +61-234-567-89-01      IN
    ... > +46-234 5678901        GB
    ... > +1 (234) 56 89 901     US
    ... > +1 (234) 56-89 901     US
    ... > +46.234.567.8901       GB
    ... > +1/234/567/8901        US
    ... > 999-99-9999            SocSec
    ... > 089.123456, 120.123456 Lat/Lon
    ... > 12345-1234             Zipcode
    ... > 2023-07-03 10:58       Date
    ... 
    ... ''')
    >>> str(lat_lon_list)
    '[[89.123456, 120.123456]]'
    """
    
    pat_lat_lon = re.compile(r'[-+]?\d{2,3}\.\d{5,6}')

    def parse(self, txt):

        def parse_float(match, line):
            pos_beg = match.start()
            pos_end = match.end()
            hit = match.group(ZERO)
            result = float(hit)
            line = f'{line[:pos_beg]}<font color=gray>{hit}</font>{line[pos_end:]}'
            return (result, line)
        
        result = txt
        lines = result.splitlines()
        for (line_ndx, line) in enumerate(lines):
            matches = []
            for match in self.pat_lat_lon.finditer(line):
                matches.append(match)
            matches.reverse()
            if len(matches) == 2:
                match_lon = matches[ZERO]
                (lon, line) = parse_float(matches[ZERO], line)
                (lat, line) = parse_float(matches[1], line)
                self.append([lat, lon])
            lines[line_ndx] = line
        return MARKDN_LINE_END.join(lines)


def parse_uri(txt_in):

    """Parse URLs.

    """

    links = URIs()
    txt_out = links.parse(txt_in)
    result = (links, txt_out)
    return result


class URIs(list):

    """Match URIs and eMail addresses.

    >>> uri_list = URIs()
    >>> txt = uri_list.parse('''
    ... 
    ... me@walmart.com
    ... "Charles Curtis Rhode" <CRhode@LacusVeris.com>
    ... mailto:crhode@lacusveris.com
    ... http://LacusVeris.com/Phenology
    ... www.lacusveris.com/WX/index.shtml?County=WIC117&Lat=43.78&Lon=-87.85
    ...
    ... ''')
    >>> str(uri_list).replace('"', '?')
    "['me@walmart.com', '?Charles Curtis Rhode? <CRhode@LacusVeris.com>', 'mailto:crhode@lacusveris.com', 'http://LacusVeris.com/Phenology', 'www.lacusveris.com/WX/index.shtml?County=WIC117&Lat=43.78&Lon=-87.85']"
    """
    
    rex_domain = r'[A-Z0-9.-]+\.[A-Z]{2,}'
    rex_email = rf'\b[A-Z0-9._%+-]+@{rex_domain}\b'
    rex_web = rf'(?:(?:http://)|(?:www\.)){rex_domain}'
    pat_link = re.compile(rf'(?:{rex_email})|(?:{rex_web})', re.IGNORECASE)

    def parse(self, txt):
        result = txt
        lines = result.splitlines()
        for (line_ndx, line) in enumerate(lines):
            matches = []
            for match in self.pat_link.finditer(line):
                matches.append(match)
            matches.reverse()
            for match in matches:
                pos_beg = match.start()
                pos_end = match.end()
                hit = match.group(ZERO)
                line = f'{line[:pos_beg]}<font color=gray>{hit}</font>{line[pos_end:]}'
                self.append(hit)
            lines[line_ndx] = line
        return MARKDN_LINE_END.join(lines)


ADR_BY_COUNTRY = {
    'Argentina': AdrArgentina,
    'Australia': AdrAustralia,
    'Austria': AdrAustria,
    'Bangladesh': AdrBangladesh,
    'Belgium': AdrBelgium,
    'Belgique': AdrBelgium,
    'Brazil': AdrBrazil,
    'Canada': AdrCanada,
    'China': AdrChina,
    'P.R. China': AdrChina,
    'Croatia': AdrCroatia,
    'Denmark': AdrDenmark,
    'Estonia': AdrEstonia,
    'Finland': AdrFinland,
    'France': AdrFrance,
    'Germany': AdrGermany,
    'Greece': AdrGreece,
    'Gréce': AdrGreece,
    'Iceland': AdrIceland,
    'India': AdrIndia,
    'Iraq': AdrIraq,
    'Ireland': AdrIreland,
    'Israel': AdrIsrael,
    'Italy': AdrItaly,
    'Japan': AdrJapan,
    '(Japan)': AdrJapan,
    'Latvia': AdrLatvia,
    'Malaysia': AdrMalaysia,
    'Mexico': AdrMexico,
    'México': AdrMexico,
    'Norway': AdrNorway,
    'Pakistan': AdrPakistan,
    'Philippines': AdrPhilippines,
    'Poland': AdrPoland,
    'Polska': AdrPoland,
    'Portugal': AdrPortugal,
    'Russia': AdrRussia,
    'Россия': AdrRussia,
    'Kingdom of Saudi Arabia': AdrSaudiArabia,
    'Saudi Arabia': AdrSaudiArabia,
    'Serbia': AdrSerbia,
    'Singapore': AdrSingapore,
    'Slovakia': AdrSlovakia,
    'Slovensko': AdrSlovakia,
    'South Korea': AdrSouthKorea,
    'Spain': AdrSpain,
    'Sri Lanka': AdrSriLanka,
    'Sweden': AdrSweden,
    'Switzerland': AdrSwitzerland,
    'Thailand': AdrThailand,
    'Ukraine': AdrUkraine,
    'UKRAINE': AdrUkraine,
    'Україна': AdrUkraine,
    'United Kingdom': AdrUK,
    'United States': AdrUS,
    'USA': AdrUS,
    }


if __name__ == "__main__":

    """This code is run when this module is executed, not when it is included.

    Do doc tests.

    """
    
    import doctest
    doctest.testmod()

    
# Fin
