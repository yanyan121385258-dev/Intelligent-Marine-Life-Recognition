from rest_framework import serializers
from django.core.validators import RegexValidator
from drf_spectacular.utils import extend_schema_field
from studio_django_utils.validators import EmailValidator, PhoneValidator, PasswordValidator
from studio_django_utils.crypto import EncryptionUtils
from ..models import HertzUser, HertzRole, HertzMenu, HertzDepartment, HertzUserRole, HertzRoleMenu


class UserManagementSerializer(serializers.ModelSerializer):
    """用户管理序列化器"""
    department_name = serializers.CharField(source='department.dept_name', read_only=True)
    roles = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = HertzUser
        fields = [
            'user_id', 'username', 'email', 'phone', 'real_name', 'avatar',
            'gender', 'birthday', 'department_id', 'department_name', 'status',
            'last_login_time', 'last_login_ip', 'created_at', 'updated_at',
            'roles', 'password'
        ]
        read_only_fields = [
            'user_id', 'last_login_time', 'last_login_ip', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'required': False, 'allow_blank': True}
        }
    
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_roles(self, obj):
        """获取用户角色列表"""
        roles = obj.roles.filter(status=1)
        return [{
            'role_id': role.role_id,
            'role_name': role.role_name,
            'role_code': role.role_code
        } for role in roles]
    
    def validate_username(self, value):
        # 更新时排除当前用户
        queryset = HertzUser.objects.filter(username=value)
        if self.instance:
            queryset = queryset.exclude(user_id=self.instance.user_id)
        if queryset.exists():
            raise serializers.ValidationError('用户名已存在')
        return value
    
    def validate_email(self, value):
        if not EmailValidator.is_valid_email(value):
            raise serializers.ValidationError('邮箱格式不正确')
        # 更新时排除当前用户
        queryset = HertzUser.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(user_id=self.instance.user_id)
        if queryset.exists():
            raise serializers.ValidationError('邮箱已被使用')
        return value
    
    def validate_phone(self, value):
        if not PhoneValidator.is_valid_phone(value):
            raise serializers.ValidationError('手机号格式不正确')
        # 更新时排除当前用户
        queryset = HertzUser.objects.filter(phone=value)
        if self.instance:
            queryset = queryset.exclude(user_id=self.instance.user_id)
        if queryset.exists():
            raise serializers.ValidationError('手机号已被使用')
        return value
    
    def validate_password(self, value):
        # 如果密码为空或空字符串，则跳过验证
        if not value or value.strip() == '':
            return value
        # 只有当密码不为空时才进行强度验证
        is_valid, errors = PasswordValidator.validate_password_strength(value)
        if not is_valid:
            raise serializers.ValidationError('; '.join(errors))
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if password:
            validated_data['password'] = EncryptionUtils.md5_hash(password)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        # 只有当密码不为空且不是空字符串时才更新密码
        if password and password.strip():
            validated_data['password'] = EncryptionUtils.md5_hash(password)
        return super().update(instance, validated_data)


class UserRoleAssignSerializer(serializers.Serializer):
    """用户角色分配序列化器"""
    user_id = serializers.IntegerField(help_text="用户ID")
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="角色ID列表"
    )
    
    def validate_user_id(self, value):
        if not HertzUser.objects.filter(user_id=value, status=1).exists():
            raise serializers.ValidationError('用户不存在或已被禁用')
        return value
    
    def validate_role_ids(self, value):
        if not value:
            raise serializers.ValidationError('至少选择一个角色')
        
        existing_roles = HertzRole.objects.filter(role_id__in=value, status=1)
        if len(existing_roles) != len(value):
            raise serializers.ValidationError('部分角色不存在或已被禁用')
        return value


class RoleManagementSerializer(serializers.ModelSerializer):
    """角色管理序列化器"""
    menu_count = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HertzRole
        fields = [
            'role_id', 'role_name', 'role_code', 'description', 'status',
            'sort_order', 'created_at', 'updated_at', 'menu_count', 'user_count'
        ]
        read_only_fields = ['role_id', 'created_at', 'updated_at']
    
    @extend_schema_field(serializers.IntegerField())
    def get_menu_count(self, obj):
        """获取角色关联的菜单数量"""
        return obj.menus.filter(status=1).count()
    
    @extend_schema_field(serializers.IntegerField())
    def get_user_count(self, obj):
        """获取角色关联的用户数量"""
        from ..models import HertzUser
        return HertzUser.objects.filter(
            hertzuserrole__role=obj,
            status=1
        ).count()
    
    def validate_role_code(self, value):
        # 更新时排除当前角色
        queryset = HertzRole.objects.filter(role_code=value)
        if self.instance:
            queryset = queryset.exclude(role_id=self.instance.role_id)
        if queryset.exists():
            raise serializers.ValidationError('角色编码已存在')
        return value


class RoleMenuAssignSerializer(serializers.Serializer):
    """角色菜单分配序列化器"""
    role_id = serializers.IntegerField(help_text="角色ID")
    menu_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="菜单ID列表",
        allow_empty=True
    )
    
    def validate_role_id(self, value):
        if not HertzRole.objects.filter(role_id=value, status=1).exists():
            raise serializers.ValidationError('角色不存在或已被禁用')
        return value
    
    def validate_menu_ids(self, value):
        if value:
            existing_menus = HertzMenu.objects.filter(menu_id__in=value, status=1)
            if len(existing_menus) != len(value):
                raise serializers.ValidationError('部分菜单不存在或已被禁用')
        return value


