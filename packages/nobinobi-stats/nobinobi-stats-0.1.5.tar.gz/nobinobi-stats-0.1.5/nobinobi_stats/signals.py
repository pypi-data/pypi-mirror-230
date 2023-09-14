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

from sys import stdout

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_permissions_stats(sender, **kwargs):
    from nobinobi_daily_follow_up.models import DailyFollowUp
    content_type = ContentType.objects.get_for_model(DailyFollowUp)
    permission, created = Permission.objects.get_or_create(
        codename='view_stats',
        name='Can View Stats',
        content_type=content_type,
    )
    if created:
        stdout.write("Permission {} created successfully.\n".format(permission))

    try:
        group_admin = Group.objects.get(name="Admin")
    except Group.DoesNotExist:
        pass
    else:
        group_admin.permissions.add(permission)
        stdout.write("Permission {} added to {} successfully.\n".format(permission, group_admin))
