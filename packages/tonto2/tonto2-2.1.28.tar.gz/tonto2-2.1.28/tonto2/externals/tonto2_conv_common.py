#!/usr/bin/python3

# tonto2_conv_common.py
# ccr . 2023 Aug 07

# ==================================================boilerplate»=====
# *Tonto2* is a rewrite of *tonto* v1.2.
# 
# Copyright 2006—2023 by Chuck Rhode.
# 
# See LICENSE.txt for your rights.
# =================================================«boilerplate======

"""Common module for tonto2_conv_adr.py and tonto2_conv_cal.py.

"""

# ccr . 2023 Aug 20 . All vobject fields should be str valued.

ZERO = 0
SPACE =  ' '
NULL = ''
NUL = '\x00'
NA = -1
RETCD_ERR = 0x16
RETCD_OK = ZERO
DATE_EDIT_FORMAT = '%Y/%m/%d'
TIME_EDIT_FORMAT = '%H:%M'
DATE_TIME_EDIT_FORMAT = f'{DATE_EDIT_FORMAT} {TIME_EDIT_FORMAT}'
V_DATE_TIME_FORMAT = '%Y%m%dT%H%M%SZ'

import sys           # Python Standard Library
import re            # Python Standard Library
import pathlib       # Python Standard Library
import csv           # Python Standard Library
import datetime      # Python Standard Library
#                    # *tzdata* Debian Package required by zoneinfo
import zoneinfo      # Python Standard Library
import uuid          # Python Standard Library
import dateparser    # *python3-dateparser Debian Package
import vobject       # *python3-vobject* Debian Package
import tonto2.tonto2_main as tonto2


DELTA_DAY = datetime.timedelta(days=1)
DELTA_HOUR = datetime.timedelta(hours=1)
TZ_UTC = zoneinfo.ZoneInfo("UTC")
PAT_OFFSET_DAY = re.compile(r'([-+\d]*)((?:SU)|(?:MO)|(?:TU)|(?:WE)|(?:TH)|(?:FR)|(?:SA)|(?:WE))')

TAGS_ADR_GOOGLE = {
    "Name": None,
    "Given Name": tonto2.TAG_FIRST_NAME,
    "Additional Name": None,
    "Family Name": tonto2.TAG_LAST_NAME,
    "Yomi Name": None,
    "Given Name Yomi": None,
    "Additional Name Yomi": None,
    "Family Name Yomi": None,
    "Name Prefix": tonto2.TAG_POLITE_MODE,
    "Name Suffix": tonto2.TAG_TITLE,
    "Initials": None,
    "Nickname": None,
    "Short Name": None,
    "Maiden Name": None,
    "Birthday": None,
    "Gender": None,
    "Location": None,
    "Billing Information": None,
    "Directory Server": None,
    "Mileage": None,
    "Occupation": None,
    "Hobby": None,
    "Sensitivity": None,
    "Priority": None,
    "Subject": None,
    "Notes": tonto2.TAG_REMARKS,
    "Group Membership": None,
    "E-mail 1 - Type": tonto2.TAG_LISTING_TYPE,
    "E-mail 1 - Value": tonto2.TAG_EMAIL,
    "E-mail 2 - Type": None,
    "E-mail 2 - Value": None,
    "E-mail 3 - Type": None,
    "E-mail 3 - Value": None,
    "E-mail 4 - Type": None,
    "E-mail 4 - Value": None,
    "IM 1 - Type": None,
    "IM 1 - Service": None,
    "IM 1 - Value": None,
    "Phone 1 - Type": tonto2.TAG_PHONE_TYPE_1,
    "Phone 1 - Value": tonto2.TAG_PHONE_1,
    "Phone 2 - Type": tonto2.TAG_PHONE_TYPE_2,
    "Phone 2 - Value": tonto2.TAG_PHONE_2,
    "Phone 3 - Type": tonto2.TAG_PHONE_TYPE_3,
    "Phone 3 - Value": tonto2.TAG_PHONE_3,
    "Phone 4 - Type": tonto2.TAG_PHONE_TYPE_4,
    "Phone 4 - Value": tonto2.TAG_PHONE_4,
    "Phone 5 - Type": None,
    "Phone 5 - Value": None,
    "Address 1 - Type": tonto2.TAG_LISTING_TYPE,
    "Address 1 - Formatted": None,
    "Address 1 - Street": tonto2.TAG_STREET,
    "Address 1 - City": tonto2.TAG_CITY,
    "Address 1 - PO Box": None,
    "Address 1 - Region": tonto2.TAG_STATE,
    "Address 1 - Postal Code": tonto2.TAG_ZIP,
    "Address 1 - Country": tonto2.TAG_COUNTRY,
    "Address 1 - Extended Address": None,
    "Address 2 - Type": None,
    "Address 2 - Formatted": None,
    "Address 2 - Street": None,
    "Address 2 - City": None,
    "Address 2 - PO Box": None,
    "Address 2 - Region": None,
    "Address 2 - Postal Code": None,
    "Address 2 - Country": None,
    "Address 2 - Extended Address": None,
    "Address 3 - Type": None,
    "Address 3 - Formatted": None,
    "Address 3 - Street": None,
    "Address 3 - City": None,
    "Address 3 - PO Box": None,
    "Address 3 - Region": None,
    "Address 3 - Postal Code": None,
    "Address 3 - Country": None,
    "Address 3 - Extended Address": None,
    "Organization 1 - Type": None,
    "Organization 1 - Name": tonto2.TAG_COMPANY,
    "Organization 1 - Yomi Name": None,
    "Organization 1 - Title": None,
    "Organization 1 - Department": tonto2.TAG_DEPT_MAIL_STOP,
    "Organization 1 - Symbol": None,
    "Organization 1 - Location": None,
    "Organization 1 - Job Description": None,
    "Relation 1 - Type": None,
    "Relation 1 - Value": None,
    "Relation 2 - Type": None,
    "Relation 2 - Value": None,
    "Website 1 - Type": None,
    "Website 1 - Value": tonto2.TAG__URI,
    "Website 2 - Type": None,
    "Website 2 - Value": None,
    "Event 1 - Type": None,
    "Event 1 - Value": None,
    }

