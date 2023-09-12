#!/usr/bin/python3

# tonto2_conv_cal.py
# 2023 Aug 07 . ccr

# ==================================================boilerplate»=====
# *Tonto2* is a rewrite of *tonto* v1.2.
# 
# Copyright 2006—2023 by Chuck Rhode.
# 
# See LICENSE.txt for your rights.
# =================================================«boilerplate======

"""Tonto2 common calendar converter.

Tonto2 reads and writes only *.csv files and has no export/import
capability.  This utility substitutes for that.

This utility does not support locales ... yet.

No tests at volume have been attempted.

NOTE: Recurring dates will not be passed through *.csv files.

"""

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1

import sys           # Python Standard Library
import argparse      # Python Standard Library
import tonto2.externals.tonto2_conv_common as tonto2_conv_common


class Conv:

    """A *.csv converter.

    """
    
    def __init__(self, fn):
        self.fn = fn
        return


class ConvTo(Conv):

    """A 'to' *.csv converter.

    """
    
    def perform(self):
        with tonto2_conv_common.UnitInTonto(fn=PARMS.tonto, title='Tonto file', cls=tont2_conv_common.tonto2.RelCalendar) as rel:
            with tonto2_conv_common.UnitOutCsv(tags=self.tags.keys(), fn=self.fn, title=self.title) as csv_writer:
                for (ndx_rec, rec_tonto) in enumerate(rel.recs):
                    rel.stage_rec(ndx_rec)
                    rec_out = {}
                    for (tag_out, tag_tonto) in self.tags.items():
                        if tag_tonto is None:
                            pass
                        elif isinstance(tag_tonto, str):
                            col = rel.pages.find(tag_tonto)
                            if col and col.has_value:
                                val = col.val_store
                                rec_out[tag_out] = val
                            else:
                                rec_out[tag_out] = NULL
                        else:
                            (method, tags) = (tag_tonto[ZERO], tag_tonto[1:])
                            parms = []
                            for tag in tags:
                                col = rel.pages.find(tag)
                                if col and col.has_value:
                                    val = col.val_comp  # Use the computational form.
                                else:
                                    val = tont2_conv_common.tonto2.NOT_AVAIL
                                parms.append(val)
                            val = method(*parms)
                            rec_out[tag_out] = val
                    if (rec_out['Subject'] in tont2_conv_common.tonto2.BLANK_VALUES) or (rec_out['Start Date'] in tont2_conv_common.tonto2.BLANK_VALUES):
                        pass
                    else:
                        csv_writer.writerow(rec_out)
        return self


class ConvFrom(Conv):

    """A 'from' *.csv converter.

    """
    
    def perform(self):
        with tonto2_conv_common.UnitOutTonto(cls_name='Calendar', fn=PARMS.tonto, title='Tonto file') as rel:
            with tonto2_conv_common.UnitInCsv(fn=self.fn, title=self.title) as csv_reader:
                for rec_in in csv_reader:
                    rec_tonto={}
                    for (tag_tonto, tag_in) in self.tags.items():
                        col = rel.pages.find(tag_tonto)
                        if col:
                            if tag_in is None:
                                pass
                            elif isinstance(tag_in, str):
                                val = rec_in.get(tag_in, tont2_conv_common.tonto2.NOT_AVAIL)
                                col.val_store = val
                            else:
                                (method, tags) = (tag_tonto[ZERO], tag_tonto[1:])
                                parms = []
                                for tag in tags:
                                    val = rec_in.get(tag_in, tont2_conv_common.tonto2.NOT_AVAIL)
                                parms.append(val)
                                val = method(*parms)
                                col.val_comp = val  # Use the computational form.
                            rel.destage_col(rec_tonto, col)
                    rel.recs.append(rec_tonto)
        return self


class ConvToGoogle(ConvTo):

    """A 'to' Google *.csv converter.

    """
    
    tags = tonto2_conv_common.TAGS_CAL_TO_GOOGLE
    title = 'Google file'


class ConvToOutlook(ConvTo):

    """A 'to' Outlook *.csv converter.

    """
    
    tags = tonto2_conv_common.TAGS_CAL_TO_OUTLOOK
    title = 'Outlook file'


