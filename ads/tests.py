from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Category, Advertisement, Notification
from decimal import Decimal

# Create your tests here.

class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.assertEqual(str(category), 'Electronics')
        self.assertEqual(category.slug, 'electronics')

class AdvertisementModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpass123',
            is_staff=True
        )

    def test_advertisement_creation(self):
        ad = Advertisement.objects.create(
            title='Test Ad',
            description='Test Description',
            price=Decimal('99.99'),
            category=self.category,
            seller=self.user
        )
        self.assertEqual(str(ad), 'Test Ad')
        self.assertEqual(ad.status, 'pending')
        self.assertTrue(ad.slug)

    def test_staff_ad_auto_approval(self):
        ad = Advertisement.objects.create(
            title='Staff Ad',
            description='Staff Description',
            price=Decimal('99.99'),
            category=self.category,
            seller=self.staff_user
        )
        self.assertEqual(ad.status, 'approved')

class AdvertisementViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpass123',
            is_staff=True
        )
        self.ad = Advertisement.objects.create(
            title='Test Ad',
            description='Test Description',
            price=Decimal('99.99'),
            category=self.category,
            seller=self.user,
            status='approved'
        )

    def test_ad_list_view(self):
        response = self.client.get(reverse('ads:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/list.html')
        self.assertContains(response, 'Test Ad')

    def test_ad_detail_view(self):
        response = self.client.get(reverse('ads:detail', args=[self.ad.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/detail.html')
        self.assertContains(response, 'Test Ad')

    def test_ad_create_view_authentication(self):
        # Test unauthenticated access
        response = self.client.get(reverse('ads:create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test authenticated access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ads:create'))
        self.assertEqual(response.status_code, 200)

    def test_ad_create_submission(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'title': 'New Ad',
            'description': 'New Description',
            'price': '199.99',
            'category': self.category.id,
        }
        response = self.client.post(reverse('ads:create'), data)
        self.assertEqual(Advertisement.objects.count(), 2)
        new_ad = Advertisement.objects.get(title='New Ad')
        self.assertEqual(new_ad.status, 'pending')

class NotificationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.ad = Advertisement.objects.create(
            title='Test Ad',
            description='Test Description',
            price=Decimal('99.99'),
            category=self.category,
            seller=self.user
        )

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user,
            notification_type='ad_approved',
            title='Ad Approved',
            message='Your ad has been approved',
            related_ad=self.ad
        )
        self.assertEqual(str(notification), 'Ad Approved for testuser')
        self.assertFalse(notification.read)

class AdvertisementEdgeCaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
    def test_price_validation(self):
        """Test price validation for negative and zero values"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test negative price
        data = {
            'title': 'Test Ad',
            'description': 'Description',
            'price': '-10.00',
            'category': self.category.id,
        }
        response = self.client.post(reverse('ads:create'), data)
        self.assertEqual(response.status_code, 200)  # Form should not submit
        self.assertFalse(Advertisement.objects.filter(title='Test Ad').exists())

    def test_xss_prevention(self):
        """Test that HTML in title and description is escaped"""
        ad = Advertisement.objects.create(
            title='<script>alert("xss")</script>',
            description='<script>alert("xss")</script>',
            price=Decimal('99.99'),
            category=self.category,
            seller=self.user
        )
        response = self.client.get(reverse('ads:detail', args=[ad.slug]))
        self.assertNotContains(response, '<script>')

class AdvertisementPermissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        
    def test_edit_permissions(self):
        """Test that users can only edit their own ads"""
        ad = Advertisement.objects.create(
            title='Test Ad',
            description='Description',
            price=Decimal('99.99'),
            category=self.category,
            seller=self.user1
        )
        
        # Try editing as user2
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('ads:edit', args=[ad.slug]))
        self.assertEqual(response.status_code, 302)  # Should redirect

class ModerationWorkflowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.user = User.objects.create_user(username='user', password='pass123')
        self.staff = User.objects.create_user(
            username='staff',
            password='pass123',
            is_staff=True
        )
        
    def test_moderation_workflow(self):
        """Test the complete moderation workflow"""
        ad = Advertisement.objects.create(
            title='Test Ad',
            description='Description',
            price=Decimal('99.99'),
            category=self.category,
            seller=self.user
        )
        
        # Verify initial state
        self.assertEqual(ad.status, 'pending')
        
        # Staff approves ad
        self.client.login(username='staff', password='pass123')
        response = self.client.post(reverse('ads:approve', args=[ad.slug]))
        ad.refresh_from_db()
        self.assertEqual(ad.status, 'approved')
        
        # Check notification was created
        self.assertTrue(
            Notification.objects.filter(
                user=self.user,
                notification_type='ad_approved'
            ).exists()
        )
