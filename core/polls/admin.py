from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
# Register your models here.

from .models import Block, Question, Answer, Comment


class AnswerInline(admin.TabularInline):
    """Админка для ответов"""

    model = Answer
    extra = 4


class BlockAdminForm(forms.ModelForm):
    """Форма для блоков вопросов в админке"""

    class Meta:
        model = Block
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label='Questions',
        widget=FilteredSelectMultiple(
            verbose_name='Questions',
            is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(BlockAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial = self.instance.questions.all().select_subclasses()

    def save(self, commit=True):
        block = super(BlockAdminForm, self).save(commit=False)
        block.save()
        block.questions.set(self.cleaned_data['questions'])
        self.save_m2m()
        return block


class BlockAdmin(admin.ModelAdmin):
    """Админка для Блоков вопросов"""

    form = BlockAdminForm
    list_display = ('id', 'title', 'description', )
    search_fields = ('description', 'title', )


class QuestionAdmin(admin.ModelAdmin):
    """Админка для вопросов"""

    list_display = ('block', 'title', )
    list_filter = ('block',)
    fields = ('block', 'title', 'description')
    search_fields = ('title', 'description')

    inlines = [AnswerInline]


admin.site.register(Block, BlockAdmin)
admin.site.register(Comment)
admin.site.register(Question, QuestionAdmin)


