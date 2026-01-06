from django.shortcuts import render
from django.db.models import Sum, Avg, Max, Min, Count
from .models import (
    FCP, ValeurLiquidative, SouscriptionRachat, ActifNet,
    CompositionFCP, Benchmark, PoidsQuotidien
)


def home(request):
    """Page d'accueil"""
    # Récupérer des statistiques pour la page d'accueil
    context = {
        'total_fcps': FCP.objects.filter(actif=True).count(),
        'total_operations': SouscriptionRachat.objects.count(),
        'dernier_benchmark': Benchmark.objects.order_by('-date').first(),
        'fcps': FCP.objects.filter(actif=True).order_by('nom')
    }
    return render(request, 'fcp_app/home.html', context)


def valeurs_liquidatives(request):
    """Valeurs liquidatives"""
    # Récupérer les dernières valeurs liquidatives pour chaque FCP
    fcps = FCP.objects.filter(actif=True)
    
    data = []
    for fcp in fcps:
        derniere_vl = ValeurLiquidative.objects.filter(fcp=fcp).order_by('-date').first()
        if derniere_vl:
            data.append({
                'fcp': fcp,
                'date': derniere_vl.date,
                'valeur': derniere_vl.valeur
            })
    
    context = {
        'valeurs': data,
        'fcps': fcps
    }
    return render(request, 'fcp_app/valeurs_liquidatives.html', context)


def composition_fcp(request):
    """Composition FCP"""
    fcp_id = request.GET.get('fcp_id')
    
    fcps = FCP.objects.filter(actif=True).order_by('nom')
    compositions = []
    fcp_selectionne = None
    
    if fcp_id:
        fcp_selectionne = FCP.objects.filter(id=fcp_id).first()
        if fcp_selectionne:
            compositions = CompositionFCP.objects.filter(
                fcp=fcp_selectionne
            ).select_related(
                'type_fcp', 'classe', 'secteur', 'pays', 'secteur_obligation', 'cotation'
            ).order_by('-pourcentage')
    
    context = {
        'fcps': fcps,
        'fcp_selectionne': fcp_selectionne,
        'compositions': compositions
    }
    return render(request, 'fcp_app/composition_fcp.html', context)


def fiche_signaletique(request):
    """Fiche signalétique"""
    fcp_id = request.GET.get('fcp_id')
    
    fcps = FCP.objects.filter(actif=True).order_by('nom')
    fcp_selectionne = None
    stats = {}
    
    if fcp_id:
        fcp_selectionne = FCP.objects.filter(id=fcp_id).first()
        if fcp_selectionne:
            # Statistiques sur les valeurs liquidatives
            vl_stats = ValeurLiquidative.objects.filter(fcp=fcp_selectionne).aggregate(
                max_vl=Max('valeur'),
                min_vl=Min('valeur'),
                avg_vl=Avg('valeur')
            )
            
            # Dernière valeur liquidative
            derniere_vl = ValeurLiquidative.objects.filter(
                fcp=fcp_selectionne
            ).order_by('-date').first()
            
            # Dernier actif net
            dernier_actif = ActifNet.objects.filter(
                fcp=fcp_selectionne
            ).order_by('-date').first()
            
            # Statistiques sur les opérations
            ops_stats = SouscriptionRachat.objects.filter(fcp=fcp_selectionne).aggregate(
                total_operations=Sum('montant'),
                nb_operations=Count('id')
            )
            
            # Dernier poids quotidien
            dernier_poids = PoidsQuotidien.objects.filter(
                fcp=fcp_selectionne
            ).order_by('-date').first()
            
            stats = {
                'vl_stats': vl_stats,
                'derniere_vl': derniere_vl,
                'dernier_actif': dernier_actif,
                'ops_stats': ops_stats,
                'dernier_poids': dernier_poids
            }
    
    context = {
        'fcps': fcps,
        'fcp_selectionne': fcp_selectionne,
        'stats': stats
    }
    return render(request, 'fcp_app/fiche_signaletique.html', context)


def souscriptions_rachats(request):
    """Souscriptions rachats & Actifs net"""
    fcp_id = request.GET.get('fcp_id')
    
    fcps = FCP.objects.filter(actif=True).order_by('nom')
    fcp_selectionne = None
    operations = []
    actifs_nets = []
    
    if fcp_id:
        fcp_selectionne = FCP.objects.filter(id=fcp_id).first()
        if fcp_selectionne:
            # Récupérer les opérations récentes
            operations = SouscriptionRachat.objects.filter(
                fcp=fcp_selectionne
            ).select_related(
                'type_client', 'type_operation'
            ).order_by('-date')[:50]
            
            # Récupérer les actifs nets récents
            actifs_nets = ActifNet.objects.filter(
                fcp=fcp_selectionne
            ).order_by('-date')[:30]
    
    context = {
        'fcps': fcps,
        'fcp_selectionne': fcp_selectionne,
        'operations': operations,
        'actifs_nets': actifs_nets
    }
    return render(request, 'fcp_app/souscriptions_rachats.html', context)


def about(request):
    """A propos"""
    # Ajouter des statistiques globales
    from django.db.models import Count
    
    stats = {
        'total_fcps': FCP.objects.count(),
        'total_vl': ValeurLiquidative.objects.count(),
        'total_operations': SouscriptionRachat.objects.count(),
        'total_actifs': ActifNet.objects.count(),
        'total_compositions': CompositionFCP.objects.count(),
        'total_poids': PoidsQuotidien.objects.count(),
        'total_benchmarks': Benchmark.objects.count(),
    }
    
    context = {'stats': stats}
    return render(request, 'fcp_app/about.html', context)