class ConvToICal(ConvTo):

    """A 'to' iCal converter.

    """
    
    title = 'ICal file'

    def perform(self):
        with tonto2_conv_common.UnitInTonto(fn=PARMS.tonto, title='Tonto file', cls=tont2_conv_common.tonto2.RelCalendar) as rel:
            ical = tonto2_conv_common.ICal()
            with tonto2_conv_common.UnitOutIcs(fn=self.fn, title=self.title) as unit:
                for (ndx_rec, rec_tonto) in enumerate(rel.recs):
                    rel.stage_rec(ndx_rec)
                    vevent = ical.add('vevent')
                    tonto2_conv_common.conjure_ical(rel, vevent)
#                    print(f'vevent:  {vevent}')
                unit.write(ical.serialize())
        return self


class ConvFromGoogle(ConvFrom):

    """A 'from' Google *.csv converter.

    """
    
    tags = tonto2_conv_common.TAGS_CAL_FROM_GOOGLE
    title = 'Google file'


class ConvFromOutlook(ConvFrom):

    """A 'from' Outlook *.csv converter.

    """
    
    tags = tonto2_conv_common.TAGS_CAL_FROM_OUTLOOK
    title = 'Outlook file'


class ConvFromICal(ConvFrom):

    """A 'from' iCal converter.

    """
    
    title = 'ICal file'
    
    def perform(self):
        with tonto2_conv_common.UnitOutTonto(cls_name='Calendar', fn=PARMS.tonto, title='Tonto file') as rel:
            with tonto2_conv_common.UnitInIcs(fn=self.fn, title=self.title) as gen:
                for rec_in in gen:
                    rec_tonto={}
                    rel.pages.append([])
                    ndx_page = len(rel.pages) - 1
                    for tag_in in rec_in.keys():
                        col = rel.pages.find(tag_in)
                        if col:
                            pass
                        else:
                            col = tont2_conv_common.tonto2.ItmText(tag_in)
                            ndx_itm = len(rel.pages[ndx_page])
                            rel.pages[ndx_page].insert(ndx_itm, col)
                        col.val_store = rec_in[tag_in]  # Use the storage form.
                        rel.destage_col(rec_tonto, col)
                    rel.recs.append(rec_tonto)
        return self


def main_line():
    if PARMS.to_google:
        ConvToGoogle(fn=PARMS.to_google).perform()
    elif PARMS.to_outlook:
        ConvToOutlook(fn=PARMS.to_outlook).perform()
    elif PARMS.to_ical:
        ConvToICal(PARMS.to_ical).perform()
    elif PARMS.from_google:
        ConvFromGoogle(fn=PARMS.from_google).perform()
    elif PARMS.from_outlook:
        ConvFromOutlook(fn=PARMS.from_outlook).perform()
    elif PARMS.from_ical:
        ConvFromICal(PARMS.from_ical).perform()
    else:
        raise NotImplementedError
    return


def entry_point():

    global PARMS

    PARM_PARSER = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
        )
    PARM_PARSER.add_argument(
        '--tonto',
        required=True,
        help="Tonto Calendar *.csv file",
        metavar="Tonto_file.dd",
        )
    group = PARM_PARSER.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--to-google',
        help="Google *.csv file",
        metavar="Goggle_file.csv",
        )
    group.add_argument(
        '--to-outlook',
        help="Outlook *.csv file",
        metavar="Outlook_file.csv",
        )
    group.add_argument(
        '--to-ical',
        help="*.ics file",
        metavar="iCal_file.ics",
        )
    group.add_argument(
        '--from-google',
        help="Google *.csv file",
        metavar="Goggle_file.csv",
        )
    group.add_argument(
        '--from-outlook',
        help="Outlook *.csv file",
        metavar="Outlook_file.csv",
        )
    group.add_argument(
        '--from-ical',
        help="*.ics file",
        metavar="iCal_file.ics",
        )
    PARMS = PARM_PARSER.parse_args()
    tont2_conv_common.tonto2.ALARMS = tont2_conv_common.tonto2.Alarms()
    main_line()
    sys.exit(tonto2_conv_common.RETCD_OK)


if __name__ == "__main__":
    entry_point()
    
# Fin
