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

import datetime
from statistics import mean

import arrow
from datetimerange import DateTimeRange
from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import make_naive
from django.utils.translation import gettext as _
from django.views.generic import FormView, TemplateView
from nobinobi_child.models import Classroom, Period, WEEKDAY_CHOICES, Child, AbsenceGroup, ChildToPeriod, Absence
from nobinobi_core.models import Holiday, OrganisationClosure
from nobinobi_daily_follow_up.models import Presence, DailyFollowUp

from nobinobi_stats import utils
from nobinobi_stats.forms import ChoiceAttendancePeriodForm, ChoiceAttendanceCalendarForm, ChoiceOccupancyPeriodForm, \
    ChoiceAttendanceChildForm
from nobinobi_stats.utils import week_span_from_date


class ChoiceAttendancePeriod(LoginRequiredMixin, FormView):
    """ Vue de choix pour aller sur la page de attedance"""
    form_class = ChoiceAttendancePeriodForm
    template_name = "nobinobi_stats/attendance/choice_attendance_period.html"

    def __init__(self):
        super().__init__()
        self.from_date = None
        self.end_date = None

    def get_context_data(self, **kwargs):
        context = super(ChoiceAttendancePeriod, self).get_context_data(**kwargs)
        context["title"] = _("Choice attendance period")
        return context

    def form_valid(self, form):
        self.from_date = form.cleaned_data["from_date"]
        self.end_date = form.cleaned_data["end_date"]
        return super(ChoiceAttendancePeriod, self).form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_stats:attendance_period",
                       kwargs={"from_date": self.from_date, "end_date": self.end_date})


