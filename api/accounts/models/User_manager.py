from django.contrib.auth.models import BaseUserManager

# 自定義的UserManager来管理用户
class UserManager(BaseUserManager):
    # 創建用戶
    def _create_user(self, email, password, **kwargs):
        email = self.normalize_email(email)
        is_staff = kwargs.pop('is_staff', False)
        is_superuser = kwargs.pop('is_superuser', False)
        user = self.model(
            email=email,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    # 創建用戶並設置密碼
    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    # 創建管理員用戶並設置密碼
    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, is_staff=True, is_superuser=True, **extra_fields)
