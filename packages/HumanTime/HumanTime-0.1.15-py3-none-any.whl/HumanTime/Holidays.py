
# Copyright (c) 2019-2023 Agalmic Ventures LLC (www.agalmicventures.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#NOTE: Currently this is US and CA, UK holidays only.

import collections
import datetime

from HumanTime.Durations import DAY
from HumanTime.Weekdays import MONDAY, SATURDAY, THURSDAY, dayOfWeekOnOrAfter, dayOfWeekOnOrBefore
from HumanTime.Utility import today

def newYearsDay(year):
	"""
	Returns the date of New Year's Day in a given year.

	:param year: int
	:return: datetime.datetime
	"""
	return datetime.datetime(year, 1, 1)

def martinLutherKingJrDay(year):
	"""
	Returns the date of Martin Luther King Jr. Day in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	if year < 1986:
		return None

	#3rd Monday in Jan
	firstMonday = dayOfWeekOnOrAfter(datetime.datetime(year, 1, 1), MONDAY)
	return firstMonday + datetime.timedelta(days=14)

def presidentsDay(year):
	"""
	Returns the date of Presidents' Day in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	if year < 1971:
		return None

	#3rd Monday in Feb
	firstMonday = dayOfWeekOnOrAfter(datetime.datetime(year, 2, 1), MONDAY)
	return firstMonday + datetime.timedelta(days=14)

def goodFriday(year):
	"""
	Returns the date of Good Friday in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	t0 = easter(year)
	if t0 is None:
		return None

	return t0 - datetime.timedelta(days=2)

def easter(year):
	"""
	Returns the date of Western Easter in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	#Implements Butcher's algorithm: https://en.wikipedia.org/wiki/Computus
	a = year % 19 #https://en.wikipedia.org/wiki/Golden_number_(time)
	b = year // 100
	c = year % 100
	d = b // 4
	e = b % 4
	f = (b + 8) // 25
	g = (b - f + 1) // 3
	h = (19 * a + b - d - g + 15) % 30
	i = c // 4
	k = c % 4
	l = (32 + 2 * e + 2 * i - h - k) % 7
	m = (a + 11 * h + 22 * l) // 451

	month = (h + l - 7 * m + 114) // 31
	day = (h + l - 7 * m + 114) % 31 + 1
	return datetime.datetime(year, month, day)

def easterMonday(year):
	"""
	Returns the date of Easter Monday in a given year (observed in the UK).

	:param year: int
	:return: datetime.datetime or None
	"""
	t0 = easter(year)
	if t0 is None:
		return None

	return t0 + DAY

def ascensionDay(year):
	"""
	Returns the date of Ascension Day (Easter + 39d) in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	t0 = easter(year)
	if t0 is None:
		return None

	return t0 + datetime.timedelta(days=39)

def whitMonday(year):
	"""
	Returns the date of Whit Monday (Easter + 50d) in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	t0 = easter(year)
	if t0 is None:
		return None

	return t0 + datetime.timedelta(days=50)

def victoriaDay(year):
	"""
	Returns the date of Victoria Day (CA) in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	if year < 1901:
		return None
	elif year < 1971:
		return None #TODO: Be more accurate with a table https://en.wikipedia.org/wiki/Victoria_Day
	else:
		#Last Monday before May 25th (so on or before the 24th)
		return dayOfWeekOnOrBefore(datetime.datetime(year, 5, 24), MONDAY)

def memorialDay(year):
	"""
	Returns the date of Labor Day in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	if year < 1868:
		return None
	elif year < 1971:
		return datetime.datetime(year, 5, 30)
	else:
		#Last Monday in May
		return dayOfWeekOnOrBefore(datetime.datetime(year, 5, 31), MONDAY)

def juneteenth(year):
	"""
	Returns the date of Juneteenth in a given year.

	:param year: int
	:return: datetime.datetime
	"""
	#Although it was technically a holiday in 2021, the legislation was signed
	#only days before, so most financial firms and markets were open.
	if year <= 2021:
		return None
	else:
		return datetime.datetime(year, 6, 19)

def canadaDay(year):
	"""
	Returns the date of Canada Day in a given year.

	:param year: int
	:return: datetime.datetime
	"""
	return datetime.datetime(year, 7, 1)

def independenceDay(year):
	"""
	Returns the date of Indepdence Day in a given year.

	:param year: int
	:return: datetime.datetime
	"""
	return datetime.datetime(year, 7, 4)

