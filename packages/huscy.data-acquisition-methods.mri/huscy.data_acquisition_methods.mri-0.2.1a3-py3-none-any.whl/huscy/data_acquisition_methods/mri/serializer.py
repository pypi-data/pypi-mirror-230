from rest_framework import serializers

from . import models, services


class MagneticResonanceImagingTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MagneticResonanceImagingType
        fields = (
            'short_name',
            'name',
        )

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request.method == 'POST':
            fields['short_name'].read_only = False
        return fields

    def create(self, validated_data):
        return services.create_magnetic_resonance_imaging_type(**validated_data)

    def update(self, magnetic_resonance_imaging_type, validated_data):
        return services.update_magnetic_resonance_imaging_type(magnetic_resonance_imaging_type,
                                                               **validated_data)


class MagneticResonanceImagingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MagneticResonanceImaging
        fields = (
            'id',
            'data_acquisition_method',
            'type',
        )

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request.method == 'PUT':
            fields['data_acquisition_method'].read_only = True
        return fields

    def create(self, validated_data):
        type = validated_data.pop('type')
        return services.create_magnetic_resonance_imaging(magnetic_resonance_imaging_type=type,
                                                          **validated_data)

    def update(self, magnetic_resonance_imaging, validated_data):
        return services.update_magnetic_resonance_imaging(magnetic_resonance_imaging,
                                                          **validated_data)
