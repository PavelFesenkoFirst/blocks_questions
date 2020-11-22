from django.db import models
from django.utils.text import slugify
import json
from django.urls import reverse
import re
from django.core.exceptions import ValidationError, ImproperlyConfigured
from model_utils.managers import InheritanceManager
from django.core.validators import MaxValueValidator, validate_comma_separated_integer_list
from django.conf import settings
from django.utils.timezone import now


class Block(models.Model):
    """Модель блока, которая будет содержать в себе вопросы"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='b_author',
                             verbose_name='Создатель')
    title = models.CharField(max_length=128, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание блока')
    slug = models.SlugField(allow_unicode=True, default='', blank=True)
    count_proh = models.IntegerField(default=0, verbose_name='Кол-во прохождений пользователями')
    pass_mark = models.SmallIntegerField(blank=False, default=0, validators=[MaxValueValidator(100)],
                                         help_text="Установить процент прохождения блока",
                                         verbose_name="Процент прохождения")
    min_question = models.PositiveIntegerField(blank=True, null=True, default=5,
                                               verbose_name='Отображение минимального количества тестов')
    success_text = models.TextField(blank=False, help_text="Текст, для отображения при успешном прохождении теста",
                                    verbose_name="Поздравительный текст")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания блока')
    fail_text = models.TextField(verbose_name="Провал блока с тестами", blank=False,
                                 help_text="Текст, для отображения при неудачном прохождении теста")

    class Meta:
        verbose_name = "Блок"
        verbose_name_plural = "Блоки"
        ordering = ['-id']

    def get_absolute_url(self):
        return reverse('polls:block_start_page', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    def get_questions(self):
        all_q = self.questions.all().select_subclasses()
        for q_all in all_q:
            if q_all.answers.exists():
                f = q_all.count_c_n()
                q_all.count_a()
                if f > 3:
                    q_all.delete()
            else:
                q_all.delete()
        return self.questions.all().select_subclasses()

    @property
    def get_max_score(self):
        return self.get_questions().count()

    def score_id(self):
        return str(self.id) + '_score'

    def q_list(self):
        return str(self.id) + '_q_list'

    def q_data(self):
        return str(self.id) + "_data"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        if self.pass_mark > 100:
            raise ValidationError('%s больше чем нужно(100)' % self.pass_mark)
        super().save(*args, **kwargs)


class ProgressManager(models.Manager):

    def new_progress(self, user):
        new_progress = self.create(user=user, score="")
        new_progress.save()
        return new_progress


class Progress(models.Model):
    """
    Промежуточная таблица для хранени прогресса юзера
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author',
                                verbose_name='Пользователь')
    score = models.CharField(validators=[validate_comma_separated_integer_list], max_length=128,
                             verbose_name='Счет')
    correct_answer = models.CharField(max_length=10, verbose_name='Правильный ответ')
    wrong_answer = models.CharField(max_length=10, verbose_name='Не правильный ответ')

    objects = ProgressManager()

    class Meta:
        verbose_name = 'Прогресс Пользователя'
        verbose_name_plural = 'Прогресс Пользователей'

    @property
    def list_all_block_scores(self):
        score_before = self.score
        output = {}

        for block in Block.objects.all():
            to_find = re.escape(block.title) + r",(\d+),(\d+),"
            match = re.search(to_find, self.score, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                possible = int(match.group(2))
                try:
                    percent = int(round((float(score) / float(possible))
                                        * 100))
                except:
                    percent = 0
                output[block.title] = [score, possible, percent]
            else:
                self.score += block.title + ",0,0,"
                output[block.title] = [0, 0]

        if len(self.score) > len(score_before):
            self.save()
        return output

    def update_score(self, question, score_to_add=0, possible_to_add=0):
        block_test = Block.objects.filter(title=question.block).exists()
        if any([item is False for item in [block_test,
                                           score_to_add,
                                           possible_to_add,
                                           isinstance(score_to_add, int),
                                           isinstance(possible_to_add, int)]]):
            return 'error', 'блок не существует или недействительный счет'

        to_find = re.escape(str(question.block)) +\
            r",(?P<score>\d+),(?P<possible>\d+),"

        match = re.search(to_find, self.score, re.IGNORECASE)

        if match:
            updated_score = int(match.group('score')) + abs(score_to_add)
            updated_possible = int(match.group('possible')) + abs(possible_to_add)

            new_score = ",".join(
                [
                    str(question.block),
                    str(updated_score),
                    str(updated_possible), ''
                ])

            self.score = self.score.replace(match.group(), new_score)
            self.save()

        else:
            self.score += ",".join(
                [
                    str(question.block),
                    str(score_to_add),
                    str(possible_to_add),
                    ""
                ])
            self.save()

    def show_exams(self):
        return Sitting.objects.filter(user=self.user, complete=True)

    def __str__(self):
        return self.user.username + ' - ' + self.score


class SittingManager(models.Manager):

    def new_sitting(self, user, block):

        question_set = block.questions.all().select_subclasses()

        question_set = [item.id for item in question_set]

        if len(question_set) == 0:
            raise ImproperlyConfigured('Набор вопросов блока пуст.  '
                                       'Пожалуйста, настройте вопросы правильно')

        if block.min_question and block.min_question < len(question_set):
            question_set = question_set[block.min_question:]
        questions = ",".join(map(str, question_set)) + ","
        new_sitting = self.create(user=user, block=block, question_order=questions, question_list=questions,
                                  incorrect_questions="", current_score=0, complete=False, user_answers='{}')
        return new_sitting

    def user_sitting(self, user, block):
        try:
            sitting = self.get(user=user, block=block, complete=False)
        except Sitting.DoesNotExist:
            sitting = self.new_sitting(user, block)
        except Sitting.MultipleObjectsReturned:
            sitting = self.filter(user=user, block=block, complete=False)[0]
        return sitting


class Sitting(models.Model):
    """
    Промежуточная таблица для хранения ответов пользователя. Хранит
    список ID вопорсов в порядке их перечисления. Question_list - список целых чисел,
    которые представляют собой идентификаторы вопросов без ответов. Вопросы с неправильными
    ответами - это список в том же формате
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE)
    block = models.ForeignKey(Block, related_name='sitting', verbose_name='блок', on_delete=models.CASCADE)
    question_order = models.CharField(validators=[validate_comma_separated_integer_list], max_length=1024,
                                      verbose_name='Отсортированый список вопросов')
    question_list = models.CharField(validators=[validate_comma_separated_integer_list], max_length=1024,
                                     verbose_name='Список вопросов')
    incorrect_questions = models.CharField(validators=[validate_comma_separated_integer_list], max_length=1024,
                                           blank=True, verbose_name='Не правильные ответы')
    current_score = models.IntegerField(verbose_name='Текущий счет')
    complete = models.BooleanField(default=False, blank=False, verbose_name='Завершен или нет')
    user_answers = models.TextField(blank=True, default='{}', verbose_name='Ответы пользователя')
    start = models.DateTimeField(auto_now_add=True, verbose_name='начало')
    end = models.DateTimeField(null=True, blank=True, verbose_name='конец')

    objects = SittingManager()

    class Meta:
        pass

    def get_first_question(self):

        if not self.question_list:
            return False

        first, _ = self.question_list.split(',', 1)
        question_id = int(first)
        return Question.objects.get_subclass(id=question_id)

    def remove_first_question(self):
        if not self.question_list:
            return

        _, others = self.question_list.split(',', 1)
        self.question_list = others
        self.save()

    def add_to_score(self, points):
        self.current_score += int(points)
        self.save()

    @property
    def get_current_score(self):
        return self.current_score

    def _question_ids(self):
        return [int(n) for n in self.question_order.split(',') if n]

    @property
    def get_percent_correct(self):
        dividend = float(self.current_score)
        divisor = len(self._question_ids())

        if divisor < 1:
            return 0

        if dividend > divisor:
            return 100
        correct = int(round((dividend / divisor) * 100))

        if correct >= 1:
            return correct
        else:
            return 0

    def mark_quiz_complete(self):
        self.complete = True
        self.end = now()
        self.save()

    def add_incorrect_question(self, question):
        if len(self.incorrect_questions) > 0:
            self.incorrect_questions += ','
        self.incorrect_questions += str(question.id) + ","
        if self.complete:
            self.add_to_score(-1)
        self.save()

    @property
    def get_incorrect_questions(self):
        return [int(q) for q in self.incorrect_questions.split(',') if q]

    def remove_incorrect_question(self, question):
        current = self.get_incorrect_questions
        current.remove(question.id)
        self.incorrect_questions = ','.join(map(str, current))
        self.add_to_score(1)
        self.save()

    @property
    def check_if_passed(self):
        return self.get_percent_correct >= self.block.pass_mark

    @property
    def result_message(self):
        if self.check_if_passed:
            return self.block.success_text
        else:
            return self.block.fail_text

    def add_user_answer(self, question, guess):
        current = json.loads(self.user_answers)
        current[question.id] = guess
        self.user_answers = json.dumps(current)
        self.save()

    def get_questions(self, with_answers=False):
        question_ids = self._question_ids()
        questions = sorted(
            self.block.questions.filter(id__in=question_ids).select_subclasses(),
            key=lambda q: question_ids.index(q.id)
        )
        if with_answers:
            user_answers = json.loads(self.user_answers)
            for question in questions:
                question.user_answer = user_answers[str(question.id)]
        return questions

    @property
    def questions_with_user_answers(self):
        return {
            q: q.user_answer for q in self.get_questions(with_answers=True)
        }

    @property
    def get_max_score(self):
        return len(self._question_ids())

    def progress(self):
        answered = len(json.loads(self.user_answers))
        total = self.get_max_score
        return answered, total


class Question(models.Model):
    """Модель вопросов"""

    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=128, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')

    objects = InheritanceManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['id']

    def check_if_correct(self, guess):
        answer = Answer.objects.get(id=guess)
        if answer.correct is True:
            return True
        else:
            return False

    def order_answers(self, queryset):
        return queryset.order_by('id')

    def get_answers(self):
        return self.order_answers(Answer.objects.filter(answer=self))

    def get_answers_corrects(self):
        return [answer.correct for answer in self.order_answers(Answer.objects.filter(answer=self))]

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in self.order_answers(Answer.objects.filter(answer=self))]

    def answer_choice_to_string(self, guess):
        return Answer.objects.get(id=guess).content



    def get_answers_ids(self):
        return [answer.id for answer in self.order_answers(Answer.objects.filter(answer=self))]

    def count_c_n(self):
        b = self.order_answers(Answer.objects.filter(answer=self, correct=False))
        return b.count()



#???
    def count_a(self):
        b = self.order_answers(Answer.objects.filter(answer=self, correct=True))
        print(b.count())
        if b.count() > 3:
            c = b.last()
            c.correct = False
            c.save()
            if b.count() > 2:
                c = b.last()
                c.correct = False
                c.save()
                if b.count() > 1:
                    c = b.last()
                    c.correct = False
                    c.save()
        elif b.count() > 2:
            c = b.last()
            print(c)
            c.correct = False
            c.save()
            if b.count() > 1:
                c = b.last()
                c.correct = False
                c.save()
        elif b.count() > 1:
            c = b.last()
            print(c)
            c.correct = False
            c.save()
        return b



    def __str__(self):
        return self.title


class Answer(models.Model):
    """Модель ответов"""

    answer = models.ForeignKey(Question, verbose_name='answer', on_delete=models.CASCADE, related_name='answers')
    content = models.CharField(max_length=1000, blank=False, verbose_name="Ответ")
    correct = models.BooleanField(default=False, help_text="Выберите 1 правильный ответ",
                                  verbose_name="Правильный ответ")

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE,)
    test = models.ForeignKey(Block, verbose_name='Блок тестов', on_delete=models.CASCADE)
    name = models.CharField(max_length=128, verbose_name='имя', blank=True, null=True)
    text = models.TextField(verbose_name='Коментарий')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = "Коментарии"
        verbose_name_plural = "Коментарии"

    def __str__(self):
        return self.test.slug
