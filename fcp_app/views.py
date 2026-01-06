from django.shortcuts import render
from django.db.models import Sum, Avg, Max, Min, Count
from django.http import JsonResponse
from datetime import datetime, timedelta
from decimal import Decimal
import json
from .models import (
    FCP, ValeurLiquidative, SouscriptionRachat, ActifNet,
    CompositionFCP, Benchmark, PoidsQuotidien, FicheSignaletique
)


def calculate_performance_volatility(fcp, date_debut=None, date_fin=None):
    """Calcule la performance et la volatilité d'un FCP sur une période
    Retourne: (performance, volatilité, nb_jours)"""
    
    # Récupérer les valeurs liquidatives dans la période
    vl_query = ValeurLiquidative.objects.filter(fcp=fcp, valeur__isnull=False).order_by('date')
    
    if date_debut:
        vl_query = vl_query.filter(date__gte=date_debut)
    if date_fin:
        vl_query = vl_query.filter(date__lte=date_fin)
    
    vl_list = list(vl_query.values_list('date', 'valeur'))
    
    if len(vl_list) < 2:
        return None, None, 0
    
    # Calculer le nombre de jours entre première et dernière date
    premiere_date = vl_list[0][0]
    derniere_date = vl_list[-1][0]
    nb_jours = (derniere_date - premiere_date).days
    
    # Calculer la performance
    premiere_valeur = float(vl_list[0][1])
    derniere_valeur = float(vl_list[-1][1])
    performance = ((derniere_valeur - premiere_valeur) / premiere_valeur) * 100
    
    # Calculer la volatilité (écart-type des rendements quotidiens)
    rendements = []
    for i in range(1, len(vl_list)):
        rendement = ((float(vl_list[i][1]) - float(vl_list[i-1][1])) / float(vl_list[i-1][1])) * 100
        rendements.append(rendement)
    
    if rendements:
        moyenne_rendements = sum(rendements) / len(rendements)
        variance = sum((r - moyenne_rendements) ** 2 for r in rendements) / len(rendements)
        volatilite = variance ** 0.5
    else:
        volatilite = 0
    
    return round(performance, 2), round(volatilite, 2), nb_jours


def get_period_dates(period_type, custom_start=None, custom_end=None):
    """Retourne les dates de début et fin selon le type de période"""
    # Utiliser la dernière date disponible dans les données comme référence
    last_vl = ValeurLiquidative.objects.order_by('-date').first()
    if last_vl:
        reference_date = last_vl.date
    else:
        reference_date = datetime.now().date()
    
    if period_type == 'personnalise':
        return custom_start, custom_end
    elif period_type == 'wtd':  # Week to Date
        days_since_monday = reference_date.weekday()
        start_date = reference_date - timedelta(days=days_since_monday)
        return start_date, reference_date
    elif period_type == 'mtd':  # Month to Date
        start_date = reference_date.replace(day=1)
        return start_date, reference_date
    elif period_type == 'qtd':  # Quarter to Date
        quarter = (reference_date.month - 1) // 3
        start_month = quarter * 3 + 1
        start_date = reference_date.replace(month=start_month, day=1)
        return start_date, reference_date
    elif period_type == 'std':  # Semester to Date
        if reference_date.month <= 6:
            start_date = reference_date.replace(month=1, day=1)
        else:
            start_date = reference_date.replace(month=7, day=1)
        return start_date, reference_date
    elif period_type == 'ytd':  # Year to Date
        start_date = reference_date.replace(month=1, day=1)
        return start_date, reference_date
    elif period_type == '1m':  # 1 mois glissant
        start_date = reference_date - timedelta(days=30)
        return start_date, reference_date
    elif period_type == '3m':  # 3 mois glissants
        start_date = reference_date - timedelta(days=90)
        return start_date, reference_date
    elif period_type == '6m':  # 6 mois glissants
        start_date = reference_date - timedelta(days=180)
        return start_date, reference_date
    elif period_type == '1y':  # 1 an glissant
        start_date = reference_date - timedelta(days=365)
        return start_date, reference_date
    elif period_type == '5y':  # 5 ans glissants
        start_date = reference_date - timedelta(days=365 * 5)
        return start_date, reference_date
    else:  # origine (toute la période)
        return None, None


