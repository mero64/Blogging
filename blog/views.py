from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, FormView, CreateView

from .forms import MyUserCreationForm, PostForm
from .models import Post


class StartingPageView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'blog/post-list.html'
    model = Post
    ordering = ['-date']
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super().get_queryset()
        data = queryset[:100]
        return data

    def get_context_data(self, **kwargs):
        context = {'title': 'Latest Blog Posts'}
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class UserPageView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'blog/user-page.html'
    model = Post
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = Post.objects.filter(author__username=self.kwargs['username']).order_by('-date')
        return queryset

    def get_context_data(self, **kwargs):
        blogger_name = self.kwargs['username']
        context = {'blogger_name': self.kwargs['username']}

        if blogger_name == self.request.user.username:
            context['form'] = PostForm()

        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request, username):
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()
            post.tags.set(post_form.cleaned_data['tags'])
            post.save()
        return redirect('user-page', username)


class PostView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'blog/post-detail.html'
    model = Post

    def get(self, request, username, slug):
        post = get_object_or_404(Post, slug=slug)
        context = {
            'post': post,
            'tags': post.tags.all()
        }
        return render(request, 'blog/post-detail.html', context)


class TagPageView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'blog/post-list.html'
    model = Post
    ordering = ['-date']
    context_object_name = 'posts'

    def get_queryset(self):
        data = Post.objects.filter(tags__name__in=[self.kwargs['tag']])
        return data

    def get_context_data(self, **kwargs):
        context = {'title': f"Posts with Tag: {self.kwargs['tag']}"}
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'blog/login-page.html'
    success_url = reverse_lazy('starting-page')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(self.request, user)
            return HttpResponseRedirect(self.success_url)
        else:
            raise ValidationError()


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


class RegisterView(CreateView):
    form_class = MyUserCreationForm
    template_name = 'blog/registration-page.html'
    success_url = reverse_lazy('starting-page')

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        new_user = authenticate(username=username, password=password)
        if new_user is not None and new_user.is_active:
            login(self.request, new_user)
            return HttpResponseRedirect(self.success_url)
        else:
            raise ValidationError()