TAGS_ADR_OUTLOOK = {
    "Title": tonto2.TAG_POLITE_MODE,
    "First Name": tonto2.TAG_FIRST_NAME,
    "Middle Name": None,
    "Last Name": tonto2.TAG_LAST_NAME,
    "Suffix": tonto2.TAG_TITLE,
    "Company": tonto2.TAG_COMPANY,
    "Department": None,
    "Job Title": None,
    "Business Street": None,
    "Business Street 2": None,
    "Business Street 3": None,
    "Business City": None,
    "Business State": None,
    "Business Postal Code": None,
    "Business Country/Region": None,
    "Home Street": tonto2.TAG_DEPT_MAIL_STOP,
    "Home Street 2": tonto2.TAG_LOCUS,
    "Home Street 3": tonto2.TAG_STREET,
    "Home City": tonto2.TAG_CITY,
    "Home State": tonto2.TAG_STATE,
    "Home Postal Code": tonto2.TAG_ZIP,
    "Home Country/Region": tonto2.TAG_COUNTRY,
    "Other Street": None,
    "Other Street 2": None,
    "Other Street 3": None,
    "Other City": None,
    "Other State": None,
    "Other Postal Code": None,
    "Other Country/Region": None,
    "Assistant's Phone": None,
    "Business Fax": None,
    "Business Phone": None,
    "Business Phone 2": None,
    "Callback": None,
    "Car Phone": None,
    "Company Main Phone": None,
    "Home Fax": None,
    "Home Phone": tonto2.TAG_PHONE_2,
    "Home Phone 2": tonto2.TAG_PHONE_3,
    "ISDN": None,
    "Mobile Phone": None,
    "Other Fax": None,
    "Other Phone": tonto2.TAG_PHONE_4,
    "Pager": None,
    "Primary Phone": tonto2.TAG_PHONE_1,
    "Radio Phone": None,
    "TTY/TDD Phone": None,
    "Telex": None,
    "Account": None,
    "Anniversary": None,
    "Assistant's Name": None,
    "Billing Information": None,
    "Birthday": None,
    "Business Address PO Box": None,
    "Categories": tonto2.TAG_LISTING_TYPE,
    "Children": None,
    "Directory Server": None,
    "E-mail Address": tonto2.TAG_EMAIL,
    "E-mail Type": tonto2.TAG_LISTING_TYPE,
    "E-mail Display Name": None,
    "E-mail 2 Address": None,
    "E-mail 2 Type": None,
    "E-mail 2 Display Name": None,
    "E-mail 3 Address": None,
    "E-mail 3 Type": None,
    "E-mail 3 Display Name": None,
    "Gender": None,
    "Government ID Number": None,
    "Hobby": None,
    "Home Address PO Box": None,
    "Initials": None,
    "Internet Free Busy": None,
    "Keywords": tonto2.TAG_KEYWORDS,
    "Language": None,
    "Location": None,
    "Manager's Name": None,
    "Mileage": None,
    "Notes": tonto2.TAG_REMARKS,
    "Office Location": None,
    "Organizational ID Number": None,
    "Other Address PO Box": None,
    "Priority": None,
    "Private": None,
    "Profession": None,
    "Referred By": None,
    "Sensitivity": None,
    "Spouse": None,
    "User 1": None,
    "User 2": None,
    "User 3": None,
    "User 4": None,
    "Web Page": tonto2.TAG__URI, }


def diagnostic(msg, fatal=False):

    """Print error message.

    """
    
    print(msg, file=sys.stderr)
    if fatal:
        sys.exit(RETCD_ERR)
    return


def localize(time):

    """Obliterate time-zone information.  

    Interpret as local time depending on locale.

    """
    
    result = time.replace(tzinfo=None)
    result = result.astimezone()
    return result


def get_week_day(date):

    """Return two-char day of week for ISO8601 day of week.

    """
    
    return ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'][date.weekday()]
        

def calc_start_date(start_date_time):

    """Convert to text.

    """
    
    if start_date_time in tonto2.BLANK_VALUES:
        result = tonto2.NOT_AVAIL
    else:
        result = start_date_time.strftime(DATE_EDIT_FORMAT)
    return result


def calc_start_time(start_date_time):

    """Convert to text.

    """
    
    if start_date_time in tonto2.BLANK_VALUES:
        result = tonto2.NOT_AVAIL
    else:
        result = start_date_time.strftime(TIME_EDIT_FORMAT)
    return result


def calc_end_date(start_date_time, duration_hrs):

    """Convert to text.

    """
    
    if start_date_time in tonto2.BLANK_VALUES:
        result = tonto.NOT_AVAIL
    else:
        if duration_hrs in tonto2.BLANK_VALUES:
            result = start_date_time
        else:
            delta = datetime.timedelta(hours=duration_hrs)
            result = start_date_time + delta
        result = result.strftime(DATE_EDIT_FORMAT)
    return result


def calc_end_time(start_date_time, duration_hrs):

    """Convert to text.

    """
    
    if start_date_time in tonto2.BLANK_VALUES:
        result = tonto.NOT_AVAIL
    else:
        if duration_hrs in tonto2.BLANK_VALUES:
            result = start_date_time
        else:
            delta = datetime.timedelta(hours=duration_hrs)
            result = start_date_time + delta
        result = result.strftime(TIME_EDIT_FORMAT)
    return result


def patch_all_day_event(result):

    """Dummy function.

    """
    
    return result


def calc_has_reminder(advance_alarm_min):

    """Convert to text.

    """
    
    result = advance_alarm_min in tonto2.BLANK_VALUES
    if result:
        result = 'OFF'
    else:
        result = 'ON'
    return result


def calc_reminder_date(start_date_time, advance_alarm_min):

    """Convert to text.

    """
    
    if start_date_time in tonto2.BLANK_VALUES:
        result = tonto.NOT_AVAIL
    else:
        if advance_alarm_min in tonto2.BLANK_VALUES:
            result = start_date_time
        else:
            delta = datetime.timedelta(hours=-advance_alarm_min)
            result = start_date_time + delta
        result = result.strftime(DATE_EDIT_FORMAT)
    return result


def calc_reminder_time(start_date_time, advance_alarm_min):

    """Convert to text.

    """
    
    if start_date_time in tonto2.BLANK_VALUES:
        result = tonto.NOT_AVAIL
    else:
        if advance_alarm_min in tonto2.BLANK_VALUES:
            result = start_date_time
        else:
            delta = datetime.timedelta(hours=-advance_alarm_min)
            result = start_date_time + delta
        result = result.strftime(TIME_EDIT_FORMAT)
    return result


def calc_start(start_date, start_time):

    """Convert to computational.

    """
    
    result = datetime.datetime.combine(start_date, start_time)
    return result


def calc_duration(start_date, start_time, end_date, end_time):

    """Convert to computational.

    """
    
    start_datetime = calc_start(start_date, start_time)
    end_datetime = calc_start(end_date, end_time)
    diff = end_datetime - start_datetime
    diff_secs = diff.days * 24 * 3600 + diff.seconds
    result = diff_secs / 3600.0
    return result


def calc_advance_alarm(start_date, start_time, reminder_date, reminder_time):

    """Convert to computational.

    """
    
    start_datetime = calc_start(start_date, start_time)
    reminder_datetime = calc_start(reminder_date, reminder_time)
    diff = start_datetime - reminder_datetime
    diff_secs = diff.days * 24 * 3600 + diff.seconds
    result = int(round(diff_secs / 60.0))
    return result


TAGS_CAL_TO_OUTLOOK = {
    "Subject": tonto2.TAG_TITLE,
    "Start Date": (calc_start_date, tonto2.TAG__START),
    "Start Time": (calc_start_time, tonto2.TAG__START),
    "End Date": (calc_end_date, tonto2.TAG__START, tonto2.TAG__DURATION),
    "End Time": (calc_end_time, tonto2.TAG__START, tonto2.TAG__DURATION),
    "All Day Event": (patch_all_day_event, "FALSE"),
    "Categories": tonto2.TAG_PROJECT,
    "Show Time As": None,
    "Location": None,
    "Reminder On/Off": (calc_has_reminder, tonto2.TAG_ADVANCE_ALARM),
    "Reminder Date": (calc_reminder_date, tonto2.TAG__START, tonto2.TAG_ADVANCE_ALARM),
    "Reminder Time": (calc_reminder_time, tonto2.TAG__START, tonto2.TAG_ADVANCE_ALARM),
    "Private": None,
    "Sensitivity": None,
    "Description    ": tonto2.TAG_REMARKS,
    }

TAGS_CAL_TO_GOOGLE = TAGS_CAL_TO_OUTLOOK

