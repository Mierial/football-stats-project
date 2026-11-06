import requests
from django.conf import settings
from api.models import Team, Country, Tournament, Player, MatchEvent,PlayerStats, Match, Group, TeamStats
from django.db import transaction
from api.integrations.api_client import FootballApiClient
from django.db import transaction
from django.db.models import F

client = FootballApiClient(settings.FOOTBALL_API_KEY)
leagues = ['CL', 'PL', 'ELC', 'PD', 'SA', 'BL1', 'FL1', 'DED', 'PPL']


def sync_all_competitions():
    data = client.get_all_competitions()
    if not data or not data.get('competitions'):
        return {}

    competitions_data = data.get('competitions')

    tournaments_ids = [c.get('id') for c in competitions_data if c.get('id')]
    actual_tournaments = Tournament.objects.filter(external_id__in=tournaments_ids)
    tournaments_dict = {t.external_id: t for t in actual_tournaments}
    tournaments_to_update = []

    for tournament_data in competitions_data:
        tournament_obj = tournaments_dict.get(tournament_data.get('id'))
        if tournament_obj:
            current_season_data = tournament_data.get('currentSeason')
            current_match_day = current_season_data.get('currentMatchday')
            tournament_obj.matchday = current_match_day
            tournaments_to_update.append(tournament_obj)
    if tournaments_to_update:
        Tournament.objects.bulk_update(tournaments_to_update,
                                    fields=['matchday'])

def sync_all_countries():
    data = client.get_areas()
    if not data or 'areas' not in data:
        return 0


    areas_data = data.get('areas', [])
    
    countries_to_save = [
        Country(
            external_id=area.get('id'),
            name=area.get('name'),
            flag=area.get('flag')
        )
        for area in areas_data
    ]

    # 3. Використовуємо bulk_create з update_conflicts
    if countries_to_save:
        Country.objects.bulk_create(
            countries_to_save,
            update_conflicts=True,
            unique_fields=['external_id'],  # Поле ОБОВ'ЯЗКОВО має бути unique=True в models.py
            update_fields=['name', 'flag']  # Оновлюємо назву і прапор, якщо країна вже існує
        )

    return len(countries_to_save)

def sync_league_teams(league_code: str):
    data = client.get_teams(league_code=league_code)
    if not data:
        return None
    teams_list = data.get('teams', [])
    comp_data = data.get('competition', {})

    teams_to_update = []
    teams_to_create = []

    with transaction.atomic():
        tournament_obj, _ = Tournament.objects.update_or_create(
            external_id=comp_data.get('id'),
            defaults={
                'name': comp_data.get('name', ''),
                'code': comp_data.get('code', league_code),
                'image': comp_data.get('emblem', ''),
            }
        )
        external_ids = [t.id for t in teams_list]
        teams = Team.objects.filter(external_id__in=external_ids)
        teams_map = {t.external_id: t for t in teams if t.external_id}
        for team_data in teams_list:
            external_id = team_data.get('id')  
            obj = teams_map.get(external_id)
            if obj:
                obj.name = team_data.get('name', '')
                obj.short_name= team_data.get('tla', '') or team_data.get('shortName', '')
                obj.image= team_data.get('crest', '')
                obj.website= team_data.get('website', '')
                obj.stadium= team_data.get('venue', ''  )
                obj.main_league= tournament_obj
                teams_to_update.append(obj)
            else:
                new_obj = Team(
                    external_id=external_id,
                    name=team_data.get('name', ''),
                    short_name=team_data.get('tla', '') or team_data.get('shortName', ''),
                    image=team_data.get('crest', ''),
                    website=team_data.get('website', ''),
                    stadium=team_data.get('venue', ''),
                    main_league=tournament_obj
                )
                teams_to_create.append(new_obj)
        if teams_to_create:
            Team.objects.bulk_create(teams_to_create, batch_size=100)

        if teams_to_update:
            Team.objects.bulk_update(
                teams_to_update, 
                ['name', 'short_name', 'image', 'website', 'stadium', 'main_league'], 
                batch_size=100
                )
        

        return data

def create_players_list(players_list: list, team_obj: Team) -> list[Player]:
    nationality_ids = [p.get('nationality') for p in players_list if p.get('nationality')]
    existing_countries = {c.name: c for c in Country.objects.filter(name__in=nationality_ids)}
    players_to_upsert = []
    for player in players_list:
        player_country = existing_countries[player.get('nationality')] if player.get('nationality') else None
        raw_name = player.get('name', '').strip()
        name_parts = raw_name.split()
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        players_to_upsert.append(
            Player(
                external_id=player.get('id'),
                name=first_name,
                surname=last_name,
                position=player.get('position'),
                birth_date=player.get('dateOfBirth') or None,
                game_number=player.get('shirtNumber') or 0,
                country=player_country,
                team=team_obj,
            )
        )
    return players_to_upsert

