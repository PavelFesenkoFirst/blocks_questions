from rest_framework import generics
from core.api.v1.serializers import BlockListSerializer

from core.polls.models import Block


class BlockListUpView(generics.ListAPIView):
    serializer_class = BlockListSerializer
    queryset = Block.objects.all().order_by('date_creation')


class BlockListDownView(generics.ListAPIView):
    serializer_class = BlockListSerializer
    queryset = Block.objects.all().order_by('-date_creation')


class BlockListFilterView(generics.ListAPIView):
    serializer_class = BlockListSerializer

    def get_queryset(self):
        users = self.request.user
        all_block = Block.objects.filter(r_block__done=True, r_block__r_user_id=users)
        return all_block
