from django.urls import path
from . import views

app_name = 'fcp_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('valeurs-liquidatives/', views.valeurs_liquidatives, name='valeurs_liquidatives'),
    path('composition-fcp/', views.composition_fcp, name='composition_fcp'),
    path('fiche-signaletique/', views.fiche_signaletique, name='fiche_signaletique'),
    path('souscriptions-rachats/', views.souscriptions_rachats, name='souscriptions_rachats'),
    path('about/', views.about, name='about'),
]
