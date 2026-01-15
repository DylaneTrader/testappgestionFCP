from django.urls import path
from . import views

app_name = 'fcp_app'

urlpatterns = [
    path('', views.valeurs_liquidatives, name='valeurs_liquidatives'),
    path('composition/', views.composition, name='composition'),
    path('fiche-signaletique/', views.fiche_signaletique, name='fiche_signaletique'),
    path('a-propos/', views.a_propos, name='a_propos'),
    path('api/vl-data/', views.api_vl_data, name='api_vl_data'),
    path('api/scatter-data/', views.api_scatter_data, name='api_scatter_data'),
]
