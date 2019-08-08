# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-04 07:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def forwards_func(apps, schema_editor):

    DeviceType = apps.get_model("lava_scheduler_app", "DeviceType")
    Device = apps.get_model("lava_scheduler_app", "Device")
    TestJob = apps.get_model("lava_scheduler_app", "TestJob")
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    GroupDeviceTypePermission = apps.get_model(
        "lava_scheduler_app", "GroupDeviceTypePermission"
    )
    GroupDevicePermission = apps.get_model(
        "lava_scheduler_app", "GroupDevicePermission"
    )
    db_alias = schema_editor.connection.alias

    ct_devicetype = ContentType.objects.get_for_model(DeviceType)
    ct_device = ContentType.objects.get_for_model(Device)
    ct_testjob = ContentType.objects.get_for_model(TestJob)

    # Create custom permissions first if they do not exist.
    Permission.objects.using(db_alias).get_or_create(
        name="Can view device type",
        content_type=ct_devicetype,
        codename="view_devicetype",
    )
    Permission.objects.using(db_alias).get_or_create(
        name="Can submit jobs to device type",
        content_type=ct_devicetype,
        codename="submit_to_devicetype",
    )
    Permission.objects.using(db_alias).get_or_create(
        name="Can admin device type",
        content_type=ct_devicetype,
        codename="admin_devicetype",
    )
    Permission.objects.using(db_alias).get_or_create(
        name="Can view device", content_type=ct_device, codename="view_device"
    )
    Permission.objects.using(db_alias).get_or_create(
        name="Can submit jobs to device",
        content_type=ct_device,
        codename="submit_to_device",
    )
    Permission.objects.using(db_alias).get_or_create(
        name="Can admin device", content_type=ct_device, codename="admin_device"
    )
    Permission.objects.using(db_alias).get_or_create(
        name="Can submit test job", content_type=ct_testjob, codename="submit_testjob"
    )

    # Create user groups (groups with the same name as each user with only
    # corresponding user in the group)
    for user in User.objects.using(db_alias).all():
        group, _ = Group.objects.using(db_alias).get_or_create(name=user.username)
        group.user_set.add(user)

    for device_type in DeviceType.objects.using(db_alias).filter(owners_only=True):
        view_permission = Permission.objects.using(db_alias).get(
            content_type=ct_devicetype, codename="view_devicetype"
        )
        submit_permission = Permission.objects.using(db_alias).get(
            content_type=ct_devicetype, codename="submit_to_devicetype"
        )
        for device in device_type.device_set.filter(user__isnull=False):
            # Add this user's private group with 'view' permission for the
            # device type.
            group = Group.objects.using(db_alias).get(name=device.user.username)
            kwargs = {
                "permission": view_permission,
                "group": group,
                "devicetype": device_type,
            }
            GroupDeviceTypePermission.objects.get_or_create(**kwargs)
            kwargs["permission"] = submit_permission
            GroupDeviceTypePermission.objects.get_or_create(**kwargs)

        for device in device_type.device_set.filter(group__isnull=False):
            # same as above, only for groups
            kwargs = {
                "permission": view_permission,
                "group": device.group,
                "devicetype": device_type,
            }
            GroupDeviceTypePermission.objects.get_or_create(**kwargs)
            kwargs["permission"] = submit_permission
            GroupDeviceTypePermission.objects.get_or_create(**kwargs)

    for device in Device.objects.using(db_alias).filter(is_public=False):
        view_permission = Permission.objects.using(db_alias).get(
            content_type=ct_device, codename="view_device"
        )
        submit_permission = Permission.objects.using(db_alias).get(
            content_type=ct_device, codename="submit_to_device"
        )
        admin_permission = Permission.objects.using(db_alias).get(
            content_type=ct_device, codename="admin_device"
        )
        if device.user:
            group = Group.objects.using(db_alias).get(name=device.user.username)
        elif device.group:
            group = device.group

        if device.user or device.group:
            kwargs = {"permission": view_permission, "group": group, "device": device}
            GroupDevicePermission.objects.get_or_create(**kwargs)
            kwargs["permission"] = submit_permission
            GroupDevicePermission.objects.get_or_create(**kwargs)
            kwargs["permission"] = admin_permission
            GroupDevicePermission.objects.get_or_create(**kwargs)

    for job in TestJob.objects.using(db_alias).filter(visibility=1):
        group = Group.objects.using(db_alias).get(name=job.submitter.username)
        job.viewing_groups.add(group)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0008_alter_user_username_max_length"),
        ("lava_scheduler_app", "0041_notification_charfield_to_textfield"),
    ]

    operations = [
        migrations.CreateModel(
            name="GroupDevicePermission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                )
            ],
        ),
        migrations.CreateModel(
            name="GroupDeviceTypePermission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                )
            ],
        ),
        migrations.AlterModelOptions(
            name="device",
            options={
                "permissions": (
                    ("view_device", "Can view device"),
                    ("submit_to_device", "Can submit jobs to device"),
                    ("admin_device", "Can admin device"),
                )
            },
        ),
        migrations.AlterModelOptions(
            name="devicetype",
            options={
                "permissions": (
                    ("view_devicetype", "Can view device type"),
                    ("submit_to_devicetype", "Can submit jobs to device type"),
                    ("admin_devicetype", "Can admin device type"),
                )
            },
        ),
        migrations.AlterModelOptions(
            name="testjob",
            options={"permissions": (("submit_testjob", "Can submit test job"),)},
        ),
        migrations.AddField(
            model_name="groupdevicetypepermission",
            name="devicetype",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="permissions",
                to="lava_scheduler_app.DeviceType",
            ),
        ),
        migrations.AddField(
            model_name="groupdevicetypepermission",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="auth.Group"
            ),
        ),
        migrations.AddField(
            model_name="groupdevicetypepermission",
            name="permission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="auth.Permission"
            ),
        ),
        migrations.AddField(
            model_name="groupdevicepermission",
            name="device",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="permissions",
                to="lava_scheduler_app.Device",
            ),
        ),
        migrations.AddField(
            model_name="groupdevicepermission",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="auth.Group"
            ),
        ),
        migrations.AddField(
            model_name="groupdevicepermission",
            name="permission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="auth.Permission"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="groupdevicetypepermission",
            unique_together=set([("group", "permission", "devicetype")]),
        ),
        migrations.AlterUniqueTogether(
            name="groupdevicepermission",
            unique_together=set([("group", "permission", "device")]),
        ),
        migrations.RunPython(forwards_func, noop),
        migrations.RemoveField(model_name="defaultdeviceowner", name="user"),
        migrations.AlterModelOptions(name="testjobuser", options={}),
        migrations.RemoveField(model_name="device", name="group"),
        migrations.RemoveField(model_name="device", name="is_public"),
        migrations.RemoveField(model_name="device", name="user"),
        migrations.RemoveField(model_name="devicetype", name="owners_only"),
        migrations.RemoveField(model_name="testjob", name="group"),
        migrations.RemoveField(model_name="testjob", name="user"),
        migrations.RemoveField(model_name="testjob", name="visibility"),
        migrations.DeleteModel(name="DefaultDeviceOwner"),
    ]
