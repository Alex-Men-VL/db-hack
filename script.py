import random
from textwrap import dedent

from datacenter.models import (Chastisement, Commendation, Lesson, Mark,
                               Schoolkid)


class BDException(Exception):
    pass


def get_schoolkid_account(schoolkid):
    try:
        child = Schoolkid.objects.get(full_name__contains=schoolkid)
    except Schoolkid.MultipleObjectsReturned:
        raise BDException(dedent('''\
        Ошибка: Найдено сразу несколько учеников с введенным именем.
        Решение: Уточните имя ученика, добавив фамилию или отчество.'''))
    except Schoolkid.DoesNotExist:
        raise BDException(dedent('''\
        Ошибка: Введено несуществующее имя.
        Решение: Проверьте правильность написания имени и порядок. Сначала \
идет фамилия, потом имя, затем отчество.'''))
    else:
        return child


def get_schoolkid_lesson(schoolkid, lesson_name):
    schoolkid_lesson = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject__title=lesson_name
    )
    if not schoolkid_lesson:
        raise BDException(dedent('''\
        Ошибка: Введенный урок не найден.
        Решение: Проверьте правильность написания названия урока. Название \
должно быть таким, как на сайте электронного дневника.'''))
    return schoolkid_lesson.last()


def fix_bad_marks(schoolkid):
    child_marks = Mark.objects.filter(schoolkid__full_name=schoolkid.full_name,
                                      points__in=[2, 3])
    for mark in child_marks:
        mark.points = 5
        mark.save()


def remove_chastisements(schoolkid):
    child_chastisements = Chastisement.objects.filter(
        schoolkid__full_name=schoolkid.full_name)
    child_chastisements.delete()


def create_commendation(schoolkid, lesson):
    teacher_commendations = Commendation.objects.filter(
        teacher__full_name=lesson.teacher.full_name,
        subject__title=lesson.subject.title
    )

    with open('commendations.txt') as file:
        commendations = file.readlines()
    commendation = random.choice(commendations)

    teacher_commendations.create(text=commendation,
                                 created=lesson.date,
                                 schoolkid=schoolkid,
                                 subject=lesson.subject,
                                 teacher=lesson.teacher)


def fix_diary(child_name, lesson_name):
    try:
        schoolkid = get_schoolkid_account(child_name)
        lesson = get_schoolkid_lesson(schoolkid, lesson_name)
    except BDException as error:
        print(error)
        return

    fix_bad_marks(schoolkid)
    remove_chastisements(schoolkid)
    create_commendation(schoolkid, lesson)
