from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('storyteller/', views.storyteller_view, name='storyteller'),
    path('lecture-extractor/', views.lecture_extractor_view, name='lecture_extractor'),
]
