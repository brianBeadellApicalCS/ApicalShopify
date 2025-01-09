from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Apical Order Manager API",
        default_version='v1',
        description="API documentation for Apical Order Manager",
        terms_of_service="https://www.apical.com/terms/",
        contact=openapi.Contact(email="contact@apical.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
) 