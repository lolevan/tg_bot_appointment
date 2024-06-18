import os

from django.db import models
from django.core.files import File

from enum import Enum

from datetime import timedelta, datetime, time

from typing import Dict, List

from users.models import User


class WorkDay(models.Model):
    date = models.DateField('Дата', unique=True)
    appointments = models.ManyToManyField('Appointment', related_name='workday_appointment', blank=True)
    work_hour_start = models.TimeField('Начало рабочего дня', default="09:00:00")
    work_hour_end = models.TimeField('Конец рабочего дня', default="18:00:00")

    is_visible = models.BooleanField('Видимый', default=False)
    is_weekend = models.BooleanField('Выходной день', default=False)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Рабочий день'
        verbose_name_plural = 'Рабочие дни'

    def __str__(self) -> str:
        return str(self.date)

    def get_day_of_week(self) -> str:
        return self.date.strftime('%A')

    def get_or_create_appointments_slots(self) -> List['Appointment']:
        appointments_exist: bool = self.appointments.exists()

        if not appointments_exist:
            appointment = self.appointments.create(
                date=self,
                start_time=self.work_hour_start,
                end_time=self.work_hour_end,
                available_slot=True
            )
            self.appointments.add(appointment)
            self.save()

            appointments: List[Appointment] = list(self.appointments.filter(available_slot=True))

            return appointments

        all_appointments: List[Appointment] = list(self.appointments.filter(available_slot=True))

        return all_appointments

    def get_available_time_slot(self, procedure_stages: Dict[str, timedelta | dict],
                                user: User) -> Dict[str, str | bool]:
        total_time: timedelta = procedure_stages['end_time']

        appointments_slots: List[Appointment] = self.get_or_create_appointments_slots()

        appointments_slots.sort(key=lambda appointment_info: appointment_info.start_time)

        current_appointment: None = None
        delete_current_appointment: bool = False

        for appointment in appointments_slots:
            if appointment.user_id == user and not appointment.user_id.first_name == "bot_one":
                continue

            appointment_total_time: timedelta = appointment.get_total_time()

            if total_time == appointment_total_time:
                delete_current_appointment: bool = True
                current_appointment: Appointment = appointment
                break
            elif total_time < appointment_total_time:
                current_appointment: Appointment = appointment
                break

        # Для данной процедуры нету времени
        if not current_appointment:
            return {'cancelled': True}

        start_time: datetime = datetime.combine(self.date, current_appointment.start_time)
        end_time: datetime = start_time + total_time

        start_time: str = start_time.time().strftime('%H:%M')
        end_time: str = end_time.time().strftime('%H:%M')

        return {
            'start_time': start_time,
            'end_time': end_time,
            'delete_current_appointment': delete_current_appointment,
            'cancelled': False,
        }

    def make_appointment(
            self,
            user: User,
            procedure_stages: Dict[str, timedelta | Dict[str, timedelta]],
            delete_current_appointment: bool,
            start_time: time,
            procedure_name: str
    ) -> None:

        delete_appointment = self.appointments.get(start_time=start_time)
        print(delete_appointment)
        delete_appointment.delete()
        self.save()
        start_time: datetime = datetime.combine(self.date, start_time)

        for index, stage in enumerate(procedure_stages['stages'].values(), 1):
            start_time_stage: datetime = start_time
            end_time_stage: datetime = start_time_stage + stage
            start_time += stage

            print(start_time_stage.time(), end_time_stage.time())

            appointment_stage = self.appointments.create(
                date=self,
                start_time=start_time_stage.time(),
                end_time=end_time_stage.time(),
                user_id=user,
                procedure=None if index % 2 == 0 else procedure_name,
                available_slot=True if index % 2 == 0 else False
            )
            self.appointments.add(appointment_stage)
        self.save()

        if not delete_current_appointment:
            appointment_stage_available = self.appointments.create(
                date=self,
                start_time=start_time,
                end_time=self.work_hour_end,
                procedure=None,
                user_id=None,
                available_slot=True
            )
            self.appointments.add(appointment_stage_available)

        print(self.appointments.all())

        self.save()