def sync_team_by_id(team_id: int):
    data = client.get_team(team_id=team_id)
    if not data:
        return None

    with transaction.atomic():
        area_data = data.get('area') or {}
        main_competition_obj = None
        coach_name = ''
        coach_data = data.get('coach', '')
        if coach_data:
            coach_name = coach_data.get('name') if coach_data.get('name') else f"{coach_data.get('firstName')} {coach_data.get('lastName')}"

        country_obj = Country.objects.filter(name=area_data.get('name')).first()
        tournament_ids = [t.get('id') for t in data.get('runningCompetitions', []) if t.get('type')=='LEAGUE' and 'id' in t]
        if tournament_ids:
            main_competition_obj = Tournament.objects.filter(external_id__in=tournament_ids).first()

        team_obj, _ = Team.objects.update_or_create(
            external_id=team_id,
            defaults={
                'name': data.get('name', ''),
                'short_name': data.get('tla', ''),
                'image': data.get('crest', ''),
                'website': data.get('website', ''),
                'coach': coach_name,
                'stadium': data.get('venue', ''),
                'country': country_obj,
                'main_league': main_competition_obj,
            }
        )

        
        squad_data = data.get('squad') or []
        if len(squad_data)>0:
            players_to_save = create_players_list(squad_data, team_obj)

            if players_to_save:
                Player.objects.bulk_create(
                    players_to_save,
                    update_conflicts=True,
                    unique_fields=['external_id'],
                    update_fields=[
                    'name',
                    'surname',
                    'position',
                    'birth_date',
                    'game_number',
                    'country',
                    'team',
            ]
        )
        return team_obj


def register_match_event(match, player, event_type: str, minute: int) -> MatchEvent:
    event_obj, created = MatchEvent.objects.get_or_create(
        match=match,
        player=player,
        type=event_type,
        minute=minute
    )
    if created and event_type == 'GOAL':
        stats, stats_created = PlayerStats.objects.select_for_update().get_or_create(
            player=player,
            tournament=match.tournament,
            defaults={'goals': 1}
        )
        if not stats_created:
            stats.goals = F('goals') + 1
            stats.save(update_fields=['goals'])
        
    return event_obj

def sync_match_info_by_id(match_id: int) -> dict | None:
    data = client.get_match(match_id)
    print(data)

    if data is None:
        return {}

    with transaction.atomic():
        match_obj = Match.objects.get(external_id=match_id)
        for event_goal in data.get('goals', []):
            minute = event_goal.get('minute')
            scorer = event_goal.get('scorer', None)
            assist_player = event_goal.get('assist', None)

            player_obj, _ = Player.objects.get_or_create(
                external_id=scorer.get('id', None),
                defaults={'name': scorer.get('name', 'Unkown Player')}
            )

            if assist_player:
                Player.objects.get_or_create(
                    external_id=assist_player.get('id'),
                    defaults={'name': assist_player.get('name', 'Unkown player')}
                )

            register_match_event(match_obj, player_obj, 'GOAL', minute)
        return data




def sync_all_matches() -> dict | None:
    for league in leagues:
        try:
            data = client.get_matches(league)
        except Exception as e:
            print(f"[Помилка] Збій під час синхронізації {league}: {e}")
            continue
        if not data:
            continue

        try:
            with transaction.atomic():
                _sync_league_data(data)
        except Exception as e:
            print(f'Database error: {e}')
        
    return data

def _sync_league_data(data: dict):
    tournament_obj, _ = Tournament.objects.get_or_create(
        external_id = data.get('competition').get('id')
    )

    teams_to_load_map = {}

    for match_data in data['matches']:
        for side in ('homeTeam', 'awayTeam'):
            team_item = match_data[side]
            teams_to_load_map[team_item['id']] = Team(
                external_id=team_item['id'],
                name=team_item['name'],
                short_name=team_item.get('shortName'),
                tla=team_item.get('tla'),
                image=team_item.get('crest'),
            )

    Team.objects.bulk_create(
        teams_to_load_map.values(),
        update_conflicts=True,
        unique_fields=['external_id'],
        update_fields=['name', 'short_name', 'tla', 'image']
    )        

    actual_teams = Team.objects.in_bulk(
    teams_to_load_map.keys(), 
    field_name='external_id'
    )

    matches_to_upsert = []

    raw_groups = {m.get('group') for m in data['matches'] if m.get('group')}

    groups_objects = {}

    for group_name in raw_groups:
        group_object, _ = Group.objects.get_or_create(
            group_name=group_name,
            tournament=tournament_obj,
        )
        groups_objects[group_name]= group_object


    default_group, _ = Group.objects.get_or_create(
        tournament=tournament_obj,
        group_name=None,
    )

    for match_data in data['matches']:
        stage = match_data.get('stage')
        group_obj = groups_objects.get(match_data.get('group')) or default_group
        if group_obj == None:
            group_obj = default_group

        score_data = (match_data.get('score') or {}).get('fullTime') or {}

        home_team_id = int(match_data['homeTeam']['id'])
        away_team_id = int(match_data['awayTeam']['id'])


        matches_to_upsert.append(
            Match(
            external_id=match_data.get('id'),
            home_team=actual_teams[home_team_id],
            away_team=actual_teams[away_team_id],
            stage = stage if stage!='REGULAR SEASON' else None,
            group=group_obj,
            tournament=tournament_obj,
            matchday= match_data.get('matchday'),
            date= match_data['utcDate'],
            home_goals=score_data.get('home'),
            away_goals=score_data.get('away'),
            status=match_data['status'],
            current_minute=match_data.get('minute'),
        ))

    Match.objects.bulk_create(
        matches_to_upsert,
        update_conflicts=True, 
        unique_fields=['external_id'],
        update_fields=[
        'home_team',
        'away_team',
        'group',
        'tournament',
        'stage',
        'matchday',
        'date',
        'home_goals',
        'away_goals',
        'status',
        'current_minute',
        ]
    )



