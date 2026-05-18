from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('storyteller/', views.storyteller_view, name='storyteller'),
    path('lecture-extractor/', views.lecture_extractor_view, name='lecture_extractor'),
    
    # Rotas de Contratos Inteligentes
    path('contracts/', views.contracts_list_view, name='contracts_list'),
    path('contracts/upload/', views.contract_upload_view, name='contract_upload'),
    path('contracts/<int:contract_id>/', views.contract_detail_view, name='contract_detail'),
    path('contracts/<int:contract_id>/edit/', views.contract_edit_view, name='contract_edit'),
    path('contracts/<int:contract_id>/delete/', views.contract_delete_view, name='contract_delete'),
]
