import django_filters
from django.db.models import Q
from .models import Match, PlayerStats

class MatchFilter(django_filters.FilterSet):
    team = django_filters.CharFilter(method='filter_by_team')

    class Meta:
        model = Match
        fields = ['matchday', 'tournament__code', 'status']

    def filter_by_team(self, queryset, name, value):
        return queryset.filter(
            Q(home_team__external_id=value) | Q(away_team__external_id=value)
        ).order_by()
