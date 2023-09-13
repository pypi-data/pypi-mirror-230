# -*- coding: utf-8 -*-

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

from django.urls import path, include, register_converter
from nobinobi_core.functions import FourDigitConverter, TwoDigitConverter
from nobinobi_daily_follow_up.utils import IsoDateConverter

from nobinobi_stats import views

app_name = 'nobinobi_stats'

register_converter(FourDigitConverter, 'yyyy')
register_converter(TwoDigitConverter, 'mmdd')
register_converter(IsoDateConverter, 'isodate')

urlpatterns = [
    path("stats/", include([
        path("attendance/", include([
            path("period/", include([
                path("~choice/", view=views.ChoiceAttendancePeriod.as_view(), name='choice_attendance_period'),
                path("<isodate:from_date>/<isodate:end_date>/", view=views.AttendancePeriod.as_view(),
                     name='attendance_period'),
            ])),
            path("calendar/", include([
                path("~choice/", view=views.ChoiceAttendanceCalendar.as_view(), name='choice_attendance_calendar'),
                path("<isodate:date>/", view=views.AttendanceCalendar.as_view(), name='attendance_calendar'),
            ])),
            path("child/", include([
                path("~choice/", view=views.ChoiceAttendanceChild.as_view(), name='choice_attendance_child'),
                path(
                    "<isodate:from_date>/<isodate:end_date>/<uuid:child>/",
                    view=views.AttendanceChild.as_view(),
                    name='attendance_child'
                ),
            ])),
        ])),
        path("occupancy/", include([
            path("period/", include([
                path("~choice/", view=views.ChoiceOccupancyPeriod.as_view(), name='choice_occupancy_period'),
                path("<isodate:from_date>/<isodate:end_date>/", view=views.OccupancyPeriod.as_view(),
                     name='occupancy_period'),
            ])),
        ])),
    ])),
]
