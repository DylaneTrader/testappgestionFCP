from django.shortcuts import render

# Create your views here.


def valeurs_liquidatives(request):
    """Vue pour la page des Valeurs Liquidatives"""
    context = {
        'page_title': 'Valeurs Liquidatives',
        'page_description': 'Suivi et historique des valeurs liquidatives des FCP'
    }
    return render(request, 'fcp_app/valeurs_liquidatives.html', context)


def composition(request):
    """Vue pour la page de Composition"""
    context = {
        'page_title': 'Composition',
        'page_description': 'Composition détaillée du portefeuille FCP'
    }
    return render(request, 'fcp_app/composition.html', context)


def fiche_signaletique(request):
    """Vue pour la page Fiche Signalétique"""
    context = {
        'page_title': 'Fiche Signalétique',
        'page_description': 'Informations générales et caractéristiques du FCP'
    }
    return render(request, 'fcp_app/fiche_signaletique.html', context)


def a_propos(request):
    """Vue pour la page A Propos"""
    context = {
        'page_title': 'À Propos',
        'page_description': 'Informations sur l\'application de reporting FCP'
    }
    return render(request, 'fcp_app/a_propos.html', context)
