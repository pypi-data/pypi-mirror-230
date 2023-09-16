import os

from django.contrib import auth


from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .subscription import Subscription
from .base import BaseModelAbstract

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from ..fields.media_field import MediaField


def upload_to(instance, filename):
    f, ext = os.path.splitext(filename)
    return f'avatars/{instance.id}{ext}'


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        # email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        # GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)

        User = get_user_model()
        username = User().normalize_username(username)

        print("extra_fields", )

        # extra_fields.pop('last_name')
        print("extra_fields",extra_fields )

        user = self.model(username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(AbstractUser, BaseModelAbstract):
    """
        Overrides django's default auth model
    """
    email = None
    last_name = None
    REQUIRED_FIELDS = ["first_name"]
    objects = UserManager()

    reset_token = models.CharField(max_length=10, null=True, blank=True,
                                   editable=False)
    reset_token_expiry = models.DateTimeField(null=True, blank=True,
                                              editable=False)
    avatar = models.ImageField(upload_to=upload_to, null=True, blank=True)

    @property
    def current_subscription(self):
        return Subscription.objects.filter(
            created_by=self
        ).latest('created_at')

    @property
    def has_active_subscription(self) -> bool:
        if self.current_subscription:
            return not (
                self.current_subscription.expired or
                self.current_subscription.expiry <= timezone.now()
            )
        return False


class Token(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(
        User, related_name='auth_token',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField("Created", auto_now_add=True)

    class Meta:
        db_table = 'authtoken_token'
        managed = False