TAGS_CAL_FROM_OUTLOOK = {
    tonto2.TAG_TITLE: "Subject",
    tonto2.TAG__START: (calc_start, "Start Date", "Start Time"),
    tonto2.TAG__DURATION: (calc_duration, "Start Date", "Start Time", "End Date", "End Time"),
    tonto2.TAG_PROJECT: "Categories",
    tonto2.TAG_ADVANCE_ALARM: (calc_advance_alarm, "Start Date", "Start Time", "Reminder Date", "Reminder Time"),
    tonto2.TAG_REMARKS: "Description",
    }

TAGS_CAL_FROM_GOOGLE = TAGS_CAL_FROM_OUTLOOK

    
class RRule(dict):

    """Recurrence Rule.

    """
    
    def parse(self, rule):
        keywords = rule.split(';')
        for keyword in keywords:
            key_val = keyword.split('=')
            if len(key_val) == 2:
                pass
            else:
                raise NotImplementedError
            (key, valword) = key_val
            key = key.strip().upper()
            vals = [val.strip().upper() for val in valword.split(',')]
            self.set_key_0(key, vals)
        return self

    def get_key_0(self, key):
        result = self.get(key, None)
        if result is None:
            return None
        else:
            if len(result) == 1:
                return result[ZERO]
            else:
                raise NotImplementedError

    def set_key_0(self, key, val):
        self[key] = val
        return self

    def get_until(self):
        date_time = self.get_key_0('UNTIL')
        if date_time is None:
            result = None
        else:
            result = datetime.datetime.strptime(date_time, V_DATE_TIME_FORMAT)
            result = localize(result)
            result = result.astimezone()
        return result

    def set_until(self, last_occurrence):
        if tonto2.is_date_instance(last_occurrence):
            last_occurrence = datetime.datetime.combine(last_occurrence, datetime.time(hour=ZERO, minute=ZERO))
        result = localize(last_occurrence)
        result = result.strftime(V_DATE_TIME_FORMAT)
        self.set_key_0('UNTIL', result)
        return self

    def get_freq(self):
        return self.get_key_0('FREQ')

    def is_daily(self):
        return self.get_freq() in ['DAILY']

    def is_weekly(self):
        return self.get_freq() in ['WEEKLY']

    def is_monthly(self):
        return self.get_freq() in ['MONTHLY']

    def is_yearly(self):
        return self.get_freq() in ['YEARLY']

    def get_by_days(self):
        return self.getorecsx('BYDAY', None)

    def get_by_day(self):
        by_day = self.get_key_0('BYDAY')
        if by_day is None:
            result = None
        else:
            match = PAT_OFFSET_DAY.match(by_day)
            if match is None:
                result = None
            else:
                result = match.group(1, 2)
        return result

    def get_by_month_day(self):
        return self.get_key_0('BYMONTHDAY')

    def get_interval(self):
        return self.get_key_0('INTERVAL')

    def get_offsets(self, start_date):

        result = []
        interval = self.get_interval()
        if interval:
            interval = int(interval)
        else:
            interval = 1
        if self.is_daily():
            offset = str(interval)
            offset_type_days = 'Y'
            offset_in_month = tonto2.NOT_AVAIL
            offset_in_month_type_days = tonto2.NOT_AVAIL
            result.append([start_date, offset, offset_type_days, offset_in_month, offset_in_month_type_days])
        elif self.is_weekly():
            offset = str(7 * interval)
            offset_type_days = 'Y'
            offset_in_month = tonto2.NOT_AVAIL
            offset_in_month_type_days = tonto2.NOT_AVAIL
            days = self.get_by_days()
            day0 = start_date.replace()
            while days:
                day_of_week = get_week_day(day0)
                if day_of_week in days:
                    ndx = days.index(day_of_week)
                    days.pop(ndx)
                    result.append([day0, offset, offset_type_days, offset_in_month, offset_in_month_type_days])
                day0 += DELTA_DAY
        elif self.is_monthly():
            offset = str(interval)
            offset_type_days = 'N'
            offset_in_month_type_days = 'Y'            
            offset_and_day = self.get_by_day()
            offset_in_month = self.get_by_month_day()
            if offset_and_day is not None:
                offset_in_month_type_days = 'N'
                (offset_in_month, day) = offset_and_day
            elif offset_in_month is not None:
                pass
            else:
                offset_in_month = start_date.day
            result.append([start_date, offset, offset_type_days, offset_in_month, offset_in_month_type_days])
        elif self.is_yearly():
            offset = str(12 * interval)
            offset_type_days = 'N'
            offset_in_month = tonto2.NOT_AVAIL
            offset_in_month_type_days = tonto2.NOT_AVAIL
            result.append([start_date, offset, offset_type_days, offset_in_month, offset_in_month_type_days])
        else:
            raise NotImplementedError
        return result

    def set_from_rec(self, rel):

        def from_rec(tag):
            itm = rel.pages.find(tag)
            if itm and itm.has_value:
                result = itm.val_comp
            else:
                result = None
            return result
        
        start_date = from_rec(tonto2.TAG__START)
        offset = from_rec(tonto2.TAG_OFFSET)
        offset_type_days = from_rec(tonto2.TAG_IS_OFFSET_TYPE_DAYS)
        offset_in_month = from_rec(tonto2.TAG_OFFSET_IN_MONTH)
        offset_in_month_type_days = from_rec(tonto2.TAG_IS_OFFSET_IN_MONTH_TYPE_DAYS)
        if offset in tonto2.BLANK_VALUES:
            self.clear()
        else:
            if offset_type_days in ['Y']:
                self.set_key_0('FREQ', 'DAILY')
                self.set_key_0('INTERVAL', offset)
            elif offset_type_days in ['N']:
                self.set_key_0('FREQ', 'MONTHLY')
                self.set_key_0('INTERVAL', offset)
                if offset_in_month_type_days in ['N']:
                    if offset_in_month in tonto2.BLANK_VALUES:
                        pass
                    else:
                        self.set_key_0('BYDAY', f'{offset_in_month}{get_week_day(start_date)}')
                elif offset_in_month in tonto2.BLANK_VALUES:
                    pass
                else:
                    self.set_key_0('BYMONTHDAY', offset_in_month)
            else:
                print(f'offset_type_days: {offset_type_days}')
                raise NotImplementedError
        last_occurrence_date = from_rec(tonto2.TAG_STOP)
        if last_occurrence_date in tonto2.BLANK_VALUES:
            pass
        else:
            self.set_until(last_occurrence_date)
        return self

    def __str__(self):
        if list(self.keys()) == ['UNTIL']:
            result = NULL
        else:
            result = []
            for (key, val) in self.items():
                if isinstance(val, list):
                    val = ','.join(val)
                result.append(f'{key}={val}')
            if result:
                result.append('WKST=SU')
            result = ';'.join(result)
        return result


class VFld:

    """VObject item for use with vCard.

    This is initialized with a field name.

    """
        
    def __init__(self, v_fld):
        self.v_fld = v_fld
        return

    def getorecsxs(self, vobj, min=ZERO, max=1):
        result = getattr(vobj, f'{self.v_fld}_list', [])
        count = len(result)
        if min <= count <= max:
            pass
        else:
            diagnostic(f'Card "{vobj.fn}" should have between {min} and {max} "self.vfld."  {count} found.')
        return result

    def getorecsx(self, vobj, rec_out, tag, ndx=ZERO):
        flds = self.getorecsxs(vobj)
        if flds:
            val = flds[ndx].value
            if isinstance(val, list):  # 2014 Mar 25
                if len(val) == 1:
                    val = val[ZERO]
            if isinstance(val, list):
                val = ', '.join(val)   # 2014 Mar 25
            rec_out[tag] = val
        return self

    def setvaluex(self, val, vobj, ndx=-1):
        if ndx in [NA]:
            vobj.add(self.v_fld)
        flds = getattr(vobj, f'{self.v_fld}_list')
        flds[ndx].value = str(val)  # 2023 Aug 20
        return self


