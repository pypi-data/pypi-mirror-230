from django.urls import path, include
from moko.views import todo_view, login_for_session
urlpatterns = [
    path('', todo_view, name='moko-home'),
    path('login/', login_for_session, name='moko-session'),
]

