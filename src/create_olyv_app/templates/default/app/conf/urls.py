from django.urls import include, path

urlpatterns = [
    path("olyv/", include("olyv.conf.urls")),
    path("", include("app.home.urls")),
    path("dashboard/", include("app.school.urls")),
]
