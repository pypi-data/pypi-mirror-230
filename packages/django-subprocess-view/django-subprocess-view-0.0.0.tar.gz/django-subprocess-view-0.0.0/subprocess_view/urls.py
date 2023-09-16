from django.urls import path


from . import views


urlpatterns = [
    path("process", views.process_view, name="subprocess-view-process"),
    path("", views.main_view, name="subprocess-view-main"),
]
