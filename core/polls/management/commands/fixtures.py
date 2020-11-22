from django.core.management.base import BaseCommand

from core.polls.models import Block, Question, Answer


class Command(BaseCommand):
    """Фикстура для создания 2-х вопросов(без выбора ответов)
    Создается новый блок вопросов с названием First"""

    def handle(self, *args, **options):
        Block.objects.get_or_create(user_id=1, pass_mark=50, title='First')
        Block.objects.get_or_create(user_id=1, pass_mark=50, title='Second')

        block = Block.objects.get(user_id=1, title='First')
        block_second = Block.objects.get(user_id=1, title='Second')

        questions_list = []
        questions_list_second = []
        for i in range(2):
            questions_list.append(
                Question(
                    block=block,
                    title=f'question #{i}',
                    description=f'question #{i}',
                )
            )
        for i in range(2):
            questions_list_second.append(
                Question(
                    block=block_second,
                    title=f'question second #{i}',
                    description=f'question second #{i}',
                )
            )

        Question.objects.bulk_create(questions_list)
        Question.objects.bulk_create(questions_list_second)
        self.stdout.write(
            self.style.SUCCESS(f' 4 questions was created.')
        )


# Переделать. Много повторяющихся строк кода
        for i in range(4):
            Answer.objects.create(answer=Question.objects.filter(title='question #0').last(), content=f'answer #{i}',
                                  correct=False)

            if i == 1:
                answer_one = Answer.objects.filter(content='answer #1').last()
                answer_one.correct = True
                answer_one.save()

        for i in range(4):
            Answer.objects.create(answer=Question.objects.filter(title='question #1').last(), content=f'answer #{i}',
                                  correct=False)

            if i == 2:
                answer_one = Answer.objects.filter(content='answer #2').last()
                answer_one.correct = True
                answer_one.save()

        for i in range(4):
            Answer.objects.create(answer=Question.objects.filter(title='question second #0').last(),
                                  content=f'answer #{i}', correct=False)

            if i == 0:
                answer_one = Answer.objects.filter(content='answer #0').last()
                answer_one.correct = True
                answer_one.save()

        for i in range(4):
            Answer.objects.create(answer=Question.objects.filter(title='question second #1').last(),
                                  content=f'answer #{i}', correct=False)

            if i == 3:
                answer_one = Answer.objects.filter(content='answer #3').last()
                answer_one.correct = True
                answer_one.save()