class Appointment(models.Model):
    date = models.ForeignKey(WorkDay, on_delete=models.CASCADE)
    start_time = models.TimeField('Начало процедуры')
    end_time = models.TimeField('Конец процедуры')
    procedure = models.CharField('Имя процедуры', max_length=100, blank=True, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    is_cancelled = models.BooleanField('Отменено', default=False)
    available_slot = models.BooleanField('Доступный ВС', default=False)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self) -> str:
        return f'date: {self.date} - username: {self.user_id.username if self.user_id else None}' \
               f' - procedure: {self.procedure}'

    def get_total_time(self) -> timedelta:
        start_datetime: datetime = datetime.combine(datetime.now(), self.start_time)
        end_datetime: datetime = datetime.combine(datetime.now(), self.end_time)

        total_time: timedelta = end_datetime - start_datetime

        return total_time


class UserAuthenticationRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authentication_requests')
    hair_photo_first = models.ImageField('Первая фотография волос', upload_to='authentication_photos/', blank=True)
    hair_photo_second = models.ImageField('Вторая фотография волос', upload_to='authentication_photos/', blank=True)
    hair_photo_three = models.ImageField('Третья фотография волос', upload_to='authentication_photos/', blank=True)

    created_at = models.DateTimeField('Дата и время запроса', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Запрос аутентификации'
        verbose_name_plural = 'Запросы аутентификации'

    def __str__(self) -> str:
        return f'user: {self.user.username} - created_at: {self.created_at}'

    def add_photo(self, photo_path: str) -> bool:
        photo_add: bool = False

        if not self.hair_photo_first:
            self.hair_photo_first.save(os.path.basename(photo_path), File(open(photo_path, 'rb')))
            photo_add: bool = True
        elif not self.hair_photo_second:
            self.hair_photo_second.save(os.path.basename(photo_path), File(open(photo_path, 'rb')))
            photo_add: bool = True
        elif not self.hair_photo_three:
            self.hair_photo_three.save(os.path.basename(photo_path), File(open(photo_path, 'rb')))
            photo_add: bool = True

        self.save()

        return photo_add


class ComplexityEnum(Enum):
    EASY: str = 'EASY'
    AVERAGE: str = 'AVERAGE'
    DIFFICULT: str = 'DIFFICULT'


class Procedure:
    name_eng: str
    name_rus: str
    complexity: ComplexityEnum

    def __init__(self, name_eng: str, name_rus: str, complexity: ComplexityEnum) -> None:
        self.name_eng = name_eng
        self.name_rus = name_rus
        self.complexity = complexity

    def __str__(self) -> str:
        return self.name_eng

    def get_complexity_name(self) -> str:
        return self.complexity.value

    def get_underline_name(self) -> str:
        return self.name_eng.replace(' ', '_')

    def calculate_duration(self, hair_length: str, hair_density: str) -> dict:
        pass


class ProcedurePermanent(Procedure):
    duration_procedures: Dict[str, Dict[str, int]]

    def calculate_duration(self, hair_length: str, hair_density: str, *args: list,
                           **kwargs: dict) -> Dict[str, timedelta | Dict[str, timedelta]]:
        end_time: int = self.duration_procedures[hair_density][hair_length]
        end_time_minutes: timedelta = timedelta(minutes=end_time)
        stage_1_end_time: timedelta = end_time_minutes

        return {
            'end_time': end_time_minutes,
            'stages': {'stage_1': stage_1_end_time}
        }


class ProcedureNonPermanent(Procedure):
    stage_1_start: Dict[str, Dict[str, int]]
    stage_2_wait: int
    stage_3_end: Dict[str, Dict[str, int]]

    def calculate_duration(self, hair_length: str, hair_density: str) -> Dict[str, timedelta | Dict[str, timedelta]]:
        stage_1_start_time: int = self.stage_1_start[hair_density][hair_length]
        stage_2_wait_time: int = self.stage_2_wait
        stage_3_end_time: int = self.stage_3_end[hair_density][hair_length]

        end_time: int = stage_1_start_time + stage_2_wait_time + stage_3_end_time
        end_time_minutes: timedelta = timedelta(minutes=end_time)

        stage_1_end_time: timedelta = timedelta(minutes=stage_1_start_time)
        stage_2_end_time: timedelta = timedelta(minutes=stage_2_wait_time)
        stage_3_end_time: timedelta = timedelta(minutes=stage_3_end_time)

        return {
            'end_time': end_time_minutes,
            'stages': {
                'stage_1': stage_1_end_time,
                'stage_2': stage_2_end_time,
                'stage_3': stage_3_end_time,
            }
        }


class ProcedureHaircut(ProcedurePermanent):
    def __init__(self) -> None:
        super().__init__('Haircut', 'Стрижка', ComplexityEnum.EASY)
        self.duration_procedures = {
            'THIN': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 90,
            },
            'MEDIUM': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 90,
            },
            'THICK': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 90,
            },
        }


