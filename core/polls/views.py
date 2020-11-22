from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView
from django.views.generic.edit import FormView

from .forms import QuestionForm, CommentForm
from .models import Block, Progress, Sitting, Comment
from core.users.models import ResultsUsers


class IndexView(ListView):
    """Главная страница"""

    model = Block
    queryset = Block.objects.all()
    template_name = 'testing/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        all_block = Block.objects.all()
        context['block_list'] = all_block
        return context


def detail_block_test(request, pk):
    """Детальное отображение блока с ворпосами"""

    block = get_object_or_404(Block, pk=pk)
    block.get_questions()
    comment = Comment.objects.filter(test=block.pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.test = block
            form.save()
            return redirect('polls:block_start_page', pk)
    else:
        form = CommentForm()
    return render(request, 'platform_testing/block_detail.html', {'bloc': block, 'comment': comment, 'form': form})


class BlockTake(FormView):
    """Для прохождения тестов"""

    form_class = QuestionForm
    template_name = 'testing/question.html'

    def dispatch(self, request, *args, **kwargs):
        self.block = get_object_or_404(Block, pk=self.kwargs['pk'])
        self.logged_in_user = self.request.user.is_authenticated

        if self.logged_in_user:
            self.sitting = Sitting.objects.user_sitting(request.user, self.block)

        if self.sitting is False:
            return render(request, 'testing/result.html')

        return super(BlockTake, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=QuestionForm):
        if self.logged_in_user:
            self.question = self.sitting.get_first_question()
            self.progress = self.sitting.progress()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(BlockTake, self).get_form_kwargs()
        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        if self.logged_in_user:
            self.form_valid_user(form)
            if self.sitting.get_first_question() is False:
                return self.final_result_user()
        self.request.POST = {}

        return super(BlockTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(BlockTake, self).get_context_data(**kwargs)
        context['question'] = self.question
        context['block'] = self.block
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        return context

    def form_valid_user(self, form):
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        guess = form.cleaned_data['answers']
        is_correct = self.question.check_if_correct(guess)

        if is_correct is True:
            self.sitting.add_to_score(1)
            progress.update_score(self.question, 1, 1)
        else:
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 1)
        self.previous = {}
        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()

    def final_result_user(self):
        results = {
            'block': self.block,
            'score': self.sitting.get_current_score,
            'max_score': self.sitting.get_max_score,
            'percent': self.sitting.get_percent_correct,
            'sitting': self.sitting,
            'previous': self.previous,
        }

        block_q = Block.objects.get(title=results['block'])
        results['block_q'] = block_q
        self.block.count_proh += 1

        user = self.request.user
        ResultsUsers.objects.update_or_create(r_user=user, r_block=results['block'])
        check_done = ResultsUsers.objects.get(r_user=user, r_block=results['block'])
        check_done.count_try += 1
        check_done.results = results['percent']
        check_done.check_done()
        check_done.save()

        self.block.save()
        self.sitting.mark_quiz_complete()

        return render(self.request, 'testing/result.html', results)


class SearchView(ListView):
    """Поиск по сайту"""

    template_name = 'testing/block/search.html'
    context_object_name = 'block_list'

    def get_queryset(self):
        return Block.objects.filter(title__icontains=self.request.GET.get('s'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
