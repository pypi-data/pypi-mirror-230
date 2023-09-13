#  Copyright (c) 2021 <Florian Alu - alu@prolibre.com - https://www.prolibre.com>
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import math

import arrow
from dateutil.rrule import WEEKLY, DAILY, MO, TU, WE, TH, FR, rrule


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def weeks_between(start_date, end_date):
    weeks = rrule(WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()


def week_span_from_date(day):
    first_last_day_week = arrow.get(day).span('week')
    # Business days list
    week_dates = [r for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                   dtstart=first_last_day_week[0],
                                   until=first_last_day_week[-1])]
    return week_dates


def has_view_stats(request):
    valid = False
    if request.user.groups.filter(name='Admin').exists():
        valid = True
    elif request.user.has_perm('nobinobi_daily_follow_up.view_stats'):
        valid = True
    elif request.user.is_superuser:
        valid = True
    return valid
