from django import forms
from .models import CONDITION_CHOICES, Ad

SEARCH_CHOICES = (
    ("NONE", "-"),
    ("NEW", "New"),
    ("USED", "Used"),
)

FILTER_STATUS_CHOICES = (
    ("NONE", "-"),
    ("WAITING", "Waiting"),
    ("ACCEPTED" , "Accepted"),
    ("DECLINED", "Declined")
)

class AdForm(forms.Form):
    title = forms.CharField(max_length=32)
    description = forms.CharField(max_length=512, required=False)
    image_url = forms.URLField(max_length=128, required=False)
    category = forms.CharField(max_length=16)
    condition = forms.ChoiceField(choices=CONDITION_CHOICES)

class SearchForm(forms.Form):
    prompt = forms.CharField(max_length=512, required=False)
    category = forms.CharField(max_length=16, required=False)
    condition = forms.ChoiceField(choices=SEARCH_CHOICES, required=False)

class ExchangeProposalForm(forms.Form):
    ad_sender = forms.ModelChoiceField(queryset=Ad.objects.all())
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            ad_sender = self.fields['ad_sender']
            ad_sender.queryset = ad_sender.queryset.filter(user=user)
    comment = forms.CharField(max_length=512, required=False)

class OfferFilterForm(forms.Form):
    sender = forms.CharField(max_length=64, required=False)
    receiver = forms.CharField(max_length=64, required=False)
    status = forms.ChoiceField(choices=FILTER_STATUS_CHOICES, required=False)

class PendingOfferFilterForm(forms.Form):
    sender = forms.CharField(max_length=64, required=False)
