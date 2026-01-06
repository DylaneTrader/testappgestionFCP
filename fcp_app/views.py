from django.shortcuts import render

def home(request):
    """Page d'accueil"""
    return render(request, 'fcp_app/home.html')

def valeurs_liquidatives(request):
    """Valeurs liquidatives"""
    return render(request, 'fcp_app/valeurs_liquidatives.html')

def composition_fcp(request):
    """Composition FCP"""
    return render(request, 'fcp_app/composition_fcp.html')

def fiche_signaletique(request):
    """Fiche signalétique"""
    return render(request, 'fcp_app/fiche_signaletique.html')

def souscriptions_rachats(request):
    """Souscriptions rachats & Actifs net"""
    return render(request, 'fcp_app/souscriptions_rachats.html')

def about(request):
    """A propos"""
    return render(request, 'fcp_app/about.html')
