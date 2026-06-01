from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from chat.models import ChatRoom
from posts.models import Category, SharingParticipant, Wish, groupsParticipant, groupsPost, sharingPost


class PostParticipationTests(TestCase):
    def setUp(self):
        self.host = User.objects.create_user(username='01011112222', password='pass12345')
        self.member = User.objects.create_user(username='01033334444', password='pass12345')
        self.category = Category.objects.create(name='food')
        self.deadline = timezone.now() + timezone.timedelta(days=1)

    def create_group(self, status='recruiting'):
        return groupsPost.objects.create(
            host=self.host,
            category=self.category,
            title='group post',
            content='content',
            min_members=3,
            current_members=0,
            price_per=1000,
            location='station',
            deadline=self.deadline,
            status=status,
        )

    def test_group_create_redirects_to_list_and_creates_chat_room(self):
        self.client.force_login(self.host)
        deadline = timezone.now() + timezone.timedelta(days=2)

        response = self.client.post(reverse('posts:group_create'), {
            'category': self.category.id,
            'title': 'new group post',
            'content': 'content',
            'min_members': 3,
            'price_per': 1500,
            'location': 'station',
            'deadline_date': deadline.strftime('%Y-%m-%d'),
            'deadline_time': deadline.strftime('%H:%M'),
            'link': 'https://example.com/product',
        })

        group = groupsPost.objects.get(title='new group post')
        room = ChatRoom.objects.get(group_post=group)
        self.assertRedirects(response, reverse('posts:group_list'), fetch_redirect_response=False)
        self.assertEqual(group.host, self.host)
        self.assertEqual(group.link, 'https://example.com/product')
        self.assertEqual(room.name, ChatRoom.group_room_name(group.id))

    def test_group_create_accepts_legacy_product_url_field(self):
        self.client.force_login(self.host)
        deadline = timezone.now() + timezone.timedelta(days=2)

        response = self.client.post(reverse('posts:group_create'), {
            'category': self.category.id,
            'title': 'legacy link group post',
            'content': 'content',
            'min_members': 3,
            'price_per': 1500,
            'location': 'station',
            'deadline_date': deadline.strftime('%Y-%m-%d'),
            'deadline_time': deadline.strftime('%H:%M'),
            'product_url': 'https://example.com/legacy-product',
        })

        group = groupsPost.objects.get(title='legacy link group post')
        self.assertRedirects(response, reverse('posts:group_list'), fetch_redirect_response=False)
        self.assertEqual(group.link, 'https://example.com/legacy-product')

    def test_group_create_creates_default_category_when_missing(self):
        Category.objects.all().delete()
        self.client.force_login(self.host)
        deadline = timezone.now() + timezone.timedelta(days=2)

        response = self.client.post(reverse('posts:group_create'), {
            'title': 'group without category',
            'content': 'content',
            'min_members': 3,
            'price_per': '1,500',
            'location': 'station',
            'deadline_date': deadline.strftime('%Y-%m-%d'),
            'deadline_time': deadline.strftime('%H:%M'),
        })

        group = groupsPost.objects.get(title='group without category')
        self.assertRedirects(response, reverse('posts:group_list'), fetch_redirect_response=False)
        self.assertEqual(group.category.name, '식품')
        self.assertEqual(group.price_per, 1500)
        self.assertTrue(ChatRoom.objects.filter(group_post=group).exists())

    def create_share(self, status='recruiting'):
        return sharingPost.objects.create(
            host=self.host,
            category=self.category,
            title='share post',
            content='content',
            quantity=3,
            location='station',
            deadline=self.deadline,
            status=status,
        )

    def test_share_create_redirects_to_list_and_creates_chat_room(self):
        self.client.force_login(self.host)
        deadline = timezone.now() + timezone.timedelta(days=2)

        response = self.client.post(reverse('posts:share_create'), {
            'category': self.category.id,
            'title': 'new share post',
            'content': 'content',
            'quantity': 2,
            'location': 'station',
            'deadline_date': deadline.strftime('%Y-%m-%d'),
            'deadline_time': deadline.strftime('%H:%M'),
        })

        share = sharingPost.objects.get(title='new share post')
        room = ChatRoom.objects.get(sharing_post=share)
        self.assertRedirects(response, reverse('posts:share_list'), fetch_redirect_response=False)
        self.assertEqual(share.host, self.host)
        self.assertEqual(room.name, ChatRoom.sharing_room_name(share.id))

    def test_share_create_creates_default_category_when_missing(self):
        Category.objects.all().delete()
        self.client.force_login(self.host)
        deadline = timezone.now() + timezone.timedelta(days=2)

        response = self.client.post(reverse('posts:share_create'), {
            'title': 'share without category',
            'content': 'content',
            'quantity': 2,
            'location': 'station',
            'deadline_date': deadline.strftime('%Y-%m-%d'),
            'deadline_time': deadline.strftime('%H:%M'),
        })

        share = sharingPost.objects.get(title='share without category')
        self.assertRedirects(response, reverse('posts:share_list'), fetch_redirect_response=False)
        self.assertEqual(share.category.name, '식품')
        self.assertTrue(ChatRoom.objects.filter(sharing_post=share).exists())

    def test_group_participate_uses_group_id_and_creates_chat_room(self):
        group = self.create_group()
        self.client.force_login(self.member)

        response = self.client.post(reverse('posts:group_participate', args=[group.id]))

        room = ChatRoom.objects.get(group_post=group)
        self.assertRedirects(response, reverse('chat:room', args=[room.id]), fetch_redirect_response=False)
        self.assertEqual(room.name, ChatRoom.group_room_name(group.id))
        self.assertTrue(groupsParticipant.objects.filter(group=group, user=self.member).exists())
        group.refresh_from_db()
        self.assertEqual(group.current_members, 1)

    def test_group_wish_toggle_creates_and_deletes_wish(self):
        group = self.create_group()
        self.client.force_login(self.member)

        response = self.client.post(reverse('posts:group_wish_toggle', args=[group.id]))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'wished': True})
        self.assertTrue(self.member.wishes.filter(group=group).exists())

        response = self.client.post(reverse('posts:group_wish_toggle', args=[group.id]))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'wished': False})
        self.assertFalse(self.member.wishes.filter(group=group).exists())

    def test_group_list_heart_button_includes_authentication_data(self):
        self.create_group()
        self.client.force_login(self.member)

        response = self.client.get(reverse('posts:group_list'))

        self.assertContains(response, 'data-authenticated="true"')
        self.assertContains(response, reverse('accounts:login'))

    def test_group_list_wish_filter_shows_only_wished_posts(self):
        wished_group = self.create_group()
        other_group = groupsPost.objects.create(
            host=self.host,
            category=self.category,
            title='other group post',
            content='content',
            min_members=3,
            current_members=0,
            price_per=1000,
            location='station',
            deadline=self.deadline,
        )
        Wish.objects.create(user=self.member, group=wished_group)
        self.client.force_login(self.member)

        response = self.client.get(reverse('posts:group_list'), {'wish': '1'})

        self.assertContains(response, wished_group.title)
        self.assertNotContains(response, other_group.title)
        self.assertContains(response, 'class="alarm-btn active"')

    def test_group_participate_rejects_duplicate_active_participation(self):
        group = self.create_group()
        groupsParticipant.objects.create(group=group, user=self.member)
        self.client.force_login(self.member)

        response = self.client.post(reverse('posts:group_participate', args=[group.id]))

        self.assertEqual(response.status_code, 400)

    def test_group_participate_rejects_closed_post(self):
        group = self.create_group(status='closed')
        self.client.force_login(self.member)

        response = self.client.post(reverse('posts:group_participate', args=[group.id]))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(ChatRoom.objects.filter(group_post=group).exists())

    def test_share_participate_uses_share_id_and_creates_chat_room(self):
        share = self.create_share()
        self.client.force_login(self.member)

        response = self.client.post(reverse('posts:share_participate', args=[share.id]))

        room = ChatRoom.objects.get(sharing_post=share)
        self.assertRedirects(response, reverse('chat:room', args=[room.id]), fetch_redirect_response=False)
        self.assertEqual(room.name, ChatRoom.sharing_room_name(share.id))
        self.assertTrue(SharingParticipant.objects.filter(sharing=share, user=self.member).exists())

    def test_share_detail_context_includes_chat_room(self):
        share = self.create_share()
        room, _ = ChatRoom.get_or_create_for_share(share)
        self.client.force_login(self.member)
        SharingParticipant.objects.create(sharing=share, user=self.member)

        response = self.client.get(reverse('posts:share_detail', args=[share.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['room'], room)
        self.assertTrue(response.context['is_participated'])

    def test_share_wish_toggle_creates_and_deletes_wish(self):
        share = self.create_share()
        self.client.force_login(self.member)

        response = self.client.post(reverse('posts:sharing_wish_toggle', args=[share.id]))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'wished': True})
        self.assertTrue(self.member.wishes.filter(sharing=share).exists())

        response = self.client.post(reverse('posts:sharing_wish_toggle', args=[share.id]))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'wished': False})
        self.assertFalse(self.member.wishes.filter(sharing=share).exists())

    def test_share_list_heart_button_includes_authentication_data(self):
        self.create_share()
        self.client.force_login(self.member)

        response = self.client.get(reverse('posts:share_list'))

        self.assertContains(response, 'data-authenticated="true"')
        self.assertContains(response, reverse('accounts:login'))

    def test_share_list_wish_filter_shows_only_wished_posts(self):
        wished_share = self.create_share()
        other_share = sharingPost.objects.create(
            host=self.host,
            category=self.category,
            title='other share post',
            content='content',
            quantity=3,
            location='station',
            deadline=self.deadline,
        )
        Wish.objects.create(user=self.member, sharing=wished_share)
        self.client.force_login(self.member)

        response = self.client.get(reverse('posts:share_list'), {'wish': '1'})

        self.assertContains(response, wished_share.title)
        self.assertNotContains(response, other_share.title)
        self.assertContains(response, 'class="alarm-btn active"')