def swissNationalDay(year):
	"""
	Returns the date of the Swiss National Day (CH) in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	if year < 1899:
		return None

	#1st of Aug
	return datetime.datetime(year, 8, 1)

def civicHoliday(year):
	"""
	Returns the date of the Civic Holiday (CA; known under other various names) in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	if year < 1974:
		return None

	#1st Monday in Aug
	firstMonday = dayOfWeekOnOrAfter(datetime.datetime(year, 8, 1), MONDAY)
	return firstMonday

def laborDay(year):
	"""
	Returns the date of Labor Day in a given year.

	:param year: int
	:return: datetime.datetime
	"""
	#Labor day was first recognized at the federal level in the US,
	#and in Canada, in 1984
	if year < 1894:
		return None

	#1st Monday in Sep
	return dayOfWeekOnOrAfter(datetime.datetime(year, 9, 1), MONDAY)

def nationalDayForTruthAndReconciliation(year):
	"""
	Returns the date of National Day for Truth and Reconciliation (CA) in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	if year < 2021:
		return None

	return datetime.datetime(year, 9, 30)

def columbusDay(year):
	"""
	Returns the date of Columbus Day in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	if year < 1971:
		return None

	#2nd Monday in Oct
	firstMonday = dayOfWeekOnOrAfter(datetime.datetime(year, 10, 1), MONDAY)
	return firstMonday + datetime.timedelta(days=7)

