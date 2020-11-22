from django.urls import path

from core.api.v1.views import BlockListUpView, BlockListDownView, BlockListFilterView

urlpatterns = [
    path('block/up', BlockListUpView.as_view()),
    path('block/down', BlockListDownView.as_view()),
    path('block/filter', BlockListFilterView.as_view()),
]