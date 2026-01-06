from django.urls import path
from . import views

app_name = 'fcp_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('valeurs-liquidatives/', views.valeurs_liquidatives, name='valeurs_liquidatives'),
    path('api/performance-data/', views.api_performance_data, name='api_performance_data'),
    path('api/evolution-vl/', views.api_evolution_vl, name='api_evolution_vl'),
    path('composition-fcp/', views.composition_fcp, name='composition_fcp'),
    path('fiche-signaletique/', views.fiche_signaletique, name='fiche_signaletique'),
    path('about/', views.about, name='about'),
]
