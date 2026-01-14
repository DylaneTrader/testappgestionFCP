from django.urls import path
from . import views

app_name = 'fcp_app'

urlpatterns = [
    path('', views.valeurs_liquidatives, name='valeurs_liquidatives'),
    path('composition/', views.composition, name='composition'),
    path('fiche-signaletique/', views.fiche_signaletique, name='fiche_signaletique'),
    path('a-propos/', views.a_propos, name='a_propos'),
]
