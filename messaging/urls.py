from django.urls import path

from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('start/', views.start_conversation, name='start'),
    path(
        'start/<str:username>/',
        views.send_message_to_user,
        name='start-with-user',
    ),
    path('<int:pk>/', views.conversation_detail, name='conversation'),
]
