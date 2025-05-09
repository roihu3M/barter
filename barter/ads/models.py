from django.db import models
from django.contrib.auth.models import User
# Create your models here.
CONDITION_CHOICES = (
    ("NEW", "New"),
    ("USED", "Used"),
    
)
STATUS_CHOICES = (
    ("WAITING", "Waiting"),
    ("ACCEPTED" , "Accepted"),
    ("DECLINED", "Declined")
)

class Ad(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=512)
    image_url = models.CharField(max_length=128, blank=True, default='')
    category = models.CharField(max_length=16)
    condition = models.CharField(max_length=6, choices=CONDITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_disabled = models.BooleanField(default=False)
    def __init__(self):
        return str(self.id) + ': ' + str(self.title)

class ExchangeProposal(models.Model):
    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='%(class)s_ad_sender_requests_created')
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='%(class)s_ad_receiver_requests_created')
    comment = models.CharField(max_length=256)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)