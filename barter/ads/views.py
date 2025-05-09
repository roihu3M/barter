from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as logout1
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import Ad, ExchangeProposal
from .forms import AdForm, SearchForm, ExchangeProposalForm, OfferFilterForm, PendingOfferFilterForm

class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
         context = {
            'form': UserCreationForm()
        }
         return render(request, self.template_name, context)
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect('/')
        context = {
                'form': form
            }
        return render(request, self.template_name, context)

@login_required
def create(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid:
            entry = Ad.objects.create(user = request.user)
            entry.title = request.POST.get('title')
            entry.description = request.POST.get('description')
            entry.image_url = request.POST.get('image_url')
            entry.category = request.POST.get('category')
            entry.condition = request.POST.get('condition')
            entry.is_disabled = False
            entry.save()
            return HttpResponseRedirect('/')
    else:
        form = AdForm()
        return render(request, "create.html", {"form": form},)

def index(request):
    search_form = SearchForm(request.POST)
    if search_form.is_valid:
        return render(request, 'index.html', {"search_form" : search_form})

def search(request):
    search_form = SearchForm(request.POST)
    if request.method == 'POST':
            return render(request, "search.html", {"search_form" :search_form})
    page = request.GET.get('page', default=1)
    page = int(page)
    prompt = request.GET.get('prompt')
    category = request.GET.get('category')
    condition = request.GET.get('condition')
    posts_per_page = 10
    previous_page = page - 1
    next_page = page + 1
    display_posts_start = posts_per_page * (page - 1)
    display_posts_end = posts_per_page * page
    found_ids = set()
    for ad in Ad.objects.all():
        found_in_title = ad.title.find(prompt)
        found_in_desc = ad.description.find(prompt)
        if found_in_title + found_in_desc != -2:
            found_ids.add(ad.id)
    if category != '':
        for ad in Ad.objects.filter(id__in=found_ids):
            if category != ad.category: found_ids.remove(ad.id)
    if condition != 'NONE':
        for ad in Ad.objects.filter(id__in=found_ids):
            if condition != ad.condition: found_ids.remove(ad.id)
    #display part
    pages_count = Ad.objects.filter(id__in=found_ids).count() // posts_per_page
    if Ad.objects.filter(id__in=found_ids).count() % posts_per_page != 0:
        pages_count +=1
    if found_ids:
        context = {
            'post' : Ad.objects.filter(id__in=found_ids).order_by('-pk')[display_posts_start:display_posts_end],
            'pages_count' : pages_count,
            'current_page' : page,
            'previous_page' : previous_page,
            'next_page' : next_page,
            'not_found' : False,
            'prompt' : prompt,
            'category' : category,
            'condition' : condition,
            "search_form" :search_form
        }
        return render(request, 'search.html', context)
    else:
        context = {
            'not_found' : True,
            "search_form" :search_form
        }
        return render(request, 'search.html', context)
    
def viewad(request, ad_id):
    if Ad.objects.filter(id=ad_id):
        ad = Ad.objects.get(id=ad_id)
        can_edit = False
        can_offer = False
        is_disabled = False
        if request.user == ad.user:
            can_edit = True
        elif ad.is_disabled == True:
            is_disabled = True
        elif request.user != 'AnonymousUser':
            can_offer = True
        context = {
            'ad' : ad,
            'does_exist' : True,
            'can_edit' : can_edit,
            'can_offer': can_offer,
            'is_disabled' : is_disabled
        }
    else:
        context = {
            'does_exist' : False
        }
    return render(request, 'ad.html', context)

@login_required
def edit(request, ad_id):
    entry = Ad.objects.filter(id=ad_id).first()
    if entry == None:
        return render(request, "edit.html", {'does_not_exist' : True})
    if entry.user != request.user:
        return render(request, "edit.html", {'can_edit' : False})
    if request.method == 'POST':
        edit_form = AdForm(request.POST)
        if edit_form.is_valid: 
            entry.title = request.POST.get('title')
            entry.description = request.POST.get('description')
            entry.image_url = request.POST.get('image_url')
            entry.category = request.POST.get('category')
            entry.condition = request.POST.get('condition')
            entry.save()
            return HttpResponseRedirect('/ad/' + str(ad_id) + '/')
    else:
        edit_form = AdForm()
        return render(request, "edit.html", {"form": edit_form, "ad_id" : ad_id})

@login_required  
def delete(request, ad_id):
    entry = Ad.objects.filter(id=ad_id).first()
    if entry == None:
        return render(request, "delete.html", {'does_not_exist' : True})
    if entry.user != request.user:
        return render(request, "delete.html", {'can_delete' : False})
    if request.method == 'POST':
        entry.delete()
        return HttpResponseRedirect('/')
    return render(request, "delete.html", {"ad_id" : ad_id})

@login_required
def make_offer(request, ad_id):
    exchange_form = ExchangeProposalForm(user=request.user)
    exist_id = Ad.objects.filter(id=ad_id).first()
    if exist_id == None:
        return render(request, "make_offer.html", {'does_not_exist' : True})
    if request.method == 'POST':
        exchange = ExchangeProposal.objects.create(ad_receiver = exist_id, ad_sender = Ad.objects.get(id=request.POST.get('ad_sender')))
        exchange.comment = request.POST.get('comment')
        exchange.status = 'WAITING'
        exchange.save()
        return HttpResponseRedirect('/offers_list/?sender=&receiver=&status=NONE')
    else:
        return render(request, "make_offer.html", {"form": exchange_form, "ad_id" : ad_id})
    
def offers_list(request):
    offer_filter = OfferFilterForm(request.POST)
    if request.method == 'POST':
            return render(request, "offers_list.html", {"offer_filter" : offer_filter})
    page = request.GET.get('page', default=1)
    page = int(page)
    sender = request.GET.get('sender')
    receiver = request.GET.get('receiver')
    status = request.GET.get('status')
    posts_per_page = 10
    previous_page = page - 1
    next_page = page + 1
    display_posts_start = posts_per_page * (page - 1)
    display_posts_end = posts_per_page * page
    found_ids = set()
    for ids in ExchangeProposal.objects.all():
        found_ids.add(ids.id)
    if sender != '':
        for offer in ExchangeProposal.objects.filter(id__in=found_ids):
            if offer.ad_sender.user != sender: found_ids.remove(offer.id)
    if receiver != '':
        for offer in ExchangeProposal.objects.filter(id__in=found_ids):
            if receiver!= offer.ad_receiver.user: found_ids.remove(offer.id)
    if status != 'NONE':
        for offer in ExchangeProposal.objects.filter(id__in=found_ids):
            if status != offer.status: found_ids.remove(offer.id)
    pages_count = ExchangeProposal.objects.filter(id__in=found_ids).count() // posts_per_page
    if ExchangeProposal.objects.filter(id__in=found_ids).count() % posts_per_page != 0:
        pages_count +=1
    if found_ids:
        context = {
            'post' : ExchangeProposal.objects.filter(id__in=found_ids).order_by('-pk')[display_posts_start:display_posts_end],
            'pages_count' : pages_count,
            'current_page' : page,
            'previous_page' : previous_page,
            'next_page' : next_page,
            'not_found' : False,
            'offer_filter' : offer_filter,
            'sender' : sender,
            'receiver' : receiver,
            'status' : status
        }
        return render(request, 'offers_list.html', context)
    else:
        context = {
            'not_found' : True,
            'offer_filter' : offer_filter
        }
        return render(request, 'offers_list.html', context)
        
@login_required
def pending_offers(request):
    offer_filter = PendingOfferFilterForm(request.POST)
    if request.method == 'POST':
            return render(request, "offers_list.html", {"offer_filter" : offer_filter})
    page = request.GET.get('page', default=1)
    page = int(page)
    posts_per_page = 10
    previous_page = page - 1
    next_page = page + 1
    display_posts_start = posts_per_page * (page - 1)
    display_posts_end = posts_per_page * page
    found_ids = set()
    for offer in ExchangeProposal.objects.all():
        if offer.ad_receiver.user == request.user and offer.status == 'WAITING':
            found_ids.add(offer.ad_sender.id)
    pages_count = ExchangeProposal.objects.filter(id__in=found_ids).count() // posts_per_page
    if ExchangeProposal.objects.filter(id__in=found_ids).count() % posts_per_page != 0:
        pages_count +=1
    if found_ids:
        context = {
            'post' : ExchangeProposal.objects.filter(id__in=found_ids).order_by('-pk')[display_posts_start:display_posts_end],
            'pages_count' : pages_count,
            'current_page' : page,
            'previous_page' : previous_page,
            'next_page' : next_page,
            'not_found' : False,
            'offer_filter' : offer_filter
        }
        return render(request, 'pending_offers.html', context)
    else:
        context = {
            'not_found' : True,
            'offer_filter' : offer_filter
        }
        return render(request, 'pending_offers.html', context)
    
@login_required
def offer(request, offer_id):
    if ExchangeProposal.objects.filter(id=offer_id):
        offer = ExchangeProposal.objects.get(id=offer_id)
        can_accept = False
        is_waiting = False
        if offer.ad_receiver.user == request.user:
            can_accept = True
        if offer.status == 'WAITING':
            is_waiting = True
        context = {
            'offer' : offer,
            'does_exist' : True,
            'can_accept' : can_accept,
            'is_waiting' : is_waiting
        }
    else:
        context = {
            'does_exist' : False
        }
    return render(request, 'offer.html', context)

@login_required
def offer_accept(request, offer_id):
    offer = ExchangeProposal.objects.get(id=offer_id)
    if offer == None:
        return render(request, "offer.html", {'does_exist' : False})
    if offer.ad_receiver.user != request.user:
        return render(request, "offer.html", {'can_accept' : False})
    offer.ad_sender.is_disabled = True
    offer.ad_receiver.is_disabled = True
    offer.ad_sender.save()
    offer.ad_receiver.save()
    offer.status = 'ACCEPTED'
    offer.save()
    return HttpResponseRedirect('/pending_offers/')

@login_required
def offer_decline(request, offer_id):
    offer = ExchangeProposal.objects.get(id=offer_id)
    if offer == None:
        return render(request, "offer.html", {'does_exist' : False})
    if offer.ad_receiver.user != request.user:
        return render(request, "offer.html", {'can_accept' : False})
    offer.ad_sender.is_disabled = True
    offer.ad_receiver.is_disabled = True
    offer.ad_sender.save()
    offer.ad_receiver.save()
    offer.status = 'DECLINED'
    offer.save()
    return HttpResponseRedirect('/pending_offers/')

def logout(request):
    if request.user == 'AnonymousUser':
        return(request, "logout.html")
    else:
        logout1(request)
        return HttpResponseRedirect('/')
