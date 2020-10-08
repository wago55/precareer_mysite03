from django.urls import path

from . import views

app_name = 'matching'
urlpatterns = [
    # Anyone can access pages.
    path('', views.index, name='home'),  # ホーム
    path('signup/student/', views.student_signup, name='student_signup'),  # 学生登録
    path('signup/recruiter/', views.recruiter_signup, name='recruiter_signup'),  # リクルーター登録
    path('login/', views.login_user, name='login'),  # ログイン
    path('logout/', views.logout_user, name='logout'),  # ログアウト

    # User can access pages, without login.
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),  # パスワードリセット申請
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),  # パスワードリセット申請完了
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    # パスワードリセット実行
    path('reset/done/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),  # パスワードリセット実行完了

    # User, both student and recruiter, can access pages.
    path('user/', views.user_profile, name='user'),  # ユーザープロフィール
    path('user/edit/', views.user_edit, name='user_edit'),  # ユーザープロフィール変更
    path('user/password_chnage/', views.UserPasswordChange.as_view(), name='user_password_change'),  # パスワード変更
    path('user/del/', views.user_del, name='user_del'),  # ユーザー削除

    # Page that user access no authority page, tell user it.
    path('user/no_authority', views.no_authority, name='no_authority'),  # 閲覧権限のないアクセス

    # Only student user can access pages.
    path('user/events_list/', views.events_list, name='events_list'),  # イベント一覧
    path('user/retry_matching/', views.retry_matching, name='retry_matching'),  # イベントの更新
    path('user/event/detail/<str:event_id>', views.event_detail, name='event_detail'),  # イベントの詳細
    path('user/my_events_list/', views.MyEventsList.as_view(), name='my_events_list'),  # 参加予定のイベント一覧
    path('user/events/add/<str:event_id>/', views.my_event_edit, name='my_event_add'),  # イベントへの参加
    path('user/events/del/<str:event_id>/', views.my_event_del, name='my_event_del'),  # イベントの辞退

    # Only recruiter user can access pages.
    path('user/host_events_list/', views.MyHostEventsList.as_view(), name='host_events_list'),
    # 自分の主催するイベント一覧
    path('user/host_event/add/', views.host_event_edit, name='host_event_add'),  # イベントの開催
    path('user/host_event/mod/<str:event_id>/', views.host_event_edit, name='host_event_mod'),  # イベントの編集
    path('user/host_event/del/<str:event_id>/', views.host_event_del, name='host_event_del'),  # イベントの削除
    path('user/host_event/analyse', views.analyse_my_event,
         name='analyse_my_event'),
    # 分析ページ

]
