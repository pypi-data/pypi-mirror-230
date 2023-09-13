from django.shortcuts import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin, ListModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from . import serializer, services

from huscy.project_design.models import Session


class MagneticResonanceImagingTypeViewSet(ModelViewSet):
    permission_classes = IsAuthenticated, DjangoModelPermissions
    serializer_class = serializer.MagneticResonanceImagingTypeSerializer

    def get_queryset(self):
        return services.get_magnetic_resonance_imaging_types()

    def perform_destroy(self, magnetic_resonance_imaging_type):
        services.delete_magnetic_resonance_imaging_type(magnetic_resonance_imaging_type)


class MagneticResonanceImagingViewSet(CreateModelMixin, DestroyModelMixin, ListModelMixin,
                                      UpdateModelMixin, GenericViewSet):
    permission_classes = IsAuthenticated,
    serializer_class = serializer.MagneticResonanceImagingSerializer

    def initial(self, request, *args, **kwargs):
        self.session = get_object_or_404(
            Session,
            experiment=self.kwargs['experiment_pk'],
            experiment__project=self.kwargs['project_pk'],
            pk=self.kwargs['session_pk'],
        )
        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return services.get_magnetic_resonance_imagings(self.session)

    def perform_create(self, serializer):
        serializer.save(session=self.session)

    def perform_destroy(self, questionaire):
        services.delete_magnetic_resonance_imaging(questionaire)