class AttendancePeriod(LoginRequiredMixin, TemplateView):
    """ Vue de choix pour aller sur la page de attedance"""
    template_name = "nobinobi_stats/attendance/attendance_period.html"

    def get_context_data(self, **kwargs):
        context = super(AttendancePeriod, self).get_context_data(**kwargs)
        context["title"] = _("Attendance period")
        context["from_date"] = self.kwargs.get("from_date")
        context["end_date"] = self.kwargs.get("end_date")
        dict_table = self.get_dict_table()
        dict_table_filled = self.fill_dict_table(dict_table)
        context["dict_table"] = dict_table_filled
        return context

    @staticmethod
    def get_dict_table():
        # We create the basic dictionary
        dict_table = {
            "classroom": {},
            "total": {
                "period": {},
                "average": {
                    "total": 0.0,
                    "total_list": [],
                    "percentage": 0.0
                },
                "classroom": 0
            }
        }
        # We fill the dictionary with the classrooms
        # We get the classrooms back.
        classrooms = Classroom.objects.all().order_by("order").values("id", "name", "capacity")
        # We get the periods back
        periods = Period.objects.all().order_by("order").values("id", "name", "weekday")
        # We fill the classrooms in the dictionary
        for classroom in classrooms:
            dict_table['classroom'][classroom["id"]] = {
                "name": classroom["name"],
                "capacity": classroom["capacity"],
                "period": {},
                "average": {
                    "total": 0,
                    "percentage": 0,
                    "average": [],
                }
            }
            # We fill the periods in the dictionary
            for period in periods:
                dict_table['classroom'][classroom["id"]]['period'][period["id"]] = {
                    "date": {},
                    # "total": 0.0,
                    "average": 0,
                    "average_list": [],
                    "percentage": 0.0
                }

        # the dictionary is filled with the periods for the totals
        for period in periods:
            dict_table["total"]["period"][period["id"]] = {
                "name": WEEKDAY_CHOICES[period["weekday"]] + " " + period["name"],
                "percentage": 0.0,
                "average": 0.0,
                "average_list": []
                # "total": 0.0
            }

        return dict_table

    def fill_dict_table(self, dict_table):
        """ Here we will fill in the dictionary """
        from_date = self.kwargs.get("from_date")
        end_date = self.kwargs.get("end_date")

        # holiday
        holidays = Holiday.objects.filter(date__gte=from_date, date__lte=end_date).values_list("date", flat=True)

        # Business days list
        range_dates = [r.date() for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                               dtstart=from_date,
                                               until=end_date) if r.date() not in holidays]

        # get presence
        presences = Presence.objects.filter(date__gte=range_dates[0], date__lte=range_dates[-1],
                                            arrival_time__isnull=False, departure_time__isnull=False)
        periods = Period.objects.all().order_by("order").values("id", "weekday", "start_time", "end_time")

        for presence in presences:
            arrival_time = presence.arrival_time
            departure_time = presence.departure_time
            start_date = datetime.datetime.combine(presence.date, arrival_time)
            end_date = datetime.datetime.combine(presence.date, departure_time)
            if end_date >= start_date:

                presence_time_range = DateTimeRange(start_date, end_date)

                for period in periods:
                    if period["weekday"] == presence.date.isoweekday():
                        start_date_period = datetime.datetime.combine(presence.date, period["start_time"])
                        end_date_period = datetime.datetime.combine(presence.date, period["end_time"])
                        period_time_range = DateTimeRange(start_date_period, end_date_period)
                        if presence_time_range.is_intersection(period_time_range):
                            if presence.date not in \
                                dict_table["classroom"][presence.classroom_id]["period"][period["id"]]["date"]:
                                dict_table["classroom"][presence.classroom_id]["period"][period["id"]]["date"][
                                    presence.date] = {"total": 0}

                            dict_table["classroom"][presence.classroom_id]["period"][period["id"]]["date"][
                                presence.date]["total"] += 1
        # periods

        # calcul percentage
        # We get the classrooms back.
        classrooms = Classroom.objects.all().order_by("order").values("id", "capacity")
        for classroom in classrooms.iterator():
            # fill list with total by period
            for period_id, period_value in dict_table["classroom"][classroom["id"]]["period"].items():
                for tot in period_value["date"].values():
                    dict_table["classroom"][classroom["id"]]["period"][period_id]["average_list"].append(tot["total"])
                # set average for period
                if len(dict_table["classroom"][classroom["id"]]["period"][period_id]["average_list"]) >= 1:
                    dict_table["classroom"][classroom["id"]]["period"][period_id]["average"] = utils.round_up(mean(
                        dict_table["classroom"][classroom["id"]]["period"][period_id]["average_list"]), 2)
                dict_table["classroom"][classroom["id"]]["period"][period_id]["percentage"] = utils.round_up(
                    utils.percentage(dict_table["classroom"][classroom["id"]]["period"][period_id]["average"],
                                     dict_table['classroom'][classroom["id"]]["capacity"]))

                dict_table["classroom"][classroom["id"]]["average"]["average"].append(
                    dict_table["classroom"][classroom["id"]]["period"][period_id]["average"])
                # on ajoute au total col
                dict_table["total"]["period"][period_id]["average_list"].append(
                    dict_table["classroom"][classroom["id"]]["period"][period_id]["average"])
                dict_table["total"]["period"][period_id]["average"] = utils.round_up(sum(
                    dict_table["total"]["period"][period_id]["average_list"]), 2)
            # set average for row
            dict_table["classroom"][classroom["id"]]["average"]["total"] = utils.round_up(mean(
                dict_table["classroom"][classroom["id"]]["average"]["average"]))

            # add total list
            dict_table["total"]["average"]["total_list"].append(
                dict_table["classroom"][classroom["id"]]["average"]["total"])

            dict_table["total"]["classroom"] += classroom["capacity"]
            percentage = utils.round_up(
                utils.percentage(dict_table["classroom"][classroom["id"]]["average"]["total"], classroom["capacity"]),
                0)
            dict_table["classroom"][classroom["id"]]["average"]["percentage"] = percentage

            # total dict
            dict_table["total"]["average"]["total"] = utils.round_up(sum(dict_table["total"]["average"]["total_list"]),
                                                                     1)
        percentage = utils.round_up(
            utils.percentage(dict_table["total"]["average"]["total"], dict_table["total"]["classroom"]), 1)
        dict_table["total"]["average"]["percentage"] = percentage

        for period_id, period_value in dict_table["total"]["period"].items():
            percentage = utils.round_up(
                utils.percentage(
                    dict_table["total"]["period"][period_id]["average"], dict_table["total"]["classroom"]
                ),
                1
            )
            dict_table["total"]["period"][period_id]["percentage"] = percentage

        return dict_table


