#!/opt/local/bin/python

import base
import datetime
import math
import weakref
import zoneinfo

from django.conf              import settings
from django.db                import models
from django.http              import Http404
from django.urls              import reverse, get_resolver
from django.utils.safestring  import mark_safe


base.Enum.Define(('SPECIALWHEN', 'SpecialWhens'), (
    ('star',                  'Dawn of Time',   'dawn',           'DAWN_OF_TIME'),
    ('calendar-minus',        'Yesterday',      'past',           'YESTERDAY'),
    ('calendar-day',          'Today',          'day',            'TODAY'),
    ('calendar-star',         'Now',            'now',            'NOW'),
    ('calendar-plus',         'Tomorrow',       'plus',           'TOMORROW'),
    ('hexagon',               'End of Days',    'dusk',           'END_OF_DAYS'),
))


class When(base.Thing):
  ''' a replacement for datetime, extensible for use with timelines that are not gregorian '''

  ATTRIBUTES        = [         # which of our attributes get copied
      'era', 'timezone', 'tzname', 'special',
      'year', 'month', 'day', 'weekday', 'hour', 'minute', 'second',
  ]

  era               = None      # Era subclass
  tzname            = None      # uppercase alphabetic code for the timezone
  timezone          = None      # zoneinfo instance

  special           = None      # SpecialWhens

  year              = None      # int
  month             = None      # int, subtract 1 to get an index into era.months
  day               = None      # int
  weekday           = None      # int, also an index into era.weekdays

  hour              = None      # int
  minute            = None      # int
  second            = None      # real

  @classmethod
  def From(klass, thing, **kwargs):
    ''' convert the thing -- string or datetime -- into a When '''
    return base.CommonEra.MakeWhen(thing, **kwargs)

  @property
  def text(self):
    return self.era and self.era.WhenText(self) or ''

  @property
  def zero(self):
    ''' True if no meaningful field is filled in '''
    return bool(
        self.special  is None and
        self.year     is None and
        self.month    is None and
        self.day      is None and
        self.weekday  is None and
        self.hour     is None and
        self.minute   is None and
        self.second   is None)

  @property
  def cosmic(self):
    ''' True if we represent the start or end of time itself '''
    return self.special in (base.whens.SPECIALWHEN_DAWN_OF_TIME, base.whens.SPECIALWHEN_END_OF_DAYS)

  @property
  def datetime(self):
    ''' constructs a datetime.datetime out of our parts '''
    if self.special == base.whens.SPECIALWHEN_DAWN_OF_TIME:
      return base.consts.DATETIME_MIN
    if self.special == base.whens.SPECIALWHEN_END_OF_DAYS:
      return base.consts.DATETIME_MAX
    date, time      = self.date, self.time
    if date and time:
      return datetime.datetime.combine(date, time)

  @property
  def date(self):
    ''' constructs a datetime.date out of our date parts '''
    if self.special == base.whens.SPECIALWHEN_DAWN_OF_TIME:
      return base.consts.DATE_MIN
    if self.special == base.whens.SPECIALWHEN_END_OF_DAYS:
      return base.consts.DATE_MAX
    if self.year is None or self.month is None or self.day is None:
      return
    return datetime.date(year=self.year, month=self.month, day=self.day)

  @property
  def time(self):
    ''' constructs a datetime.time out of our date parts '''
    if self.hour is None or self.minute is None:
      return
    second          = math.floor(self.second or 0)
    usecond         = round(((self.second or 0) - second) * 1000000)
    return datetime.time(
        hour=self.hour, minute=self.minute, second=second, microsecond=usecond, tzinfo=self.TimeZone())

  def TimeZone(self):
    ''' returns the zoneinfo instance that should manage our timezone '''
    if not self.timezone and self.tzname:
      timezone      = self.tzname
      if timezone.isalpha():
        timezone    = base.utils.ZoneInfoByTzName()[timezone.strip().upper()]
      try:
        timezone    = zoneinfo.ZoneInfo(timezone)
      except:
        pass
      if not isinstance(timezone, zoneinfo.ZoneInfo):
        raise base.errors.BadWhen('unable to make sense of the timezone', self.tzname)
      self.timezone = timezone
    return self.timezone

  def Shift(self, timezone):
    ''' in-place adjusts us to a new timezone '''
    if not timezone or self.timezone == timezone:
      return
    dt              = self.datetime
    if not dt:
      raise base.errors.IncompleteWhen('may only When.Shift() with a complete date and time')
    dt              = dt.astimezone(timezone)
    self.year       = dt.year
    self.month      = dt.month
    self.day        = dt.day
    self.hour       = dt.hour
    self.minute     = dt.minute
    self.timezone   = timezone
    self.tzname     = dt.tzname()

  def __init__(self, **kwargs):
    base.utils.SetAttrs(self, **kwargs)

  def __str__(self):
    return self.text or ''

  def __hash__(self):
    return hash(self.text)

  def __eq__(self, other):
    if isinstance(other, str):
      return self.text == other
    if isinstance(other, When):
      return self.text == other.text
    return False

  def __lt__(self, other):
    if isinstance(other, str):
      return self.text < other
    if isinstance(other, When):
      if self.special == base.whens.SPECIALWHEN_END_OF_DAYS:
        return False
      if self.special == base.whens.SPECIALWHEN_DAWN_OF_TIME and other.special != base.whens.SPECIALWHEN_DAWN_OF_TIME:
        return True
      return self.text < other.text
    return False



###
## Era
#

class Era(base.Thing, metaclass=base.registry.AutoRegister, skip=1):
  ''' abstract timeline for parsing and formatting Whens.
      Eras are always used in class form, never instantiated.
      see CommonEra for a concrete implementation
  '''

  tag               = None    # smolname of this timeline
  name              = None    # fullname of this timeline
  icon              = None    # symbol
  aliases           = None    # list of alternate tags

  backwards         = False   # do years run backwards?

  months            = None    # Enum
  weekdays          = None    # Enum

  @classmethod
  def MakeWhen(klass, thing, now=None, timezone=None):
    ''' convert the thing -- string or datetime -- into a When '''

  @classmethod
  def WhenText(self, when):
    ''' format a When back into a string '''
