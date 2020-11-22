from django import forms
from django.forms.widgets import RadioSelect
from django.core.exceptions import ValidationError

from .models import Comment, Block, Answer, Question


class QuestionForm(forms.Form):
    """Форма для перебора фопросов в блоке"""
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        choice_list = [x for x in question.get_answers_list()]
        self.fields["answers"] = forms.ChoiceField(choices=choice_list, widget=RadioSelect)


class CommentForm(forms.ModelForm):
    """Форма для создания коментариев"""
    class Meta:
        model = Comment
        fields = ('text',)


class BlockForm(forms.ModelForm):
    """Форма для создания Блока тестов"""

    description = forms.CharField(widget=forms.Textarea)
    pass_mark = forms.IntegerField()

    class Meta:
        model = Block
        fields = ('title', 'description', 'pass_mark', 'success_text', 'fail_text',)

    def clean_pass_mark(self):
        new_pass_mark = self.cleaned_data['pass_mark']

        if new_pass_mark > 100:
            raise ValidationError('Значение должно быть максимум 100 или ниже')
        return new_pass_mark



class QuestionsForm(forms.ModelForm):
    """Форма для создания вопросов в блоке"""

    class Meta:
        model = Question
        fields = ('title', 'description')


class AnswerForm(forms.ModelForm):
    """Форма для создания ответов на вопрос"""

    class Meta:

        model = Answer
        fields = ('content', 'correct',)
        # widgets = {
        #     'content': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'type': 'text',}),
        #     'correct': forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': 'radio'}),
        # }