def sync_live_matches() -> dict | None:
    data = client.get_live_matches()
    if not data or not data.get('matches'):
        return None

    external_ids = [match['id'] for match in data.get('matches')]
    existing_matches = list(Match.objects.filter(external_id__in=external_ids))
    matches_dict = {m.external_id: m for m in existing_matches}
    matches_to_update=[]

    for match_data in data['matches']:
        match_obj = matches_dict.get(match_data['id'])
        if match_obj:
            match_obj.home_goals = match_data['score']['fullTime']['home']
            match_obj.away_goals = match_data['score']['fullTime']['away']
            match_obj.current_minute = match_data.get('minute')
            match_obj.status = match_data['status']
            matches_to_update.append(match_obj)

    if matches_to_update:
        Match.objects.bulk_update(
            matches_to_update, 
            ['home_goals', 'away_goals', 'current_minute', 'status']
        )


def sync_team_standings(group__tournament__code: str) -> dict | None:
    data = client.get_team_standings(group__tournament__code)

    if not data or not data.get('standings'):
        return None

    current_teams_standing = list(TeamStats.objects.filter(group__tournament__code=group__tournament__code).select_related('team'))
    teams_standings_dict = {standing.team.external_id: standing for standing in current_teams_standing}
    team_standings_to_update = []

    for standing in data['standings'][0]['table']:
        team_id = standing['team']['id']
        standing_obj = teams_standings_dict.get(team_id)
        if standing_obj:
            standing_obj.place = standing['position']
            standing_obj.games_played = standing['playedGames']
            standing_obj.wins = standing['won']
            standing_obj.draws = standing['draw']
            standing_obj.losses = standing['lost']
            standing_obj.points = standing['points']
            standing_obj.goals_for = standing['goalsFor']
            standing_obj.goals_against = standing['goalsAgainst']
            standing_obj.goal_difference = standing['goalDifference']

            team_standings_to_update.append(standing_obj)

    if team_standings_to_update:
        TeamStats.objects.bulk_update(
            team_standings_to_update,
            ['place', 'games_played', 'wins', 'draws', 'losses', 'points', 'goals_for', 'goals_against', 'goal_difference']
        )
        return {"status": "ok", "updated": len(team_standings_to_update)}

    return {"status": "empty", "updated": 0}


def sync_all_leagues_team_standings(leagues):
    for league in leagues:
        sync_team_standings(league)

def finish_match_and_update_standings(match_id: int, home_score: int, away_score: int) -> bool:
    with transaction.atomic():
        try:
            match, created = Match.objects.update_or_create(external_id=match_id)
        except Match.DoesNotExist:
            return None
        
        if match.status == 'FINISHED':
            return None
        match.home_goals = home_score
        match.away_goals = away_score
        match.status = 'FINISHED'
        match.save()
        
        teamStandings = TeamStats.objects.filter(
            team__id__in=[match.home_team.id, match.away_team.id], 
            tournament=match.tournament
            ).select_for_update().order_by('team_id')

        if not teamStandings:
            return None
        
        team_standings_dict = {s.team.id: s for s in teamStandings}

        home_team_standings = team_standings_dict[match.home_team.id]
        away_team_standings = team_standings_dict[match.away_team.id]

        home_team_standings.games_played = F('games_played')+1
        away_team_standings.games_played = F('games_played')+1

        home_team_standings.goals_for = F('goals_for')+home_score
        home_team_standings.goals_against = F('goals_against')+away_score

        away_team_standings.goals_for = F('goals_for')+away_score
        away_team_standings.goals_against = F('goals_against')+home_score

        home_team_gd = home_score-away_score
        away_team_gd = away_score-home_score


        home_team_standings.goal_difference = F('goals_difference') + home_team_gd
        away_team_standings.goal_difference = F('goals_difference') + away_team_gd
                
        if home_score > away_score:
            home_team_standings.wins = F('wins') + 1
            home_team_standings.points = F('points') + 3
            
            away_team_standings.losses = F('losses') + 1
        elif away_score > home_score:
            away_team_standings.wins = F('wins') + 1
            away_team_standings.points = F('points') + 3
            
            home_team_standings.losses = F('losses') + 1
        else:
            home_team_standings.draws = F('draws') + 1
            home_team_standings.points = F('points') + 1
            
            away_team_standings.draws = F('draws') + 1
            away_team_standings.points = F('points') + 1

        home_team_standings.save()
        away_team_standings.save()

        return True 

