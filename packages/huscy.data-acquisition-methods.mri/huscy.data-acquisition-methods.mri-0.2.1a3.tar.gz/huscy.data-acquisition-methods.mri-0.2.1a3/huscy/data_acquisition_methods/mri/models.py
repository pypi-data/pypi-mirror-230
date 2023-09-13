from django.db import models
from django.utils.translation import gettext_lazy as _

from huscy.project_design.models import DataAcquisitionMethod


class MagneticResonanceImagingType(models.Model):
    short_name = models.CharField(_('Short name'), max_length=255, primary_key=True, editable=False)
    name = models.CharField(_('Name'), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = 'name',
        verbose_name = _('Magnetic resonance imaging type')
        verbose_name_plural = _('Magnetic resonance imaging types')


class MagneticResonanceImaging(models.Model):
    data_acquisition_method = models.ForeignKey(DataAcquisitionMethod, on_delete=models.CASCADE,
                                                editable=False,
                                                verbose_name=_('Data acquisition method'))

    type = models.ForeignKey(MagneticResonanceImagingType, on_delete=models.PROTECT,
                             verbose_name=_('Type'))

    def __str__(self):
        return self.type.name

    class Meta:
        ordering = 'data_acquisition_method__order',
        verbose_name = _('Magnetic resonance imaging')
        verbose_name_plural = _('Magnetic resonance imagings')
