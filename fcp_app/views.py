from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Min, Max, Avg
from decimal import Decimal
import json
from datetime import datetime, timedelta
from .data import (
    FCP_FICHE_SIGNALETIQUE, 
    get_all_fcp_names, 
    get_fcp_data, 
    get_risk_label,
    get_type_icon,
    get_type_color
)
from .models import FicheSignaletique, FCP_VL_MODELS, get_vl_model

# Create your views here.


def valeurs_liquidatives(request):
    """Vue pour la page des Valeurs Liquidatives"""
    # Récupérer le FCP sélectionné
    selected_fcp = request.GET.get('fcp', 'FCP PLACEMENT AVANTAGE')
    
    # Liste des FCP depuis la base
    fcp_list = list(FicheSignaletique.objects.values_list('nom', flat=True).order_by('nom'))
    
    # Récupérer les données VL pour le FCP sélectionné
    vl_model = get_vl_model(selected_fcp)
    vl_data = []
    stats = {}
    perf_calendaires = {}
    perf_glissantes = {}
    analyse_stats = {}
    tracking_error = {}
    
    if vl_model:
        # Récupérer toutes les VL ordonnées par date
        vl_queryset = vl_model.objects.all().order_by('date')
        
        # Convertir en liste pour JSON
        for vl in vl_queryset:
            vl_data.append({
                'date': vl.date.strftime('%Y-%m-%d'),
                'valeur': float(vl.valeur)
            })
        
        # Calculer les statistiques
        if vl_queryset.exists():
            latest_vl = vl_queryset.last()
            first_vl = vl_queryset.first()
            today = latest_vl.date  # Dernière date de la base (pas la date du jour)
            
            # Helper pour calculer la performance
            def calc_perf(vl_ref):
                if vl_ref:
                    return round(((float(latest_vl.valeur) / float(vl_ref.valeur)) - 1) * 100, 2)
                return None
            
            # VL pour différentes périodes GLISSANTES (depuis la dernière date en base)
            vl_1d = vl_queryset.filter(date__lt=today).last()
            vl_1m = vl_queryset.filter(date__lte=today - timedelta(days=30)).last()
            vl_3m = vl_queryset.filter(date__lte=today - timedelta(days=90)).last()
            vl_6m = vl_queryset.filter(date__lte=today - timedelta(days=180)).last()
            vl_1y = vl_queryset.filter(date__lte=today - timedelta(days=365)).last()
            vl_3y = vl_queryset.filter(date__lte=today - timedelta(days=365*3)).last()
            vl_5y = vl_queryset.filter(date__lte=today - timedelta(days=365*5)).last()
            
            # Performances calendaires (To-Date) - basées sur la dernière date en base
            # WTD: dernière VL de la semaine précédente (vendredi ou avant le lundi de cette semaine)
            start_of_week = today - timedelta(days=today.weekday())  # Lundi de la semaine
            vl_wtd = vl_queryset.filter(date__lt=start_of_week).last()
            
            # MTD: dernière VL du mois précédent (dernier jour avant le 1er du mois)
            start_of_month = today.replace(day=1)
            vl_mtd = vl_queryset.filter(date__lt=start_of_month).last()
            
            # QTD: dernière VL du trimestre précédent
            quarter_month = ((today.month - 1) // 3) * 3 + 1
            start_of_quarter = today.replace(month=quarter_month, day=1)
            vl_qtd = vl_queryset.filter(date__lt=start_of_quarter).last()
            
            # STD: dernière VL du semestre précédent
            semester_month = 1 if today.month <= 6 else 7
            start_of_semester = today.replace(month=semester_month, day=1)
            vl_std = vl_queryset.filter(date__lt=start_of_semester).last()
            
            # YTD: dernière VL de l'année précédente (dernier jour avant le 1er janvier)
            start_of_year = today.replace(month=1, day=1)
            vl_ytd = vl_queryset.filter(date__lt=start_of_year).last()
            
            perf_calendaires = {
                'wtd': calc_perf(vl_wtd),
                'mtd': calc_perf(vl_mtd),
                'qtd': calc_perf(vl_qtd),
                'std': calc_perf(vl_std),
                'ytd': calc_perf(vl_ytd),
            }
            
            # Performances glissantes
            perf_glissantes = {
                'perf_1m': calc_perf(vl_1m),
                'perf_3m': calc_perf(vl_3m),
                'perf_6m': calc_perf(vl_6m),
                'perf_1y': calc_perf(vl_1y),
                'perf_3y': calc_perf(vl_3y),
                'perf_5y': calc_perf(vl_5y),
                'origine': calc_perf(first_vl),
            }
            
            stats = {
                'derniere_vl': float(latest_vl.valeur),
                'derniere_date': latest_vl.date.strftime('%d/%m/%Y'),
                'premiere_vl': float(first_vl.valeur),
                'premiere_date': first_vl.date.strftime('%d/%m/%Y'),
                'var_1j': calc_perf(vl_1d) or 0,
                'var_1m': calc_perf(vl_1m) or 0,
                'var_1y': calc_perf(vl_1y) or 0,
                'var_ytd': perf_calendaires['ytd'] or 0,
                'var_origine': perf_glissantes['origine'] or 0,
                'nb_vl': vl_queryset.count(),
            }
            
            # Calculer la Tracking Error (volatilité annualisée) pour différentes périodes
            def calc_tracking_error(start_date):
                """Calcule la tracking error (volatilité annualisée) depuis une date de référence"""
                if start_date is None:
                    return None
                period_vl = list(vl_queryset.filter(date__gte=start_date).values_list('valeur', flat=True))
                if len(period_vl) < 2:
                    return None
                period_valeurs = [float(v) for v in period_vl]
                period_rendements = [(period_valeurs[i] / period_valeurs[i-1] - 1) * 100 for i in range(1, len(period_valeurs))]
                if len(period_rendements) < 2:
                    return None
                moyenne = sum(period_rendements) / len(period_rendements)
                variance = sum((r - moyenne) ** 2 for r in period_rendements) / len(period_rendements)
                ecart_type = variance ** 0.5
                # Annualiser la volatilité
                volatilite_ann = ecart_type * (365 ** 0.5)
                return round(volatilite_ann, 2)
            
            tracking_error = {
                'wtd': calc_tracking_error(start_of_week),
                'mtd': calc_tracking_error(start_of_month),
                'qtd': calc_tracking_error(start_of_quarter),
                'std': calc_tracking_error(start_of_semester),
                'ytd': calc_tracking_error(start_of_year),
                'origine': calc_tracking_error(first_vl.date if first_vl else None),
            }
            
            # Calculer les statistiques pour l'onglet Analyse
            valeurs = [float(v) for v in vl_queryset.values_list('valeur', flat=True)]
            if len(valeurs) > 1:
                rendements = [(valeurs[i] / valeurs[i-1] - 1) * 100 for i in range(1, len(valeurs))]
                
                # Statistiques descriptives
                moyenne_rdt = sum(rendements) / len(rendements)
                variance = sum((r - moyenne_rdt) ** 2 for r in rendements) / len(rendements)
                ecart_type = variance ** 0.5
                volatilite_ann = ecart_type * (365 ** 0.5)
                
                rendements_sorted = sorted(rendements)
                n = len(rendements_sorted)
                mediane = rendements_sorted[n // 2] if n % 2 == 1 else (rendements_sorted[n//2 - 1] + rendements_sorted[n//2]) / 2
                
                # Min/Max
                vl_min = min(valeurs)
                vl_max = max(valeurs)
                rdt_min = min(rendements)
                rdt_max = max(rendements)
                
                # Jours positifs/négatifs
                jours_positifs = sum(1 for r in rendements if r > 0)
                jours_negatifs = sum(1 for r in rendements if r < 0)
                
                # Drawdown max
                peak = valeurs[0]
                max_drawdown = 0
                for v in valeurs:
                    if v > peak:
                        peak = v
                    drawdown = (peak - v) / peak * 100
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
                
                # Ratio de Sharpe (avec taux sans risque de 3,25%)
                rf = 3.25 / 365  # Taux sans risque quotidien
                sharpe = ((moyenne_rdt - rf) / ecart_type * (365 ** 0.5)) if ecart_type > 0 else 0
                
                # Ratio de Sortino
                rendements_negatifs = [r for r in rendements if r < 0]
                if rendements_negatifs:
                    downside_var = sum(r ** 2 for r in rendements_negatifs) / len(rendements_negatifs)
                    downside_std = downside_var ** 0.5
                    sortino = ((moyenne_rdt - rf) / downside_std * (365 ** 0.5)) if downside_std > 0 else 0
                else:
                    sortino = 0
                
                # Skewness (asymétrie)
                if ecart_type > 0:
                    skewness = sum((r - moyenne_rdt) ** 3 for r in rendements) / (n * ecart_type ** 3)
                else:
                    skewness = 0
                
                # Kurtosis (aplatissement) - excess kurtosis (0 pour normal)
                if ecart_type > 0:
                    kurtosis = sum((r - moyenne_rdt) ** 4 for r in rendements) / (n * ecart_type ** 4) - 3
                else:
                    kurtosis = 0
                
                # VaR Historique (Value at Risk)
                var_95 = rendements_sorted[int(n * 0.05)]  # 5ème percentile
                var_99 = rendements_sorted[int(n * 0.01)]  # 1er percentile
                
                # CVaR / Expected Shortfall (moyenne des pertes au-delà de la VaR)
                cvar_95_values = [r for r in rendements if r <= var_95]
                cvar_99_values = [r for r in rendements if r <= var_99]
                cvar_95 = sum(cvar_95_values) / len(cvar_95_values) if cvar_95_values else var_95
                cvar_99 = sum(cvar_99_values) / len(cvar_99_values) if cvar_99_values else var_99
                
                # Calcul des drawdowns détaillés
                drawdowns_data = []
                dates_list = list(vl_queryset.values_list('date', flat=True))
                peak = valeurs[0]
                peak_date = dates_list[0]
                current_dd_start = None
                current_dd_peak = valeurs[0]
                
                underwater_data = []  # Pour le graphique underwater
                
                for i, v in enumerate(valeurs):
                    if v > peak:
                        # Nouveau pic atteint
                        if current_dd_start is not None:
                            # Fin du drawdown précédent
                            dd_depth = (current_dd_peak - min(valeurs[current_dd_start:i])) / current_dd_peak * 100
                            dd_trough_idx = current_dd_start + valeurs[current_dd_start:i].index(min(valeurs[current_dd_start:i]))
                            drawdowns_data.append({
                                'start_date': dates_list[current_dd_start].strftime('%Y-%m-%d'),
                                'trough_date': dates_list[dd_trough_idx].strftime('%Y-%m-%d'),
                                'end_date': dates_list[i].strftime('%Y-%m-%d'),
                                'depth': round(dd_depth, 2),
                                'duration': i - current_dd_start,
                                'recovery': i - dd_trough_idx
                            })
                            current_dd_start = None
                        peak = v
                        peak_date = dates_list[i]
                        current_dd_peak = v
                    else:
                        if current_dd_start is None and v < peak:
                            current_dd_start = i - 1 if i > 0 else 0
                            current_dd_peak = peak
                    
                    # Calculer le drawdown courant pour underwater chart
                    dd_current = (peak - v) / peak * 100
                    underwater_data.append({
                        'date': dates_list[i].strftime('%Y-%m-%d'),
                        'drawdown': round(-dd_current, 2)  # Négatif pour l'affichage
                    })
                
                # Si on est encore en drawdown à la fin
                if current_dd_start is not None:
                    dd_depth = (current_dd_peak - min(valeurs[current_dd_start:])) / current_dd_peak * 100
                    dd_trough_idx = current_dd_start + valeurs[current_dd_start:].index(min(valeurs[current_dd_start:]))
                    drawdowns_data.append({
                        'start_date': dates_list[current_dd_start].strftime('%Y-%m-%d'),
                        'trough_date': dates_list[dd_trough_idx].strftime('%Y-%m-%d'),
                        'end_date': None,  # Encore en cours
                        'depth': round(dd_depth, 2),
                        'duration': len(valeurs) - current_dd_start,
                        'recovery': None  # Pas encore récupéré
                    })
                
                # Trier les drawdowns par profondeur (les pires en premier)
                drawdowns_data.sort(key=lambda x: x['depth'], reverse=True)
                
                # Histogramme des rendements (bins)
                hist_min = min(rendements)
                hist_max = max(rendements)
                nb_bins = 30
                bin_width = (hist_max - hist_min) / nb_bins if hist_max != hist_min else 1
                histogram_data = []
                for i in range(nb_bins):
                    bin_start = hist_min + i * bin_width
                    bin_end = bin_start + bin_width
                    count = sum(1 for r in rendements if bin_start <= r < bin_end)
                    histogram_data.append({
                        'bin_start': round(bin_start, 3),
                        'bin_end': round(bin_end, 3),
                        'count': count,
                        'frequency': round(count / n * 100, 2)
                    })
                
                stats['volatilite'] = round(volatilite_ann, 2)
                
                analyse_stats = {
                    # Statistiques descriptives
                    'nb_observations': len(rendements),
                    'rendement_moyen': round(moyenne_rdt, 4),
                    'rendement_moyen_ann': round(moyenne_rdt * 365, 2),
                    'mediane': round(mediane, 4),
                    'ecart_type': round(ecart_type, 4),
                    'volatilite_ann': round(volatilite_ann, 2),
                    'vl_min': round(vl_min, 2),
                    'vl_max': round(vl_max, 2),
                    'rdt_min': round(rdt_min, 2),
                    'rdt_max': round(rdt_max, 2),
                    # Profil de risque
                    'max_drawdown': round(max_drawdown, 2),
                    'sharpe': round(sharpe, 2),
                    'sortino': round(sortino, 2),
                    'jours_positifs': jours_positifs,
                    'jours_negatifs': jours_negatifs,
                    'ratio_positif': round(jours_positifs / len(rendements) * 100, 1) if rendements else 0,
                    # Distribution des rendements
                    'skewness': round(skewness, 3),
                    'kurtosis': round(kurtosis, 3),
                    'var_95': round(var_95, 3),
                    'var_99': round(var_99, 3),
                    'cvar_95': round(cvar_95, 3),
                    'cvar_99': round(cvar_99, 3),
                    # Données pour graphiques (JSON)
                    'histogram_data': histogram_data,
                    'underwater_data': underwater_data,
                    'drawdowns_data': drawdowns_data[:10],  # Top 10 drawdowns
                    'rendements_list': [round(r, 4) for r in rendements],  # Pour histogramme JS
                }
            else:
                stats['volatilite'] = 0
                analyse_stats = {}
    
    # Préparer les données pour tous les FCP (pour le scatter plot)
    all_fcp_stats = []
    for fcp_name in fcp_list:
        fcp_vl_model = get_vl_model(fcp_name)
        if fcp_vl_model:
            fcp_vl = fcp_vl_model.objects.all().order_by('date')
            if fcp_vl.exists() and fcp_vl.count() > 30:
                first = fcp_vl.first()
                last = fcp_vl.last()
                rendement = ((float(last.valeur) / float(first.valeur)) - 1) * 100
                
                # Calculer volatilité
                valeurs = list(fcp_vl.values_list('valeur', flat=True))
                rendements = [(float(valeurs[i]) / float(valeurs[i-1]) - 1) for i in range(1, len(valeurs))]
                if rendements:
                    moyenne = sum(rendements) / len(rendements)
                    variance = sum((r - moyenne) ** 2 for r in rendements) / len(rendements)
                    vol = (variance ** 0.5) * (365 ** 0.5) * 100
                else:
                    vol = 0
                
                # Récupérer le type de fond depuis FicheSignaletique
                try:
                    fiche = FicheSignaletique.objects.get(nom=fcp_name)
                    type_fond = fiche.type_fond
                except FicheSignaletique.DoesNotExist:
                    type_fond = 'Diversifié'
                
                all_fcp_stats.append({
                    'nom': fcp_name,
                    'rendement': round(rendement, 2),
                    'volatilite': round(vol, 2),
                    'type_fond': type_fond,
                    'selected': fcp_name == selected_fcp
                })
    
    # Extraire les données pour les graphiques (JSON)
    histogram_data_json = json.dumps(analyse_stats.get('histogram_data', []))
    underwater_data_json = json.dumps(analyse_stats.get('underwater_data', []))
    drawdowns_data_json = json.dumps(analyse_stats.get('drawdowns_data', []))
    rendements_list_json = json.dumps(analyse_stats.get('rendements_list', []))
    
    context = {
        'page_title': 'Valeurs Liquidatives',
        'page_description': 'Suivi et historique des valeurs liquidatives des FCP',
        'fcp_list': fcp_list,
        'selected_fcp': selected_fcp,
        'vl_data_json': json.dumps(vl_data),
        'stats': stats,
        'perf_calendaires': perf_calendaires,
        'perf_glissantes': perf_glissantes,
        'analyse_stats': analyse_stats,
        'tracking_error': tracking_error,
        'all_fcp_stats_json': json.dumps(all_fcp_stats),
        'histogram_data_json': histogram_data_json,
        'underwater_data_json': underwater_data_json,
        'drawdowns_data_json': drawdowns_data_json,
        'rendements_list_json': rendements_list_json,
    }
    return render(request, 'fcp_app/valeurs_liquidatives.html', context)


def api_scatter_data(request):
    """API pour récupérer les données du scatter plot avec filtre de période"""
    period = request.GET.get('period', 'origin')
    
    fcp_list = list(FicheSignaletique.objects.values_list('nom', flat=True).order_by('nom'))
    all_fcp_stats = []
    
    for fcp_name in fcp_list:
        fcp_vl_model = get_vl_model(fcp_name)
        if fcp_vl_model:
            fcp_vl = fcp_vl_model.objects.all().order_by('date')
            if fcp_vl.exists() and fcp_vl.count() > 30:
                last = fcp_vl.last()
                latest_date = last.date  # Dernière date disponible en base
                
                # Pour les calculs To-Date, on cherche la dernière VL avant le début de la période
                if period == 'wtd':  # Week-to-Date (depuis le lundi de cette semaine)
                    start_of_week = latest_date - timedelta(days=latest_date.weekday())
                    ref_vl = fcp_vl.filter(date__lt=start_of_week).last()
                elif period == 'mtd':  # Month-to-Date (depuis le début du mois)
                    start_of_month = latest_date.replace(day=1)
                    ref_vl = fcp_vl.filter(date__lt=start_of_month).last()
                elif period == 'qtd':  # Quarter-to-Date (depuis le début du trimestre)
                    quarter_month = ((latest_date.month - 1) // 3) * 3 + 1
                    start_of_quarter = latest_date.replace(month=quarter_month, day=1)
                    ref_vl = fcp_vl.filter(date__lt=start_of_quarter).last()
                elif period == 'std':  # Semester-to-Date (depuis le début du semestre)
                    semester_month = 1 if latest_date.month <= 6 else 7
                    start_of_semester = latest_date.replace(month=semester_month, day=1)
                    ref_vl = fcp_vl.filter(date__lt=start_of_semester).last()
                elif period == 'ytd':  # Year-to-Date (depuis le début de l'année)
                    start_of_year = latest_date.replace(month=1, day=1)
                    ref_vl = fcp_vl.filter(date__lt=start_of_year).last()
                else:  # origin - depuis le début des données
                    ref_vl = fcp_vl.first()
                
                if ref_vl:
                    # Calculer le rendement
                    rendement = ((float(last.valeur) / float(ref_vl.valeur)) - 1) * 100
                    
                    # Calculer la volatilité sur la période sélectionnée
                    if period == 'origin':
                        filtered_vl = fcp_vl
                    else:
                        # Filtrer depuis la date de référence jusqu'à la dernière date
                        filtered_vl = fcp_vl.filter(date__gte=ref_vl.date)
                    
                    valeurs = list(filtered_vl.values_list('valeur', flat=True))
                    if len(valeurs) > 1:
                        rendements = [(float(valeurs[i]) / float(valeurs[i-1]) - 1) for i in range(1, len(valeurs))]
                        if rendements:
                            moyenne = sum(rendements) / len(rendements)
                            variance = sum((r - moyenne) ** 2 for r in rendements) / len(rendements)
                            vol = (variance ** 0.5) * (365 ** 0.5) * 100
                        else:
                            vol = 0
                    else:
                        vol = 0
                    
                    # Récupérer le type de fond
                    try:
                        fiche = FicheSignaletique.objects.get(nom=fcp_name)
                        type_fond = fiche.type_fond
                    except FicheSignaletique.DoesNotExist:
                        type_fond = 'Diversifié'
                    
                    all_fcp_stats.append({
                        'nom': fcp_name,
                        'rendement': round(rendement, 2),
                        'volatilite': round(vol, 2),
                        'type_fond': type_fond
                    })
    
    # Récupérer la dernière date de la base (prendre la première disponible)
    last_date_str = None
    for fcp_name in fcp_list:
        fcp_vl_model = get_vl_model(fcp_name)
        if fcp_vl_model:
            last_vl = fcp_vl_model.objects.order_by('-date').first()
            if last_vl:
                last_date_str = last_vl.date.strftime('%d/%m/%Y')
                break
    
    return JsonResponse({'data': all_fcp_stats, 'last_date': last_date_str})


def api_vl_data(request):
    """API pour récupérer les données VL d'un FCP"""
    fcp_name = request.GET.get('fcp')
    period = request.GET.get('period', 'all')
    
    if not fcp_name:
        return JsonResponse({'error': 'FCP non spécifié'}, status=400)
    
    vl_model = get_vl_model(fcp_name)
    if not vl_model:
        return JsonResponse({'error': 'FCP non trouvé'}, status=404)
    
    # Filtrer par période
    vl_queryset = vl_model.objects.all().order_by('date')
    
    if vl_queryset.exists():
        latest_date = vl_queryset.last().date
        
        if period == '1m':
            start_date = latest_date - timedelta(days=30)
        elif period == '3m':
            start_date = latest_date - timedelta(days=90)
        elif period == '6m':
            start_date = latest_date - timedelta(days=180)
        elif period == '1y':
            start_date = latest_date - timedelta(days=365)
        elif period == '5y':
            start_date = latest_date - timedelta(days=365*5)
        else:
            start_date = None
        
        if start_date:
            vl_queryset = vl_queryset.filter(date__gte=start_date)
    
    data = []
    for vl in vl_queryset:
        data.append({
            'date': vl.date.strftime('%Y-%m-%d'),
            'valeur': float(vl.valeur)
        })
    
    return JsonResponse({'data': data})


def api_fcp_full_data(request):
    """API pour récupérer toutes les données d'un FCP (pour mise à jour dynamique)"""
    fcp_name = request.GET.get('fcp')
    
    if not fcp_name:
        return JsonResponse({'error': 'FCP non spécifié'}, status=400)
    
    vl_model = get_vl_model(fcp_name)
    if not vl_model:
        return JsonResponse({'error': 'FCP non trouvé'}, status=404)
    
    vl_data = []
    stats = {}
    perf_calendaires = {}
    perf_glissantes = {}
    analyse_stats = {}
    tracking_error = {}
    
    vl_queryset = vl_model.objects.all().order_by('date')
    
    # Convertir en liste pour JSON
    for vl in vl_queryset:
        vl_data.append({
            'date': vl.date.strftime('%Y-%m-%d'),
            'valeur': float(vl.valeur)
        })
    
    # Calculer les statistiques
    if vl_queryset.exists():
        latest_vl = vl_queryset.last()
        first_vl = vl_queryset.first()
        today = latest_vl.date
        
        def calc_perf(vl_ref):
            if vl_ref:
                return round(((float(latest_vl.valeur) / float(vl_ref.valeur)) - 1) * 100, 2)
            return None
        
        # VL pour différentes périodes GLISSANTES
        vl_1d = vl_queryset.filter(date__lt=today).last()
        vl_1m = vl_queryset.filter(date__lte=today - timedelta(days=30)).last()
        vl_3m = vl_queryset.filter(date__lte=today - timedelta(days=90)).last()
        vl_6m = vl_queryset.filter(date__lte=today - timedelta(days=180)).last()
        vl_1y = vl_queryset.filter(date__lte=today - timedelta(days=365)).last()
        vl_3y = vl_queryset.filter(date__lte=today - timedelta(days=365*3)).last()
        vl_5y = vl_queryset.filter(date__lte=today - timedelta(days=365*5)).last()
        
        # Performances calendaires (To-Date)
        start_of_week = today - timedelta(days=today.weekday())
        vl_wtd = vl_queryset.filter(date__lt=start_of_week).last()
        
        start_of_month = today.replace(day=1)
        vl_mtd = vl_queryset.filter(date__lt=start_of_month).last()
        
        quarter_month = ((today.month - 1) // 3) * 3 + 1
        start_of_quarter = today.replace(month=quarter_month, day=1)
        vl_qtd = vl_queryset.filter(date__lt=start_of_quarter).last()
        
        semester_month = 1 if today.month <= 6 else 7
        start_of_semester = today.replace(month=semester_month, day=1)
        vl_std = vl_queryset.filter(date__lt=start_of_semester).last()
        
        start_of_year = today.replace(month=1, day=1)
        vl_ytd = vl_queryset.filter(date__lt=start_of_year).last()
        
        perf_calendaires = {
            'wtd': calc_perf(vl_wtd),
            'mtd': calc_perf(vl_mtd),
            'qtd': calc_perf(vl_qtd),
            'std': calc_perf(vl_std),
            'ytd': calc_perf(vl_ytd),
        }
        
        perf_glissantes = {
            'perf_1m': calc_perf(vl_1m),
            'perf_3m': calc_perf(vl_3m),
            'perf_6m': calc_perf(vl_6m),
            'perf_1y': calc_perf(vl_1y),
            'perf_3y': calc_perf(vl_3y),
            'perf_5y': calc_perf(vl_5y),
            'origine': calc_perf(first_vl),
        }
        
        stats = {
            'derniere_vl': float(latest_vl.valeur),
            'derniere_date': latest_vl.date.strftime('%d/%m/%Y'),
            'premiere_vl': float(first_vl.valeur),
            'premiere_date': first_vl.date.strftime('%d/%m/%Y'),
            'var_1j': calc_perf(vl_1d) or 0,
            'var_1m': calc_perf(vl_1m) or 0,
            'var_1y': calc_perf(vl_1y) or 0,
            'var_ytd': perf_calendaires['ytd'] or 0,
            'var_origine': perf_glissantes['origine'] or 0,
            'nb_vl': vl_queryset.count(),
        }
        
        # Calculer la Tracking Error pour différentes périodes
        def calc_tracking_error(start_date):
            if start_date is None:
                return None
            period_vl = list(vl_queryset.filter(date__gte=start_date).values_list('valeur', flat=True))
            if len(period_vl) < 2:
                return None
            period_valeurs = [float(v) for v in period_vl]
            period_rendements = [(period_valeurs[i] / period_valeurs[i-1] - 1) * 100 for i in range(1, len(period_valeurs))]
            if len(period_rendements) < 2:
                return None
            moyenne = sum(period_rendements) / len(period_rendements)
            variance = sum((r - moyenne) ** 2 for r in period_rendements) / len(period_rendements)
            ecart_type = variance ** 0.5
            volatilite_ann = ecart_type * (365 ** 0.5)
            return round(volatilite_ann, 2)
        
        tracking_error = {
            'wtd': calc_tracking_error(start_of_week),
            'mtd': calc_tracking_error(start_of_month),
            'qtd': calc_tracking_error(start_of_quarter),
            'std': calc_tracking_error(start_of_semester),
            'ytd': calc_tracking_error(start_of_year),
            'origine': calc_tracking_error(first_vl.date if first_vl else None),
        }
        
        # Calculer les statistiques pour l'analyse
        valeurs = [float(v) for v in vl_queryset.values_list('valeur', flat=True)]
        if len(valeurs) > 1:
            rendements = [(valeurs[i] / valeurs[i-1] - 1) * 100 for i in range(1, len(valeurs))]
            
            moyenne_rdt = sum(rendements) / len(rendements)
            variance = sum((r - moyenne_rdt) ** 2 for r in rendements) / len(rendements)
            ecart_type = variance ** 0.5
            volatilite_ann = ecart_type * (365 ** 0.5)
            
            rendements_sorted = sorted(rendements)
            n = len(rendements_sorted)
            mediane = rendements_sorted[n // 2] if n % 2 == 1 else (rendements_sorted[n//2 - 1] + rendements_sorted[n//2]) / 2
            
            vl_min = min(valeurs)
            vl_max = max(valeurs)
            rdt_min = min(rendements)
            rdt_max = max(rendements)
            
            jours_positifs = sum(1 for r in rendements if r > 0)
            jours_negatifs = sum(1 for r in rendements if r < 0)
            
            # Drawdown max
            peak = valeurs[0]
            max_drawdown = 0
            for v in valeurs:
                if v > peak:
                    peak = v
                drawdown = (peak - v) / peak * 100
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            rf = 3.25 / 365
            sharpe = ((moyenne_rdt - rf) / ecart_type * (365 ** 0.5)) if ecart_type > 0 else 0
            
            rendements_negatifs = [r for r in rendements if r < 0]
            if rendements_negatifs:
                downside_var = sum(r ** 2 for r in rendements_negatifs) / len(rendements_negatifs)
                downside_std = downside_var ** 0.5
                sortino = ((moyenne_rdt - rf) / downside_std * (365 ** 0.5)) if downside_std > 0 else 0
            else:
                sortino = 0
            
            # Skewness et Kurtosis
            if ecart_type > 0:
                skewness = sum((r - moyenne_rdt) ** 3 for r in rendements) / (n * ecart_type ** 3)
                kurtosis = sum((r - moyenne_rdt) ** 4 for r in rendements) / (n * ecart_type ** 4) - 3
            else:
                skewness = 0
                kurtosis = 0
            
            # VaR et CVaR
            var_95 = rendements_sorted[int(n * 0.05)]
            var_99 = rendements_sorted[int(n * 0.01)]
            cvar_95_values = [r for r in rendements if r <= var_95]
            cvar_99_values = [r for r in rendements if r <= var_99]
            cvar_95 = sum(cvar_95_values) / len(cvar_95_values) if cvar_95_values else var_95
            cvar_99 = sum(cvar_99_values) / len(cvar_99_values) if cvar_99_values else var_99
            
            # Drawdowns détaillés
            drawdowns_data = []
            dates_list = list(vl_queryset.values_list('date', flat=True))
            peak = valeurs[0]
            current_dd_start = None
            current_dd_peak = valeurs[0]
            underwater_data = []
            
            for i, v in enumerate(valeurs):
                if v > peak:
                    if current_dd_start is not None:
                        dd_depth = (current_dd_peak - min(valeurs[current_dd_start:i])) / current_dd_peak * 100
                        dd_trough_idx = current_dd_start + valeurs[current_dd_start:i].index(min(valeurs[current_dd_start:i]))
                        drawdowns_data.append({
                            'start_date': dates_list[current_dd_start].strftime('%Y-%m-%d'),
                            'trough_date': dates_list[dd_trough_idx].strftime('%Y-%m-%d'),
                            'end_date': dates_list[i].strftime('%Y-%m-%d'),
                            'depth': round(dd_depth, 2),
                            'duration': i - current_dd_start,
                            'recovery': i - dd_trough_idx
                        })
                        current_dd_start = None
                    peak = v
                    current_dd_peak = v
                else:
                    if current_dd_start is None and v < peak:
                        current_dd_start = i - 1 if i > 0 else 0
                        current_dd_peak = peak
                
                dd_current = (peak - v) / peak * 100
                underwater_data.append({
                    'date': dates_list[i].strftime('%Y-%m-%d'),
                    'drawdown': round(-dd_current, 2)
                })
            
            if current_dd_start is not None:
                dd_depth = (current_dd_peak - min(valeurs[current_dd_start:])) / current_dd_peak * 100
                dd_trough_idx = current_dd_start + valeurs[current_dd_start:].index(min(valeurs[current_dd_start:]))
                drawdowns_data.append({
                    'start_date': dates_list[current_dd_start].strftime('%Y-%m-%d'),
                    'trough_date': dates_list[dd_trough_idx].strftime('%Y-%m-%d'),
                    'end_date': None,
                    'depth': round(dd_depth, 2),
                    'duration': len(valeurs) - current_dd_start,
                    'recovery': None
                })
            
            drawdowns_data.sort(key=lambda x: x['depth'], reverse=True)
            
            # Histogramme
            hist_min = min(rendements)
            hist_max = max(rendements)
            nb_bins = 30
            bin_width = (hist_max - hist_min) / nb_bins if hist_max != hist_min else 1
            histogram_data = []
            for i in range(nb_bins):
                bin_start = hist_min + i * bin_width
                bin_end = bin_start + bin_width
                count = sum(1 for r in rendements if bin_start <= r < bin_end)
                histogram_data.append({
                    'bin_start': round(bin_start, 3),
                    'bin_end': round(bin_end, 3),
                    'count': count,
                    'frequency': round(count / n * 100, 2)
                })
            
            stats['volatilite'] = round(volatilite_ann, 2)
            
            analyse_stats = {
                'nb_observations': len(rendements),
                'rendement_moyen': round(moyenne_rdt, 4),
                'rendement_moyen_ann': round(moyenne_rdt * 365, 2),
                'mediane': round(mediane, 4),
                'ecart_type': round(ecart_type, 4),
                'volatilite_ann': round(volatilite_ann, 2),
                'vl_min': round(vl_min, 2),
                'vl_max': round(vl_max, 2),
                'rdt_min': round(rdt_min, 2),
                'rdt_max': round(rdt_max, 2),
                'max_drawdown': round(max_drawdown, 2),
                'sharpe': round(sharpe, 2),
                'sortino': round(sortino, 2),
                'jours_positifs': jours_positifs,
                'jours_negatifs': jours_negatifs,
                'ratio_positif': round(jours_positifs / len(rendements) * 100, 1) if rendements else 0,
                'skewness': round(skewness, 3),
                'kurtosis': round(kurtosis, 3),
                'var_95': round(var_95, 3),
                'var_99': round(var_99, 3),
                'cvar_95': round(cvar_95, 3),
                'cvar_99': round(cvar_99, 3),
                'histogram_data': histogram_data,
                'underwater_data': underwater_data,
                'drawdowns_data': drawdowns_data[:10],
                'rendements_list': [round(r, 4) for r in rendements],
            }
        else:
            stats['volatilite'] = 0
            tracking_error = {}
    
    return JsonResponse({
        'fcp_name': fcp_name,
        'vl_data': vl_data,
        'stats': stats,
        'perf_calendaires': perf_calendaires,
        'perf_glissantes': perf_glissantes,
        'analyse_stats': analyse_stats,
        'tracking_error': tracking_error
    })


def composition(request):
    """Vue pour la page de Composition"""
    context = {
        'page_title': 'Composition',
        'page_description': 'Composition détaillée du portefeuille FCP',
        'fcp_list': get_all_fcp_names(),
    }
    return render(request, 'fcp_app/composition.html', context)


def fiche_signaletique(request):
    """Vue pour la page Fiche Signalétique"""
    selected_fcp = request.GET.get('fcp', 'FCP PLACEMENT AVANTAGE')
    fcp_data = get_fcp_data(selected_fcp)
    
    # Préparer les données enrichies pour tous les FCP
    fcp_enriched = {}
    for name, data in FCP_FICHE_SIGNALETIQUE.items():
        fcp_enriched[name] = {
            **data,
            'risk_label': get_risk_label(data['echelle_risque']),
            'type_icon': get_type_icon(data['type_fond']),
            'type_color': get_type_color(data['type_fond']),
        }
    
    context = {
        'page_title': 'Fiche Signalétique',
        'page_description': 'Informations générales et caractéristiques des FCP',
        'fcp_list': get_all_fcp_names(),
        'fcp_data': fcp_enriched,
        'selected_fcp': selected_fcp,
        'selected_fcp_data': {
            **fcp_data,
            'risk_label': get_risk_label(fcp_data['echelle_risque']),
            'type_icon': get_type_icon(fcp_data['type_fond']),
            'type_color': get_type_color(fcp_data['type_fond']),
        } if fcp_data else None,
    }
    return render(request, 'fcp_app/fiche_signaletique.html', context)


def a_propos(request):
    """Vue pour la page A Propos"""
    context = {
        'page_title': 'À Propos',
        'page_description': 'Informations sur l\'application de reporting FCP',
        'total_fcp': len(FCP_FICHE_SIGNALETIQUE),
    }
    return render(request, 'fcp_app/a_propos.html', context)


def api_correlation_matrix(request):
    """API pour calculer la matrice de corrélation entre les FCP"""
    period = request.GET.get('period', 'origin')
    
    fcp_list = list(FicheSignaletique.objects.values_list('nom', flat=True).order_by('nom'))
    
    # Récupérer les rendements de chaque FCP pour la période sélectionnée
    fcp_returns = {}
    fcp_dates = {}
    
    for fcp_name in fcp_list:
        fcp_vl_model = get_vl_model(fcp_name)
        if fcp_vl_model:
            fcp_vl = fcp_vl_model.objects.all().order_by('date')
            if fcp_vl.exists() and fcp_vl.count() > 10:
                last = fcp_vl.last()
                latest_date = last.date
                
                # Déterminer la date de début selon la période
                if period == 'wtd':
                    start_of_period = latest_date - timedelta(days=latest_date.weekday())
                    ref_vl = fcp_vl.filter(date__lt=start_of_period).last()
                elif period == 'mtd':
                    start_of_period = latest_date.replace(day=1)
                    ref_vl = fcp_vl.filter(date__lt=start_of_period).last()
                elif period == 'qtd':
                    quarter_month = ((latest_date.month - 1) // 3) * 3 + 1
                    start_of_period = latest_date.replace(month=quarter_month, day=1)
                    ref_vl = fcp_vl.filter(date__lt=start_of_period).last()
                elif period == 'std':
                    semester_month = 1 if latest_date.month <= 6 else 7
                    start_of_period = latest_date.replace(month=semester_month, day=1)
                    ref_vl = fcp_vl.filter(date__lt=start_of_period).last()
                elif period == 'ytd':
                    start_of_period = latest_date.replace(month=1, day=1)
                    ref_vl = fcp_vl.filter(date__lt=start_of_period).last()
                else:  # origin
                    ref_vl = fcp_vl.first()
                    start_of_period = ref_vl.date if ref_vl else None
                
                if ref_vl:
                    # Filtrer les VL depuis le début de la période
                    filtered_vl = fcp_vl.filter(date__gte=ref_vl.date)
                    
                    # Calculer les rendements quotidiens
                    vl_list = list(filtered_vl.values('date', 'valeur'))
                    if len(vl_list) > 1:
                        returns = {}
                        for i in range(1, len(vl_list)):
                            date_str = vl_list[i]['date'].strftime('%Y-%m-%d')
                            ret = (float(vl_list[i]['valeur']) / float(vl_list[i-1]['valeur']) - 1) * 100
                            returns[date_str] = ret
                        fcp_returns[fcp_name] = returns
                        fcp_dates[fcp_name] = set(returns.keys())
    
    # Trouver les dates communes à tous les FCP
    if fcp_dates:
        common_dates = set.intersection(*fcp_dates.values()) if len(fcp_dates) > 1 else set()
        common_dates = sorted(common_dates)
    else:
        common_dates = []
    
    # Calculer la matrice de corrélation
    fcp_names = list(fcp_returns.keys())
    n = len(fcp_names)
    correlation_matrix = []
    
    if len(common_dates) > 5:  # Au moins 5 observations communes
        for i, fcp1 in enumerate(fcp_names):
            row = []
            returns1 = [fcp_returns[fcp1].get(d, 0) for d in common_dates]
            mean1 = sum(returns1) / len(returns1)
            std1 = (sum((r - mean1) ** 2 for r in returns1) / len(returns1)) ** 0.5
            
            for j, fcp2 in enumerate(fcp_names):
                if i == j:
                    row.append(1.0)
                else:
                    returns2 = [fcp_returns[fcp2].get(d, 0) for d in common_dates]
                    mean2 = sum(returns2) / len(returns2)
                    std2 = (sum((r - mean2) ** 2 for r in returns2) / len(returns2)) ** 0.5
                    
                    if std1 > 0 and std2 > 0:
                        covariance = sum((returns1[k] - mean1) * (returns2[k] - mean2) for k in range(len(common_dates))) / len(common_dates)
                        corr = covariance / (std1 * std2)
                        row.append(round(corr, 3))
                    else:
                        row.append(0)
            correlation_matrix.append(row)
    
    return JsonResponse({
        'fcp_names': fcp_names,
        'matrix': correlation_matrix,
        'nb_observations': len(common_dates),
        'period': period
    })


def api_volatility_clustering(request):
    """API pour le clustering de volatilité"""
    fcp_name = request.GET.get('fcp')
    window = int(request.GET.get('window', 20))  # Fenêtre glissante par défaut 20 jours
    
    # Limiter la fenêtre entre 5 et 30
    window = max(5, min(30, window))
    
    if not fcp_name:
        return JsonResponse({'error': 'FCP non spécifié'}, status=400)
    
    vl_model = get_vl_model(fcp_name)
    if not vl_model:
        return JsonResponse({'error': 'FCP non trouvé'}, status=404)
    
    vl_queryset = vl_model.objects.all().order_by('date')
    
    if not vl_queryset.exists() or vl_queryset.count() < window + 10:
        return JsonResponse({'error': 'Données insuffisantes'}, status=400)
    
    # Calculer les rendements quotidiens
    vl_list = list(vl_queryset.values('date', 'valeur'))
    rendements = []
    dates = []
    
    for i in range(1, len(vl_list)):
        ret = (float(vl_list[i]['valeur']) / float(vl_list[i-1]['valeur']) - 1) * 100
        rendements.append(ret)
        dates.append(vl_list[i]['date'].strftime('%Y-%m-%d'))
    
    # Calculer la volatilité glissante (annualisée)
    volatilites = []
    vol_dates = []
    
    for i in range(window - 1, len(rendements)):
        window_returns = rendements[i - window + 1:i + 1]
        mean_ret = sum(window_returns) / len(window_returns)
        variance = sum((r - mean_ret) ** 2 for r in window_returns) / len(window_returns)
        vol = (variance ** 0.5) * (365 ** 0.5)  # Volatilité annualisée
        volatilites.append(vol)
        vol_dates.append(dates[i])
    
    if len(volatilites) < 10:
        return JsonResponse({'error': 'Données insuffisantes pour le clustering'}, status=400)
    
    # Clustering K-means simplifié (3 clusters)
    # Trier les volatilités pour déterminer les seuils
    sorted_vols = sorted(volatilites)
    n = len(sorted_vols)
    
    # Seuils basés sur les percentiles 33 et 66
    threshold_low = sorted_vols[int(n * 0.33)]
    threshold_high = sorted_vols[int(n * 0.66)]
    
    # Classification des régimes
    regimes = []
    for vol in volatilites:
        if vol <= threshold_low:
            regimes.append(0)  # Faible
        elif vol <= threshold_high:
            regimes.append(1)  # Intermédiaire
        else:
            regimes.append(2)  # Élevé
    
    # Statistiques par régime
    regime_stats = {
        0: {'nom': 'Faible', 'count': 0, 'vols': [], 'color': '#28a745'},
        1: {'nom': 'Intermédiaire', 'count': 0, 'vols': [], 'color': '#ffc107'},
        2: {'nom': 'Élevé', 'count': 0, 'vols': [], 'color': '#dc3545'}
    }
    
    for i, regime in enumerate(regimes):
        regime_stats[regime]['count'] += 1
        regime_stats[regime]['vols'].append(volatilites[i])
    
    # Calculer moyennes et écarts-types par régime
    for regime in regime_stats:
        if regime_stats[regime]['vols']:
            vols = regime_stats[regime]['vols']
            regime_stats[regime]['mean'] = round(sum(vols) / len(vols), 2)
            regime_stats[regime]['min'] = round(min(vols), 2)
            regime_stats[regime]['max'] = round(max(vols), 2)
        else:
            regime_stats[regime]['mean'] = 0
            regime_stats[regime]['min'] = 0
            regime_stats[regime]['max'] = 0
        del regime_stats[regime]['vols']  # Supprimer la liste pour alléger la réponse
    
    # Matrice de transition (probabilités de passer d'un régime à un autre)
    transition_matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    transition_counts = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    
    for i in range(1, len(regimes)):
        prev_regime = regimes[i - 1]
        curr_regime = regimes[i]
        transition_counts[prev_regime][curr_regime] += 1
    
    # Convertir en probabilités
    for i in range(3):
        total = sum(transition_counts[i])
        if total > 0:
            for j in range(3):
                transition_matrix[i][j] = round(transition_counts[i][j] / total * 100, 1)
    
    # Régime actuel
    current_regime = regimes[-1] if regimes else 0
    current_volatility = round(volatilites[-1], 2) if volatilites else 0
    
    # Données pour le graphique
    chart_data = []
    for i in range(len(volatilites)):
        chart_data.append({
            'date': vol_dates[i],
            'volatility': round(volatilites[i], 2),
            'regime': regimes[i]
        })
    
    return JsonResponse({
        'fcp_name': fcp_name,
        'window': window,
        'chart_data': chart_data,
        'regime_stats': regime_stats,
        'transition_matrix': transition_matrix,
        'current_regime': current_regime,
        'current_volatility': current_volatility,
        'thresholds': {
            'low': round(threshold_low, 2),
            'high': round(threshold_high, 2)
        },
        'total_observations': len(volatilites)
    })


def api_rolling_metrics(request):
    """API pour les métriques glissantes (Sharpe et Beta)"""
    fcp_name = request.GET.get('fcp')
    window = int(request.GET.get('window', 20))
    benchmark = request.GET.get('benchmark', 'FCP ACTIONS PERFORMANCES')
    
    # Limiter la fenêtre entre 10 et 60
    window = max(10, min(60, window))
    
    if not fcp_name:
        return JsonResponse({'error': 'FCP non spécifié'}, status=400)
    
    vl_model = get_vl_model(fcp_name)
    if not vl_model:
        return JsonResponse({'error': 'FCP non trouvé'}, status=404)
    
    vl_queryset = vl_model.objects.all().order_by('date')
    
    if not vl_queryset.exists() or vl_queryset.count() < window + 10:
        return JsonResponse({'error': 'Données insuffisantes'}, status=400)
    
    # Calculer les rendements quotidiens du FCP
    vl_list = list(vl_queryset.values('date', 'valeur'))
    rendements = []
    dates = []
    
    for i in range(1, len(vl_list)):
        ret = (float(vl_list[i]['valeur']) / float(vl_list[i-1]['valeur']) - 1) * 100
        rendements.append(ret)
        dates.append(vl_list[i]['date'])
    
    # Calculer les rendements du benchmark
    benchmark_returns = {}
    benchmark_model = get_vl_model(benchmark)
    if benchmark_model and benchmark != fcp_name:
        bench_vl = list(benchmark_model.objects.all().order_by('date').values('date', 'valeur'))
        for i in range(1, len(bench_vl)):
            ret = (float(bench_vl[i]['valeur']) / float(bench_vl[i-1]['valeur']) - 1) * 100
            benchmark_returns[bench_vl[i]['date']] = ret
    
    # Taux sans risque journalier (3.25% annuel)
    rf_daily = 3.25 / 365
    
    # Calculer les métriques glissantes
    rolling_sharpe = []
    rolling_beta = []
    rolling_dates = []
    
    for i in range(window - 1, len(rendements)):
        window_returns = rendements[i - window + 1:i + 1]
        window_dates_list = dates[i - window + 1:i + 1]
        
        # Sharpe Ratio glissant
        mean_ret = sum(window_returns) / len(window_returns)
        variance = sum((r - mean_ret) ** 2 for r in window_returns) / len(window_returns)
        std_ret = variance ** 0.5
        
        if std_ret > 0:
            sharpe = ((mean_ret - rf_daily) / std_ret) * (365 ** 0.5)
        else:
            sharpe = 0
        
        rolling_sharpe.append(round(sharpe, 3))
        rolling_dates.append(dates[i].strftime('%Y-%m-%d'))
        
        # Beta glissant (si benchmark disponible)
        if benchmark_returns:
            bench_window = [benchmark_returns.get(d, 0) for d in window_dates_list]
            
            # Vérifier qu'on a assez de données benchmark
            if sum(1 for b in bench_window if b != 0) > window * 0.5:
                mean_bench = sum(bench_window) / len(bench_window)
                
                # Covariance et variance du benchmark
                covariance = sum((window_returns[k] - mean_ret) * (bench_window[k] - mean_bench) 
                                for k in range(len(window_returns))) / len(window_returns)
                var_bench = sum((b - mean_bench) ** 2 for b in bench_window) / len(bench_window)
                
                if var_bench > 0:
                    beta = covariance / var_bench
                else:
                    beta = 1
                
                rolling_beta.append(round(beta, 3))
            else:
                rolling_beta.append(None)
        else:
            rolling_beta.append(None)
    
    return JsonResponse({
        'fcp_name': fcp_name,
        'window': window,
        'benchmark': benchmark if benchmark_returns else None,
        'dates': rolling_dates,
        'sharpe': rolling_sharpe,
        'beta': rolling_beta,
        'current_sharpe': rolling_sharpe[-1] if rolling_sharpe else None,
        'current_beta': rolling_beta[-1] if rolling_beta and rolling_beta[-1] is not None else None
    })


def api_tail_risk(request):
    """API pour l'analyse du Tail Risk (événements extrêmes)"""
    fcp_name = request.GET.get('fcp')
    
    if not fcp_name:
        return JsonResponse({'error': 'FCP non spécifié'}, status=400)
    
    vl_model = get_vl_model(fcp_name)
    if not vl_model:
        return JsonResponse({'error': 'FCP non trouvé'}, status=404)
    
    vl_queryset = vl_model.objects.all().order_by('date')
    
    if not vl_queryset.exists() or vl_queryset.count() < 30:
        return JsonResponse({'error': 'Données insuffisantes'}, status=400)
    
    # Calculer les rendements quotidiens
    vl_list = list(vl_queryset.values('date', 'valeur'))
    rendements = []
    dates = []
    
    for i in range(1, len(vl_list)):
        ret = (float(vl_list[i]['valeur']) / float(vl_list[i-1]['valeur']) - 1) * 100
        rendements.append(ret)
        dates.append(vl_list[i]['date'].strftime('%Y-%m-%d'))
    
    # Calculer moyenne et écart-type
    n = len(rendements)
    mean_ret = sum(rendements) / n
    variance = sum((r - mean_ret) ** 2 for r in rendements) / n
    std_ret = variance ** 0.5
    
    # Seuils sigma
    sigma_1 = mean_ret - std_ret
    sigma_2 = mean_ret - 2 * std_ret
    sigma_3 = mean_ret - 3 * std_ret
    
    # Compteurs d'événements extrêmes (pertes)
    losses_1_sigma = []  # Pertes > 1σ
    losses_2_sigma = []  # Pertes > 2σ
    losses_3_sigma = []  # Pertes > 3σ
    
    for i, ret in enumerate(rendements):
        if ret < sigma_1:
            losses_1_sigma.append({'date': dates[i], 'return': round(ret, 3)})
            if ret < sigma_2:
                losses_2_sigma.append({'date': dates[i], 'return': round(ret, 3)})
                if ret < sigma_3:
                    losses_3_sigma.append({'date': dates[i], 'return': round(ret, 3)})
    
    # Statistiques
    total_days = len(rendements)
    
    # Distribution théorique vs réelle (règle empirique: 68-95-99.7)
    theoretical_1_sigma = 15.87  # % attendu au-delà de 1σ (en dessous de la moyenne)
    theoretical_2_sigma = 2.28   # % attendu au-delà de 2σ
    theoretical_3_sigma = 0.13   # % attendu au-delà de 3σ
    
    actual_1_sigma = (len(losses_1_sigma) / total_days) * 100
    actual_2_sigma = (len(losses_2_sigma) / total_days) * 100
    actual_3_sigma = (len(losses_3_sigma) / total_days) * 100
    
    # Top 10 pires jours
    worst_days = sorted(zip(dates, rendements), key=lambda x: x[1])[:10]
    worst_days_list = [{'date': d, 'return': round(r, 3)} for d, r in worst_days]
    
    # Top 10 meilleurs jours
    best_days = sorted(zip(dates, rendements), key=lambda x: x[1], reverse=True)[:10]
    best_days_list = [{'date': d, 'return': round(r, 3)} for d, r in best_days]
    
    # Calculer le rapport gain/perte des événements extrêmes
    extreme_losses = [r for r in rendements if r < sigma_2]
    extreme_gains = [r for r in rendements if r > mean_ret + 2 * std_ret]
    
    avg_extreme_loss = sum(extreme_losses) / len(extreme_losses) if extreme_losses else 0
    avg_extreme_gain = sum(extreme_gains) / len(extreme_gains) if extreme_gains else 0
    
    return JsonResponse({
        'fcp_name': fcp_name,
        'total_days': total_days,
        'statistics': {
            'mean': round(mean_ret, 4),
            'std': round(std_ret, 4),
            'sigma_1_threshold': round(sigma_1, 4),
            'sigma_2_threshold': round(sigma_2, 4),
            'sigma_3_threshold': round(sigma_3, 4)
        },
        'tail_analysis': {
            '1_sigma': {
                'count': len(losses_1_sigma),
                'frequency': round(actual_1_sigma, 2),
                'expected': theoretical_1_sigma,
                'ratio': round(actual_1_sigma / theoretical_1_sigma, 2) if theoretical_1_sigma > 0 else 0,
                'events': losses_1_sigma[-20:]  # 20 derniers événements
            },
            '2_sigma': {
                'count': len(losses_2_sigma),
                'frequency': round(actual_2_sigma, 2),
                'expected': theoretical_2_sigma,
                'ratio': round(actual_2_sigma / theoretical_2_sigma, 2) if theoretical_2_sigma > 0 else 0,
                'events': losses_2_sigma[-10:]  # 10 derniers événements
            },
            '3_sigma': {
                'count': len(losses_3_sigma),
                'frequency': round(actual_3_sigma, 2),
                'expected': theoretical_3_sigma,
                'ratio': round(actual_3_sigma / theoretical_3_sigma, 2) if theoretical_3_sigma > 0 else 0,
                'events': losses_3_sigma  # Tous les événements (rares)
            }
        },
        'worst_days': worst_days_list,
        'best_days': best_days_list,
        'extreme_stats': {
            'avg_extreme_loss': round(avg_extreme_loss, 3),
            'avg_extreme_gain': round(avg_extreme_gain, 3),
            'extreme_losses_count': len(extreme_losses),
            'extreme_gains_count': len(extreme_gains)
        }
    })


def api_calendar_data(request):
    """API pour les données du calendrier de performance"""
    fcp_name = request.GET.get('fcp')
    
    if not fcp_name:
        return JsonResponse({'error': 'FCP non spécifié'}, status=400)
    
    vl_model = get_vl_model(fcp_name)
    if not vl_model:
        return JsonResponse({'error': 'FCP non trouvé'}, status=404)
    
    vl_queryset = vl_model.objects.all().order_by('date')
    
    if not vl_queryset.exists() or vl_queryset.count() < 30:
        return JsonResponse({'error': 'Données insuffisantes'}, status=400)
    
    # Calculer les rendements quotidiens
    vl_list = list(vl_queryset.values('date', 'valeur'))
    daily_returns = {}
    
    for i in range(1, len(vl_list)):
        date = vl_list[i]['date']
        ret = (float(vl_list[i]['valeur']) / float(vl_list[i-1]['valeur']) - 1) * 100
        daily_returns[date] = ret
    
    # 1. Heatmap mensuelle (performance par mois)
    monthly_data = {}
    monthly_vl_start = {}
    
    for vl in vl_list:
        date = vl['date']
        year = date.year
        month = date.month
        key = f"{year}-{month:02d}"
        
        if key not in monthly_vl_start:
            monthly_vl_start[key] = float(vl['valeur'])
        monthly_data[key] = float(vl['valeur'])
    
    # Calculer les rendements mensuels
    monthly_returns = {}
    prev_month_end = None
    for key in sorted(monthly_data.keys()):
        if prev_month_end is not None:
            monthly_returns[key] = ((monthly_data[key] / prev_month_end) - 1) * 100
        prev_month_end = monthly_data[key]
    
    # Format heatmap
    heatmap_data = []
    for key, ret in monthly_returns.items():
        year, month = key.split('-')
        heatmap_data.append({
            'year': int(year),
            'month': int(month),
            'return': round(ret, 2)
        })
    
    # 2. Performance par jour de la semaine
    weekday_stats = {i: [] for i in range(5)}  # 0=Lundi, 4=Vendredi
    weekday_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
    
    for date, ret in daily_returns.items():
        weekday = date.weekday()
        if weekday < 5:  # Exclure weekends
            weekday_stats[weekday].append(ret)
    
    weekday_analysis = []
    for i in range(5):
        if weekday_stats[i]:
            returns = weekday_stats[i]
            mean = sum(returns) / len(returns)
            positive = sum(1 for r in returns if r > 0)
            negative = sum(1 for r in returns if r < 0)
            weekday_analysis.append({
                'day': weekday_names[i],
                'dayIndex': i,
                'mean': round(mean, 4),
                'count': len(returns),
                'positive': positive,
                'negative': negative,
                'win_rate': round(positive / len(returns) * 100, 1),
                'best': round(max(returns), 2),
                'worst': round(min(returns), 2)
            })
    
    # 3. Saisonnalité - Performance par mois (historique tous les mois)
    month_stats = {i: [] for i in range(1, 13)}
    month_names = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                   'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    
    for key, ret in monthly_returns.items():
        month = int(key.split('-')[1])
        month_stats[month].append(ret)
    
    seasonality = []
    for month in range(1, 13):
        if month_stats[month]:
            returns = month_stats[month]
            mean = sum(returns) / len(returns)
            positive = sum(1 for r in returns if r > 0)
            seasonality.append({
                'month': month_names[month - 1],
                'monthIndex': month,
                'mean': round(mean, 2),
                'count': len(returns),
                'positive': positive,
                'negative': len(returns) - positive,
                'win_rate': round(positive / len(returns) * 100, 1),
                'best': round(max(returns), 2),
                'worst': round(min(returns), 2)
            })
    
    # Trier pour trouver les meilleurs/pires mois
    sorted_seasonality = sorted(seasonality, key=lambda x: x['mean'], reverse=True)
    best_months = sorted_seasonality[:3]
    worst_months = sorted_seasonality[-3:]
    
    # 4. Données pour heatmap quotidienne (dernières 52 semaines)
    from datetime import timedelta
    if vl_list:
        last_date = vl_list[-1]['date']
        start_date = last_date - timedelta(days=365)
        
        daily_heatmap = []
        for date, ret in daily_returns.items():
            if date >= start_date:
                daily_heatmap.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'weekday': date.weekday(),
                    'week': date.isocalendar()[1],
                    'year': date.year,
                    'return': round(ret, 3)
                })
    
    return JsonResponse({
        'fcp_name': fcp_name,
        'monthly_heatmap': heatmap_data,
        'weekday_analysis': weekday_analysis,
        'seasonality': seasonality,
        'best_months': best_months,
        'worst_months': worst_months,
        'daily_heatmap': daily_heatmap
    })
