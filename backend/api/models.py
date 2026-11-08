from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

class Tournament(models.Model):
    external_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField('Назва турніру', max_length=30)
    season = models.CharField('Сезон (рік)', max_length=30)
    image = models.URLField('Логотип (URL)', max_length=255)
    code = models.CharField('URL код ліги', max_length=5)
    country = models.ForeignKey('Country', on_delete=models.PROTECT, null=True)
    start_date = models.DateField('Дата початку сезону', null=True, blank=True)
    end_date = models.DateField('Дата закінчення сезону', null=True, blank=True)
    matchday = models.IntegerField(null=True, blank=True)
    class Meta:
        verbose_name = 'Турнір'
        verbose_name_plural = 'Турніри'

    def __str__(self):
        return self.name
    
    @property
    def days_to_end(self):
        days = (self.end_date - self.start_date).days
        return max(0, days)

class Group(models.Model):
    tournament = models.ForeignKey(Tournament, 
                                   on_delete=models.CASCADE, 
                                   related_name='groups', 
                                   verbose_name='Турнір'
                                   )
    group_name = models.CharField('Назва групи / таблиці', max_length=25, null=True, blank=True)
    
    teams = models.ManyToManyField(
        'Team',
        through='TeamStats',
        verbose_name='Команди в турнірі/групі',
        related_name='tournament_groups',
        blank=True,

    )

    class Meta:
        verbose_name = 'Турнірна таблиця / Група'
        verbose_name_plural = 'Турнірні таблиці / Групи'
    
    def __str__(self):
        if self.group_name:
            return f"{self.tournament.name}: Група {self.group_name}"
        return f"{self.tournament}"