def api_performance_data(request):
    """API pour récupérer les données de performance/volatilité selon la période"""
    
    # Récupérer les paramètres
    periode = request.GET.get('periode', 'origine')
    custom_start = request.GET.get('date_debut')
    custom_end = request.GET.get('date_fin')
    
    # Convertir les dates personnalisées si présentes
    date_debut, date_fin = None, None
    if custom_start:
        try:
            date_debut = datetime.strptime(custom_start, '%Y-%m-%d').date()
        except:
            pass
    if custom_end:
        try:
            date_fin = datetime.strptime(custom_end, '%Y-%m-%d').date()
        except:
            pass
    
    # Calculer les dates selon la période
    if periode != 'personnalise':
        date_debut, date_fin = get_period_dates(periode, date_debut, date_fin)
    
    # Récupérer tous les FCP actifs
    fcps = FCP.objects.filter(actif=True).select_related('fiche_signaletique').order_by('nom')
    
    # Calculer les performances et volatilités
    performance_data = []
    for fcp in fcps:
        fiche = getattr(fcp, 'fiche_signaletique', None)
        
        # Calculer performance, volatilité et nombre de jours
        performance, volatilite, nb_jours = calculate_performance_volatility(fcp, date_debut, date_fin)
        
        if performance is not None and volatilite is not None:
            performance_data.append({
                'id': fcp.id,
                'nom': fcp.nom,
                'performance': performance,
                'volatilite': volatilite,
                'nb_jours': nb_jours,
                'type': fiche.type_fcp if fiche else None,
                'profil': fiche.profil_risque if fiche else None,
            })
    
    # Informations sur la période
    periode_info = {
        'type': periode,
        'date_debut': str(date_debut) if date_debut else None,
        'date_fin': str(date_fin) if date_fin else None,
    }
    
    return JsonResponse({
        'performance_data': performance_data,
        'periode_info': periode_info,
    })


