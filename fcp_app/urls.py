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
    path('api/correlation-matrix/', views.api_correlation_matrix, name='api_correlation_matrix'),
    path('api/volatility-clustering/', views.api_volatility_clustering, name='api_volatility_clustering'),
    path('api/rolling-metrics/', views.api_rolling_metrics, name='api_rolling_metrics'),
    path('api/tail-risk/', views.api_tail_risk, name='api_tail_risk'),
    path('api/calendar-data/', views.api_calendar_data, name='api_calendar_data'),
    path('api/fcp-full-data/', views.api_fcp_full_data, name='api_fcp_full_data'),
]