class Country(models.Model):
    external_id = models.IntegerField(unique=True, null=True)
    name = models.CharField('Назва країни', max_length=50)
    flag = models.URLField('Прапор', null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Країна'
        verbose_name_plural = 'Країни'


    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField('Назва команди', max_length=100)
    image = models.URLField('Логотип (URL)', 
                            max_length=255,
                            blank=True, 
                            default='https://cdn.freebiesupply.com/logos/large/2x/england-football-association-1-logo-black-and-white.png')
    short_name = models.CharField('Назва для ліги', max_length=20, null=True, blank=True)
    coach = models.CharField('Тренер', max_length=100, null=True, blank=True)
    stadium = models.CharField('Стадіон', max_length=100, null=True, blank=True)
    external_id = models.IntegerField(unique=True, null=True, blank=True)
    website = models.URLField(max_length=250, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    tla = models.CharField('Скоросена назва' ,max_length=3, null=True, blank=True)
    main_league = models.ForeignKey('Tournament', 
                                    on_delete=models.SET_NULL, 
                                    verbose_name='Основна ліга', 
                                    related_name='teams',
                                    null=True,
                                    blank=True
                                    )
    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команди'

    def __str__(self):
        return self.name

    @property
    def get_recent_form(self):
        recent_matches = Match.objects.filter(Q(home_team=self) | Q(away_team=self), status='FINISHED').select_related('home_team', 'away_team').order_by('-date')[:5]
        recent_form = []

        for match in recent_matches:
            match_obj = {}
            result = ''
            is_home = self.id == match.home_team_id
            opponent = match.home_team.name if not is_home else match.away_team.name
            goals_for = match.home_goals if is_home else match.away_goals
            goals_away = match.away_goals if is_home else match.home_goals
            score = f"{goals_for} : {goals_away}"

            if goals_for>goals_away:
                result = 'W'
            elif goals_for==goals_away:
                result = 'D'
            else:
                result = 'L'
            match_obj['result'] = result
            match_obj['opponent'] = opponent
            match_obj['score'] = score
            recent_form.append(match_obj)
        return recent_form

    @property
    def get_next_match(self):
        next_match = Match.objects.filter(Q(home_team=self) | Q(away_team=self), Q(status='SCHEDULED') | Q(status='TIMED')).order_by('date').first()
        return next_match

    @property
    def get_mini_standings(self):
        standings = TeamStats.objects.filter(
            group__tournament__code=self.main_league.code
            ).order_by('place').select_related('team')
        
        current_team_stats = self.stats.filter(group__tournament__code=self.main_league.code).first()
        team_position = current_team_stats.place
        total_teams = standings.count()
        if team_position == 1:
            start_pos, end_pose = 0,3
        elif team_position == total_teams:
           start_pos, end_pose = total_teams-3, total_teams
        else:
            start_pos = team_position-2
            end_pose = team_position +1
        return standings[start_pos:end_pose]
    
class MatchStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', 'Ще не почався'
    IN_PLAY = 'IN_PLAY', 'Триває'
    FINISHED = 'FINISHED', 'Завершено'

class Match(models.Model):
    external_id = models.IntegerField(unique=True)
    home_team = models.ForeignKey(Team, 
                                  on_delete=models.CASCADE, 
                                  related_name='home_matches', 
                                  verbose_name='Господарі'
                                  )
    away_team = models.ForeignKey(Team, 
                                  on_delete=models.CASCADE, 
                                  related_name='away_matches', 
                                  verbose_name='Гості'
                                  )
    home_goals = models.IntegerField('Голи господарів', default=0, null=True, blank=True)
    away_goals = models.IntegerField('Голи гостей', default=0, null=True, blank=True)
    stage = models.CharField('Стадія плей-офф', max_length=20, null=True, blank=True)
    group = models.ForeignKey(Group, 
                              on_delete=models.CASCADE, 
                              related_name='matches', 
                              null=True, 
                              blank=True, 
                              verbose_name='Група / Таблиця'
                              )
    tournament = models.ForeignKey(Tournament, 
                                   on_delete=models.CASCADE, 
                                   related_name='matches',
                                     null=True, 
                                     blank=True, 
                                     verbose_name='Турнір'
                                     )
    status = models.CharField(max_length=20,
                              choices=MatchStatus.choices,
                              default=MatchStatus.SCHEDULED)
    date = models.DateTimeField()
    current_minute = models.IntegerField(default = 0, null=True, blank=True)
    matchday = models.IntegerField(default=0, null=True, blank=True)
    
    class Meta:
        ordering = ['date']
        verbose_name = 'Матч'
        
        verbose_name_plural = 'Матчі'
    def __str__(self):
        return f"{self.home_team} {self.home_goals}:{self.away_goals} {self.away_team}"

class TeamStats(models.Model):
    team = models.ForeignKey(Team, 
                             on_delete=models.CASCADE, 
                             related_name='stats', 
                             verbose_name='Команда'
                             )
    group = models.ForeignKey(Group, 
                              on_delete=models.CASCADE, 
                              related_name='team_stats', 
                              verbose_name='Група / Таблиця'
                              )
    
    place = models.IntegerField('Місце', default=0)
    games_played = models.IntegerField('Ігор зіграно', default=0)
    wins = models.IntegerField('Перемог', default=0)
    draws = models.IntegerField('Нічиїх', default=0)
    losses = models.IntegerField('Поразок', default=0)
    goals_for = models.IntegerField('Забито голів', default=0)       
    goals_against = models.IntegerField('Пропущено голів', default=0)   
    goal_difference = models.IntegerField('Різниця м\'ячів', default=0)
    points = models.IntegerField('Очки', default=0)

    class Meta:
        verbose_name = 'Статистика команди'
        verbose_name_plural = 'Турнірні таблиці (Статистика)'
        ordering = ['-points', '-goal_difference', '-goals_for']
        unique_together = ['team', 'group']

    def __str__(self):
        return f"{self.team.name} - {self.points} очок ({self.group.tournament.name})"


class PlayerPositions(models.TextChoices):
    GK = 'GK', 'Воротар (GK)'

    CB = 'CB', 'Центральний захисник (CB)'
    LB = 'LB', 'Лівий захисник (LB)'
    RB = 'RB', 'Правий захисник (RB)'
    LWB = 'LWB', 'Лівий вінгбек (LWB)'
    RWB = 'RWB', 'Правий вінгбек (RWB)'

    CDM = 'CDM', 'Опорний півзахисник (CDM)'
    CM = 'CM', 'Центральний півзахисник (CM)'
    CAM = 'CAM', 'Атакувальний півзахисник (CAM)'
    LM = 'LM', 'Лівий півзахисник (LM)'
    RM = 'RM', 'Правий півзахисник (RM)'

    LW = 'LW', 'Лівий вінгер (LW)'
    RW = 'RW', 'Правий вінгер (RW)'
    CF = 'CF', 'Відтягнутий нападник (CF)'
    ST = 'ST', 'Центральний нападник (ST)'


class TransferType(models.TextChoices):
    PERMANENT = 'PERM', 'Полноценный трансфер'
    LOAN = 'LOAN', 'Аренда'
    RETURN_LOAN = 'RET', 'Возврат из аренды'
    FREE = 'FREE', 'Свободный агент'

class Player(models.Model):
    external_id = models.IntegerField(unique=True)
    name = models.CharField('Ім\'я футболіста',max_length=40, null=True)
    surname = models.CharField('Фамілія футболіста', max_length=30, null=True, blank=True)
    team = models.ForeignKey('Team', 
                             related_name='players', 
                             verbose_name='Команда', 
                             on_delete=models.CASCADE
                             )
    position = models.CharField('Позиція', max_length=25, choices=PlayerPositions, null=True)
    market_value = models.IntegerField('Трансферна ціна', default=0)
    image = models.URLField('Фото (URL)', max_length=250, blank=True, default='https://res.cloudinary.com/stage-nflclubs/image/upload/49ers/f6b7udz3xm3jglfakq9q.svg')
    game_number = models.IntegerField('Ігровий номер', default=1)
    birth_date = models.DateField('Дата народження', null=True, blank=True)
    country = models.ForeignKey('Country', null=True, on_delete=models.SET_NULL)

    @property
    def age(self):
        today = timezone.now()
        age = today.year - self.birth_date.year
        return age if today.month < self.birth_date.month or (today.month == self.birth_date.month and today.day >= self.birth_date.day) else age -1

    class Meta:
        verbose_name = 'Гравець'
        verbose_name_plural = 'Гравці'

    def __str__(self):
        return f"{self.surname if self.surname else self.name} ({self.team.name})"

    @property
    def get_full_name(self):
        surname = self.surname if self.surname else ''
        return f"{self.name} {surname}"

    
class PlayerStats(models.Model):
    player = models.ForeignKey(
        'Player', 
        on_delete=models.CASCADE,
        verbose_name='Гравець',
        related_name='stats'
    )
    tournament = models.ForeignKey(
        'Tournament',
        on_delete=models.CASCADE,
        verbose_name='Турнір',
        related_name='players_stat'
    )
    

    matches_played = models.PositiveIntegerField(
        default=0, 
        verbose_name='Зіграні матчі'
    )
    minutes_played = models.PositiveIntegerField(
        default=0, 
        verbose_name='Зіграні хвилини'
    )
  
    goals = models.PositiveIntegerField(
        default=0,
        verbose_name='Кількість голів'
    )
    assists = models.PositiveIntegerField(
        default=0, 
        verbose_name='Кількість асистів'
    )

    yellow_cards = models.PositiveIntegerField(
        default=0, 
        verbose_name='Жовті картки'
    )
    red_cards = models.PositiveIntegerField(
        default=0, 
        verbose_name='Червоні картки'
    )

    place = models.PositiveIntegerField(
        default=1,
        verbose_name='Місце в турнірі'
        )

    class Meta: 
        verbose_name = 'Статистика гравця'
        verbose_name_plural = 'Статистика гравців'
        ordering = ['place']
        unique_together = ['tournament', 'player']

    def __str__(self):
        return f"{self.player} | {self.tournament} (Голи: {self.goals}, Асисти: {self.assists})"
    

class PlayerTransfer(models.Model):
    player = models.ForeignKey('Player', 
                               on_delete=models.CASCADE, 
                               related_name='transfers', 
                               verbose_name='Гравець')
    
    from_team = models.ForeignKey('Team', 
                                  on_delete=models.PROTECT, 
                                  related_name='transfers_out',
                                  verbose_name='Перехід з команди',
                                  null=True,
                                  blank=True
                                  )
    
    to_team = models.ForeignKey('Team', 
                                on_delete=models.PROTECT, 
                                related_name='transfers_in', 
                                verbose_name='Перехід в команду',
                                null=True,
                                blank=True
                                )
    
    fee = models.IntegerField('Ціна переходу', blank=True)
    date = models.DateField('Дата трансферу')

    type = models.CharField('Тип трансферу', 
                            max_length=10, 
                            choices=TransferType,
                            default=TransferType.PERMANENT
                            )
    season = models.CharField('Season', max_length=10, blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Трансфер'
        verbose_name_plural = 'Історія трансферів'

    def __str__(self):
        from_name = self.from_team.name if self.from_team else 'Вільний агент'
        to_name = self.to_team.name if self.to_team else 'Вільний агент'
        return f"{self.player.name} | {from_name} -> {to_name} ({self.date.year})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.to_team:
            self.player.team = self.to_team
            self.player.save()
        
        if self.from_team and not self.to_team:
            self.player.team = None
            self.save()
  
class MatchEventType(models.TextChoices):
    GOAL = 'GA', 'Гол'
    ASSIST = 'AS', 'Ассист'
    YELLOW_CARD = 'YC', 'Жовта картка'
    RED_CARD = 'RC', 'Червона картка'
    INJURY = 'IJ', 'Травма'
    SUBSTITUTION = 'SB', 'Заміна'

class MatchEvent(models.Model): 
    external_id = models.IntegerField(unique=True, db_index=True)
    type = models.CharField('Подія', max_length=2, choices=MatchEventType)
    match = models.ForeignKey('Match', 
                              on_delete=models.CASCADE, 
                              related_name='events', 
                              verbose_name='Подія'
                              )
    
    player = models.ForeignKey('Player', 
                               on_delete=models.CASCADE, 
                               related_name='match_events', 
                               verbose_name='Гравець'
                               )
    player_assist = models.ForeignKey('Player',
                                    on_delete=models.CASCADE,
                                    related_name='match_assists',
                                    null=True,
                                    blank=True,
                                    verbose_name='Ассист'
                                    )
    minute = models.CharField('Хвилина', max_length=5)
    class Meta:
        ordering = ['-minute']
        verbose_name = 'Подія'
        verbose_name_plural = 'Події'

    def __str__(self):
        return f"{self.player.surname if self.player.surname else self.player.name} - {self.type} ({self.minute})"

    def arrange_player_stats_places(self, tournament):
        player_stats = PlayerStats.objects.filter(tournament=tournament).order_by('-goals', '-assists')

        for index, stat in enumerate(player_stats, start=1):
            stat.place=index
        PlayerStats.objects.bulk_update(player_stats, ['place'])

    def save(self, *args, **kwargs):
        self.arrange_player_stats_places(tournament=self.match.tournament)
        
        