class VFld1:

    """vObject item for use with iCal.

    This is initialized with a field name.

    """
        
    def __init__(self, v_fld):
        self.v_fld = v_fld
        return

    def getorecsx(self, vobj, rec_out, tag, ndx=ZERO):
        fld = getattr(vobj, self.v_fld, None)
        if fld:
            val = fld.value
            rec_out[tag] = val
        return self

    def setvaluex(self, val, vobj):
        fld = getattr(vobj, self.v_fld, vobj.add(self.v_fld))
        fld.value = val
        return self

    
class VUid(VFld):

    pass


class VUid1(VFld1):

    pass


class VPhoto(VFld):

    """A base64 encoded image.  

    Tonto2 doesn't deal with this.

    """
        
    def getorecsx(self, vobj, rec_out, tag, ndx=ZERO):
        flds = self.getorecsxs(vobj)
        if flds:
            photo = flds[ndx]
            rec_out[tag] = photo.value.encode('Base64')
        return self

    def setvaluex(self, val, vobj, ndx=-1):
        flds = getattr(vobj, f'{self.v_fld}_list')
        flds[ndx].encoding_param = 'B'
        flds[ndx].value = val.decode('Base64')
        return self


class VList(VFld):

    """A list of values,

    """
    
    
    def setvaluex(self, val, vobj, ndx=-1):
        if ndx in [NA]:
            vobj.add(self.v_fld)
        flds = getattr(vobj, f'{self.v_fld}_list')
        flds[ndx].value = [val]
        return self


class VObjFld:
        
    """vObject stand-alone item.

    This is initialized with an vObject and a field name.

    """

    def __init__(self, v_obj, v_fld):
        self.v_obj = v_obj
        self.v_fld = v_fld
        return

    def getorecsx(self, vobj, rec_out, tag, ndx=ZERO):
        objs = getattr(vobj, f'{self.v_obj}_list', None)
        if objs is not None:
            obj = objs[ndx].value
            fld = getattr(obj, self.v_fld, None)
            if fld is not None:
                rec_out[tag] = fld
        return

    def setvaluex(self, val, vobj, ndx=-1):
        objs = getattr(vobj, f'{self.v_obj}_list', [])
        if objs:
            pass
        else:
            vobj.add(self.v_obj)
            objs = getattr(vobj, f'{self.v_obj}_list')
        obj = objs[ndx]
        obj.add(self.v_fld)
        flds = getattr(obj, f'{self.v_fld}_list')
        flds[-1].value = val
        return self


class VOrdFld(VObjFld):

    """vObject multiple.

    This is initialized with an vObject and a field name.

    """

    def setvaluex(self, val, vobj, ndx=-1):
        objs = getattr(vobj, f'{self.v_obj}_list', [])
        if objs:
            pass
        else:
            vobj.add(self.v_obj)
            objs = getattr(vobj, f'{self.v_obj}_list')
        obj = objs[ndx]
        setattr(obj.value, self.v_fld, val)
        return self


class VAdrFld(VOrdFld):

    """vObject multiple.

    This is initialized with an vObject and a field name.

    """

    pass


class VType(VFld):

    """vObject multiple field type.

    """
        
    def getorecsx(self, vobj, rec_out, tag, ndx=ZERO):
        flds = self.getorecsxs(vobj)
        if flds:
            rec_out[tag] = flds[ndx].type_param
            if tag in TAGS:
                pass
            else:
                TAGS.append(tag)
        return self

    def setvaluex(self, val, vobj, ndx=-1):
        vobj.add(self.v_fld)
        flds = getattr(vobj, f'{self.v_fld}_list')
        fld = flds[ndx]
        fld.type_param = val
        return self


class VAdrType(VType):

    """vObject multiple field type.

    """
        
    pass


class VTelType(VType):

    """vObject multiple field type.

    """
        
    def getorecsx(self, vobj, rec_out, tag):
        ndx = 1
        for fld in self.getorecsxs(vobj, max=4):
            this_tag = f'{tag}{ndx}'
            rec_out[this_tag] = getattr(fld, 'type_param', None)  # 2014 Mar 25
            ndx += 1
        return self


class VTel(VFld):

    """vObject Phone.

    """
    
    
    def getorecsx(self, vobj, rec_out, tag):
        ndx = 1
        for fld in self.getorecsxs(vobj, max=4):
            this_tag = f'{tag}{ndx}'
            rec_out[this_tag] = fld.value
            ndx += 1
        return self


class VConst:

    """vObject Constant.

    """
    
    def __init__(self, const):
        self.const = const
        return

    def getorecsx(self, vobj, rec_out, tag):
        rec_out[tag] = self.const
        return self

    def setvaluex(self, val, vobj):
        return self


class VDateTime(VFld1):

    """vObject date/time.

    """
    
    def getorecsx(self, vobj, rec_out, tag, ndx=ZERO):
        fld = getattr(vobj, self.v_fld, None)
        if fld:
            val = fld.value
            if tonto2.is_date_instance(val):
                val = datetime.datetime.combine(val, datetime.time(hour=ZERO, minute=ZERO))
            val = val.astimezone()
            rec_out[tag] = val.strftime(DATE_TIME_EDIT_FORMAT)
        return self

    def setvaluex(self, val, vobj):
        fld = getattr(vobj, self.v_fld, vobj.add(self.v_fld))
        fld.value = val # .strftime(V_DATE_TIME_FORMAT)
        return self


class VUpdateTime(VDateTime):

    """vObject modification date/time.

    """
    
    
    def __init__(self, v_fld, v_fld_last_mod):
        super().__init__(v_fld)
        self.v_fld_last_mod = v_fld_last_mod
        return

    def getorecsx(self, vobj, rec_out, tag):
        for fld in [self.v_fld, self.v_fld_last_mod]:
            fld = getattr(vobj, fld, None)
            if fld is not None:
                val = fld.value.astimezone()
                rec_out[tag] = val.strftime(DATE_TIME_EDIT_FORMAT)
                break
        return self

    def setvaluex(self, val, vobj):
        v_fld = self.v_fld
        fld = getattr(vobj, v_fld, vobj.add(v_fld))
        val = localize(val)
        val = val.astimezone(TZ_UTC)
        fld.value = val
        v_fld = self.v_fld_last_mod
        fld = getattr(vobj, v_fld, vobj.add(v_fld))
        val = localize(val)
        val = val.astimezone(TZ_UTC)
        fld.value = val.strftime(V_DATE_TIME_FORMAT)
        return self


class VRRule(VFld1):

    """vObject recurrence rule.

    """    
    
    def getorecsx(self, vobj, rec_out, tag, ndx=ZERO):
        raise NotImplementedError

    def setvaluex(self, val, vobj):
        fld = vobj.add(self.v_fld)
        fld.value = val
        return self


