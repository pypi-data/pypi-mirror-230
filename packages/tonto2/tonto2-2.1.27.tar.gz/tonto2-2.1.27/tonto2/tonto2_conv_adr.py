#!/usr/bin/python3

# tonto2_conv_adr.py
# 2023 Aug 04 . ccr

# ==================================================boilerplate»=====
# *Tonto2* is a rewrite of *tonto* v1.2.
# 
# Copyright 2006—2023 by Chuck Rhode.
# 
# See LICENSE.txt for your rights.
# =================================================«boilerplate======

"""Tonto2 common address-list converter.

Tonto2 reads and writes only *.csv files and has no export/import
capability.  This utility substitutes for that.

This utility does not support locales ... yet.

No tests at volume have been attempted.

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
        with tonto2_conv_common.UnitInTonto(fn=PARMS.tonto, title='Tonto file', cls=tont2_conv_common.tonto2.RelAddressList) as rel:
            with tonto2_conv_common.UnitOutCsv(tags=self.tags.keys(), fn=self.fn, title=self.title) as csv_writer:
                for (ndx_rec, rec_tonto) in enumerate(rel.recs):
                    rel.stage_rec(ndx_rec)
                    rec_out = {}
                    for (tag_out, tag_tonto) in self.tags.items():
                        if tag_tonto:
                            col = rel.pages.find(tag_tonto)
                            val = col.val_store
                            if col and col.has_value:
                                rec_out[tag_out] = val
                            else:
                                rec_out[tag_out] = NULL
                    csv_writer.writerow(rec_out)
        return self


class ConvFrom(Conv):

    """A 'from' *.csv converter.

    """
    
    def perform(self):
        with tonto2_conv_common.UnitOutTonto(cls_name='Address List', fn=PARMS.tonto, title='Tonto file') as rel:
            with tonto2_conv_common.UnitInCsv(fn=self.fn, title=self.title) as csv_reader:
                for rec_in in csv_reader:
                    rec_tonto={}
                    for (tag_in, tag_tonto) in self.tags.items():
                        if tag_tonto:
                            col = rel.pages.find(tag_tonto)
                            col.val_store = rec_in.get(tag_in, tont2_conv_common.tonto2.NOT_AVAIL)
                            rel.destage_col(rec_tonto, col)
                    rel.recs.append(rec_tonto)
        return self


class ConvToGoogle(ConvTo):

    """A 'to' Google *.csv converter.

    """
    
    tags = tonto2_conv_common.TAGS_ADR_GOOGLE
    title = 'Google file'


class ConvToOutlook(ConvTo):

    """A 'to' Outlook *.csv converter.

    """
    
    tags = tonto2_conv_common.TAGS_ADR_OUTLOOK
    title = 'Outlook file'


class ConvToVCard(ConvTo):

    """A 'to' vCard converter.

    """
    
    title = 'VCard file'

    def perform(self):
        with tonto2_conv_common.UnitInTonto(fn=PARMS.tonto, title='Tonto file', cls=tont2_conv_common.tonto2.RelAddressList) as rel:
            with tonto2_conv_common.UnitOutVcf(fn=self.fn, title=self.title) as unit:
                for (ndx_rec, rec_tonto) in enumerate(rel.recs):
                    rel.stage_rec(ndx_rec)
                    vcard = tonto2_conv_common.conjure_vcard(rel)
                    if getattr(vcard, 'fn', None):
                        unit.write(vcard.serialize())
        return self


class ConvFromGoogle(ConvFrom):

    """A 'from' Google *.csv converter.

    """
    
    tags = tonto2_conv_common.TAGS_ADR_GOOGLE
    title = 'Google file'


class ConvFromOutlook(ConvFrom):

    """A 'from' Outlook *.csv converter.

    """
    
    tags = tonto2_conv_common.TAGS_ADR_OUTLOOK
    title = 'Outlook file'


class ConvFromVCard(ConvFrom):

    """A 'from' vCard converter.

    """
    
    title = 'VCard file'
    
    def perform(self):
        with tonto2_conv_common.UnitOutTonto(cls_name='Address List', fn=PARMS.tonto, title='Tonto file') as rel:
            with tonto2_conv_common.UnitInVcf(fn=self.fn, title=self.title) as gen:
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
                        col.val_store = rec_in[tag_in]
                        rel.destage_col(rec_tonto, col)
                    rel.recs.append(rec_tonto)
        return self


def main_line():
    if PARMS.to_google:
        ConvToGoogle(fn=PARMS.to_google).perform()
    elif PARMS.to_outlook:
        ConvToOutlook(fn=PARMS.to_outlook).perform()
    elif PARMS.to_vcard:
        ConvToVCard(PARMS.to_vcard).perform()
    elif PARMS.from_google:
        ConvFromGoogle(fn=PARMS.from_google).perform()
    elif PARMS.from_outlook:
        ConvFromOutlook(fn=PARMS.from_outlook).perform()
    elif PARMS.from_vcard:
        ConvFromVCard(PARMS.from_vcard).perform()
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
        help="Tonto Address List *.csv file",
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
        '--to-vcard',
        help="*.vcf file",
        metavar="vCard_file.vcf",
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
        '--from-vcard',
        help="*.vcf file",
        metavar="vCard_file.vcf",
        )
    PARMS = PARM_PARSER.parse_args()
    main_line()
    sys.exit(tonto2_conv_common.RETCD_OK)


if __name__ == "__main__":
    entry_point()

# Fin
