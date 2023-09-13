from . import models
from huscy.project_design.services import create_data_acquisition_method


def create_magnetic_resonance_imaging(session, magnetic_resonance_imaging_type, location=''):
    data_acquisition_method = create_data_acquisition_method(session, type='mri', location=location)

    return models.MagneticResonanceImaging.objects.create(
        data_acquisition_method=data_acquisition_method,
        type=magnetic_resonance_imaging_type,
    )


def create_magnetic_resonance_imaging_type(short_name, name):
    return models.MagneticResonanceImagingType.objects.create(
        short_name=short_name,
        name=name,
    )


def delete_magnetic_resonance_imaging(magnetic_resonance_imaging):
    magnetic_resonance_imaging.data_acquisition_method.delete()


def delete_magnetic_resonance_imaging_type(magnetic_resonance_imaging_type):
    magnetic_resonance_imaging_type.delete()


def get_magnetic_resonance_imagings(session):
    return models.MagneticResonanceImaging.objects.filter(data_acquisition_method__session=session)


def get_magnetic_resonance_imaging_types():
    return models.MagneticResonanceImagingType.objects.all()


def update_magnetic_resonance_imaging(magnetic_resonance_imaging, type=None):
    if type is not None and magnetic_resonance_imaging.type != type:
        magnetic_resonance_imaging.type = type
        magnetic_resonance_imaging.save(update_fields=['type'])
    return magnetic_resonance_imaging


def update_magnetic_resonance_imaging_type(magnetic_resonance_imaging_type, name=None):
    if name is not None and magnetic_resonance_imaging_type.name != name:
        magnetic_resonance_imaging_type.name = name
        magnetic_resonance_imaging_type.save(update_fields=['name'])
    return magnetic_resonance_imaging_type
