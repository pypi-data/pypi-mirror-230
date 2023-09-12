#!/opt/local/bin/python
''' legacy time parsing; please use Whens instead '''

import base
import datetime
import logging
import re


def ParseTimestamp(text, force_datetime=False):
  ''' Does our very best to extract a meaningful timestamp from the text string given.

        force_datetime -- calls DateTimeFromDate() if needed
  '''
  _, timestamp    = SplitPathToTextAndTime(text)
  if force_datetime and isinstance(timestamp, datetime.date):
    timestamp     = base.utils.DateTimeFromDate(timestamp)
  return timestamp



def SplitPathToTextAndTime(filepath):
  ''' Given a filepath, we split and return (TEXT, TIME) where:
        TEXT is the textual part of the filename, not counting time or date info (or extension)
        TIME is either a datetime.date or datetime.time object if we can find date/time info in the filepath.
  '''

  def IsSepDigits(str):
    ''' Helper to test if a string is composed entirely of separators or digits. '''
    return str and not str.strip('0123456789-_ .')

  def IsFalseMatch(groups):
    ''' Our regexps, below, have a possible false-match case.  This because we want to be tolerant about
        single-digit date parts, and yet simultaneously allow date strings with no separators at all.
        What happens is '2012/16-framenumber' comes out as '2012', '/1', '6'.  Ergo: if we have a
        single digit part that does NOT begin with a separator, we know we false-matched.
    '''
    for num in (2, 3, 5, 6):
      if num < len(groups) and len(groups[num]) == 1:
        return True
    return False

  filepath      = filepath.replace(':', '.')

  if not filepath:
    return (None, None)

  # Split into path chunks
  chunks        = filepath.split('/')

  # Filename is simply the last (non-empty) chunk
  chunks        = [x for x in chunks if x]
  if not chunks:
    return (None, None)
  filename      = chunks.pop(-1)

  # Strip off ALL extensions (there may be more than one).  Note that timestamps are often encoded
  # into a filename with dots (e.g.: 'Screen Shot 2011-10-09 at 3.10.24 AM.jpg') so we say that extensions
  # may not begin with a digit.
  filename      = filename.strip('.')
  while '.' in filename:
    pos         = filename.rfind('.')
    if filename[pos+1].isdigit():
      break
    filename    = filename[:pos].strip('.')
  if not filename:
    return (None, None)

  # At minimum we want to run the (remaining) filename through our regexps.  If that name begins with
  # digits though, and if the parent chunks are entirely digits or separators, we want to also run
  # variations with up to two parent chunks prefixed in.
  variants      = [filename]
  if filename[0].isdigit():
    if chunks and IsSepDigits(chunks[-1]):
      variants.append(chunks.pop(-1) + '/' + filename)
      if chunks and IsSepDigits(chunks[-1]):
        variants.append(chunks.pop(-1) + '/' + variants[-1])

  # We have two regexps to test -- a datetime and a date
  REGEXP_TIME   = re.compile(r'^(\D*)(\d{4})([\-\._/ ]*\d\d?)([\-\._/ ]*\d\d?)( at| ?[tT]| |/)( ?\d\d?)(\.?\d\d?)(\.?\d\d?)?(\.\d+)? ?([zZ]|[aApP][mM]?)?(.*)$')
  REGEXP_DATE   = re.compile(r'^(\D*)(\d{4})([\-\._/ ]*\d\d?)([\-\._/ ]*\d\d?)(.*)$')
  for variant in variants:
    match       = REGEXP_TIME.match(variant)
    if match and not IsFalseMatch(match.groups()):
      break
    match       = REGEXP_DATE.match(variant)
    if match and not IsFalseMatch(match.groups()):
      break
    match       = None

  if not match:
    return (filename, None)

  groups        = match.groups()

  # Date info is always in groups 1, 2, and 3
  yr            = int(groups[1].strip('-._/ '))
  mo            = int(groups[2].strip('-._/ '))
  dy            = int(groups[3].strip('-._/ '))

  # Time info may be present or not
  have_time     = len(groups) > 5
  if have_time:
    hr, mn, sc, ms = groups[5:9]
    mod         = groups[9]
    tz          = base.consts.TIME_ZONE

    hr          = int(hr.strip(' '))
    mn          = int(mn.strip('.'))
    sc          = sc is not None and int(sc.strip('.')) or 0
    ms          = ms is not None and int(ms.strip('.')) or 0

    if mod:
      mod       = mod.upper()
      if  mod in ('P', 'PM'):
        hr        += 12
      elif mod == 'Z':
        tz      = base.consts.TIME_UTC
      elif mod not in ('A', 'AM'):
        raise base.errors.TimezoneParsingNotImpl(filename)

  # Build the date
  try:
    if have_time:
      while ms > 999999:
        ms      = round(ms / 10)
      if tz:
        time    = datetime.datetime(yr, mo, dy, hr, mn, sc, ms, tzinfo=tz)
      else:
        time    = datetime.datetime(yr, mo, dy, hr, mn, sc, ms)
    else:
      time      = datetime.date(yr, mo, dy)
  except ValueError as e:
    return (filename, None)

  # The text part is then just prefix text plus suffix text
  text          = (groups[0] + ' ' + groups[-1]).strip('-._/ ')
  if not text:
    text        = None

  return (text, time)



