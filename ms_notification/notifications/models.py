from django.db import models

class Notification(models.Model):

    TYPE_CHOICES = [
        ('notification.revenue.ajoute',     'Revenu ajouté'),
        ('notification.depense.ajoutee',    'Dépense ajoutée'),
        ('notification.objectif.atteint',   'Objectif atteint'),
        ('notification.reclamation.creee',  'Réclamation créée'),
        ('notification.post.cree',          'Post créé'),
    ]

    user_id   = models.BigIntegerField()
    message   = models.TextField()
    type      = models.CharField(max_length=100, choices=TYPE_CHOICES)
    data      = models.JSONField(default=dict, blank=True)
    is_read   = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.type}] User {self.user_id} — {self.message[:50]}"