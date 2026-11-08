from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MatchViewSet, 
    TournamentViewSet, 
    GroupViewSet, 
    TeamViewSet, 
    TeamStatsViewSet, 
    PlayerViewSet, 
    PlayerStatsViewSet, 
    HomePageAPIView,
    register,
    user_profile,
    TournamentStatisticAPIView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView
)



router = DefaultRouter()

router.register(r'matches', MatchViewSet, basename='match')
router.register(r'groups', GroupViewSet, basename='group')     
router.register(r'tables', TeamStatsViewSet, basename='table') 
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'player_stats', PlayerStatsViewSet, basename='stats')

urlpatterns = [
    path('home/', HomePageAPIView.as_view(), name='home-page'),
    path('tournaments/<int:external_id>/stats', TournamentStatisticAPIView.as_view(), name='tournament-stats'),
    path('auth/register', register, name='register'),
    path('auth/login', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/me', user_profile, name='user_profile'),

    path('', include(router.urls)),
]