def api_evolution_vl(request):
    """API pour récupérer l'évolution d'un FCP et son benchmark composite"""
    
    fcp_id = request.GET.get('fcp_id')
    periode = request.GET.get('periode', 'tout')
    
    if not fcp_id:
        return JsonResponse({'error': 'fcp_id requis'}, status=400)
    
    try:
        fcp = FCP.objects.select_related('fiche_signaletique').get(id=fcp_id)
    except FCP.DoesNotExist:
        return JsonResponse({'error': 'FCP non trouvé'}, status=404)
    
    # Calculer la date de début selon la période
    last_vl = ValeurLiquidative.objects.filter(fcp=fcp).order_by('-date').first()
    if not last_vl:
        return JsonResponse({'error': 'Aucune VL disponible'}, status=404)
    
    reference_date = last_vl.date
    
    if periode == '1m':
        date_debut = reference_date - timedelta(days=30)
    elif periode == '3m':
        date_debut = reference_date - timedelta(days=90)
    elif periode == '6m':
        date_debut = reference_date - timedelta(days=180)
    elif periode == '1y':
        date_debut = reference_date - timedelta(days=365)
    else:  # 'tout'
        date_debut = None
    
    # Récupérer les VL du FCP
    vl_query = ValeurLiquidative.objects.filter(fcp=fcp, valeur__isnull=False).order_by('date')
    if date_debut:
        vl_query = vl_query.filter(date__gte=date_debut)
    
    vl_list = list(vl_query.values('date', 'valeur'))
    
    if len(vl_list) < 2:
        return JsonResponse({'error': 'Données insuffisantes'}, status=404)
    
    # Calculer l'évolution cumulée en %
    premiere_valeur = float(vl_list[0]['valeur'])
    evolution_fcp = []
    for vl in vl_list:
        perf_cumulee = ((float(vl['valeur']) - premiere_valeur) / premiere_valeur) * 100
        evolution_fcp.append({
            'date': str(vl['date']),
            'valeur': round(perf_cumulee, 2)
        })
    
    # Récupérer les proportions de benchmark du FCP
    fiche = getattr(fcp, 'fiche_signaletique', None)
    evolution_benchmark = []
    benchmark_info = None
    
    if fiche and (fiche.benchmark_obligataire or fiche.benchmark_brvmc):
        # Les poids sont stockés en fraction décimale (ex: 0.75 = 75%)
        poids_oblig = float(fiche.benchmark_obligataire or 0)
        poids_action = float(fiche.benchmark_brvmc or 0)
        
        benchmark_info = {
            'poids_obligataire': poids_oblig,
            'poids_actions': poids_action,
            'benchmark_obligataire': 'MBI UEMOA',
            'benchmark_actions': 'BRVM Composite'
        }
        
        # Récupérer les benchmarks pour les mêmes dates
        dates = [vl['date'] for vl in vl_list]
        benchmarks = Benchmark.objects.filter(date__in=dates).order_by('date')
        
        if benchmarks.exists():
            bench_dict = {b.date: b for b in benchmarks}
            
            # Trouver le premier benchmark disponible
            first_bench = None
            for d in dates:
                if d in bench_dict:
                    first_bench = bench_dict[d]
                    break
            
            if first_bench:
                first_oblig = float(first_bench.benchmark_obligataire or 0)
                first_action = float(first_bench.benchmark_actions or 0)
                
                # Calculer le benchmark composite initial
                first_composite = poids_oblig * first_oblig + poids_action * first_action
                
                for vl in vl_list:
                    bench = bench_dict.get(vl['date'])
                    if bench:
                        oblig = float(bench.benchmark_obligataire or 0)
                        action = float(bench.benchmark_actions or 0)
                        
                        # Benchmark composite pondéré
                        composite = poids_oblig * oblig + poids_action * action
                        
                        # Évolution cumulée du benchmark
                        if first_composite != 0:
                            perf_bench = ((composite - first_composite) / first_composite) * 100
                        else:
                            perf_bench = 0
                        
                        evolution_benchmark.append({
                            'date': str(vl['date']),
                            'valeur': round(perf_bench, 2)
                        })
    
    return JsonResponse({
        'fcp_nom': fcp.nom,
        'evolution_fcp': evolution_fcp,
        'evolution_benchmark': evolution_benchmark,
        'benchmark_info': benchmark_info,
        'periode': periode
    })


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
    """Valeurs liquidatives avec analyses de performance et volatilité"""
    
    # Récupérer tous les FCP actifs avec leur fiche signalétique
    fcps = FCP.objects.filter(actif=True).select_related('fiche_signaletique').order_by('nom')
    
    # Récupérer les paramètres de filtrage
    periode = request.GET.get('periode', 'origine')
    types_fond = request.GET.getlist('types_fond')
    profils_risque = request.GET.getlist('profils_risque')
    fcps_selection = request.GET.getlist('fcps_selection')
    custom_start = request.GET.get('date_debut')
    custom_end = request.GET.get('date_fin')
    
    # Convertir les dates personnalisées si présentes
    date_debut, date_fin = None, None
    if custom_start:
        try:
            date_debut = datetime.strptime(custom_start, '%Y-%m-%d').date()
        except:
            pass
    if custom_end:
        try:
            date_fin = datetime.strptime(custom_end, '%Y-%m-%d').date()
        except:
            pass
    
    # Calculer les dates selon la période
    if periode != 'personnalise':
        date_debut, date_fin = get_period_dates(periode, date_debut, date_fin)
    
    # Préparer les données pour le tableau de classification
    classification_data = []
    for fcp in fcps:
        fiche = getattr(fcp, 'fiche_signaletique', None)
        if fiche:
            classification_data.append({
                'id': fcp.id,
                'nom': fcp.nom,
                'type_fcp': fiche.type_fcp or '-',
                'echelle_risque': fiche.echelle_risque or '-',
                'profil_risque': fiche.profil_risque,
                'benchmark_obligataire': float(fiche.benchmark_obligataire) if fiche.benchmark_obligataire else '-',
                'benchmark_brvmc': float(fiche.benchmark_brvmc) if fiche.benchmark_brvmc else '-',
                'horizon': fiche.horizon_investissement or '-',
            })
    
    # Calculer les performances et volatilités
    performance_data = []
    for fcp in fcps:
        fiche = getattr(fcp, 'fiche_signaletique', None)
        
        # Appliquer les filtres
        if types_fond and fiche and fiche.type_fcp:
            type_map = {
                'action': 'Actions',
                'capital-risque': 'Capital-Risque',
                'diversifie': 'Diversifié',
                'monetaire': 'Monétaire',
                'obligataire': 'Obligataire'
            }
            if not any(fiche.type_fcp.lower().find(type_map.get(t, '').lower()) >= 0 for t in types_fond):
                continue
        
        if profils_risque and fiche:
            profil_map = {
                'prudent': 'Prudent',
                'equilibre': 'Équilibré',
                'dynamique': 'Dynamique'
            }
            if not any(fiche.profil_risque == profil_map.get(p) for p in profils_risque):
                continue
        
        # Calculer performance, volatilité et nombre de jours
        performance, volatilite, nb_jours = calculate_performance_volatility(fcp, date_debut, date_fin)
        
        if performance is not None and volatilite is not None:
            est_selectionne = not fcps_selection or str(fcp.id) in fcps_selection
            performance_data.append({
                'id': fcp.id,
                'nom': fcp.nom,
                'performance': performance,
                'volatilite': volatilite,
                'nb_jours': nb_jours,
                'type': fiche.type_fcp if fiche else None,
                'profil': fiche.profil_risque if fiche else None,
                'selectionne': est_selectionne,
            })
    
    context = {
        'fcps': fcps,
        'classification_data': json.dumps(classification_data),
        'performance_data': json.dumps(performance_data),
        'periode': periode,
        'types_fond': types_fond,
        'profils_risque': profils_risque,
        'fcps_selection': fcps_selection,
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