def halloween(year):
	"""
	Returns the date of Halloween in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	return datetime.datetime(year, 10, 31)

def veteransDay(year):
	"""
	Returns the date of Veterans' Day in a given year.

	:param year: int
	:return: datetime.datetime or None
	"""
	if year < 1938:
		return None

	return datetime.datetime(year, 11, 11)

def remembranceDay(year):
	"""
	Returns the date of Remembrance Day (CA) in a given year.

	The main difference between this and Veteran's Day in the US is the starting year.

	:param year: int
	:return: datetime.datetime or None
	"""
	if year < 1931:
		return None

	return datetime.datetime(year, 11, 11)

def thanksgiving(year):
	"""
	Returns the date of Thanksgiving (US) in a given year.

	:param year: int
	:return: datetime.datetime
	"""
	#4th Thurs in Nov
	firstThursday = dayOfWeekOnOrAfter(datetime.datetime(year, 11, 1), THURSDAY)
	return firstThursday + datetime.timedelta(days=21)

def thanksgivingCA(year):
	"""
	Returns the date of Thanksgiving (CA) in a given year.

	:param year: int
	:return: datetime.datetime
	"""
	if year < 1957:
		#TODO: Be accurate before 1957. Requires a table, see https://en.wikipedia.org/wiki/Thanksgiving_(Canada)
		return None

	#2nd Mon in Oct
	firstMonday = dayOfWeekOnOrAfter(datetime.datetime(year, 10, 1), MONDAY)
	return firstMonday + datetime.timedelta(days=7)

def christmas(year):
	"""
	Returns the date of Christmas in a given year.

	:param year: int
	:return: datetime.datetime
	"""
	return datetime.datetime(year, 12, 25)

def boxingDay(year):
	"""
	Returns the Boxing Day in a given year.

	:param year: int
	:return: datetime.datetime
	"""
	return datetime.datetime(year, 12, 26)

def stStephensDay(year):
	"""
	Returns the St. Stephen's Day in a given year.

	:param year: int
	:return: datetime.datetime
	"""
	return datetime.datetime(year, 12, 26)

CA_HOLIDAYS = collections.OrderedDict([
	("New Year's Day", newYearsDay),
	('Good Friday', goodFriday),
	('Victoria Day', victoriaDay),
	('Canada Day', canadaDay),
	('Civic Holiday', civicHoliday), #Not an official holiday but celebrated almost everywhere
	('Labour Day', laborDay),
	('National Day for Truth and Reconciliation', nationalDayForTruthAndReconciliation),
	('Thanksgiving', thanksgivingCA),
	('Remembrance Day', remembranceDay),
	('Christmas', christmas),
	('Boxing Day', boxingDay),
])

#From https://en.wikipedia.org/wiki/Public_holidays_in_Switzerland
CH_HOLIDAYS = collections.OrderedDict([
	("New Year's Day", newYearsDay),
	#TODO: Berchtold's Day?
	('Good Friday', goodFriday),
	('Easter Monday', easterMonday),
	('Ascension Day', ascensionDay),
	('Whit Monday', whitMonday),
	#TODO: Corpus Christi?
	#TODO: Assumption?
	('Swiss National Day', swissNationalDay),
	('Christmas', christmas),
	("St. Stephen's Day", stStephensDay),
])

UK_HOLIDAYS = collections.OrderedDict([
	("New Year's Day", newYearsDay),
	('Good Friday', goodFriday),
	('Easter Monday', easterMonday),
	('Christmas', christmas),
	('Boxing Day', boxingDay),
])

US_HOLIDAYS = collections.OrderedDict([
	("New Year's Day", newYearsDay),
	('Martin Luther King Jr. Day', martinLutherKingJrDay),
	("Presidents' Day", presidentsDay),
	('Good Friday', goodFriday),
	('Memorial Day', memorialDay),
	('Juneteenth National Independence Day', juneteenth),
	('Independence Day', independenceDay),
	('Labor Day', laborDay),
	('Columbus Day', columbusDay),
	("Veterans' Day", veteransDay),
	('Thanksgiving', thanksgiving),
	('Christmas', christmas),
])

COUNTRY_TO_HOLIDAYS = {
	'CA': CA_HOLIDAYS,
	'UK': UK_HOLIDAYS,
	'US': US_HOLIDAYS,
}

#The default holiday calendar may be adjusted by altering this value
DEFAULT_HOLIDAYS = US_HOLIDAYS

def holidayCalendar(fromYear, toYear, holidays=DEFAULT_HOLIDAYS, observed=False):
	"""
	Returns a business holiday calendar from one year to another (inclusive).

	:param fromYear: int
	:param toYear: int
	:param holidays: collections.OrderedDict of name to holiday function
	:param observed: bool Calculate observed holidays for those that fall on weekends
	:return: datetime.datetime
	"""
	calendar = []
	for year in range(fromYear, toYear + 1):
		for name in holidays:
			holiday = holidays[name]
			date = holiday(year)
			if date is None:
				continue

			calendar.append( (date, name) )

	return applyObservanceRules(calendar) if observed else calendar

#TODO: other observance rules
def applyObservanceRules(calendar, suffix=' (Observed)'):
	"""
	Apply observance rules to a calendar of (date, name) pairs.

	This allows for neighboring holidays such as Christmas and Boxing Day (UK).

	:param calendar: [ (datetime.date, str) ]
	:return: [ (datetime.date, str) ]
	"""
	newCalendar = []
	swap = None
	for n, (date, name) in enumerate(calendar):
		if date.weekday() >= SATURDAY:
			#Always add a suffix
			name += suffix

			#Subtract a day on Saturday, add a day on Sunday
			if date.weekday() == SATURDAY:
				date -= DAY
				#Unless Friday is already a holiday
				if calendar[n - 1][0] == date:
					#Then move to Monday
					#TODO: support 3 holidays in a row?
					date += 3 * DAY
			else:
				date += DAY
				#Unless the next day is also a holiday, in which case add 2
				#This also means this event is now after the next
				if len(calendar) > n and calendar[n + 1][0] == date:
					date += DAY
					swap = (date, name)
					continue
		newCalendar.append( (date, name) )
		if swap:
			newCalendar.append(swap)
			swap = None
	return newCalendar

#The holidays used to compute business days
HOLIDAY_CALENDAR = holidayCalendar(1900, 2100)
HOLIDAYS = {h[0] for h in HOLIDAY_CALENDAR}

def businessDayOnOrAfter(t, holidays=None):
	"""
	Returns the first business day on or after a given time.

	:param t: datetime.datetime
	:return: datetime.datetime
	"""
	if holidays is None:
		holidays = HOLIDAYS

	t = today(t)
	while t.weekday() >= SATURDAY or t in holidays:
		t += datetime.timedelta(days=1)
	return t

def businessDayOnOrBefore(t, holidays=None):
	"""
	Returns the first business day on or before a given time.

	:param t: datetime.datetime
	:return: datetime.datetime
	"""
	if holidays is None:
		holidays = HOLIDAYS

	t = today(t)
	while t.weekday() >= SATURDAY or t in holidays:
		t -= datetime.timedelta(days=1)
	return t