class TestLegacyTimeParsing(base.TestCase):
  ''' Tests our ability to parse timestamps from filepaths. '''

  CASES             = [
      ('abcde:/',                                                 'abcde',            None),
      ('2012:/01-02 - Max.min',                                   'Max',              datetime.date(2012, 1, 2)),
      ('abcde:/Foo/20140225 - 8633 Miles/',                       '8633 Miles',       datetime.date(2014, 2, 25)),
      ('abcde:/Foo/2012-FrameNumber.jpg.lrbak',                   '2012-FrameNumber', None),
      ('abcde:/Foo/2012/16-FrameNumber.jpg',                      '16-FrameNumber',   None),
      ('abcde:/Foo/2012/08/16-EventName.jpg',                     'EventName',        datetime.date(2012, 8, 16)),
      ('abcde:/Foo/2012/08/16 - EventName.jpg',                   'EventName',        datetime.date(2012, 8, 16)),
      ('abcde:/Foo/2012 - 08/16 - EventName.jpg',                 'EventName',        datetime.date(2012, 8, 16)),
      ('abcde:/Foo/2000-2004 - Xyz/',                             '2000-2004 - Xyz',  None),
  ]

  if base.consts.TIME_ZONE:
    CASES.extend([
      ('abcde:/Foo/Screen Shot 2012-9-4 at 1.6.44 AM.jpg',        'Screen Shot',      datetime.datetime(2012, 9,  4,  1,  6, 44, tzinfo=base.consts.TIME_ZONE)),
      ('abcde:/Foo/Screen Shot 2012-9-4 at 1.13.44 PM.jpg',       'Screen Shot',      datetime.datetime(2012, 9,  4, 13, 13, 44, tzinfo=base.consts.TIME_ZONE)),
      ('abcde:/Foo/2012-01-26 21.22.06.jpg',                      None,               datetime.datetime(2012, 1, 26, 21, 22,  6, tzinfo=base.consts.TIME_ZONE)),
      ('abcde:/Foo/2012-01-26/21.22.06.jpg',                      None,               datetime.datetime(2012, 1, 26, 21, 22,  6, tzinfo=base.consts.TIME_ZONE)),
      ('abcde:/Foo/20120816T010203.456Z.jpg',                     None,               datetime.datetime(2012, 8, 16, 1, 2, 3, 456, tzinfo=base.consts.TIME_UTC)),
      ('abcde:/Foo/20120816T010203.jpg',                          None,               datetime.datetime(2012, 8, 16, 1, 2, 3, tzinfo=base.consts.TIME_ZONE)),
      ('abcde:/Foo/20120816T0102.jpg',                            None,               datetime.datetime(2012, 8, 16, 1, 2, tzinfo=base.consts.TIME_ZONE)),
      ('2021-03-23T15:55:15.574494Z',                             None,               datetime.datetime(2021, 3, 23, 15, 55, 15, 574494, tzinfo=base.consts.TIME_UTC)),
      ('2020-08-17T01:05:08.7733076Z',                            None,               datetime.datetime(2020, 8, 17, 1, 5, 8, 773308, tzinfo=base.consts.TIME_UTC)),
  ])

  def Run(self):
    for (src, stext, stime) in self.CASES:
      (rtext, rtime)  = SplitPathToTextAndTime(src)
      passed          = stext == rtext and stime == rtime
      message         = '{}  -->  {!s:32} {!s}'.format(base.utils.PadString(src, 55), rtext, rtime)
      if not passed:
        message       = message + '  EXPECTED:  {!s:32} {!s}'.format(stext, stime)
      self.LogResult(passed, message)
