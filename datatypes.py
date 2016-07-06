# For reference, the bultin types
# Courtesty libpqtypes http://libpqtypes.esilo.com/browse_source.html?file=libpqtypes-int.h
#  Numerics types 
# INT2OID            21 Y
# INT4OID            23 Y
# INT8OID            20 Y
# FLOAT4OID         700 Y
# FLOAT8OID         701 Y
# NUMERICOID       1700 Needs doing
#  Geo types
# POINTOID          600 N
# LSEGOID           601 N
# PATHOID           602 N
# BOXOID            603 N
# POLYGONOID        604 N
# LINEOID           628 N 
# CIRCLEOID         718 N
#  Network types
# INETOID           869 ?
# CIDROID           650 ?
# MACADDROID        829 ?
#  Variable length types 
# BPCHAROID        1042
# VARCHAROID       1043 Y
# NAMEOID            19 ?
# TEXTOID            25 Y
# ZPBITOID         1560 /* not supported yet */
# VARBITOID        1562 /* not supported yet */
# BYTEAOID           17 ?
#  Date and time types 
# DATEOID          1082 Y
# TIMEOID          1083 Y
# TIMETZOID        1266 ?
# TIMESTAMPOID     1114 Y
# TIMESTAMPTZOID   1184 Y
# INTERVALOID      1186 Y
#  Misc types 
# CHAROID            18 Needs doing! 
# BOOLOID            16 Y
# OIDOID             26 ? 
# CASHOID           790 ?
# RECORDOID        2249 ?
# UUIDOID          2950 ?

import datetime
import abc
import ctypes
import collections

try:
    import pytz
except ImportError:
    pytz = None

import errors

TYPE_MAP = {}
OID_MAP = {}


class AutoRegisteringPQType(abc.ABCMeta):

    def __new__(mcs, name, bases, dict):
        cls = super(AutoRegisteringPQType, mcs).__new__(mcs, name, bases, dict)
        if cls.auto_register:
            for c in cls.python_types:
                register_adapter(c, cls.to_postgres)
            register_type(cls)
        return cls


def register_adapter(cls, adapter):
    TYPE_MAP[cls] = adapter

def new_type(oids, name, adapter):
    return type(name, (_PyPQDataType,), {'to_python': adapter, 'oids': oids})

def register_type(cls):
    for oid in cls.oids:
        OID_MAP[oid] = cls


class _PyPQDataType(object):
    oids = ()
    python_types = ()

    @classmethod
    def to_python(cls, value):
        return value

    @classmethod
    def to_postgres(cls, value):
        return str(value), cls._get_oid(value)

    @classmethod
    def _get_oid(cls, value):
        if cls.oids:
            return cls.oids[0]
        else:
            return 0


class PyPQDataType(_PyPQDataType):

    __metaclass__ = AutoRegisteringPQType

    auto_register = True


class Integer(PyPQDataType):

    oids = (20, 21, 23)

    python_types = (int, )

    @classmethod
    def _get_oid(cls, value):
        return 0

    @classmethod
    def to_python(cls, value):
        return int(value)

    
class ROWID(Integer):

    oids = (26, )
    python_types = ()


class Float(PyPQDataType):

    oids = (700, 701)

    python_types = (float, )

    @classmethod
    def to_python(cls, value):
        return float(value)


class String(PyPQDataType):

    oids = (25, 1043)

    python_types = (str, )

    @classmethod
    def _get_oid(cls, value):
        return 0

    
class Unicode(String):

    python_types = (unicode, )

    @classmethod
    def to_postgres(cls, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return value, 25


class AutoUnicode(Unicode):

    auto_register = False

    @classmethod
    def to_python(cls, value):
        return value.decode('utf-8')

    
class Date(PyPQDataType):

    oids = (1082,)

    python_types = (datetime.date, )

    @classmethod
    def to_python(cls, value):
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()


class DateTime(PyPQDataType):

    oids = (1114, )

    python_types = (datetime.datetime, )

    @classmethod
    def to_python(cls, value):
        format = '%Y-%m-%d %H:%M:%S'
        if '.' in value:
            format += '.%f'
        return datetime.datetime.strptime(value, format)


class DateTimeTz(PyPQDataType):

    oids = (1184,)

    @classmethod
    def to_python(cls, value):
        # TODO: Implement timezone handling
        value = value.split('+')[0]
        return DateTime.to_python(value)

    
class Time(PyPQDataType):

    oids = (1083,)

    python_types = (datetime.time,)

    @classmethod
    def to_python(cls, value):
        h,m,s,ms = 0,0,0,0
        if '.' in value:
            value, ms = value.split('.')
            ms = int(ms)

        if ':' in value:
            h,m,s = map(int, value.split(':'))
        return datetime.time(h,m,s,ms)


class PgInterval(datetime.timedelta):

    def __init__(self, *args, **kwargs):
        super(PgInterval, self).__init__(*args, **kwargs)
        self.original_interval = None
        

# Converting into python Timedelta destroys some information
# so we use PgInterval instead, which saves the original info
class Interval(PyPQDataType):

    oids = (1186,)

    python_types = (datetime.timedelta, PgInterval)

    @classmethod
    def to_postgres(cls, value):
        if isinstance(value, PgInterval):
            return value.original_interval, 1186
        return '%s days %s seconds %s microseconds' % \
               (value.days, value.seconds, value.microseconds), 1186

    @classmethod
    def to_python(cls, value):
        years, months, days = 0,0,0

        # This will be stored in the resulting PgInterval object
        original_value = value

        # example value: '10 years 10 mons 15 days 10:10:10'
        if 'year' in value:
            years, value = value.split(' year')
            years = int(years)
            try:
                value = value.split(' ', 1)[1]
            except IndexError:
                value = ''

        if 'mon' in value:
            months, value = value.split(' mon')
            months = int(months)
            try:
                value = value.split(' ', 1)[1]
            except IndexError:
                value = ''

        if 'day' in value:
            days, value = value.split(' day')
            days = int(days)
            try:
                value = value.split(' ', 1)[1]
            except IndexError:
                value = ''

        time = Time.to_python(value)

        interval = PgInterval(365 * years + 31 * months + days, hours=time.hour,
                    minutes=time.minute, seconds=time.second,
                    microseconds=time.microsecond)
        interval.original_interval = original_value
        return interval

    
class Boolean(PyPQDataType):

    python_types = (bool, ) 

    oids = (16,)

    @classmethod
    def to_python(cls, value):
        value = value.lower()
        if value == 't':
            return True
        elif value == 'f':
            return False
        raise errors.Error('Cannot convert "%s" to bool' % value)

    
def to_postgres(value):
    try:
        adapter = TYPE_MAP[type(value)]
    except KeyError:
        raise errors.NotSupportedError('Cannot cast %s to postgres type' % type(value))
    return adapter(value)

adapt = to_postgres


def to_python(value, oid=None):
    cls = get_type_by_oid(oid)
    return cls.to_python(value)


def get_type_by_oid(oid, default=String):
    return OID_MAP.get(oid, default)
