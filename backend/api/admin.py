from django.contrib import admin

from .models import Match, Team, Tournament, Group, TeamStats, MatchEvent, PlayerTransfer, Player, Country, PlayerStats

admin.site.register(Team)
admin.site.register(Match)
admin.site.register(Tournament)
admin.site.register(TeamStats)
admin.site.register(MatchEvent)
admin.site.register(PlayerTransfer)
admin.site.register(Country)
admin.site.register(Player)
admin.site.register(PlayerStats)


class TeamStatsInline(admin.TabularInline):
    model = TeamStats
    extra = 1

    fields = ['team', 'place', 'games_played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'points']
    
    readonly_fields = ['games_played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'points']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    inlines = [TeamStatsInline]