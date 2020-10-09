import os

from django import template
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from django.http import HttpResponse

from .forms import StudentSignUpForm, RecruiterSignUpForm, LoginForm, StudentEditForm, RecruiterEditForm, EventEditForm
from .models import Event
from . import match

register = template.Library()

"""
register filter
"""


@register.filter
def get_filename(value):
    return os.path.basename(value.file.name)


"""
Anyone can access pages.
"""


def index(request, user=None):
    """ホームページ"""
    return render(request, 'matching/index.html', {'user': user, })


def student_signup(request):
    """学生登録"""
    form = StudentSignUpForm()

    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('matching:login')

    return render(request, 'matching/signup.html', {'form': form, })


def recruiter_signup(request):
    """リクルーター登録"""
    form = RecruiterSignUpForm()

    if request.method == 'POST':
        form = RecruiterSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('matching:login')

    return render(request, 'matching/signup.html', {'form': form, })


def login_user(request):
    """ログイン"""
    form = LoginForm(request.POST)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user=user)
            user = request.user
            return render(request, 'matching/index.html', {'user': user, })
        else:
            return render(request, 'matching/login.html', {'form': form, })
    else:
        return render(request, 'matching/login.html', {'form': form, })


def logout_user(request):
    """ログアウト"""
    logout(request)
    return redirect('matching:index')


"""  
 User can access pages, without login.
"""


