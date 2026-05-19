from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class HertzUserManager(BaseUserManager):
    """
    用户管理器
    """
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('用户名不能为空')
        if not email:
            raise ValueError('邮箱不能为空')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 1)
        
        return self.create_user(username, email, password, **extra_fields)


class HertzUser(AbstractBaseUser):
    """
    用户表
    """
    STATUS_CHOICES = [
        (0, '禁用'),
        (1, '启用'),
    ]
    
    GENDER_CHOICES = [
        (0, '未知'),
        (1, '男'),
        (2, '女'),
    ]
    
    user_id = models.AutoField(primary_key=True, verbose_name='用户ID')
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=128, verbose_name='密码')
    email = models.EmailField(unique=True, verbose_name='邮箱')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    real_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='真实姓名')
    avatar = models.URLField(blank=True, null=True, verbose_name='头像URL')
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0, verbose_name='性别')
    birthday = models.DateField(blank=True, null=True, verbose_name='生日')
    department_id = models.ForeignKey('HertzDepartment', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='部门ID')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='状态')
    last_login_time = models.DateTimeField(blank=True, null=True, verbose_name='最后登录时间')
    last_login_ip = models.CharField(max_length=128,blank=True, null=True, verbose_name='最后登录IP')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # Django内置字段
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = HertzUserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'hertz_auth_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser
    
    @property
    def roles(self):
        """获取用户角色"""
        return HertzRole.objects.filter(
            hertzuserrole__user=self,
            status=1
        )


class HertzRole(models.Model):
    """
    角色表
    """
    STATUS_CHOICES = [
        (0, '禁用'),
        (1, '启用'),
    ]
    
    role_id = models.AutoField(primary_key=True, verbose_name='角色ID')
    role_name = models.CharField(max_length=50, unique=True, verbose_name='角色名称')
    role_code = models.CharField(max_length=50, unique=True, verbose_name='角色代码')
    description = models.TextField(blank=True, null=True, verbose_name='角色描述')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='状态')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hertz_auth_role'
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return self.role_name
    
    @property
    def menus(self):
        """获取角色关联的菜单"""
        return HertzMenu.objects.filter(
            hertzrolemenu__role=self
        )


class HertzMenu(models.Model):
    """
    菜单表
    """
    MENU_TYPE_CHOICES = [
        (1, '目录'),
        (2, '菜单'),
        (3, '按钮'),
    ]
    
    STATUS_CHOICES = [
        (0, '禁用'),
        (1, '启用'),
    ]
    
    menu_id = models.AutoField(primary_key=True, verbose_name='菜单ID')
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name='父菜单ID')
    menu_name = models.CharField(max_length=50, verbose_name='菜单名称')
    menu_code = models.CharField(max_length=100, unique=True, verbose_name='菜单代码')
    menu_type = models.IntegerField(choices=MENU_TYPE_CHOICES, verbose_name='菜单类型')
    path = models.CharField(max_length=200, blank=True, null=True, verbose_name='路由路径')
    component = models.CharField(max_length=200, blank=True, null=True, verbose_name='组件路径')
    icon = models.CharField(max_length=100, blank=True, null=True, verbose_name='菜单图标')
    permission = models.CharField(max_length=100, blank=True, null=True, verbose_name='权限标识')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='状态')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_external = models.BooleanField(default=False, verbose_name='是否外链')
    is_cache = models.BooleanField(default=True, verbose_name='是否缓存')
    is_visible = models.BooleanField(default=True, verbose_name='是否显示')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hertz_auth_menu'
        verbose_name = '菜单'
        verbose_name_plural = '菜单'
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return self.menu_name


class HertzDepartment(models.Model):
    """
    部门表
    """
    STATUS_CHOICES = [
        (0, '禁用'),
        (1, '启用'),
    ]
    
    dept_id = models.AutoField(primary_key=True, verbose_name='部门ID')
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name='父部门ID')
    dept_name = models.CharField(max_length=50, verbose_name='部门名称')
    dept_code = models.CharField(max_length=50, unique=True, verbose_name='部门代码')
    leader = models.CharField(max_length=50, blank=True, null=True, verbose_name='负责人')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='联系电话')
    email = models.EmailField(blank=True, null=True, verbose_name='邮箱')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='状态')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hertz_auth_department'
        verbose_name = '部门'
        verbose_name_plural = '部门'
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return self.dept_name


class HertzUserRole(models.Model):
    """
    用户角色关联表
    """
    id = models.AutoField(primary_key=True, verbose_name='ID')
    user = models.ForeignKey(HertzUser, on_delete=models.CASCADE, verbose_name='用户')
    role = models.ForeignKey(HertzRole, on_delete=models.CASCADE, verbose_name='角色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'hertz_auth_user_role'
        verbose_name = '用户角色'
        verbose_name_plural = '用户角色'
        unique_together = ['user', 'role']
    
    def __str__(self):
        return f'{self.user.username} - {self.role.role_name}'


class HertzRoleMenu(models.Model):
    """
    角色菜单关联表
    """
    id = models.AutoField(primary_key=True, verbose_name='ID')
    role = models.ForeignKey(HertzRole, on_delete=models.CASCADE, verbose_name='角色')
    menu = models.ForeignKey(HertzMenu, on_delete=models.CASCADE, verbose_name='菜单')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'hertz_auth_role_menu'
        verbose_name = '角色菜单'
        verbose_name_plural = '角色菜单'
        unique_together = ['role', 'menu']
    
    def __str__(self):
        return f'{self.role.role_name} - {self.menu.menu_name}'
