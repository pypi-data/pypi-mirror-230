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

from django.urls import reverse
from django.utils.translation import gettext as _
from menu import Menu, MenuItem

from nobinobi_stats.utils import has_view_stats

Menu.add_item(
    "main",
    MenuItem(
        title=_("Statistics"),
        url="/stats/",
        icon="fa fa-chart-bar",
        children=[
            MenuItem(
                title=_("Attendance period"),
                url=reverse("nobinobi_stats:choice_attendance_period"),
                icon="fa fa-chart-bar"),
            MenuItem(
                title=_("Attendance calendar"),
                url=reverse("nobinobi_stats:choice_attendance_calendar"),
                icon="fa fa-chart-bar"),
            MenuItem(
                title=_("Attendance child"),
                url=reverse("nobinobi_stats:choice_attendance_child"),
                icon="fa fa-chart-bar"),
            MenuItem(
                title=_("Occupancy calendar"),
                url=reverse("nobinobi_stats:choice_occupancy_period"),
                icon="fa fa-chart-bar"),
        ],
        check=lambda request: has_view_stats(request)
    )
)

# Menu.add_item("main", MenuItem("Staff Only",
#                                reverse("reports.views.staff"),
#                                check=lambda request: request.user.is_staff))
#
# Menu.add_item("main", MenuItem("Superuser Only",
#                                reverse("reports.views.superuser"),
#                                check=lambda request: request.user.is_superuser))
