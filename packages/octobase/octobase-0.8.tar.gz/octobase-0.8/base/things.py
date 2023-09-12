#!/opt/local/bin/python

import base

from django.conf              import settings
from django.db                import models
from django.http              import Http404
from django.urls              import reverse, get_resolver
from django.utils.safestring  import mark_safe


class Thing:
  ''' base class for every (new) thing in our system '''

  def __init__(self, **kwargs):
    base.utils.SetAttrs(self, **kwargs)

  __in_repr         = False
  def __repr__(self):
    if self.__in_repr:
      return ''
    basic           = base.utils.ClassName(self) + '_' + hex(id(self))[-3:]
    self.__in_repr  = True
    stred           = str(self)
    self.__in_repr  = False
    return stred and (basic + "('" + str(self) + "')") or basic

  ###
  ## ATTRIBUTES
  #     very basic ways of thunking this object

  ATTRIBUTES        = None          # meaningful attributes that should be included in Dupe() and Copy()

  @base.utils.anyproperty
  def attributes(zelf):
    ''' returns a list of the names of meaningful attributes on ourself '''
    return zelf.ATTRIBUTES or []

  def Attributes(self, skip=None, skip_nones=False):
    ''' returns a dictionary of our attributes '''
    if skip and isinstance(skip, str):
      skip          = set([skip])
    results         = {x: getattr(self, x) for x in self.ATTRIBUTES if not skip or not x in skip}
    if skip_nones:
      results       = {x:y for x,y in results.items() if y is not None}
    return results

  def Reset(self):
    ''' returns our attrs to a pristine state '''
    base.utils.SetAttrs(self, {x: None for x in (self.ATTRIBUTES or [])})

  def Dupe(self):
    ''' returns a copy of ourself '''
    return type(self)().Copy(self)

  def Copy(self, other, nones=True):
    ''' copies any attrs we can from the other into ourself; returns self '''
    attr0           = self.ATTRIBUTES and set(self.ATTRIBUTES) or set()
    attr1           = hasattr(other, 'ATTRIBUTES') and other.ATTRIBUTES and set(other.ATTRIBUTES) or attr0
    attrs           = attr0 & attr1
    if not attrs:
      raise base.errors.NoAttributes(self, other)
    for attr in (attr0 & attr1):
      val           = getattr(other, attr)
      if nones or val is not None:
        setattr(self, attr, val)
    return self
