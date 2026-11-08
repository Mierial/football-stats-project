from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import Match, Tournament, Group, Team, TeamStats, Player, PlayerStats
from .serializers import MatchSerializer, TournamentSerializer, GroupSerializer, TeamBaseSerializer, TeamStatsSerializer, PlayerSerializer, PlayerStatsSerializer, TeamListSerializer, TeamOverviewSerializer, HomePageSerializer, CompactTeamStandingsSerializer, UserSerializer
from .services import get_tournament_stats
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .filters import MatchFilter
from datetime import timedelta
from django.utils import timezone
from .tasks import sync_team_task, sync_match_info_task
from django.core.cache import cache

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user=user)

        return Response({
            'user': serializer.data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
        }, 
        status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user_serializer = UserSerializer(request.user)
    return Response(user_serializer.data, status=status.HTTP_200_OK)

    

class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MatchSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = MatchFilter
    lookup_field = 'external_id'
    ordering_fields = ['date']
    ordering = 'date'
    def get_queryset(self):
        return Match.objects.select_related('home_team', 'away_team', 'tournament').order_by('id')

    def retrieve(self, request, *args, **kwargs):
        match_id = self.kwargs.get('external_id')
        match_obj = Match.objects.filter(external_id=match_id).select_related('home_team', 'away_team').first()
        if not match_obj and match_id:
            lock_key = f"sync_match_info{match_id}"
            if cache.add(lock_key, True, timeout=60):
                sync_match_info_task.delay(match_id)
        if match_obj:
            serializer = MatchSerializer(match_obj)
            return Response(serializer.data)

        return Response(
                {"status": "pending", "message": "Дані матчу завантажуються"},
                status=status.HTTP_202_ACCEPTED
            )

    
class TournamentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tournament']

class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'external_id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeamListSerializer
        return TeamBaseSerializer

    def get_queryset(self):
        queryset = Team.objects.all()
        if self.action == 'list':
            queryset = Team.objects.all().select_related('country')            
        league_code = self.request.query_params.get('league_code') or self.request.query_params.get('group__tournament__code')

        if league_code:
            queryset = queryset.filter(main_league__code=league_code)
        return queryset

    @action(detail=True, methods=['get'], url_path='overview')
    def overview(self, request, external_id=None):
        obj = self.get_object()
        serializer = TeamOverviewSerializer(obj, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        team_id = self.kwargs.get(self.lookup_field) 

        team = self.get_queryset().filter(external_id=team_id).prefetch_related('players').first()
        if team and team.stadium:
            serializer = self.get_serializer(team)
            return Response(serializer.data)

        lock_key=f"syncing_team_{team_id}"
        if cache.add(lock_key, True, timeout=60):
            sync_team_task.delay(team_id=team_id)

        return Response(
            {"status": "pending", "message": "Дані команди завантажуються"},
            status=status.HTTP_202_ACCEPTED
        )

    def list(self, request, *args, **kwargs):
        serilaizer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serilaizer.data)

        
class TeamStatsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TeamStats.objects.all()
    serializer_class = TeamStatsSerializer
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group__tournament__code', 'group']

    @method_decorator(cache_page(60*60))
    def list(self, request, *args, **kwargs):
        league_code = request.query_params.get('group__tournament__code')

        stats_queryset = TeamStats.objects.filter(
            group__tournament__code=league_code
        ).select_related('team', 'group')

        tournament = Tournament.objects.filter(code=league_code).first()

        tournament_data = TournamentSerializer(tournament).data
        standings_data = TeamStatsSerializer(stats_queryset, many=True).data

        return Response({
            'tournament': tournament_data,
            'standings': standings_data
            })

class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all().select_related('team')
    serializer_class = PlayerSerializer
    lookup_field = 'external_id'

    filter_backends = [DjangoFilterBackend]
    
    filterset_fields = ['team__external_id', 'position']


class PlayerStatsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlayerStats.objects.all().select_related('tournament', 'player', 'player__team')
    serializer_class = PlayerStatsSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['tournament__code', 'player__team__external_id']
    ordering_fields = ['goals', 'assists']

    ordering = ['-goals']


class HomePageAPIView(APIView):
    @method_decorator(cache_page(60*5))
    def get(self, request):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        top_leagues_code = ['PL', 'PD', 'SA', 'BL1', 'FL1']

        all_matches = list(
            Match.objects.select_related('home_team', 'away_team', 'tournament')
            .filter(date__range=(yesterday, tomorrow))
            .order_by('date')
        )

        raw_standings = TeamStats.objects.filter(group__tournament__code__in=top_leagues_code).select_related('team', 'group__tournament').order_by('place')

        grouped_standings = {code: [] for code in top_leagues_code}
        TOP_N_TEAMS = 6
        for stats in raw_standings:
            league_code = stats.group.tournament.code

            if len(grouped_standings[league_code]) < TOP_N_TEAMS: 
                grouped_standings[league_code].append(stats)

        yesterday_matches = [m for m in all_matches if m.date.date() == yesterday]
        today_matches = [m for m in all_matches if m.date.date() == today]
        tomorrow_matches = [m for m in all_matches if m.date.date() == tomorrow]

        team_standings_data = {
            code: CompactTeamStandingsSerializer(standings, many=True).data for code, standings in grouped_standings.items() 
        }

        response_data = {
            'matches': {
                'yesterday': MatchSerializer(yesterday_matches, many=True).data,
                'today': MatchSerializer(today_matches, many=True).data,
                'tomorrow': MatchSerializer(tomorrow_matches, many=True).data,
            },
            'standings': team_standings_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
        



class TournamentStatisticAPIView(APIView): 
    def get(self, request, external_id):
        tournament = get_object_or_404(Tournament, external_id=external_id)
        return Response(get_tournament_stats(tournament), status=status.HTTP_200_OK)   