class VAlarm:

    """vObject alarm.

    """
        
    def getorecsx(self, vobj, rec_out, tag):
        v_alarm = getattr(vobj, 'valarm', None)
        if v_alarm is None:
            rec_out[tag] = '#N/A'
        else:
            trigger = getattr(v_alarm, 'trigger', None)
            delta = trigger.value
            days = delta.days
            secs = delta.seconds + days * 24 * 3600
            mins = round(secs / 60.0)
            rec_out[tag] =  str(-mins)
        return self

    def setvaluex(self, val, vobj):
        delta = datetime.timedelta(minutes=val)
        valarm = vobj.add('valarm')
        valarm.add('action').value = 'DISPLAY'
        valarm.add('trigger').value = -delta
        valarm.add('description').value = 'This is an event reminder'
        return self


REPERTOIRE_ADR = {
    tonto2.TAG_LISTING_TYPE: VAdrType('adr'),
    tonto2.TAG_GREETING: None,
    tonto2.TAG_POLITE_MODE: VOrdFld('n', 'prefix'),
    tonto2.TAG_FIRST_NAME: VOrdFld('n', 'given'),
    tonto2.TAG_LAST_NAME: VOrdFld('n', 'family'),
    tonto2.TAG_TITLE: VFld('title'),
    tonto2.TAG_COMPANY: VList('org'),
    tonto2.TAG_DEPT_MAIL_STOP: VAdrFld('adr', 'box'),
    tonto2.TAG_LOCUS: VAdrFld('adr', 'extended'),
    tonto2.TAG_STREET: VAdrFld('adr', 'street'),
    tonto2.TAG_CITY: VAdrFld('adr', 'city'),
    tonto2.TAG_STATE: VAdrFld('adr', 'region'),
    tonto2.TAG_ZIP: VAdrFld('adr', 'code'),
    tonto2.TAG_COUNTRY: VAdrFld('adr', 'country'),
    tonto2.TAG_LATITUDE: VObjFld('geo', 'latitude'),
    tonto2.TAG_LONGITUDE: VObjFld('geo', 'longitude'),
    'PhoneType': VTelType('tel'),
    'Phone': VTel('tel'),
    tonto2.TAG_EMAIL: VFld('email'),
    tonto2.TAG__URI: VFld('url'),
    tonto2.TAG__ACCESSION_DATE: None,
    tonto2.TAG__UPDATE_DATE: VFld('rev'),
    tonto2.TAG_KEYWORDS: VConst('#sync'),
    tonto2.TAG_REMARKS: VFld('note'),
    tonto2.TAG_UNIQUE_ID: VUid('uid'),
    'AIM': VFld('x-aim'),
    'ICQ': VFld('x-icq'),
    'JABBER': VFld('x-jabber'),
    'MSN': VFld('x-msn'),
    'YAHOO': VFld('x-yahoo'),
    'TWITTER': VFld('x-twitter'),
    'SKYPE': VFld('x-skype'),
#    'PhotoType': VType('photo'),
#    'Photo': VPhoto('photo'),
    }


def conjure_vcard(rel):

    """From relation, return vCard.

    """
    
    def fix_phones(rel):

        """Accumulate phone numbers.  

        Discard blank phone numbers and phone types.

        """

        phones = []
        for ndx in [1, 2, 3, 4]:
            phone_type = rel.pages.find(f'PhoneType{ndx}')
            phone_number = rel.pages.find(f'Phone{ndx}')
            if phone_type and phone_number and phone_number.has_value:
                phones.append([phone_type.val_comp, phone_number.val_comp])
        result = len(phones)
        for ndx in [1, 2, 3, 4]:
            phones.append([tonto2.NOT_AVAIL, tonto2.NOT_AVAIL])
        for (offset, ndx) in enumerate([1, 2, 3, 4]):
            phone_type = rel.pages.find(f'PhoneType{ndx}')
            phone_number = rel.pages.find(f'Phone{ndx}')
            if phone_type and phone_number:
                (phone_type.val_comp, phone_number.val_comp) = phones[offset]
        return result

    def conjure_name(vobj):
        name = getattr(vobj, 'n', None)
        company = getattr(vobj, 'org', None)
        if name is None:
            if company is None:
                pass
            else:
                company_names = company.value
                if company_names:
                    vobj.add('n')
                    vobj.n.value.given = company_names[ZERO]
        return
    
    def conjure_formatted_name(vobj):
        formatted_name = None
        name = getattr(vobj, 'n', None)
        if name:
            prefix = name.value.prefix
            first_name = name.value.given
            last_name = name.value.family
            names = [prefix, first_name, last_name]
            names = [name for name in names if name not in tonto2.BLANK_VALUES]
            formatted_name = SPACE.join(names)
        if formatted_name not in tonto2.BLANK_VALUES:
            vobj.add('fn')
            vobj.fn.value = formatted_name
        return

    count_phones = fix_phones(rel)
    result = vobject.vCard()
    for (tag_tonto, vfld) in REPERTOIRE_ADR.items():
        if vfld is None:
            pass
        elif isinstance(vfld, VTelType) or isinstance(vfld, VTel):
            for (offset, ndx) in enumerate([1, 2, 3, 4]):
                if ndx > count_phones:
                    pass
                else:
                    tag_tonto_nth = f'{tag_tonto}{ndx}'
                    col = rel.pages.find(tag_tonto_nth)
                    if col.has_value:
                        val = col.val_comp
                        vfld.setvaluex(val, vobj=result)
        elif isinstance(vfld, VUid):
            col = rel.pages.find(tag_tonto)
            if col and col.has_value:
                val = col.val_comp
            else:
                val = str(uuid.uuid4())
            vfld.setvaluex(val, vobj=result)
        else:
            col = rel.pages.find(tag_tonto)
            if col and col.has_value:
                val = col.val_comp
                vfld.setvaluex(val, vobj=result)
    conjure_formatted_name(result)
    conjure_name(result)
    return result


REPERTOIRE_CAL = {
    tonto2.TAG_UNIQUE_ID: VUid1('uid'),
    tonto2.TAG_TITLE: VFld1('summary'),
    tonto2.TAG_REMARKS: VFld1('description'),
    tonto2.TAG_STATUS: VFld1('status'),
    tonto2.TAG__START: VDateTime('dtstart'),
    tonto2.TAG_ADVANCE_ALARM: VAlarm(),
#    tonto2.TAG_STOP: VDateTime('dtend'),  Not!  Better 'rrule:until'.
    tonto2.TAG__ACCESSION_DATE: VDateTime('created'),
    tonto2.TAG__UPDATE_DATE: VUpdateTime('dtstamp', 'last_modified'),
    tonto2.TAG_KEYWORDS: VConst('#sync'),
    tonto2.TAG_OFFSET: VRRule('rrule'),
    }


def conjure_ical(rel, vevent):

    """From relation and vevent return iCal.

    """
    
    for (tag_tonto, vfld) in REPERTOIRE_CAL.items():
        val = None
        if vfld is None:
            pass
        elif isinstance(vfld, VRRule):
            rrule = RRule().set_from_rec(rel)
            rrule_text = str(rrule)
            if rrule_text in tonto2.BLANK_VALUES:
                pass
            else:
                vfld.setvaluex(rrule_text, vobj=vevent)
        else:
            col = rel.pages.find(tag_tonto)
            if col and col.has_value:
                val = col.val_comp
                vfld.setvaluex(val, vobj=vevent)
    if hasattr(vevent, 'dtend'):
        pass
    elif 'UNTIL' in rrule:
        vfld = VDateTime('dtend')
        val = datetime.datetime.strptime(rrule['UNTIL'], V_DATE_TIME_FORMAT)
        vfld.setvaluex(val, vevent)
    else:
        vfld = VDateTime('dtend')
        start_date_time_vfld = vevent.dtstart
        start_date_time_value = vevent.dtstart.value
        if getattr(start_date_time_vfld, 'value_param', None) == 'DATE':
            fld = vfld.setvaluex(start_date_time_value + DELTA_DAY, vevent)
            fld.value_param = 'DATE'
        else:
            vfld.setvaluex(start_date_time_value + DELTA_HOUR, vevent)
    return
                        

