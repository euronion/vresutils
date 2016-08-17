from __future__ import absolute_import

import pandas as pd
import shapefile
from itertools import count, chain
from operator import itemgetter
from collections import OrderedDict
from six import iteritems
from six.moves import map, zip

from .array import unique_sorted
from .shapes import nuts1, nuts3

from . import make_toModDir
toModDir = make_toModDir(__file__)

def aggregate(data, mapping, how="sum", axis=0):
    try:
        agg = getattr(np, how)
    except AttributeError:
        raise ValueError('`how` must be a string describing a numpy function like `sum`')

    cntries = varray.unique_sorted(np.asanyarray(mapping))
    res = np.empty(shape=data.shape[:axis] + data.shape[axis+1:], dtype=data.dtype)
    for i, cnt in enumerate(cntries):
        res[i] = agg(np.take(data, np.where(mapping.index == cnt)[0], axis=axis), axis=axis)
    return res

def countries_to_nuts1(series=True):
    """
    Returns a mapping from european countries to lists of their nuts1
    regions.  Some countries like Kosovo or Turkey are omitted, as
    well as a couple of islands.
    """

    excludenuts = set(('EL4', 'PT2', 'PT3', 'ES7', 'FI2', 'FR9'))
    excludecountry = set(('MT', 'TR', 'LI', 'IS', 'CY', 'KV'))
    mapcountry = dict(UK=u'GB', EL=u'GR')

    mapping = pd.Series({x: mapcountry.get(x[:2], x[:2])
                         for x in nuts1()
                         if x not in excludenuts and
                            x[:2] not in excludecountry})

    if not series:
        od = OrderedDict()
        for nuts, country in iteritems(mapping):
            od.setdefault(country, []).append(nuts)
        mapping = od

    return mapping

def countries_to_nuts3(series=True):
    """
    Returns a mapping from european countries to lists of their nuts1
    regions.  Some countries like Kosovo or Turkey are omitted, as
    well as a couple of islands.
    """

    excludenuts = set(('FRA10', 'FRA20', 'FRA30', 'FRA40', 'FRA50',
                       'PT200', 'PT300',
                       'ES707', 'ES703', 'ES704','ES705', 'ES706', 'ES708', 'ES709', 'FI2', 'FR9'))
    excludecountry = set(('MT', 'TR', 'LI', 'IS', 'CY', 'KV'))
    mapcountry = dict(UK=u'GB', EL=u'GR')

    mapping = pd.Series({x: mapcountry.get(x[:2], x[:2])
                         for x in nuts3()
                         if x not in excludenuts and
                            x[:2] not in excludecountry})

    if not series:
        od = OrderedDict()
        for nuts, country in iteritems(mapping):
            od.setdefault(country, []).append(nuts)
        mapping = od

    return mapping


def iso2_to_iso3():
    """
    Extract a mapping from iso2 country codes to iso3 country codes
    from the countries dataset.
    """
    sf = shapefile.Reader(toModDir('data/ne_10m_admin_0_countries/ne_10m_admin_0_countries'))
    fields = dict(zip(map(itemgetter(0), sf.fields[1:]), count()))
    def name(rec):
        if rec[fields['ISO_A2']] != '-99':
            return rec[fields['ISO_A2']]
        elif rec[fields['WB_A2']] != '-99':
            return rec[fields['WB_A2']]
        else:
            return rec[fields['ADM0_A3']][:-1]
    return dict(chain(
        ((name(r),r[fields['ISO_A3']])
         for r in sf.iterRecords()
         if r[fields['ISO_A3']] != '-99'),
        iteritems(dict(FR="FRA", NO="NOR"))
    ))

def iso2_to_name():
    """
    Extract a mapping from iso2 country codes to country names
    from the countries dataset.
    """
    sf = shapefile.Reader(toModDir('data/ne_10m_admin_0_countries/ne_10m_admin_0_countries'))
    fields = dict(zip(map(itemgetter(0), sf.fields[1:]), count()))
    def name(rec):
        if rec[fields['ISO_A2']] != '-99':
            return rec[fields['ISO_A2']]
        elif rec[fields['WB_A2']] != '-99':
            return rec[fields['WB_A2']]
        else:
            return rec[fields['ADM0_A3']][:-1]
    return dict((name(r),r[fields['NAME']].decode('utf-8'))
                for r in sf.iterRecords())
