from django.shortcuts import render
from .data import (
    FCP_FICHE_SIGNALETIQUE, 
    get_all_fcp_names, 
    get_fcp_data, 
    get_risk_label,
    get_type_icon,
    get_type_color
)

# Create your views here.


def valeurs_liquidatives(request):
    """Vue pour la page des Valeurs Liquidatives"""
    context = {
        'page_title': 'Valeurs Liquidatives',
        'page_description': 'Suivi et historique des valeurs liquidatives des FCP',
        'fcp_list': get_all_fcp_names(),
    }
    return render(request, 'fcp_app/valeurs_liquidatives.html', context)


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
