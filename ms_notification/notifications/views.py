from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    """
    GET  /api/notifications/          → toutes les notifs (admin)
    GET  /api/notifications/?user_id=3 → notifs d'un utilisateur
    """
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if user_id:
            notifs = Notification.objects.filter(user_id=user_id)
        else:
            notifs = Notification.objects.all()
        return Response(NotificationSerializer(notifs, many=True).data)


class NotificationMarkReadView(APIView):
    """
    PUT /api/notifications/{id}/read/ → marquer comme lue
    """
    def put(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk)
            notif.is_read = True
            notif.save()
            return Response(NotificationSerializer(notif).data)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification introuvable.'}, status=404)


class NotificationMarkAllReadView(APIView):
    """
    PUT /api/notifications/read-all/?user_id=3 → tout marquer lu
    """
    def put(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id requis.'}, status=400)
        Notification.objects.filter(user_id=user_id, is_read=False).update(is_read=True)
        return Response({'message': 'Toutes les notifications marquées comme lues.'})


class NotificationDeleteView(APIView):
    """
    DELETE /api/notifications/{id}/ → supprimer une notif
    """
    def delete(self, request, pk):
        try:
            Notification.objects.get(pk=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification introuvable.'}, status=404)


class UnreadCountView(APIView):
    """
    GET /api/notifications/unread-count/?user_id=3 → nombre de non lues
    """
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id requis.'}, status=400)
        count = Notification.objects.filter(user_id=user_id, is_read=False).count()
        return Response({'unread_count': count})