class ProcedureSimpleColor(ProcedureNonPermanent):
    def __init__(self) -> None:
        super().__init__('Simple Color', 'Простое окрашивание', ComplexityEnum.EASY)
        self.stage_1_start = {
            'THIN': {
                'SHORT': 10,
                'MEDIUM': 10,
                'LONG': 10,
            },
            'MEDIUM': {
                'SHORT': 10,
                'MEDIUM': 10,
                'LONG': 10,
            },
            'THICK': {
                'SHORT': 20,
                'MEDIUM': 20,
                'LONG': 20,
            },
        }
        self.stage_2_wait = 40
        self.stage_3_end = {
            'THIN': {
                'SHORT': 10,
                'MEDIUM': 10,
                'LONG': 10,
            },
            'MEDIUM': {
                'SHORT': 10,
                'MEDIUM': 10,
                'LONG': 10,
            },
            'THICK': {
                'SHORT': 10,
                'MEDIUM': 10,
                'LONG': 10,
            },
        }


class ProcedureComplexColor(ProcedureNonPermanent):
    def __init__(self) -> None:
        super().__init__('Complex Color', 'Сложное окрашивание', ComplexityEnum.AVERAGE)
        self.stage_1_start = {
            'THIN': {
                'SHORT': 60,
                'MEDIUM': 90,
                'LONG': 90,
            },
            'MEDIUM': {
                'SHORT': 90,
                'MEDIUM': 90,
                'LONG': 120,
            },
            'THICK': {
                'SHORT': 120,
                'MEDIUM': 150,
                'LONG': 180,
            },
        }
        self.stage_2_wait = 60
        self.stage_3_end = {
            'THIN': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 90,
            },
            'MEDIUM': {
                'SHORT': 90,
                'MEDIUM': 90,
                'LONG': 90,
            },
            'THICK': {
                'SHORT': 90,
                'MEDIUM': 90,
                'LONG': 90,
            },
        }


class ProcedureBotox(ProcedureNonPermanent):
    def __init__(self) -> None:
        super().__init__('Botox', 'Ботокс', ComplexityEnum.AVERAGE)
        self.stage_1_start = {
            'THIN': {
                'SHORT': 15,
                'MEDIUM': 15,
                'LONG': 20,
            },
            'MEDIUM': {
                'SHORT': 20,
                'MEDIUM': 20,
                'LONG': 30,
            },
            'THICK': {
                'SHORT': 30,
                'MEDIUM': 30,
                'LONG': 30,
            },
        }
        self.stage_2_wait = 60
        self.stage_3_end = {
            'THIN': {
                'SHORT': 10,
                'MEDIUM': 10,
                'LONG': 10,
            },

            'MEDIUM': {
                'SHORT': 10,
                'MEDIUM': 10,
                'LONG': 10,
            },
            'THICK': {
                'SHORT': 10,
                'MEDIUM': 10,
                'LONG': 10,
            },
        }


class ProcedureKeratin(ProcedureNonPermanent):
    def __init__(self) -> None:
        super().__init__('Keratin', 'Кератин', ComplexityEnum.AVERAGE)
        self.stage_1_start = {
            'THIN': {
                'SHORT': 15,
                'MEDIUM': 15,
                'LONG': 20,
            },
            'MEDIUM': {
                'SHORT': 20,
                'MEDIUM': 20,
                'LONG': 30,
            },
            'THICK': {
                'SHORT': 30,
                'MEDIUM': 30,
                'LONG': 30,
            },
        }
        self.stage_2_wait = 60
        self.stage_3_end = {
            'THIN': {
                'SHORT': 10,
                'MEDIUM': 10,
                'LONG': 10,
            },

            'MEDIUM': {
                'SHORT': 10,
                'MEDIUM': 10,
                'LONG': 10,
            },
            'THICK': {
                'SHORT': 10,
                'MEDIUM': 10,
                'LONG': 10,
            },
        }


