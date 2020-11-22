from rest_framework import serializers

from core.polls.models import Block


class BlockListSerializer(serializers.ModelSerializer):
    questions = serializers.CharField(source='questions.count')
    link = serializers.CharField(source='get_absolute_url')

    class Meta:
        model = Block
        fields = ('title', 'description', 'questions', 'link')
