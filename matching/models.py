from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from .utils import constract, utils


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username or not email:
            raise ValueError('Users must have an username and an email address')

        user = self.model(
            username=self.model.normalize_username(username),
            email=email,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given username, email and password.
        """
        user = self.create_user(
            username,
            password=password,
            email=email,
        )
        user.is_admin = True
        user.is_student = True
        user.enable_host_event = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    # Common elements of both Student and Recruiter
    username = models.CharField('ユーザー名', max_length=255, unique=True)
    email = models.EmailField('メールアドレス', unique=True)
    first_name = models.CharField('名前', max_length=255, )
    last_name = models.CharField('苗字', max_length=255, )
    profile_image = models.ImageField('プロフィール画像', upload_to='profile_images/')
    profile_image_edit = ImageSpecField(source='profile_image', processors=[ResizeToFill(100, 100)], )

    # Elements of only Student
    nickname = models.CharField('ニックネーム', max_length=255, blank=True)
    university = models.CharField('大学名', max_length=255, blank=True)
    date_of_birth = models.DateField('誕生日', blank=True, null=True)
    sex = models.CharField('性別', max_length=255, choices=constract.SEX_CATEGORY, default='', blank=True)
    year = models.IntegerField('卒年', choices=constract.YEAR_CATEGORY, blank=True, null=True)
    s_and_h = models.CharField('理文', max_length=255, choices=constract.S_AND_H_CATEGORY, default='', blank=True)
    major = models.CharField('専攻', max_length=255, choices=constract.MAJOR_CATEGORY, default='', blank=True)
    indestry1 = models.IntegerField('志望業種１',
                                    choices=constract.INDESTRY_CATEGORY,
                                    blank=True)
    indestry2 = models.IntegerField('志望業種２',
                                    choices=constract.INDESTRY_CATEGORY,
                                    blank=True)
    indestry3 = models.IntegerField('志望業種３',
                                    choices=constract.INDESTRY_CATEGORY,
                                    blank=True)
    job1 = models.CharField('志望職種１', max_length=255,
                            choices=constract.JOB_CATEGORY,
                            blank=True)
    job2 = models.CharField('志望職種２', max_length=255,
                            choices=constract.JOB_CATEGORY,
                            blank=True)
    job3 = models.CharField('志望職種３', max_length=255,
                            choices=constract.JOB_CATEGORY,
                            blank=True)
    company_type = models.CharField('会社規模', max_length=255, choices=constract.COMPANY_TYPE_CATEGORY, default='',
                                    blank=True)

    # Elements of only Recruiter
    recruiter_type = models.CharField('組織タイプ', choices=constract.RECRUITER_TYPE, max_length=255, blank=True)
    company_name = models.CharField('会社名・組織名', max_length=255, blank=True)
    department_name = models.CharField('部署名', max_length=255, blank=True)
    position = models.CharField('役職', max_length=255, blank=True)
    operating_medium = models.CharField('運営媒体・運営会社', max_length=255, blank=True)

    # About Permission
    is_student = models.BooleanField(verbose_name='学生であるか', default=False)
    enable_host_event = models.BooleanField(verbose_name='イベント開催できるか', default=False)
    enable_join_matching = models.BooleanField(verbose_name='マッチング対象か', default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Event(models.Model):
    """イベント・練習会"""
    event_id = models.CharField('イベントID', max_length=255, unique=True)
    name = models.CharField('イベント名', max_length=255)
    host = models.CharField('主催者', max_length=255)
    thumbnail = models.ImageField('サムネイル', upload_to='thumbnails/', )
    thumbnail_edit = ImageSpecField(source='thumbnail', processors=[ResizeToFill(250, 250)], )

    place = models.CharField('開催場所', max_length=255)
    event_type_tag = models.CharField('イベントタイプ', choices=constract.EVENT_TYPE, max_length=255)
    video_url = models.URLField('イベントリンク', max_length=3000, null=True, blank=True)
    date = models.DateTimeField('開始日時', )
    time = models.DurationField('開催時間', max_length=255)
    participant_num = models.PositiveIntegerField('参加可能人数', default=0)
    comment01 = models.TextField('当日の流れ')
    comment02 = models.TextField('主催者から一言')

    created_by = models.CharField('作成者', max_length=255, blank=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    enable_matching = models.BooleanField('全員に表示させる', default=True)
    # min_matching_score = models.IntegerField('最低マッチングスコア', null=True)
    recommend_users = models.TextField('マッチングしたユーザー', blank=True)
    # recommend_users_num = models.PositiveIntegerField('マッチングさせるユーザーの数', default=5)

    # sex = models.CharField('性別', max_length=255, choices=category_add_all(SEX_CATEGORY), default='')
    year = models.CharField('卒年', max_length=255)
    s_and_h = models.CharField('理文', max_length=255, choices=utils.category_add_all(constract.S_AND_H_CATEGORY),
                               default='')
    # major = models.CharField('専攻', max_length=255, choices=category_add_all(MAJOR_CATEGORY), default='')
    indestry1 = models.IntegerField('志望業種１',
                                    choices=utils.category_add_all(constract.INDESTRY_CATEGORY),
                                    default='')
    indestry2 = models.IntegerField('志望業種２',
                                    choices=utils.category_add_all(constract.INDESTRY_CATEGORY),
                                    default='')
    indestry3 = models.IntegerField('志望業種３',
                                    choices=utils.category_add_all(constract.INDESTRY_CATEGORY),
                                    default='')
    # job1 = models.CharField('志望職種１', max_length=255,
    #                         choices=category_add_all(JOB_CATEGORY),
    #                         default='')
    # job2 = models.CharField('志望職種２', max_length=255,
    #                         choices=category_add_all(JOB_CATEGORY),
    #                         default='')
    # job3 = models.CharField('志望職種３', max_length=255,
    #                         choices=category_add_all(JOB_CATEGORY),
    #                         default='')
    # company_type = models.CharField('会社規模', max_length=255, choices=category_add_all(COMPANY_TYPE_CATEGORY),
    #                                 default='')
    students = models.ManyToManyField(User,
                                      verbose_name='参加予定のユーザー',
                                      related_name='join_event'
                                      )

    @property
    def remaining_participant(self):
        """残り参加可能人数"""
        return self.participant_num - self.students.count()

    @property
    def participant_num_now(self):
        """参加予定人数"""
        return self.students.count()