class ChoiceAttendanceCalendar(LoginRequiredMixin, FormView):
    """ Vue de choix pour aller sur la page de attedance"""
    form_class = ChoiceAttendanceCalendarForm
    template_name = "nobinobi_stats/attendance/choice_attendance_calendar.html"

    def get_context_data(self, **kwargs):
        context = super(ChoiceAttendanceCalendar, self).get_context_data(**kwargs)
        context["title"] = _("Choice attendance calendar")
        return context

    def form_valid(self, form):
        self.date = form.cleaned_data["date"]
        return super(ChoiceAttendanceCalendar, self).form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_stats:attendance_calendar",
                       kwargs={"date": self.date})


class AttendanceCalendar(LoginRequiredMixin, TemplateView):
    """ Vue de choix pour aller sur la page de attedance"""
    template_name = "nobinobi_stats/attendance/attendance_calendar.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.date = None
        self.dates_range = None
        self.classrooms = None
        self.day_list = None
        self.classroom_dict = None
        self.total_dict = None

    def get_context_data(self, **kwargs):
        context = super(AttendanceCalendar, self).get_context_data(**kwargs)
        context["title"] = _("Attendance Calendar")
        self.date = self.kwargs.get("date")
        context['date'] = self.date
        self.dates_range = week_span_from_date(self.date)
        context['month_before'] = arrow.get(self.dates_range[0]).shift(months=-1)
        context['week_before'] = arrow.get(self.dates_range[0]).shift(weeks=-1)
        context['week_after'] = arrow.get(self.dates_range[-1]).shift(weeks=+1)
        context['month_after'] = arrow.get(self.dates_range[-1]).shift(months=+1)
        self.classrooms = Classroom.objects.all().values("id", "name", "capacity")
        self.day_list = self.create_day_list(self.dates_range)
        self.total_dict = self.create_total_dict()
        self.classroom_dict = self.create_classroom_dict()
        self.classroom_dict, self.total_dict = self.fill_data()
        context["day_list"] = self.day_list
        context["classroom_dict"] = self.classroom_dict
        context["total_dict"] = self.total_dict

        return context

    @staticmethod
    def create_day_list(dates_range):
        day_list = []
        for date in dates_range:
            day_list.append(date)

        return day_list

    def create_total_dict(self):
        total_dict = {
            "total": {
                "name": _("Total EVE"),
                "capacity": 0,
                "days": {}
            },
            "average": {
                "name": _("Total of the day"),
                "days": {}
            },
        }

        for day in self.dates_range:
            total_dict["total"]["days"][day.isoweekday()] = {
                "total": 0,
                "percentage": 0
            }
        return total_dict

    def create_classroom_dict(self):
        classroom_dict = {}

        for classroom in self.classrooms:
            # on ajoute le total au total dict
            self.total_dict["total"]["capacity"] += classroom['capacity']
            classroom_dict[classroom['id']] = {
                "name": classroom['name'],
                "capacity": classroom['capacity'],
                "days": {}
            }
            for day in self.dates_range:
                classroom_dict[classroom['id']]["days"][day.isoweekday()] = {
                    "total": 0,
                    "percentage": 0,
                    "average": 0,
                    "average_list": []
                }
        return classroom_dict

    def fill_data(self):
        classroom_dict = self.classroom_dict
        total_dict = self.total_dict

        # fill data
        presences = Presence.objects.filter(date__in=self.dates_range, arrival_time__isnull=False)
        for presence in presences:
            classroom = presence.classroom
            date = presence.date
            # on ajoute au total de classe
            classroom_dict[classroom.id]["days"][date.isoweekday()]["total"] += 1
            # et au total du jour
            total_dict["total"]["days"][date.isoweekday()]["total"] += 1

            # on ajoute au average
            classroom_dict[classroom.id]["days"][date.isoweekday()]["average"] += 1
            classroom_dict[classroom.id]["days"][date.isoweekday()]["average_list"].append(presence)

            # on calcul les average et pourcentage
            #
            percentage = utils.round_up(
                utils.percentage(classroom_dict[classroom.id]["days"][date.isoweekday()]["average"],
                                 classroom_dict[classroom.id]["capacity"]), 1)
            classroom_dict[classroom.id]["days"][date.isoweekday()]["percentage"] = percentage

        # et au total average
        for day in self.dates_range:
            #  on calcul le percentage total
            percentage = utils.round_up(
                utils.percentage(total_dict["total"]["days"][day.isoweekday()]["total"],
                                 total_dict["total"]["capacity"]), 1)
            total_dict["total"]["days"][day.isoweekday()]["percentage"] = percentage

        return classroom_dict, total_dict


