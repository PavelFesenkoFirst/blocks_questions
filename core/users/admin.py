from django.contrib import admin

from core.users.models import Users, ResultsUsers


class UserStatisticAdmin(admin.TabularInline):
    model = ResultsUsers
    raw_id_fields = ('r_user', 'r_block')
    radio_fields = {'r_user': admin.VERTICAL}


@admin.register(Users)
class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ['password']
    list_display = ['username', 'first_name', 'last_name', 'birth_date', 'description']
    inlines = [
        UserStatisticAdmin,
    ]


class ResultAdmin(admin.ModelAdmin):
    list_display = ['r_user', 'r_block', 'count_try', 'results', 'done']
    search_fields = ('r_user', 'r_block',)
    list_filter = ('done',)


admin.site.register(ResultsUsers, ResultAdmin)
