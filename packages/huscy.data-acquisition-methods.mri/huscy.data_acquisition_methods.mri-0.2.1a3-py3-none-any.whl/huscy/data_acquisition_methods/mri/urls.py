from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from huscy.project_design.urls import session_router


router = DefaultRouter()
router.register('magnetic_resonance_imaging_types', views.MagneticResonanceImagingTypeViewSet,
                basename='magneticresonanceimagingtype')

session_router.register('magnetic_resonance_imagings', views.MagneticResonanceImagingViewSet,
                        basename='magneticresonanceimaging')


urlpatterns = (
    path('api/', include(router.urls)),
    path('api/', include(session_router.urls)),
)