class UnitIn:

    """Context manager for input files.

    """    
    
    def __init__(self, fn, title, suffixes):
        self.fn_in = pathlib.Path(fn).expanduser()
        if self.fn_in.suffix.lower() in suffixes:
            pass
        else:
            diagnostic(f'WARNING:  Suffix of {title} input ({self.fn_in}) should be {suffixes}.')
        if self.fn_in.exists():
            pass
        else:
            diagnostic(f'ERROR:  {title} input ({self.fn_in}) not found.', fatal=True)
        self.unit = open(self.fn_in, 'r')
        return

    def __enter__(self):
        return self.unit

    def __exit__(self, exc_type, exc_value, traceback):
        self.unit.close()
        return


class UnitInCsv(UnitIn):

    """Context manager for input *.csv files.

    """    
    
    def __init__(self, fn, title, suffixes=['.csv']):
        super().__init__(fn, title, suffixes)
        self.csv_reader = csv.DictReader(f=self.unit)
        return

    def __enter__(self):
        return self.csv_reader


class UnitInVcf(UnitIn):

    """Context manger for input *.vcf files.

    """
        
    def __init__(self, fn, title, suffixes=['.vcf']):
        super().__init__(fn, title, suffixes)
        return

    def __enter__(self):
        return self.gen_rec()

    def gen_rec(self):

        def handle_tag(rec_in, rec_out, tag_tonto, vfld, ndx_adr=ZERO):
            if vfld is None:
                pass
            elif isinstance(vfld, VAdrFld):
                vfld.getorecsx(rec_in, rec_out, tag_tonto, ndx=ndx_adr)
            else:
                vfld.getorecsx(rec_in, rec_out, tag_tonto)
            return
        
        for rec_in in vobject.readComponents(self.unit):
            if getattr(rec_in, 'fn', None):
                tag_tonto = tonto2.TAG_LISTING_TYPE
                vfld = REPERTOIRE_ADR[tag_tonto]
                adrs = vfld.getorecsxs(rec_in, max=4)
                if adrs:
                    for (ndx_adr, adr) in enumerate(adrs):
                        result={}
                        result[tag_tonto] = getattr(adr, 'type_param', None)  # 2014 Mar 25
                        for (tag_tonto, vfld) in REPERTOIRE_ADR.items():
                            if tag_tonto in [tonto2.TAG_LISTING_TYPE]:
                                pass
                            else:
                                handle_tag(rec_in, result, tag_tonto, vfld, ndx_adr)
                else:
                    result={}
                    for (tag_tonto, vfld) in REPERTOIRE_ADR.items():
                        handle_tag(rec_in, result, tag_tonto, vfld)
            yield result
        return                

    
class UnitInIcs(UnitIn):

    """Context manager for input *.ics files.

    """
    
    def __init__(self, fn, title, suffixes=['.ics']):
        super().__init__(fn, title, suffixes)
        return

    def __enter__(self):
        return self.gen_rec()

    def gen_rec(self):

        def handle_tag(rec_in, rec_out, tag_tonto, vfld):
            if vfld is None:
                pass
            elif isinstance(vfld, VRRule):
                pass
            else:
                vfld.getorecsx(rec_in, rec_out, tag_tonto)
            return
        
        def non_recurring():
            result = {}
            result[tonto2.TAG__START] = start_date.strftime(DATE_TIME_EDIT_FORMAT)
            result[tonto2.TAG_OFFSET] = tonto2.NOT_AVAIL
            result[tonto2.TAG_IS_OFFSET_TYPE_DAYS] = tonto2.NOT_AVAIL
            if last_occurrence_date is None:
                pass
            else:
                if ((result[tonto2.TAG__START] in tonto2.BLANK_VALUES) and
                    (result['Finish_Time'] in tonto2.BLANK_VALUES) and
                    ((last_occurrence_date - start_date) == DELTA_DAY)):
                    pass
                else:
                    result[tonto2.TAG_STOP] = last_occurrence_date.strftime(DATE_TIME_EDIT_FORMAT)
                    if last_occurrence_date.strftime(DATE_TIME_EDIT_FORMAT) == start_date.strftime(DATE_TIME_EDIT_FORMAT):
                        pass
                    else:
                        result[tonto2.TAG_OFFSET] = 1
                        result[tonto2.TAG_IS_OFFSET_TYPE_DAYS] = 'Y'
            result[tonto2.TAG_OFFSET_IN_MONTH] = tonto2.NOT_AVAIL
            result[tonto2.TAG_IS_OFFSET_IN_MONTH_TYPE_DAYS] = tonto2.NOT_AVAIL
            for (tag_tonto, vfld) in REPERTOIRE_CAL.items():
                handle_tag(v_event, result, tag_tonto, vfld)
            if hasattr(v_event, 'summary'):
                val = str(v_event.summary.value)
                result[tonto2.TAG__HANDLE] = val[:12]
            yield result
            return

        def recurring():
            r_rule_text = r_rule_fld.value
            r_rule = RRule().parse(r_rule_text)
            offsets = r_rule.get_offsets(start_date)
            until = r_rule.get_until()
            for (day0, offset, offset_type_days, offset_in_month, offset_in_month_type_days) in offsets:
                result = {}
                result[tonto2.TAG__START] = day0.strftime(DATE_TIME_EDIT_FORMAT)
                result[tonto2.TAG_OFFSET] = offset
                result[tonto2.TAG_IS_OFFSET_TYPE_DAYS] = offset_type_days
                if until is not None:
                    result[tonto2.TAG_STOP] = until.strftime(DATE_TIME_EDIT_FORMAT)
                result[tonto2.TAG_OFFSET_IN_MONTH] = offset_in_month
                result[tonto2.TAG_IS_OFFSET_IN_MONTH_TYPE_DAYS] = offset_in_month_type_days
                for (tag_tonto, vfld) in REPERTOIRE_CAL.items():
                    handle_tag(v_event, result, tag_tonto, vfld)
                if hasattr(v_event, 'summary'):
                    val = str(v_event.summary.value)
                    result[tonto2.TAG__HANDLE] = val[:12]
                yield result
            return
        
        for cal in vobject.readComponents(self.unit):
            tz_name = getattr(cal, 'x_wr_timezone', None)
            if tz_name is None:
                pass
            else:
                TZ = zoneinfo.ZoneInfo(tz_name.value)
            for v_event in cal.vevent_list:
                start_date_fld = getattr(v_event, 'dtstart', None)
                if start_date_fld is None:
                    pass
                else:
                    start_date = start_date_fld.value
                last_occurrence_date_fld = getattr(v_event, 'dtend', None)
                if last_occurrence_date_fld is None:
                    last_occurrence_date = None
                else:
                    last_occurrence_date = last_occurrence_date_fld.value
                r_rule_fld = getattr(v_event, 'rrule', None)
                if r_rule_fld is None:
                    for rec in non_recurring():
                        yield rec
                else:
                    for rec in recurring():
                        yield rec
        return                

    
