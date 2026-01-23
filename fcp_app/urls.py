from django.urls import path
from . import views

app_name = 'fcp_app'

urlpatterns = [
    path('', views.valeurs_liquidatives, name='valeurs_liquidatives'),
    path('composition/', views.composition, name='composition'),
    path('exportations/', views.exportations, name='exportations'),
    path('a-propos/', views.a_propos, name='a_propos'),
    path('api/vl-data/', views.api_vl_data, name='api_vl_data'),
    path('api/export-data/', views.api_export_data, name='api_export_data'),
    path('api/export-ppt/', views.api_export_ppt, name='api_export_ppt'),
    path('api/export-pdf/', views.api_export_pdf, name='api_export_pdf'),
    path('api/export-factsheet/', views.api_export_factsheet, name='api_export_factsheet'),
    path('api/factsheet-preview/', views.api_factsheet_preview, name='api_factsheet_preview'),
    path('api/scatter-data/', views.api_scatter_data, name='api_scatter_data'),
    path('api/correlation-matrix/', views.api_correlation_matrix, name='api_correlation_matrix'),
    path('api/volatility-clustering/', views.api_volatility_clustering, name='api_volatility_clustering'),
    path('api/rolling-metrics/', views.api_rolling_metrics, name='api_rolling_metrics'),
    path('api/tail-risk/', views.api_tail_risk, name='api_tail_risk'),
    path('api/calendar-data/', views.api_calendar_data, name='api_calendar_data'),
    path('api/fcp-full-data/', views.api_fcp_full_data, name='api_fcp_full_data'),
]
