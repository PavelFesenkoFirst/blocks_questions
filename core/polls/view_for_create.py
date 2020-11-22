from django.shortcuts import render, redirect
from django.db.models import Count
from django.forms import formset_factory

from .models import Block, Question, Answer
from .forms import BlockForm, QuestionsForm, AnswerForm


def create_block(request):
    """Функция для создания блока вопросов"""
    context = {}
    form = BlockForm()

    if request.method == 'POST':
        form = BlockForm(request.POST)
        if form.is_valid():
            form_block = form.save(commit=False)
            user = request.user
            form_block.user = user
            form_block.save()
            return redirect('polls:create_question')
        return render(request, 'platform_testing/create_block.html', {'form': form})

    else:
        context['form'] = form
        return render(request, 'platform_testing/create_block.html', context)


def create_question(request):
    """Функция для создания вопросов в блоке"""
    context = {}
    form = QuestionsForm()
    f_block = Block.objects.all().first()

    if request.method == 'POST':
        form = QuestionsForm(request.POST)
        if form.is_valid():
            form_question = form.save(commit=False)
            form_question.block = f_block
            form_question.save()
            return redirect('polls:create_answer')
    else:
        context['form'] = form
        return render(request, 'platform_testing/create_questions.html', context)


def create_answer(request):
    """Функция для создания ответа. После создания, проверяет значение min_question,
    которое задает минимальное кол-во вопросов на блок"""
    context = {}
    user = request.user
    f_block = Block.objects.filter(user_id=user).first()
    last_question = Question.objects.filter(block=f_block).last()
    AnswerFormSet = formset_factory(AnswerForm, extra=4)
    radio = request.POST.getlist('correct')
    formset = AnswerFormSet(request.POST or None)
    print(radio)
    if request.method == 'POST':

        if formset.is_valid():
            for form in formset:
                answer_s = form.save(commit=False)
                answer_s.answer = last_question
                answer_s.save()

            question = Question.objects.get(id=last_question.id)
            answer_radio = question.get_answers_ids()

            if 'id_form-0-correct' in radio:
                ppppp = Answer.objects.get(id=answer_radio[0])
                ppppp.correct = True
                ppppp.save()
            elif 'id_form-1-correct' in radio:
                ppppp = Answer.objects.get(id=answer_radio[1])
                ppppp.correct = True
                ppppp.save()
            elif 'id_form-2-correct' in radio:
                ppppp = Answer.objects.get(id=answer_radio[2])
                ppppp.correct = True
                ppppp.save()
            elif 'id_form-3-correct' in radio:
                ppppp = Answer.objects.get(id=answer_radio[3])
                ppppp.correct = True
                ppppp.save()

            if f_block.min_question > Question.objects.filter(block=f_block).aggregate(Count('pk'))['pk__count']:
                return redirect('polls:create_question')
            return redirect('polls:index')
    else:
        context['form'] = AnswerFormSet
        return render(request, 'platform_testing/create_answer.html', context)
