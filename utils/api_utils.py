import requests
from datetime import datetime

def get_league_seasons(api_key, league_id, limit=None):
    url = f"https://v3.football.api-sports.io/leagues"
    headers = {'x-apisports-key': api_key}
    params = {"id": league_id}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return []

    data = response.json()
    if not data.get('response'):
        return []

    seasons = data['response'][0]['seasons']
    años = sorted([s['year'] for s in seasons], reverse=True)
    return años if limit is None else años[:limit]

def get_teams_by_league(api_key, league_id, season):
    url = "https://v3.football.api-sports.io/teams"
    headers = {'x-apisports-key': api_key}
    params = {'league': league_id, 'season': season}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {}

    data = response.json()
    return {
        item['team']['name']: item['team']['id']
        for item in data['response']
    }

def get_h2h_data(api_key, team1_id, team2_id):
    url = "https://v3.football.api-sports.io/fixtures/headtohead"
    headers = {'x-apisports-key': api_key}
    params = {'h2h': f"{team1_id}-{team2_id}"}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return []

    return response.json().get('response', [])

def get_team_fixtures(api_key, league_id, season, team_id):
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-apisports-key': api_key}
    params = {'league': league_id, 'season': season, 'team': team_id}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return []

    return response.json().get('response', [])

def agrupar_partidos_por_año(partidos, años=5):
    hoy = datetime.today()
    anio_actual = hoy.year
    min_anio = anio_actual - años + 1
    partidos_por_anio = {}

    for p in partidos:
        fecha = p['fixture']['date'][:10]
        anio = int(fecha[:4])
        if anio >= min_anio:
            partidos_por_anio.setdefault(anio, []).append(p)

    return partidos_por_anio

def calcular_resumen(partidos, equipo1, equipo2):
    resumen = {
        equipo1: {'victorias': 0, 'empates': 0, 'derrotas': 0, 'goles_favor': 0, 'goles_contra': 0},
        equipo2: {'victorias': 0, 'empates': 0, 'derrotas': 0, 'goles_favor': 0, 'goles_contra': 0}
    }

    for p in partidos:
        home = p['teams']['home']['name']
        away = p['teams']['away']['name']
        g_home = p['goals']['home']
        g_away = p['goals']['away']

        if g_home is None or g_away is None:
            continue

        if g_home == g_away:
            resumen[equipo1]['empates'] += 1
            resumen[equipo2]['empates'] += 1
        elif (home == equipo1 and g_home > g_away) or (away == equipo1 and g_away > g_home):
            resumen[equipo1]['victorias'] += 1
            resumen[equipo2]['derrotas'] += 1
        else:
            resumen[equipo2]['victorias'] += 1
            resumen[equipo1]['derrotas'] += 1

        if home == equipo1:
            resumen[equipo1]['goles_favor'] += g_home
            resumen[equipo1]['goles_contra'] += g_away
            resumen[equipo2]['goles_favor'] += g_away
            resumen[equipo2]['goles_contra'] += g_home
        else:
            resumen[equipo1]['goles_favor'] += g_away
            resumen[equipo1]['goles_contra'] += g_home
            resumen[equipo2]['goles_favor'] += g_home
            resumen[equipo2]['goles_contra'] += g_away

    return resumen