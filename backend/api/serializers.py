from django.db.models import Q
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import Team, Tournament, Group, Match, TeamStats, Player, PlayerTransfer, MatchEvent, PlayerStats

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
        model = User
        fields=['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password')
        )
        return user

class PlayerSerializer(serializers.ModelSerializer):
    position_name = serializers.CharField(
        source='get_position_display', read_only=True
        )
    team_name = serializers.CharField(source='team.name', read_only=True)
    team_logo = serializers.URLField(source='team.image', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    class Meta:
        model = Player
        fields = ['id', 'position', 'position_name', 'full_name', 
                  'market_value', 'image', 'team_name', 'team_logo']


class MatchEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchEvent
        fields = ['id', 'event', 'player', 'minute']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['player'] = {
            'id': instance.player.id,
            'name': instance.player.full_name,
        }
        representation['team_id'] = instance.team.id

        return representation

class MatchSerializer(serializers.ModelSerializer):
    home_goals = serializers.IntegerField(min_value=0, max_value=99)
    away_goals = serializers.IntegerField(min_value=0, max_value=99)
    id = serializers.IntegerField(source='external_id')
    events = MatchEventSerializer(many=True, read_only=True)
    class Meta:
        model = Match
        fields = ['id', 'home_team', 'away_team', 'home_goals', 'status', 'current_minute',
                  'away_goals', 'stage', 'group', 'tournament', 'matchday', 'date', 'events']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        representation['home_team'] = { 
            'id': instance.home_team.external_id,
            'name': instance.home_team.name if instance.home_team.image else None,
            'logo': instance.home_team.image if instance.home_team.image else None
            }
        representation['away_team'] = {
            'id': instance.away_team.external_id,
            'name': instance.away_team.name,
            'logo': instance.away_team.image
            }
        return representation
    
    def validate(self, data):
        stage = data.get('stage')
        group = data.get('group')
        tournament = data.get('tournament')

        if stage and group:
            raise ValidationError(
                'Помилка: Не може одночасно бути стадії плей-офф та групового етапу'
            )
        if not stage and not group:
            raise ValidationError(
                'Помилка: Має бути щонайменше одна опція - групова стадія або плей-офф'
            )
        if stage and not tournament:
            raise ValidationError(
                'Помилка: Для матчів плей-офф потрібно обов\'язково вказати турнір вручну!'
            )
        
        return data

class TournamentSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Tournament
        fields = '__all__'

    days_to_end = serializers.ReadOnlyField()

    def to_representation(self, instance):
        repr = super().to_representation(instance)

        if instance.country:
            repr['country'] = {
                'id': instance.country.id,
                'name': instance.country.name,
                'flag': instance.country.flag
            }
        else:
            repr['country'] = None
        return repr

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'group_name', 'tournament']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['tournament'] = {
            'id': instance.tournament.id,
            'name': instance.tournament.name }

        return representation


class TeamBaseSerializer(serializers.ModelSerializer):
    class Meta:
            model = Team
            fields = ['external_id', 'name', 'short_name', 'coach', 'stadium', 
                    'country', 'image', 'website', 'tla', 'main_league']

class TeamListSerializer(TeamBaseSerializer):
    squad = serializers.SerializerMethodField()

    class Meta(TeamBaseSerializer.Meta):
        fields = TeamBaseSerializer.Meta.fields + ['squad']

    def get_squad(self, obj):
        position_order = {
            'GK': 1,  
            'CB': 2,   
            'LB': 3,   
            'RB': 4,   
            'CDM': 5,   
            'CM': 6,   
            'CAM': 7,   
            'LW': 8,   
            'RW': 9,   
            'CF': 10,
            'ST': 11,

        }

        players = obj.players.all()

        sorted_players = sorted(players, key=lambda player: position_order.get(player.position, 99))

        return PlayerSerializer(sorted_players, many=True, context=self.context).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.country:
            representation['country'] = {
                'id': instance.country.id,
                'name': instance.country.name,
                'flag': instance.country.flag,
            }
        else:
            representation['country']=None
        if instance.main_league:
            representation['main_league'] = {
                'id': instance.main_league.id,
                'name': instance.main_league.name,
                'code': instance.main_league.code,
                'image': instance.main_league.image,
            }
        else:
            representation['main_league'] = None
            
        return representation
class TeamStatsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = TeamStats
        fields = ['id', 'team', 'group', 'games_played', 'wins', 'draws' , 'losses', 
                  'goals_for', 'goals_against', 'goal_difference', 'points', 'image', 'place'
                  ]


        read_only_fields = [
            'id', 'games_played', 'wins', 'draws', 'losses', 
            'goals_for', 'goals_against', 'goal_difference', 'points', 'image'
        ]
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['team'] = {
            'id': instance.team.external_id,
            'name': instance.team.name }
        
        group = instance.group
        representation['group'] = {
            'id': group.id,
            'name': f'Group: {group.group_name}' 
        }
        
        return representation
    
    def get_image(self, obj):
        return obj.team.image


class TeamOverviewSerializer(serializers.ModelSerializer):
    recent_form = serializers.ReadOnlyField(source='get_recent_form')
    next_match = MatchSerializer(source='get_next_match', read_only=True)
    mini_standings = TeamStatsSerializer(source='get_mini_standings', many=True, read_only=True)
    main_league = serializers.ReadOnlyField(source='main_league.name', read_only=True)
    class Meta:
        model = Team
        fields = [
            'id',
            'main_league',
            'recent_form', 
            'next_match', 
            'mini_standings'
        ]

    


class HomePageSerializer(serializers.Serializer):
    matches = MatchSerializer(many=True)
    standings = TeamStatsSerializer(many=True)

class PlayerStatsSerializer(serializers.ModelSerializer):
    tournament = TournamentSerializer()
    player = PlayerSerializer()
    class Meta:
        model = PlayerStats
        fields = '__all__'

class CompactTeamStandingsSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    team_logo = serializers.URLField(source='team.logo', read_only=True)

    class Meta:
        model = TeamStats
        fields = ['place', 'team_name', 'team_logo' ,'games_played', 'goal_difference', 'points']