class ChoiceAttendanceChild(LoginRequiredMixin, FormView):
    """ Vue de choix pour aller sur la page d'attendance"""
    form_class = ChoiceAttendanceChildForm
    template_name = "nobinobi_stats/attendance/choice_attendance_child.html"

    def form_valid(self, form):
        self.child = form.cleaned_data["child"]
        self.from_date = form.cleaned_data["from_date"]
        self.end_date = form.cleaned_data["end_date"]
        return super(ChoiceAttendanceChild, self).form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_stats:attendance_child",
                       kwargs={"child": self.child.id, "from_date": self.from_date, "end_date": self.end_date})

    def get_context_data(self, **kwargs):
        context = super(ChoiceAttendanceChild, self).get_context_data(**kwargs)
        context["title"] = _("Choice attendance child")
        return context


class AttendanceChild(LoginRequiredMixin, TemplateView):
    """ Vue de choix pour aller sur la page de attedance"""
    template_name = "nobinobi_stats/attendance/attendance_child.html"

    def get_context_data(self, **kwargs):
        context = super(AttendanceChild, self).get_context_data(**kwargs)
        context["title"] = _("Attendance child")
        child = get_object_or_404(Child, id=self.kwargs.get("child"))
        context["child"] = child
        from_date = self.kwargs.get("from_date")
        end_date = self.kwargs.get("end_date")
        dates_range = [r.isoweekday() for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                                     dtstart=from_date,
                                                     until=end_date)]
        dict_table = self.get_dict_table(child, dates_range)
        filled_dict_table = self.fill_dict_table(dict_table, child, from_date, end_date, dates_range)
        context["dict_table"] = filled_dict_table
        return context

    def get_dict_table(self, child, dates_range):
        # create dictionary
        dict_table = {
            child.id: {
                "period": {
                    "planned": {
                        "total": 0.0,
                    },
                    "present": {
                        "total": 0.0,
                    },
                    "troubleshooting": {
                        "total": 0.0,
                        "percentage": 0.0,
                    },
                    "percentage": 0.0,
                },
                "absence": {
                    "group": {},
                    "total": 0.0,
                    "percentage": 0.0
                }
            }
        }

        # fill with period
        periods = Period.objects.filter(weekday__in=dates_range).order_by("order").values("id", "weekday",
                                                                                          "name",
                                                                                          "start_time",
                                                                                          "end_time")

        for period in periods:
            # for planned
            dict_table[child.id]["period"]["planned"][period["id"]] = {
                "name": "{} {}".format(WEEKDAY_CHOICES[period["weekday"]], period["name"]),
                "total": 0.0,
                "total_list": [],
            }
            # for present
            dict_table[child.id]["period"]["present"][period["id"]] = {
                "name": "{} {}".format(WEEKDAY_CHOICES[period["weekday"]], period["name"]),
                "total": 0.0,
                "total_list": [],
            }
            # for troubleshooting
            dict_table[child.id]["period"]["troubleshooting"][period["id"]] = {
                "name": "{} {}".format(WEEKDAY_CHOICES[period["weekday"]], period["name"]),
                "total": 0.0,
                "total_list": [],
            }

        # get group absences
        # and finish create dict with groups for
        groups_absence = AbsenceGroup.objects.all().values("id", "name")
        for group_absence in groups_absence:
            dict_table[child.id]["absence"]["group"][slugify(group_absence["name"])] = {
                "total": 0.0,
                "total_list": [],
                "percentage": 0.0,
            }

        return dict_table

    def fill_dict_table(self, dict_table, child, from_date, end_date, dates_range):
        # fill planned period
        periods_planned = ChildToPeriod.objects.select_related("period").filter(child_id=child.id,
                                                                                start_date__lte=end_date,
                                                                                end_date__gte=from_date,
                                                                                period__weekday__in=dates_range)

        number_of_weeks = utils.weeks_between(from_date, end_date)
        for nbr in range(1, number_of_weeks + 1):
            for period_planned in periods_planned:
                dict_table[child.id]["period"]["planned"][period_planned.period_id]["total"] += 1
                dict_table[child.id]["period"]["planned"][period_planned.period_id]["total_list"].append(
                    period_planned
                )
                dict_table[child.id]["period"]["planned"]["total"] += 1

        # fill present period
        presences = Presence.objects.filter(child_id=child.id, date__gte=from_date, date__lte=end_date,
                                            arrival_time__isnull=False, departure_time__isnull=False)
        periods = Period.objects.all().order_by("order").values("id", "weekday", "start_time", "end_time")
        troubleshooting = []

        for presence in presences:
            arrival_time = presence.arrival_time
            departure_time = presence.departure_time
            start_date_presence = datetime.datetime.combine(presence.date, arrival_time)
            end_date_presence = datetime.datetime.combine(presence.date, departure_time)
            if end_date_presence >= start_date_presence:

                presence_time_range = DateTimeRange(start_date_presence, end_date_presence)

                for period in periods:
                    if period["weekday"] == presence.date.isoweekday():
                        start_date_period = datetime.datetime.combine(presence.date, period["start_time"])
                        end_date_period = datetime.datetime.combine(presence.date, period["end_time"])
                        period_time_range = DateTimeRange(start_date_period, end_date_period)
                        if presence_time_range.is_intersection(period_time_range):
                            dict_table[child.id]["period"]["present"][period["id"]]["total"] += 1
                            dict_table[child.id]["period"]["present"][period["id"]]["total_list"].append(presence)
                            dict_table[child.id]["period"]["present"]["total"] += 1

            # troubleshooting
            try:
                presence.dailyfollowup.troubleshooting
                # for period in presence.dailyfollowup.troubleshooting.periods.filter(period__weekday=weekday):
                if presence not in troubleshooting:
                    troubleshooting.append(presence)
            except DailyFollowUp.troubleshooting.RelatedObjectDoesNotExist:
                pass

        for ts in troubleshooting:
            child_period = ts.dailyfollowup.troubleshooting.periods.all()
            for period in child_period:
                # create time range of period
                start_date = datetime.datetime.combine(ts.date, period.start_time)
                end_date = datetime.datetime.combine(ts.date, period.end_time)
                time_range_period = DateTimeRange(start_date, end_date)
                if datetime.datetime.combine(ts.date, ts.arrival_time) in time_range_period:
                    # set information in dict_children
                    dict_table[child.id]["period"]["troubleshooting"][period.id]["total"] += 1
                    dict_table[child.id]["period"]["troubleshooting"][period.id]["total_list"].append(ts)
                    dict_table[child.id]["period"]["troubleshooting"]['total'] += 1

        # percentage entre planned et present
        total_planned = dict_table[child.id]["period"]["planned"]["total"]
        total_present = dict_table[child.id]["period"]["present"]["total"]
        dict_table[child.id]["period"]["percentage"] = utils.round_up(
            utils.percentage(total_present, total_planned),
            1
        )

        # absences
        absences = Absence.objects.filter(child=child, end_date__gte=from_date,
                                          start_date__lte=end_date)
        absences_list = []
        for absence in absences:
            absences_list.append(absence)

        for absence in absences_list:
            # absence.start_date = absence.start_date.to("")
            # create range absence date_received
            time_range_absence = DateTimeRange(make_naive(absence.start_date),
                                               make_naive(absence.end_date))
            # get period from day child
            for date_absence in time_range_absence.range(datetime.timedelta(days=1)):
                periods_child = absence.child.periods.filter(weekday=date_absence.isoweekday())
                for period in periods_child:
                    # create time range of period
                    start_date = datetime.datetime.combine(date_absence, period.start_time)
                    end_date = datetime.datetime.combine(date_absence, period.end_time)
                    time_range_period = DateTimeRange(start_date, end_date)

                    # if time range period is in time range absence
                    if time_range_absence.is_intersection(time_range_period):
                        # for date_received in time_range_absence.range(datetime.timedelta(days=1)):
                        # set information in dict
                        if date_absence.isoweekday() not in [6, 7]:
                            dict_table[child.id]["absence"]["group"][slugify(absence.type.group.name)]["total"] += 1
                            dict_table[child.id]["absence"]["group"][slugify(absence.type.group.name)][
                                "total_list"].append(absence)
                            dict_table[child.id]["absence"]["group"][slugify(absence.type.group.name)][
                                "percentage"] = utils.round_up(
                                utils.percentage(
                                    dict_table[child.id]["absence"]["group"][slugify(absence.type.group.name)][
                                        "total"],
                                    total_planned
                                )
                            )
                            dict_table[child.id]["absence"]["total"] += 1

        # calcul pourcentage de absence total
        dict_table[child.id]["absence"]["percentage"] = utils.round_up(utils.percentage(
            dict_table[child.id]["absence"]["total"], total_planned))

        # calcul pourcentage de depanage total
        dict_table[child.id]["period"]["troubleshooting"]["percentage"] = utils.round_up(utils.percentage(
            dict_table[child.id]["period"]["troubleshooting"]["total"], total_planned))

        # troubleshooting
        return dict_table