class PasswordReset(PasswordResetView):
    """パスワードリセット申請画面"""
    subject_template_name = 'matching/mail_template/reset/subject.txt'
    email_template_name = 'matching/mail_template/reset/message.txt'
    template_name = 'matching/password_reset.html'
    success_url = reverse_lazy('matching:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワードリセット申請完了画面"""
    template_name = 'matching/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """パスワードリセット実行画面"""
    success_url = reverse_lazy('matching:password_reset_complete')
    template_name = 'matching/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """パスワードリセット実行完了画面"""
    template_name = 'matching/password_reset_complete.html'


"""    
 User, both student and recruiter, can access pages.
"""


@login_required(login_url='matching/login.html')
def user_profile(request):
    """マイ情報画面"""
    return render(request, 'matching/user_profile.html')


@login_required(login_url='matching/login.html')
def user_edit(request):
    """自分の情報変更・登録ページ"""
    is_student = True
    user = request.user
    if not user.is_student:
        is_student = False

    if request.method == 'POST':
        if is_student:
            form = StudentEditForm(request.POST, request.FILES, instance=user)
        else:
            form = RecruiterEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if not user.enable_join_matching:
                user.enable_join_matching = True
            if user.enable_join_matching:
                match.do_match()
            user.save()
            return redirect('matching:user')
    else:
        if is_student:
            form = StudentEditForm(instance=user)
        else:
            form = RecruiterEditForm(instance=user)

    return render(request, 'matching/user_edit.html', {'form': form, })


class UserPasswordChange(PasswordChangeView, LoginRequiredMixin):
    """パスワード変更画面"""
    success_url = reverse_lazy('matching:user')
    template_name = 'matching/password_change.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required(login_url='matching/login.html')
def user_del(request):
    """ユーザー削除"""
    user = request.user
    is_student = user.is_student
    user.delete()
    if is_student:
        pass
    return render(request, 'matching/index.html', )


"""
    Page that user access no authority page, tell user it.
"""


@login_required(login_url='matching/login.html')
def no_authority(request):
    """閲覧権限のないページ"""
    return render(request, 'matching/no_authority.html')


"""
     Only student user can access pages.
"""


@login_required(login_url='matching/login.html')
def events_list(request):
    """イベントの一覧"""
    user = request.user
    if not user.is_student:
        return redirect('matching:no_authority')

    if not user.enable_host_event:
        events = Event.objects.all()
    else:
        events = Event.objects.exclude(created_by__in=[user.username, ])
    my_events = user.join_event.all()
    my_event_id_list = [mps.event_id for mps in my_events]

    return render(request,
                  'matching/events_list.html',
                  {'events': events,
                   'my_event_id_list': my_event_id_list, },
                  )


@login_required(login_url='matching/login.html')
def retry_matching(request):
    """イベント一覧ページでのマッチングの更新"""
    match.do_match()

    return redirect('matching:events_list')


@login_required(login_url='matching/login.html')
def event_detail(request, event_id):
    """イベントの詳細"""

    user = request.user
    if not user.is_student:
        return redirect('matching:no_authority')

    event = get_object_or_404(Event, event_id=event_id)
    my_events = user.join_event.all()

    my_event_id_list = [mps.event_id for mps in my_events]

    return render(request, 'matching/event_detail.html',
                  {'event': event,
                   'my_event_id_list': my_event_id_list, },
                  )


class MyEventsList(ListView, LoginRequiredMixin):
    """自分の参加するイベントの一覧"""
    context_object_name = 'my_events'
    template_name = 'matching/my_events_list.html'
    paginate_by = 10  # １ページは最大10件ずつでページングする

    def get(self, request):
        """自分の登録しているイベントのIDを元に全イベントデータから検索し、その情報を載せる"""
        user = self.request.user
        if not user.is_student:
            return redirect('matching:no_authority')

        my_events = user.join_event.all()

        self.object_list = Event.objects.filter(
            event_id__in=[mps.event_id for mps in my_events],
        )

        context = self.get_context_data(object_list=self.object_list)
        return self.render_to_response(context)


@login_required(login_url='matching/login.html')
def my_event_edit(request, event_id):
    """イベントへの参加"""
    user = request.user
    if not user.is_student:
        return redirect('matching:no_authority')

    target_event = get_object_or_404(Event, event_id=event_id)

    target_event.students.add(user)
    target_event.save()

    return redirect('matching:events_list')


@login_required(login_url='matching/login.html')
def my_event_del(request, event_id):
    """イベントの辞退"""
    user = request.user
    if not user.is_student:
        return redirect('matching:no_authority')

    target_event = get_object_or_404(Event, event_id=event_id)

    target_event.students.remove(user)
    target_event.save()

    return redirect('matching:events_list')


"""
     Only recruiter user can access pages.
"""


class MyHostEventsList(ListView, LoginRequiredMixin):
    """自分が主催するイベント"""
    context_object_name = 'my_host_events'
    template_name = 'matching/my_host_events_list.html'
    paginate_by = 10  # １ページは最大10件ずつでページングする

    def get(self, request):
        """イベントのcreated_byを元に検索する"""
        user = self.request.user
        if not user.enable_host_event:
            return redirect('matching:no_authority')

        self.object_list = Event.objects.filter(created_by__in=[user.username, ])

        context = self.get_context_data(object_list=self.object_list)
        return self.render_to_response(context)


@login_required(login_url='matching/login.html')
def host_event_edit(request, event_id=None):
    """自分が主催するイベントの追加・修正"""
    user = request.user
    if not user.enable_host_event:
        return redirect('matching:no_authority')

    if event_id:
        event = get_object_or_404(Event, event_id=event_id)
    else:
        event = Event()

    if request.method == 'POST':
        form = EventEditForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = user.username
            event.save()
            return redirect('matching:host_events_list')
    else:
        form = EventEditForm(instance=event)

    return render(request, 'matching/event_edit.html', {'form': form, 'event_id': event_id})


@login_required(login_url='matching/login.html')
def host_event_del(request, event_id):
    """主催するイベントの削除"""
    user = request.user
    if not user.enable_host_event:
        return redirect('matching:no_authority')

    event = get_object_or_404(Event, event_id=event_id)
    event.delete()
    return redirect('matching:host_events_list')


@login_required(login_url='matching/login.html')
def analyse_my_event(request):
    """主催するイベント分析"""
    return HttpResponse('自分が主催するイベントの分析')
