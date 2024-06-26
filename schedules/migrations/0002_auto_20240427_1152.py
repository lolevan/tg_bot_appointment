# Generated by Django 3.2.9 on 2024-04-27 03:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20240425_1102'),
        ('schedules', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField(verbose_name='Начало процедуры')),
                ('end_time', models.TimeField(verbose_name='Конец процедуры')),
                ('procedure', models.CharField(max_length=100, verbose_name='Имя процедуры')),
                ('is_cancelled', models.BooleanField(default=False, verbose_name='Отменено')),
            ],
            options={
                'verbose_name': 'Запись',
                'verbose_name_plural': 'Записи',
                'ordering': ['date'],
            },
        ),
        migrations.DeleteModel(
            name='ProcedureNonPermanent',
        ),
        migrations.DeleteModel(
            name='ProcedurePermanent',
        ),
        migrations.AddField(
            model_name='workday',
            name='is_visible',
            field=models.BooleanField(default=False, verbose_name='Видимый'),
        ),
        migrations.AddField(
            model_name='appointments',
            name='date',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedules.workday'),
        ),
        migrations.AddField(
            model_name='appointments',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user'),
        ),
    ]