class ChoiceOccupancyPeriod(LoginRequiredMixin, FormView):
    """ Vue de choix pour aller sur la page de attedance"""
    form_class = ChoiceOccupancyPeriodForm
    template_name = "nobinobi_stats/occupancy/choice_occupancy_period.html"

    def __init__(self):
        super().__init__()
        self.from_date = None
        self.end_date = None

    def form_valid(self, form):
        self.from_date = form.cleaned_data["from_date"]
        self.end_date = form.cleaned_data["end_date"]
        return super(ChoiceOccupancyPeriod, self).form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_stats:occupancy_period",
                       kwargs={"from_date": self.from_date, "end_date": self.end_date})

    def get_context_data(self, **kwargs):
        context = super(ChoiceOccupancyPeriod, self).get_context_data(**kwargs)
        context["title"] = _("Choice occupancy calendar")
        return context


class OccupancyPeriod(LoginRequiredMixin, TemplateView):
    """ Vue de choix pour aller sur la page de attedance"""
    template_name = "nobinobi_stats/occupancy/occupancy_period.html"

    def __init__(self, *args, **kwargs):
        self.dayoff = self.get_dayoff_day()
        super(OccupancyPeriod, self).__init__(*args, **kwargs)

    @staticmethod
    def get_ocs_day(end_date, from_date):
        # Organisation Closure
        ocs = OrganisationClosure.objects.filter(from_date__lte=end_date, end_date__gte=from_date)
        ocs_list_day = []
        for oc in ocs:
            oc_list = [r.date() for r in
                       rrule(DAILY, byweekday=(MO, TU, WE, TH, FR), dtstart=oc.from_date, until=oc.end_date)]
            for i in oc_list:
                ocs_list_day.append(i)
        return ocs_list_day

    @staticmethod
    def get_holiday_day(end_date, from_date):
        # holiday
        return Holiday.objects.filter(date__gte=from_date, date__lte=end_date).values_list("date", flat=True)

    @staticmethod
    def get_dayoff_day():
        # dayoff
        return {c.id: list(c.classroomdayoff_set.all().values_list("weekday", flat=True)) for c in
                Classroom.objects.all().prefetch_related("classroomdayoff_set")}

    def get_context_data(self, **kwargs):
        context = super(OccupancyPeriod, self).get_context_data(**kwargs)
        context["title"] = _("Occupancy period")
        context["from_date"] = self.kwargs.get("from_date")
        context["end_date"] = self.kwargs.get("end_date")
        holidays = self.get_holiday_day(context["from_date"], context["end_date"])
        ocs_list_day = self.get_ocs_day(context["end_date"], context["from_date"])
        dates_range_weekday = [r.isoweekday() for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                                             dtstart=context["from_date"],
                                                             until=context["end_date"]) if
                               r.date() not in holidays and r.date() not in ocs_list_day]
        dict_table = self.get_dict_table(dates_range_weekday)
        dict_table_filled = self.fill_dict_table(dict_table)
        context["dict_table"] = dict_table_filled
        return context

    @staticmethod
    def get_dict_table(dates_range_weekday):
        # We create the basic dictionary
        dict_table = {
            "classroom": {},
            "total": {
                "period": {},
                "average": {
                    "total": 0.0,
                    "total_list": [],
                    "percentage": 0.0
                },
                "classroom": 0
            }
        }
        # We fill the dictionary with the classrooms
        # We get the classrooms back.
        classrooms = Classroom.objects.all().order_by("order").values("id", "name", "capacity")
        # We get the periods back
        periods = Period.objects.filter(weekday__in=dates_range_weekday).order_by("order").values("id", "name",
                                                                                                  "weekday")
        # We fill the classrooms in the dictionary
        for classroom in classrooms:
            dict_table['classroom'][classroom["id"]] = {
                "name": classroom["name"],
                "capacity": classroom["capacity"],
                "period": {},
                "average": {
                    "total": 0.0,
                    "percentage": 0.0,
                    "average_list": [],
                }
            }
            # We fill the periods in the dictionary
            for period in periods:
                dict_table['classroom'][classroom["id"]]['period'][period["id"]] = {
                    "date": {},
                    "child": [],
                    "total": 0.0,
                    "average": 0.0,
                    "average_list": [],
                    "percentage": 0.0,
                    "dayoff": False
                }

        # the dictionary is filled with the periods for the totals
        for period in periods:
            dict_table["total"]["period"][period["id"]] = {
                "name": WEEKDAY_CHOICES[period["weekday"]] + " " + period["name"],
                "percentage": 0.0,
                "average_list": [],
                "total": 0.0,
                "dayoff": False
            }

        return dict_table

    def fill_dict_table(self, dict_table):
        """ Here we will fill in the dictionary """
        from_date = self.kwargs.get("from_date")
        end_date = self.kwargs.get("end_date")

        holidays = self.get_holiday_day(from_date, end_date)
        ocs_list_day = self.get_ocs_day(end_date, from_date)

        # Business days list
        range_dates_isoweekday = {r.date(): r.isoweekday() for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                                                          dtstart=from_date,
                                                                          until=end_date) if
                                  r.date() not in holidays and r.date() not in ocs_list_day}

        for date, weekday in range_dates_isoweekday.items():
            periods_planned = ChildToPeriod.objects.select_related("period", "child").filter(
                start_date__lte=date,
                end_date__gte=date,
                # child__status=Child.STATUS.in_progress,
            ).values("period_id", "child__classroom_id", "period__weekday", "child")

            for period_planned in periods_planned:
                if period_planned["period__weekday"] == date.isoweekday() and period_planned["child__classroom_id"] and \
                    period_planned["period__weekday"] not in self.dayoff[period_planned["child__classroom_id"]]:
                    if date not in dict_table["classroom"][period_planned["child__classroom_id"]]["period"][
                        period_planned["period_id"]]["date"]:
                        dict_table["classroom"][period_planned["child__classroom_id"]]["period"][
                            period_planned["period_id"]]["date"][date] = 0
                    dict_table["classroom"][period_planned["child__classroom_id"]]["period"][
                        period_planned["period_id"]]["child"].append(period_planned["child"])
                    dict_table["classroom"][period_planned["child__classroom_id"]]["period"][
                        period_planned["period_id"]]["date"][date] += 1
                    dict_table["classroom"][period_planned["child__classroom_id"]]["period"][
                        period_planned["period_id"]]["total"] += 1
                    dict_table["classroom"][period_planned["child__classroom_id"]]["period"][
                        period_planned["period_id"]]["average_list"].append(period_planned)
                    dict_table["classroom"][period_planned["child__classroom_id"]]["period"][
                        period_planned["period_id"]]["average"] = utils.round_up(
                        dict_table["classroom"][period_planned["child__classroom_id"]]["period"][
                            period_planned["period_id"]]["total"] / len(
                            dict_table["classroom"][period_planned["child__classroom_id"]]["period"][
                                period_planned["period_id"]]["date"]), 1)
            # dict_table["classroom"][period_planned["child__classroom_id"]]["average"]["average_list"].append(period_planned)

        # calcul percentage
        # We get the classrooms back.
        classrooms = Classroom.objects.all().order_by("order").values("id", "capacity")
        for classroom in classrooms.iterator():
            dict_table["total"]["classroom"] += classroom["capacity"]

            # fill list with total by period
            for period_id, period_value in dict_table["classroom"][classroom["id"]]["period"].items():
                if period_value['date']:
                    if period_value['child']:
                        dict_table["classroom"][classroom["id"]]["average"]["average_list"].append(
                            period_value["average"])
                    # set average for period
                    dict_table["classroom"][classroom["id"]]["period"][period_id]["percentage"] = utils.round_up(
                        utils.percentage(dict_table["classroom"][classroom["id"]]["period"][period_id]["average"],
                                         dict_table['classroom'][classroom["id"]]["capacity"]), 1)

                    # on ajoute au total col
                    dict_table["total"]["period"][period_id]["average_list"].append(
                        dict_table["classroom"][classroom["id"]]["period"][period_id]["average"])
                    dict_table["total"]["period"][period_id]["total"] = utils.round_nearest(sum(
                        dict_table["total"]["period"][period_id]["average_list"]), 0.1)

                    dict_table["total"]["period"][period_id]["percentage"] = utils.round_up(
                        utils.percentage(dict_table["total"]["period"][period_id]["total"],
                                         dict_table["total"]["classroom"]), 1)
                else:
                    dict_table["classroom"][classroom["id"]]["period"][period_id]['dayoff'] = True
                    dict_table["total"]["period"][period_id]['dayoff'] = True
            # set average for row
            dict_table["classroom"][classroom["id"]]["average"]["total"] = utils.round_up(mean(
                dict_table["classroom"][classroom["id"]]["average"]["average_list"]), 1)
            dict_table["classroom"][classroom["id"]]["average"]["percentage"] = utils.round_up(utils.percentage(
                dict_table["classroom"][classroom["id"]]["average"]["total"], classroom["capacity"]), 1)

        # add total list
        for period in dict_table["total"]['period'].values():
            if not period['dayoff']:
                dict_table["total"]["average"]["total_list"].append(
                    period['total'])

        dict_table["total"]["average"]["total"] = utils.round_up(mean(dict_table["total"]["average"]["total_list"]), 1)
        percentage = utils.round_up(
            utils.percentage(dict_table["total"]["average"]["total"], dict_table["total"]["classroom"]),
            1)
        dict_table["total"]["average"]["percentage"] = percentage

        return dict_table
