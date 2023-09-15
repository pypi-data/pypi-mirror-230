from django.urls import path
from .views import OrganizationsView
from django.conf import settings
from rest_framework.routers import SimpleRouter


router = SimpleRouter()

router.register(r"organizations", OrganizationsView, "Organizations")

urlpatterns = router.urls
