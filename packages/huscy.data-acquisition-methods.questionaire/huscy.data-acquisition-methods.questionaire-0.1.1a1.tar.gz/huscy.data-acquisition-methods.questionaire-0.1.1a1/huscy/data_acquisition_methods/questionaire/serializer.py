from rest_framework import serializers

from . import models, services


class QuestionaireSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.Questionaire
        fields = (
            'id',
            'filehandle',
            'name',
            'uploaded_at',
            'uploaded_by',
        )
        read_only_fields = 'id', 'uploaded_at', 'uploaded_by'

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request.method == 'PUT':
            fields['filehandle'].read_only = True
            fields['uploaded_by'].read_only = True
        return fields

    def create(self, validated_data):
        user = validated_data.pop('uploaded_by')
        return services.create_questionaire(user=user, **validated_data)

    def update(self, questionaire, validated_data):
        return services.update_questionaire(questionaire, **validated_data)
