from adspresso.routers import NoSlashRouter


from clients.views import ClientViewSet

router = NoSlashRouter()
router.register('', ClientViewSet, basename='clients')

urlpatterns = []

urlpatterns += router.urls