class UnitInTonto(UnitIn):

    """Context manager for input Tonto2 *.dd files.

    """
    
    def __init__(self, fn, title, cls, suffixes=['.dd', '.csv']):
        self.fn_in = pathlib.Path(fn).expanduser()
        if self.fn_in.suffix.lower() in suffixes:
            pass
        else:
            error(f'WARNING:  Suffix of {title} input ({self.fn_in}) should be {suffixes}.')
        self.fn_dd = tonto2.coerce_suffix(self.fn_in, '.dd')
        self.fn_csv = tonto2.coerce_suffix(self.fn_in, '.csv')
        if self.fn_dd.exists():
            pass
        else:
            error(f'ERROR:  {title} input ({self.fn_dd}) not found.', fatal=True)
        if self.fn_csv.exists():
            pass
        else:
            error(f'ERROR:  {title} input ({self.fn_csv}) not found.', fatal=True)
        self.tab = tonto2.Tab(tag=None, path=self.fn_dd).load_rel()
        if isinstance(self.tab.rel, cls):
            pass
        else:
            error(f'ERROR:  {title} input is not an Address List.', fatal=True)
        return

    def __enter__(self):
        return self.tab.rel

    def __exit__(self, exc_type, exc_value, traceback):
        return


class UnitOut:

    """Context manager for output files.

    """    
    
    def __init__(self, fn, title, suffixes):
        self.fn_out = pathlib.Path(fn).expanduser()
        if self.fn_out.suffix.lower() in suffixes:
            pass
        else:
            error(f'WARNING:  Suffix of {title} output ({self.fn_out}) should be {suffixes}.')
        if self.fn_out.exists():
            error(f'ERROR:  {title} output ({self.fn_out}) already exists.', fatal=True)
        self.unit = open(self.fn_out, 'w')
        return

    def __enter__(self):
        return self.unit

    def __exit__(self, exc_type, exc_value, traceback):
        self.unit.close()
        return


class UnitOutCsv(UnitOut):

    """Context manager for output *.csv files.

    """    
    
    def __init__(self, tags, fn, title, suffixes=['.csv']):
        super().__init__(fn, title, suffixes)
        self.csv_writer = csv.DictWriter(f=self.unit, fieldnames=tags)
        self.csv_writer.writeheader()
        return

    def __enter__(self):
        return self.csv_writer


class UnitOutVcf(UnitOut):

    """Context manager for output *.vcf files.

    """    
    
    def __init__(self, fn, title, suffixes=['.vcf']):
        super().__init__(fn, title, suffixes)
        return


class UnitOutIcs(UnitOutVcf):

    """Context manager for output *.ics files.

    """    
    
    def __init__(self, fn, title, suffixes=['.ics']):
        super().__init__(fn, title, suffixes)
        return

    
class UnitOutTonto(UnitOut):

    """Context manager for output Tonto2 *.dd files.

    """
    
    def __init__(self, cls_name, fn, title, suffixes=['.dd', '.csv']):
        self.fn_out = pathlib.Path(fn).expanduser()
        if self.fn_out.suffix.lower() in suffixes:
            pass
        else:
            error(f'WARNING:  Suffix of {title} output ({self.fn_out}) should be {suffixes}.')
        self.fn_dd = tonto2.coerce_suffix(self.fn_out, '.dd')
        self.fn_csv = tonto2.coerce_suffix(self.fn_out, '.csv')
        if self.fn_dd.exists():
            error(f'ERROR:  {title} output ({self.fn_dd}) already exists.', fatal=True)
        if self.fn_csv.exists():
            error(f'ERROR:  {title} output ({self.fn_csv}) already exists.', fatal=True)
        self.tab = tonto2.Tab(tag=None, path=self.fn_dd)
        self.tab.rel = tonto2.REG_RELS[cls_name].cls().conjure_pages()
        return

    def __enter__(self):
        return self.tab.rel

    def __exit__(self, exc_type, exc_value, traceback):
        self.tab.rel.rel_is_dirty = True
        self.tab.save_rel(tags=self.tab.rel.pages.get_tag_collection())
        return

# =============================================================================================

if __name__ == "__main__":  

    """This code is run when this module is executed, not when it is included.

    """
    

    def vcard_to_rec(vcard_in, rec_in):
        rec_in = rec_in.copy()
        path_vcard = pathlib.Path('/tmp/test_vcard.vcf')
        with open(path_vcard, 'w') as unit:
            unit.write(vcard_in)
        with UnitInVcf(fn=path_vcard, title='test') as gen:
            for rec_out in gen:
                break
        for (key_out, val_out) in rec_out.items():
            val_in = rec_in.pop(key_out, None)
            if val_in == val_out:
                pass
            else:
                print(rec_out)
                print(f'Reading vcard mismatch on {key_out}:  {val_out!r} should be {val_in!r}.')
                raise NotImplementedError
        for (key_in, val_in) in rec_in.items():
            print(f'Reading vcard mismatch on {key_in}:  Should be {val_in!r}.')
            raise NotImplementedError
        return

    
    def ical_to_rec(ical_in, rec_in):
        rec_in = rec_in.copy()
        path_ical = pathlib.Path('/tmp/test_ical.ics')
        with open(path_ical, 'w') as unit:
            unit.write(ical_in)
        with UnitInIcs(fn=path_ical, title='test') as gen:
            for rec_out in gen:
                break
        for (key_out, val_out) in rec_out.items():
            val_in = rec_in.pop(key_out, None)
            if val_in == val_out:
                pass
            else:
                print(rec_out)
                print(f'Reading ical mismatch on {key_out}:  {val_out!r} should be {val_in!r}.')
                raise NotImplementedError
        for (key_in, val_in) in rec_in.items():
            print(f'Reading ical mismatch on {key_in}:  Should be {val_in!r}.')
            raise NotImplementedError
        return

    
    def vcard_from_rec(rec_in, vcard_in):
        path_vcard = pathlib.Path('/tmp/test_vcard.vcf')
        path_vcard.unlink(missing_ok=True)
        with UnitOutVcf(fn=path_vcard, title='test') as unit:
            rel = tonto2.RelAddressList().conjure_pages()
            rel.recs.extend([rec_in])
            rel.stage_rec(ZERO)
            vcard = conjure_vcard(rel)
            vcard_out = vcard.serialize()
            lines_out = vcard_out.splitlines()
            lines_in = vcard_in.splitlines()
            if lines_out == lines_in:
                pass
            else:
                on1 = True
                while True:
                    if lines_in:
                        line_in = lines_in.pop(ZERO)
                        
                    else:
                        line_in = None
                    if lines_out:
                        line_out = lines_out.pop(ZERO)
                    else:
                        line_out = None
                    if line_in is None and line_out is None:
                        break
                    if on1:
                        if line_in == line_out:
                            continue
                        else:
                            on1 = False
                            print('Writing vcard missmatch:')
                    print(f'< {line_in!r}')
                    print(f'> {line_out!r}')
                raise NotImplementedError
        return

    
    def ical_from_rec(rec_in, ical_in):
        path_ical = pathlib.Path('/tmp/test_ical.ics')
        path_ical.unlink(missing_ok=True)
        with UnitOutIcs(fn=path_ical, title='test') as unit:
            ical = vobject.iCalendar()
            vevent = ical.add('vevent')
            rel = tonto2.RelCalendar().conjure_pages()
            rel.recs.extend([rec_in])
            rel.stage_rec(ZERO)
            conjure_ical(rel, vevent)
            ical_out = ical.serialize()
            lines_out = ical_out.splitlines()
            lines_in = ical_in.splitlines()
            if lines_out == lines_in:
                pass
            else:
                on1 = True
                while True:
                    if lines_in:
                        line_in = lines_in.pop(ZERO)
                        
                    else:
                        line_in = None
                    if lines_out:
                        line_out = lines_out.pop(ZERO)
                    else:
                        line_out = None
                    if line_in is None and line_out is None:
                        break
                    if on1:
                        if line_in == line_out:
                            continue
                        else:
                            on1 = False
                            print('Writing ical missmatch:')
                    print(f'< {line_in!r}')
                    print(f'> {line_out!r}')
                raise NotImplementedError
        return

    
    def round_trip_tests():

        """Round-trip tests.

        """
    
        ical_event_annual = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//PYVOBJECT//NONSGML Version 1//EN
