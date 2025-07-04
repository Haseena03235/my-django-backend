from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ImageUploadView, BannerViewSet
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'banners', BannerViewSet)
urlpatterns = router.urls
urlpatterns.append(path('upload-image/', ImageUploadView.as_view(), name='upload-image'))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
