import random

from datacenter.models import (Chastisement, Commendation, Lesson, Mark,
                               Schoolkid)


class DBException(Exception):
    pass


def check_child(schoolkid):
    try:
        child = Schoolkid.objects.get(full_name__contains=schoolkid)
    except Schoolkid.MultipleObjectsReturned:
        raise DBException('Ошибка: Найдено сразу несколько учеников с '
                          'введенным именем. Уточните имя ученика, добавив '
                          'фамилию или отчество.')
    except Schoolkid.DoesNotExist:
        raise DBException('Ошибка: Введено несуществующее имя. Проверьте '
                          'правильность написания имени.')
    else:
        return child


def check_lesson(schoolkid, lesson_name):
    lessons = Lesson.objects.filter(year_of_study=schoolkid.year_of_study,
                                    group_letter=schoolkid.group_letter)
    lessons_names = set([lesson.subject.title for lesson in lessons])
    if lesson_name in lessons_names:
        return lesson_name
    else:
        raise DBException('Ошибка: Введенный урок не найден. Проверьте '
                          'правильность написания названия урока. Название '
                          'должно быть таким, как на сайте электронного '
                          'дневника.')


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
    child_lessons = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject__title=lesson
    )
    lessons_count = child_lessons.count()
    child_lesson = child_lessons[lessons_count - 1]

    teacher_commendations = Commendation.objects.filter(
        teacher__full_name=child_lesson.teacher.full_name,
        subject__title=lesson)

    with open('commendations.txt') as file:
        commendations = file.readlines()
    commendation = random.choice(commendations)

    teacher_commendations.create(text=commendation,
                                 created=child_lesson.date,
                                 schoolkid=schoolkid,
                                 subject=child_lesson.subject,
                                 teacher=child_lesson.teacher)


def fix_diary(child_name, lesson_name):
    try:
        schoolkid = check_child(child_name)
        lesson = check_lesson(schoolkid, lesson_name)
    except DBException as error:
        print(error)
        return

    fix_bad_marks(schoolkid)
    remove_chastisements(schoolkid)
    create_commendation(schoolkid, lesson)