BEGIN:VEVENT
UID:19970901T130000Z-123403@example.com
DTSTART:19971102T000000
DTEND:19971102T010000
DTSTAMP:19970901T130000Z
LAST_MODIFIED:19970901T180000Z
RRULE:FREQ=MONTHLY;INTERVAL=12;BYMONTHDAY=2;WKST=SU
SUMMARY:Our Blissful Anniversary
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:This is an event reminder
TRIGGER:-PT30M
END:VALARM
END:VEVENT
END:VCALENDAR
"""
        rec_event_annual = {
            '_Start': '1997/11/02 00:00',
            'AdvanceAlarm': '30',
            'Offset': '12',
            'IsOffsetTypeDays': 'N',
            'OffsetInMonth': '2',
            'IsOffsetInMonthTypeDays': 'Y',
            'UniqueID': '19970901T130000Z-123403@example.com',
            '_Handle': 'Our Blissful',
            'Title': 'Our Blissful Anniversary',
            '_UpdateDate': '1997/09/01 08:00',
            'Keywords': '#sync',
            }
        ical_event_multi_day = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//PYVOBJECT//NONSGML Version 1//EN
BEGIN:VEVENT
UID:20070423T123432Z-541111@example.com
DTSTART:20070628T000000
DTEND:20070709T000000
DTSTAMP:20070423T123400Z
LAST_MODIFIED:20070423T173400Z
RRULE:FREQ=DAILY;INTERVAL=1;UNTIL=20070709T000000Z;WKST=SU
SUMMARY:Festival International de Jazz de Montreal
END:VEVENT
END:VCALENDAR
"""
        rec_event_multi_day = {
            '_Start': '2007/06/28 00:00',
            'AdvanceAlarm': '#N/A',
            'Offset': '1',
            'IsOffsetTypeDays': 'Y',
            'OffsetInMonth': '#N/A',
            'IsOffsetInMonthTypeDays': '#N/A',
            'Stop': '2007/07/09 00:00',
            'UniqueID': '20070423T123432Z-541111@example.com',
            '_Handle': 'Festival Int',
            'Title': 'Festival International de Jazz de Montreal',
            '_UpdateDate': '2007/04/23 07:34',
            'Keywords': '#sync',
            }
        ical_event_non_recurring = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//PYVOBJECT//NONSGML Version 1//EN
BEGIN:VEVENT
UID:19970610T172345Z-AF23B2@example.com
DTSTART:19970714T000000
DTEND:19970714T000000
DTSTAMP:19970610T172300Z
LAST_MODIFIED:19970610T222300Z
SUMMARY:Bastille Day Party
END:VEVENT
END:VCALENDAR
"""
        rec_event_non_recurring = {
            '_Start': '1997/07/14 00:00',
            'AdvanceAlarm': '#N/A',
            'Offset': '#N/A',
            'IsOffsetTypeDays': '#N/A',
            'OffsetInMonth': '#N/A',
            'IsOffsetInMonthTypeDays': '#N/A',
            'Stop': '1997/07/14 00:00',
            'UniqueID': '19970610T172345Z-AF23B2@example.com',
            '_Handle': 'Bastille Day', 
            'Title': 'Bastille Day Party',
            '_UpdateDate': '1997/06/10 12:23',
            'Keywords': '#sync',
            }
        vcard_email_only = """BEGIN:VCARD
VERSION:3.0
UID:b0311459-6fa4-494a-955f-07a50a68a83a
EMAIL:jdoe@example.com
FN:J. Doe
N:Doe;J.;;;
END:VCARD
"""
        rec_email_only = {
            'PoliteMode': NULL,
            'FirstName': 'J.',
            'LastName': 'Doe',
            'eMail': 'jdoe@example.com',
            'Keywords': '#sync',
            'UniqueID': 'b0311459-6fa4-494a-955f-07a50a68a83a',
            }
        vcard_phone = """BEGIN:VCARD
VERSION:3.0
UID:urn:uuid:4fbe8971-0bc3-424c-9c26-36c3e1eff6b1
EMAIL:jdoe@example.com
FN:J. Doe
N:Doe;J.;;;
TEL:tel:+1-555-555-5555
TEL:tel:+1-666-666-6666
END:VCARD
"""
        rec_phone = {
            'PoliteMode': NULL,
            'FirstName': 'J.',
            'LastName': 'Doe',
            'eMail': 'jdoe@example.com',
            'Keywords': '#sync',
            'UniqueID': 'urn:uuid:4fbe8971-0bc3-424c-9c26-36c3e1eff6b1',
            'Phone1': 'tel:+1-555-555-5555',
            'Phone2': 'tel:+1-666-666-6666',
            }
        vcard_adr = """BEGIN:VCARD
VERSION:3.0
UID:7736e75a-18d0-4f33-b170-8e4a57b6065d
ADR;TYPE=work:;Suite D2-630;2875 Laurier;Quebec;QC;G1V 2M2;Canada
EMAIL:simon.perreault@viagenie.ca
FN:Simon Perreault
N:Perreault;Simon;;;
TEL:tel:+1-418-656-9254 ext=102
TEL:tel:+1-418-262-6501
END:VCARD
"""
        rec_adr = {
            'ListingType': 'work',
            'PoliteMode': NULL,
            'FirstName': 'Simon',
            'LastName': 'Perreault',
            'DeptMailStop': NULL,
            'Locus': 'Suite D2-630',
            'Street': '2875 Laurier',
            'City': 'Quebec',
            'State': 'QC',
            'Zip': 'G1V 2M2',
            'Country': 'Canada',
            'Phone1': 'tel:+1-418-656-9254 ext=102',
            'Phone2': 'tel:+1-418-262-6501',
            'eMail': 'simon.perreault@viagenie.ca',
            'Keywords': '#sync',
            'UniqueID': '7736e75a-18d0-4f33-b170-8e4a57b6065d',
            }
        print('Annual Event')
        ical_to_rec(ical_event_annual, rec_event_annual)
        ical_from_rec(rec_event_annual, ical_event_annual)
        print('Multi-Day Event')
        ical_to_rec(ical_event_multi_day, rec_event_multi_day)
        ical_from_rec(rec_event_multi_day, ical_event_multi_day)
        print('Non-recurring Event')
        ical_to_rec(ical_event_non_recurring, rec_event_non_recurring)
        ical_from_rec(rec_event_non_recurring, ical_event_non_recurring)
        print('Email-Only vCard')
        vcard_to_rec(vcard_email_only, rec_email_only)
        vcard_from_rec(rec_email_only, vcard_email_only)
        print('Phone vCard')
        vcard_to_rec(vcard_phone, rec_phone)
        vcard_from_rec(rec_phone, vcard_phone)
        print('Address vCard')
        vcard_to_rec(vcard_adr, rec_adr)
        vcard_from_rec(rec_adr, vcard_adr)
        return

    
    round_trip_tests()

    
# Fin
