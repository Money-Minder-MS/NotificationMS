from django.urls import path
from .views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    NotificationDeleteView,
    UnreadCountView,
)

urlpatterns = [
    path('',                        NotificationListView.as_view()),
    path('<int:pk>/read/',          NotificationMarkReadView.as_view()),
    path('read-all/',               NotificationMarkAllReadView.as_view()),
    path('<int:pk>/',               NotificationDeleteView.as_view()),
    path('unread-count/',           UnreadCountView.as_view()),
]