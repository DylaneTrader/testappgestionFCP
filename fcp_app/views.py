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
            
            # Trouver VL d'il y a 1 jour, 1 mois, 1 an
            today = latest_vl.date
            vl_1d = vl_queryset.filter(date__lt=today).last()
            vl_1m = vl_queryset.filter(date__lte=today - timedelta(days=30)).last()
            vl_1y = vl_queryset.filter(date__lte=today - timedelta(days=365)).last()
            vl_ytd = vl_queryset.filter(date__year=today.year).first()
            
            stats = {
                'derniere_vl': float(latest_vl.valeur),
                'derniere_date': latest_vl.date.strftime('%d/%m/%Y'),
                'premiere_vl': float(first_vl.valeur),
                'premiere_date': first_vl.date.strftime('%d/%m/%Y'),
                'var_1j': round(((float(latest_vl.valeur) / float(vl_1d.valeur)) - 1) * 100, 2) if vl_1d else 0,
                'var_1m': round(((float(latest_vl.valeur) / float(vl_1m.valeur)) - 1) * 100, 2) if vl_1m else 0,
                'var_1y': round(((float(latest_vl.valeur) / float(vl_1y.valeur)) - 1) * 100, 2) if vl_1y else 0,
                'var_ytd': round(((float(latest_vl.valeur) / float(vl_ytd.valeur)) - 1) * 100, 2) if vl_ytd else 0,
                'var_origine': round(((float(latest_vl.valeur) / float(first_vl.valeur)) - 1) * 100, 2),
                'nb_vl': vl_queryset.count(),
            }
            
            # Calculer la volatilité (écart-type des rendements quotidiens annualisé)
            valeurs = list(vl_queryset.values_list('valeur', flat=True))
            if len(valeurs) > 1:
                rendements = [(float(valeurs[i]) / float(valeurs[i-1]) - 1) for i in range(1, len(valeurs))]
                if rendements:
                    moyenne = sum(rendements) / len(rendements)
                    variance = sum((r - moyenne) ** 2 for r in rendements) / len(rendements)
                    volatilite_quotidienne = variance ** 0.5
                    stats['volatilite'] = round(volatilite_quotidienne * (252 ** 0.5) * 100, 2)  # Annualisée
                else:
                    stats['volatilite'] = 0
            else:
                stats['volatilite'] = 0
    
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
                    vol = (variance ** 0.5) * (252 ** 0.5) * 100
                else:
                    vol = 0
                
                all_fcp_stats.append({
                    'nom': fcp_name,
                    'rendement': round(rendement, 2),
                    'volatilite': round(vol, 2),
                    'selected': fcp_name == selected_fcp
                })
    
    context = {
        'page_title': 'Valeurs Liquidatives',
        'page_description': 'Suivi et historique des valeurs liquidatives des FCP',
        'fcp_list': fcp_list,
        'selected_fcp': selected_fcp,
        'vl_data_json': json.dumps(vl_data),
        'stats': stats,
        'all_fcp_stats_json': json.dumps(all_fcp_stats),
    }
    return render(request, 'fcp_app/valeurs_liquidatives.html', context)


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
