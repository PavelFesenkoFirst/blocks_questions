from django.urls import path

from .views import BlockTake, SearchView, detail_block_test, IndexView

from .view_for_create import create_block, create_question, create_answer

app_name = 'polls'

urlpatterns = [

    path('', IndexView.as_view(), name='index'),
    path('search/', SearchView.as_view(), name='search'),
    path('block_test_name/<pk>/', detail_block_test, name='block_start_page'),
    path('<pk>/take/', BlockTake.as_view(), name='block_question'),
    path('create/block', create_block, name='create_block'),
    path('create/question', create_question, name='create_question'),
    path('create/answer', create_answer, name='create_answer'),
]