class MenuManagementSerializer(serializers.ModelSerializer):
    """菜单管理序列化器"""
    parent_name = serializers.CharField(source='parent.menu_name', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = HertzMenu
        fields = [
            'menu_id', 'parent_id', 'parent_name', 'menu_name', 'menu_code',
            'menu_type', 'path', 'component', 'icon', 'permission', 'status',
            'sort_order', 'is_external', 'is_cache', 'is_visible',
            'created_at', 'updated_at', 'children'
        ]
        read_only_fields = ['menu_id', 'created_at', 'updated_at']
    
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_children(self, obj):
        """获取子菜单"""
        children = HertzMenu.objects.filter(parent_id=obj.menu_id, status=1).order_by('sort_order')
        return MenuManagementSerializer(children, many=True).data
    
    def validate_menu_code(self, value):
        # 更新时排除当前菜单
        queryset = HertzMenu.objects.filter(menu_code=value)
        if self.instance:
            queryset = queryset.exclude(menu_id=self.instance.menu_id)
        if queryset.exists():
            raise serializers.ValidationError('菜单编码已存在')
        return value
    
    def validate_parent_id(self, value):
        if value:
            # 检查父菜单是否存在
            if not HertzMenu.objects.filter(menu_id=value, status=1).exists():
                raise serializers.ValidationError('父菜单不存在或已被禁用')
            
            # 更新时检查是否会形成循环引用
            if self.instance and value == self.instance.menu_id:
                raise serializers.ValidationError('不能将自己设为父菜单')
        return value


class DepartmentManagementSerializer(serializers.ModelSerializer):
    """部门管理序列化器"""
    parent_name = serializers.SerializerMethodField(read_only=True)
    children = serializers.SerializerMethodField(read_only=True)
    user_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = HertzDepartment
        fields = [
            'dept_id', 'parent_id', 'parent_name', 'dept_name', 'dept_code',
            'leader', 'phone', 'email', 'status', 'sort_order',
            'created_at', 'updated_at', 'children', 'user_count'
        ]
        read_only_fields = ['dept_id', 'created_at', 'updated_at']
    
    @extend_schema_field(serializers.CharField())
    def get_parent_name(self, obj):
        """获取父部门名称"""
        if obj.parent_id:
            try:
                # 如果parent_id是HertzDepartment实例，直接返回其名称
                if isinstance(obj.parent_id, HertzDepartment):
                    return obj.parent_id.dept_name
                # 如果parent_id是数字，查询数据库
                parent = HertzDepartment.objects.get(dept_id=obj.parent_id)
                return parent.dept_name
            except HertzDepartment.DoesNotExist:
                return None
        return None
    
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_children(self, obj):
        """获取子部门"""
        # 确保使用dept_id进行查询
        dept_id = obj.dept_id if hasattr(obj, 'dept_id') else obj.pk
        children = HertzDepartment.objects.filter(parent_id=dept_id, status=1).order_by('sort_order')
        return DepartmentManagementSerializer(children, many=True).data
    
    @extend_schema_field(serializers.IntegerField())
    def get_user_count(self, obj):
        """获取部门用户数量"""
        from ..models import HertzUser
        return HertzUser.objects.filter(department_id=obj.dept_id, status=1).count()
    
    def validate_dept_code(self, value):
        # 更新时排除当前部门
        queryset = HertzDepartment.objects.filter(dept_code=value)
        if self.instance:
            queryset = queryset.exclude(dept_id=self.instance.dept_id)
        if queryset.exists():
            raise serializers.ValidationError('部门编码已存在')
        return value
    
    def validate_parent_id(self, value):
        if value:
            # 如果已经是 HertzDepartment 实例，直接返回
            if isinstance(value, HertzDepartment):
                return value
            
            # 将字符串或整数转换为整数
            if isinstance(value, str):
                try:
                    value = int(value)
                except ValueError:
                    raise serializers.ValidationError('父部门ID必须是数字')
            
            # 检查父部门是否存在并获取实例
            try:
                parent_dept = HertzDepartment.objects.get(dept_id=value, status=1)
            except HertzDepartment.DoesNotExist:
                raise serializers.ValidationError('父部门不存在或已被禁用')
            
            # 更新时检查是否会形成循环引用
            if self.instance and value == self.instance.dept_id:
                raise serializers.ValidationError('不能将自己设为父部门')
            
            # 直接返回整数ID，让Django自动处理外键关系
            return value
        return value
    
    def validate_email(self, value):
        if value and not EmailValidator.is_valid_email(value):
            raise serializers.ValidationError('邮箱格式不正确')
        return value
    
    def validate_phone(self, value):
        if value and not PhoneValidator.is_valid_phone(value):
            raise serializers.ValidationError('手机号格式不正确')
        return value
    
    def create(self, validated_data):
        """创建部门"""
        # parent_id 现在是整数ID，Django会自动处理外键关系
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """更新部门"""
        # parent_id 现在是整数ID，Django会自动处理外键关系
        return super().update(instance, validated_data)


class MenuTreeSerializer(serializers.ModelSerializer):
    """菜单树序列化器"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = HertzMenu
        fields = [
            'menu_id', 'menu_name', 'menu_code', 'menu_type', 'path',
            'component', 'icon', 'permission', 'sort_order', 'is_external',
            'is_cache', 'is_visible', 'children'
        ]
    
    def get_children(self, obj):
        """获取子菜单"""
        children = HertzMenu.objects.filter(parent_id=obj.menu_id, status=1).order_by('sort_order')
        return MenuTreeSerializer(children, many=True).data


class DepartmentTreeSerializer(serializers.ModelSerializer):
    """部门树序列化器"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = HertzDepartment
        fields = [
            'dept_id', 'dept_name', 'dept_code', 'leader',
            'phone', 'email', 'sort_order', 'children'
        ]
    
    def get_children(self, obj):
        """获取子部门"""
        children = HertzDepartment.objects.filter(parent_id=obj.dept_id, status=1).order_by('sort_order')
        return DepartmentTreeSerializer(children, many=True).data