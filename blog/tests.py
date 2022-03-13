from django.test import TestCase
from django.urls import reverse

from .models import Post, User, Tag


def create_user(name):
    user = User(username=name)
    user.set_password('test')
    user.save()
    return user


def create_post(author, title, tags=None):
    post = Post(author=author, title=title, content='testtesttest')
    post.save()
    if tags:
        post = Post.objects.get(title=title)
        post.tags.set(tags)
        post.save()
    return post


class PostModelTests(TestCase):
    def test_content_preview_long(self):
        """
        If the content of a post is longer than 300 characters,
        the content_preview should be cut off at 297 characters and '...'
        should be appended.
        Otherwise, the preview should match the content.
        """
        user = create_user('testuser')
        long_content = """iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
        iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
        iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"""
        post = Post(author=user, title='long content', content=long_content)
        post.save()
        post = Post.objects.get(title='long content')

        self.assertEqual(len(post.content_preview), 300)
        self.assertEqual(post.content_preview[297:], '...')

    def test_content_preview_short(self):
        """
        See above.
        """
        user = create_user('testuser')
        short_content = """short post content"""
        post = Post(author=user, title='short content', content=short_content)
        post.save()
        post = Post.objects.get(title='short content')

        self.assertEqual(post.content_preview, post.content)


class StartingPageViewTests(TestCase):
    def test_deny_anonymous(self):
        response = self.client.get(reverse('starting-page'), follow=True)
        self.assertRedirects(response, '/login/?next=/')
        response = self.client.post(reverse('starting-page'), follow=True)
        self.assertRedirects(response, '/login/?next=/')

    def test_load(self):
        create_user('user')
        self.client.login(username='user', password='test')
        response = self.client.get(reverse('starting-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post-list.html')

    def test_post_method(self):
        create_user('user')
        self.client.login(username='user', password='test')
        response = self.client.post(reverse('starting-page'), {})
        self.assertEqual(response.status_code, 405)

    def test_blog_posts_loaded(self):
        user = create_user('user')
        create_post(user, 'test')
        self.client.login(username='user', password='test')
        response = self.client.get(reverse('starting-page'))
        posts = response.context['posts']
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].title, 'test')
        self.assertEqual(posts[0].content, 'testtesttest')


class UserPageViewTests(TestCase):
    def setUp(self):
        super().setUp()
        user = create_user('user')
        create_post(user, 'test1')
        create_post(user, 'test2')

    def test_deny_anonymous(self):
        response = self.client.get(reverse('user-page', args=['user']), follow=True)
        self.assertRedirects(response, '/login/?next=/blog/user/')
        response = self.client.post(reverse('user-page', args=['user']), follow=True)
        self.assertRedirects(response, '/login/?next=/blog/user/')

    def test_load(self):
        self.client.login(username='user', password='test')
        response = self.client.get(reverse('user-page', args=['user']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/user-page.html')
        posts = response.context['posts']
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0].title, 'test2')
        self.assertEqual(posts[0].content, 'testtesttest')

    def test_post_method(self):
        self.client.login(username='user', password='test')
        response = self.client.post(reverse('user-page', args=['user']), {})
        self.assertEqual(response.status_code, 405)

    def test_other_users_post_not_loaded(self):
        user2 = create_user('user2')
        create_post(user2, 'user2 post')
        self.client.login(username='user', password='test')
        response = self.client.get(reverse('user-page', args=['user']))
        posts = response.context['posts']
        self.assertEqual(len(posts), 2)


class PostViewTests(TestCase):
    def setUp(self):
        super().setUp()
        user = create_user('user')
        create_post(user, 'test')

    def test_deny_anonymous(self):
        response = self.client.get(reverse('post-view', args=['user', 'test']), follow=True)
        self.assertRedirects(response, '/login/?next=/blog/user/test')
        response = self.client.post(reverse('post-view', args=['user', 'test']), follow=True)
        self.assertRedirects(response, '/login/?next=/blog/user/test')

    def test_load(self):
        self.client.login(username='user', password='test')
        response = self.client.get(reverse('post-view', args=['user', 'test']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post-detail.html')

    def test_post_method(self):
        self.client.login(username='user', password='test')
        response = self.client.post(reverse('post-view', args=['user', 'test']), {})
        self.assertEqual(response.status_code, 405)


class TagPageViewTests(TestCase):
    def setUp(self):
        super().setUp()
        user = create_user('user')
        test_tag = Tag(name='test-tag')
        other_tag = Tag(name='other-tag')
        test_tag.save()
        other_tag.save()
        create_post(user, 'test1', [test_tag])
        create_post(user, 'test2', [other_tag])

    def test_deny_anonymous(self):
        response = self.client.get(reverse('tag-view', args=['test-tag']), follow=True)
        self.assertRedirects(response, '/login/?next=/tag/test-tag/')
        response = self.client.post(reverse('tag-view', args=['test-tag']), follow=True)
        self.assertRedirects(response, '/login/?next=/tag/test-tag/')

    def test_load(self):
        self.client.login(username='user', password='test')
        response = self.client.get(reverse('tag-view', args=['test-tag']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post-list.html')

    def test_post_method(self):
        self.client.login(username='user', password='test')
        response = self.client.post(reverse('tag-view', args=['test-tag']), {})
        self.assertEqual(response.status_code, 405)

    def test_tagged_post_loaded(self):
        self.client.login(username='user', password='test')
        response = self.client.get(reverse('tag-view', args=['test-tag']))
        loaded_tag_name = response.context['posts'][0].tags.all()[0].name
        self.assertEqual(loaded_tag_name, 'test-tag')

    def test_other_tag_not_loaded(self):
        self.client.login(username='user', password='test')
        response = self.client.get(reverse('tag-view', args=['test-tag']))
        loaded_tag_name = response.context['posts'][0].tags.all()[0].name
        self.assertEqual(loaded_tag_name, 'test-tag')
        self.assertEqual(len(response.context['posts']), 1)


class LoginViewTests(TestCase):
    def test_load(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/login-page.html')

    def test_login(self):
        create_user('user')
        response = self.client.post(reverse('login'), follow=True, data={
            'username': 'user',
            'password': 'test',
        })
        self.assertRedirects(response, '/')
        self.assertTrue(response.context['user'].is_authenticated)

    def test_failed_login(self):
        create_user('user')
        response = self.client.post(reverse('login'), follow=True, data={
            'username': 'user',
            'password': 'testt',
        })
        self.assertIsNotNone(response.context['form'].errors)
        self.assertFalse(response.context['user'].is_authenticated)


class RegisterViewTests(TestCase):
    def test_load(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/registration-page.html')

    def test_registration(self):
        response = self.client.post(reverse('register'), follow=True, data={
            'username': 'user',
            'password1': 'testheart',
            'password2': 'testheart',
        })

        self.assertRedirects(response, '/')
        self.assertTrue(response.context['user'].is_authenticated)

    def test_failed_registration(self):
        response = self.client.post(reverse('register'), follow=True, data={
            'username': 'user',
            'password1': 'test1',
            'password2': 'test2',
        })
        self.assertIsNotNone(response.context['form'].errors)
        self.assertFalse(response.context['user'].is_authenticated)
