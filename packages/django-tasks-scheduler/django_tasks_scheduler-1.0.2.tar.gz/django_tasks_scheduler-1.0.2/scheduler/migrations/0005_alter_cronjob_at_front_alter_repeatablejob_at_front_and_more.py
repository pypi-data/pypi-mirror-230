# Generated by Django 4.1.5 on 2023-01-13 22:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('scheduler', '0004_cronjob_at_front_repeatablejob_at_front_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cronjob',
            name='at_front',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='At front'),
        ),
        migrations.AlterField(
            model_name='repeatablejob',
            name='at_front',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='At front'),
        ),
        migrations.AlterField(
            model_name='scheduledjob',
            name='at_front',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='At front'),
        ),
    ]