class ProcedureLaying(ProcedurePermanent):
    def __init__(self) -> None:
        super().__init__('Laying', 'Укладка', ComplexityEnum.EASY)
        self.duration_procedures = {
            'THIN': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 60,
            },
            'MEDIUM': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 60,
            },
            'THICK': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 60,
            },
        }


class ProcedureCurls(ProcedurePermanent):
    def __init__(self) -> None:
        super().__init__('Curls', 'Кудри', ComplexityEnum.EASY)
        self.duration_procedures = {
            'THIN': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 90,
            },
            'MEDIUM': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 90,
            },
            'THICK': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 90,
            },
        }


class ProcedureHairstyle(ProcedurePermanent):
    def __init__(self) -> None:
        super().__init__('Hairstyle', 'Прическа', ComplexityEnum.DIFFICULT)
        self.duration_procedures = {
            'THIN': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 60,
            },
            'MEDIUM': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 90,
            },
            'THICK': {
                'SHORT': 90,
                'MEDIUM': 90,
                'LONG': 90,
            },
        }


class ProcedureHairExtensionsFull(ProcedurePermanent):
    def __init__(self) -> None:
        super().__init__('Hair ext full', 'Полное наращивание волос', ComplexityEnum.AVERAGE)
        self.full_area: int = 120

    def calculate_duration(self, area: str, *args, **kwargs) -> Dict[str, timedelta]:
        duration_procedure: int = self.full_area
        duration_procedure_minutes: timedelta = timedelta(minutes=duration_procedure)
        stage_1_time: timedelta = duration_procedure_minutes

        return {
            'end_time': duration_procedure_minutes,
            'stages': {
                'stage_1': stage_1_time,
            }
        }


class ProcedureHairExtensionsTemple(ProcedurePermanent):
    def __init__(self) -> None:
        super().__init__('Hair ext temple', 'Височное наращивание волос', ComplexityEnum.AVERAGE)
        self.temporal_area: int = 40

    def calculate_duration(self, *args, **kwargs) -> Dict[str, timedelta]:
        duration_procedure: int = self.temporal_area
        duration_procedure_minutes: timedelta = timedelta(minutes=duration_procedure)
        stage_1_time: timedelta = duration_procedure_minutes

        return {
            'end_time': duration_procedure_minutes,
            'stages': {
                'stage_1': stage_1_time,
            }
        }
    

class ProcedureHairCheck(ProcedurePermanent):
    def __init__(self) -> None:
        super().__init__('Hair check', 'Проверка волос',  ComplexityEnum.EASY)
        self.duration_procedure = 15

    def calculate_duration(self, *args: list, **kwargs: dict) -> Dict[str, timedelta | Dict[str, timedelta]]:
        duration_procedure: timedelta = timedelta(minutes=self.duration_procedure)
        stage_1_time: timedelta = duration_procedure

        return {
            'end_time': duration_procedure,
            'stages': {
                'stage_1': stage_1_time,
            }
        }


class ProcedureHighlights(ProcedureNonPermanent):
    def __init__(self) -> None:
        super().__init__('Highlights', 'Мелирование', ComplexityEnum.AVERAGE)
        self.stage_1_start = {
            'THIN': {
                'SHORT': 60,
                'MEDIUM': 90,
                'LONG': 90,
            },
            'MEDIUM': {
                'SHORT': 90,
                'MEDIUM': 90,
                'LONG': 120,
            },
            'THICK': {
                'SHORT': 120,
                'MEDIUM': 150,
                'LONG': 180,
            },
        }
        self.stage_2_wait = 60
        self.stage_3_end = {
            'THIN': {
                'SHORT': 60,
                'MEDIUM': 60,
                'LONG': 90,
            },
            'MEDIUM': {
                'SHORT': 90,
                'MEDIUM': 90,
                'LONG': 90,
            },
            'THICK': {
                'SHORT': 90,
                'MEDIUM': 90,
                'LONG': 90,
            },
        }
