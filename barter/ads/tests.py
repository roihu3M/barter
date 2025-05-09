from django.test import TestCase
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal

class GeneralTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='qwerty123')
        self.user2 = User.objects.create_user(username='testuser2', password='asdfgh456')

    def test_authenticate_user(self):
        self.client.login(username='testuser1', password='qwerty123')
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.client.login(username='testuser1', password='qwerty124')
        response = self.client.get('/create/')
        self.assertNotEqual(response.status_code, 200)
        self.client.logout()

    def test_create_ad(self):
        self.client.login(username='testuser1', password='qwerty123')
        self.client.post('/create/', {
            'title' : '123',
            'description' : '123',
            'image_url' : '',
            'category' : '123',
            'condition' : 'USED',
        })
        ad = Ad.objects.get(id=1)
        self.assertFalse(ad == None)
        self.client.logout()
    
    def test_edit_ad(self):
        self.client.login(username='testuser1', password='qwerty123')
        self.client.post('/create/', {
            'title' : '123',
            'description' : '123',
            'image_url' : '',
            'category' : '123',
            'condition' : 'USED',
        })
        self.client.post('/ad/1/edit/',{
            'title' : '124',
            'description' : '124',
            'image_url' : '',
            'category' : '124',
            'condition' : 'NEW',
        })
        ad = Ad.objects.get(id=1)
        self.assertTrue(ad.condition == 'NEW')

    def test_delete_ad(self):
        self.client.login(username='testuser1', password='qwerty123')
        self.client.post('/create/', {
            'title' : '123',
            'description' : '123',
            'image_url' : '',
            'category' : '123',
            'condition' : 'USED',
        })
        self.client.post('/ad/1/delete/')
        ad = Ad.objects.filter(id=1).first()
        self.assertTrue(ad == None)

    def test_create_offer(self):
        self.client.login(username='testuser1', password='qwerty123')
        self.client.post('/create/', {
            'title' : '123',
            'description' : '123',
            'image_url' : '',
            'category' : '123',
            'condition' : 'USED',
        })
        self.client.logout()
        self.client.login(username='testuser2', password='asdfgh456')
        self.client.post('/create/', {
            'title' : '125',
            'description' : '125',
            'image_url' : '',
            'category' : '125',
            'condition' : 'NEW',
        })
        ad2 = Ad.objects.get(id=2)
        self.client.post('/ad/1/make_offer/',{
            'ad_sender' : ad2.id,
            'comment' : '125'
        })
        offer = ExchangeProposal.objects.get(id=1)
        self.assertFalse(offer == None)

    def test_search_ad(self):
        self.client.login(username='testuser1', password='qwerty123')
        self.client.post('/create/', {
            'title' : '123',
            'description' : '123',
            'image_url' : '',
            'category' : '123',
            'condition' : 'USED',
        })
        response = self.client.post('/search/', {
            'prompt' : '',
            'category': '',
            'condition': 'USED'
        })
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/search/', {
            'prompt' : '',
            'category': '',
            'condition': 'sdasdaadsad'
        })
        self.assertEqual(response.status_code, 200)

    def test_offer_accept_decline(self):
        self.client.login(username='testuser1', password='qwerty123')
        self.client.post('/create/', {
            'title' : '123',
            'description' : '123',
            'image_url' : '',
            'category' : '123',
            'condition' : 'USED',
        })
        self.client.post('/create/', {
            'title' : '124',
            'description' : '124',
            'image_url' : '',
            'category' : '124',
            'condition' : 'USED',
        })
        self.client.logout()
        self.client.login(username='testuser2', password='asdfgh456')
        self.client.post('/create/', {
            'title' : '125',
            'description' : '125',
            'image_url' : '',
            'category' : '125',
            'condition' : 'NEW',
        })
        self.client.post('/create/', {
            'title' : '126',
            'description' : '126',
            'image_url' : '',
            'category' : '126',
            'condition' : 'NEW',
        })
        ad = Ad.objects.get(id=3)
        ad2 = Ad.objects.get(id=4)
        self.client.post('/ad/1/make_offer/',{
            'ad_sender' : ad.id,
            'comment' : '125'
        })
        self.client.post('/ad/2/make_offer/',{
            'ad_sender' : ad.id,
            'comment' : '126'
        })
        self.client.post('/ad/2/make_offer/',{
            'ad_sender' : ad2.id,
            'comment' : '126'
        })
        self.client.logout()
        self.client.login(username='testuser1', password='qwerty123')
        self.client.post('/offer/1/accept/')
        self.client.post('/offer/2/decline/')
        offer = ExchangeProposal.objects.get(id=1)
        offer2 = ExchangeProposal.objects.get(id=2)
        self.assertEqual(offer.status, 'ACCEPTED')
        self.assertEqual(offer2.status, 'DECLINED')