# django-power-admin

Django提供了快捷的生成后台管理站点的能力。本应用旨在增强Django Admin的能力，提供丰富的Admin、Widget、ListFilter、Form等等界面扩展类，同时也为常用的数据管理模型提供完整的管理功能。

## 使用说明

1. 依赖`django-middleware-global-request`，请参考[django-middleware-global-request文档](https://pypi.org/project/django-middleware-global-request/)。
1. 依赖`django_static_fontawesome`，请参考[django_static_fontawesome文档](https://pypi.org/project/django-static-fontawesome/)。
1. 依赖`django_static_jquery_ui`，请参考[django_static_jquery_ui文档](https://pypi.org/project/django-static-jquery-ui/)。
1. 推荐使用`django-app-requires`解决包依赖问题，请参考[django-app-requires文档](https://pypi.org/project/django-app-requires/)。

## 功能扩展清单

### Admin后台管理界面整体控制

| 主要功能 |
| -------- |
| `@todo` 定制化的登录界面 |
| `@todo` 登录框增加图形验证码 |
| `@todo` 登录后增加短信验证 |
| `@todo` 顶部导航 |
| `@todo` 左侧导航 |
| `@todo` 首页控制面板 |
| `@todo` 应用模块级控制面板 |
| `@todo` 用户中心子站 |
| `@todo` 中国风的组织架构管理和用户管理 |

### PowerAdmin核心功能

| 类名 | 主要功能 |
| ---- | -------- |
| ChangelistToolbar机制 | 提供列表页顶部按钮自定义功能 |
| ChangelistObjectToolbar机制 | 提供列表页行按钮自定义功能 |
| Extra View机制 | 提供添加额外视图函数的功能 |
| View Hook机制 | 提供pre_xxx_view，post_xxx_view的Hook机制，<br />方便用户在进入视图前执行准备或清除工作 |
| Extra Context机制 | 为视图渲染注入额外的模板context机制。<br />`ChangelistToolbar机制`就是通过本机制注入额外的按钮列表数据的。 |
| Read & Change机制 | 设置只读、编辑两个不同的入口。这样现符合用户的操作习惯。 |
| Simple Export机制 | 数据导出机制，<br />默认即可导出所有表字段，<br />同时支持EXCEL模板配置、表头控制、字段配置等等。 |
| [排序记录上下移动机制](#django_power_admin.admin.PowerAdmin排序记录上下移动机制) | 每行记录上有上移&下移按钮，<br />通过点击上下移动按钮调整记录的排序。|
| [ListFilter Media机制](#django_power_admin.widgets.TextInputFieldFilter实现原理) | 允许自定义的ListFilter类，<br />通过添加`class Media:`来引入额外的js/css文件。 |

### Admin辅助函数
| 函数名 | 主要功能 |
| ---- | -------- |
| add_extra_css | 为当前页添加额外的css代码段 |
| add_extra_js | 为当前页添加额外的js代码段 |


### Widget扩展类

| 类名 | 主要功能 |
| ---- | -------- |
| [Select2](#django_power_admin.widgets.Select2) | 将标准select下拉框转为select2样式下拉框 |
| SelectMultiple2 | 将标准select复选框转为select2样式下拉式复选框 |
| [ConfigTable](#django_power_admin.widgets.ConfigTable) | 健值对配置项编辑控件<br />数据json序列化后保存在TextField中 |
| PopupConfigTable | 弹出式健值对配置项编辑控件<br />数据json序列化后保存在TextField中 |
| [AllUsersSelect](#django_power_admin.widgets.AllUsersSelect) | 用户选择控件，使用Select2实现<br />提供用户信息模糊搜索功能<br />不需要用户模块管理权限 |
| `@todo` PasswordResetableWidget | 密码重置字段（只重置，不显示）|

### Field扩展类

| 类名 | 主要功能 |
| ---- | -------- |
| MPTTModelChoiceField | MPTT数据模型中的Parent字段关联的表单字段，<br />使用Select2样式控件。<br />建议在MPTTAdminForm中使用 |
| ModelChoiceFieldWithLabelProperty | 标准ModelChoiceField的扩展，<br />支持使用自定义的标签函数 |

### Form扩展类

### ListFilter扩展类

| 类名 | 主要功能 |
| --- | ----- |
| [TextInputFieldFilter](#django_power_admin.filters.TextInputFieldFilter)  | 使用文本框的过滤条件。 |
| [DateRangeFilter](#django_power_admin.filters.DateRangeFilter)  | 日期区间过滤条件。 |


## 使用方法说明

### django_power_admin的引入

*pro/settings.py*

```
INSTALLED_APPS = [
    ...
    'django_middleware_global_request',
    'django_static_fontawesome',
    'django_static_jquery_ui',
    'django_simple_tags',
    'django_power_admin',
    ...
]

MIDDLEWARE = [
    ...
    'django_middleware_global_request.middleware.GlobalRequestMiddleware',
    ...
]

```

### <a name="django_power_admin.admin.PowerAdmin排序记录上下移动机制"></a>django_power_admin.admin.PowerAdmin排序记录上下移动机制

#### django_power_admin.admin.PowerAdmin排序记录上下移动机制效果图

![django_power_admin.admin.PowerAdmin排序支持效果预览图](https://github.com/zencore-dobetter/pypi-images/raw/main/django-power-admin/admin/django_power_admin_admin_sorting_preview.png)


#### django_power_admin.admin.PowerAdmin排序记录上下移动机制使用方法

*models.py*

```
class SortableAdminExmapleModel(models.Model):
    title = models.CharField(max_length=64, verbose_name="Title")
    display_order = models.IntegerField(null=True, blank=True, verbose_name="Display Order")

    class Meta:
        verbose_name = "排序演示"
        verbose_name_plural = "排序演示"
    
    def __str__(self):
        return str(self.pk)

```

*admin.py*

```
from django.contrib import admin

from django_power_admin.admin import PowerAdmin

from .models import SortableAdminExmapleModel


class SortableAdminExmapleModelAdmin(PowerAdmin):
    list_display = ["title"]
    ordering = ["display_order"]
    changelist_object_toolbar_buttons = [
        "django_power_admin_move_up",
        "django_power_admin_move_down",
        "read_button",
        "change_button",
        "delete_button",
    ]

admin.site.register(SortableAdminExmapleModel, SortableAdminExmapleModelAdmin)

```

### <a name="django_power_admin.widgets.Select2"></a>django_power_admin.widgets.Select2

#### django_power_admin.widgets.Select2效果预览图

![django_power_admin.widgets.Select2效果预览图](https://github.com/zencore-dobetter/pypi-images/raw/main/django-power-admin/widgets/Select2/django_power_admin_widgets_select2_preview.png)

#### django_power_admin.widgets.Select2使用方法

*models.py*

```
from django.db import models

class Select2ExampleCategory(models.Model):
    name = models.CharField(max_length=64, verbose_name="Name")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Select2ExampleModel(models.Model):
    title = models.CharField(max_length=64, verbose_name="Title")
    category = models.ForeignKey(Select2ExampleCategory, on_delete=models.CASCADE, verbose_name="Category")

    class Meta:
        verbose_name = "可搜索下拉框演示"
        verbose_name_plural = "可搜索下拉框演示"

    def __str__(self):
        return self.title

```

*admin.py*

```
from django import forms
from django.contrib import admin

from django_power_admin.widgets import Select2

from .models import Select2ExampleCategory
from .models import Select2ExampleModel


class Select2ExampleCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]

class Select2ExampleModelForm(forms.ModelForm):
    class Meta:
        widgets = {
            "category": Select2(),
        }

class Select2ExampleModelAdmin(admin.ModelAdmin):
    form = Select2ExampleModelForm
    list_display = ["title"]

admin.site.register(Select2ExampleCategory, Select2ExampleCategoryAdmin)
admin.site.register(Select2ExampleModel, Select2ExampleModelAdmin)

```


### <a name="django_power_admin.widgets.ConfigTable"></a>django_power_admin.widgets.ConfigTable

#### django_power_admin.widgets.ConfigTable效果预览图

![django_power_admin.widgets.ConfigTable效果预览图](https://github.com/zencore-dobetter/pypi-images/raw/main/django-power-admin/widgets/ConfigTable/django_power_admin_widgets_config_table_preview.png)

#### django_power_admin.widgets.ConfigTable使用方法

*models.py*

```
from django.db import models

class ConfigTableExampleModel(models.Model):
    config = models.TextField(null=True, blank=True, verbose_name="配置")
    
    class Meta:
        verbose_name = "配置表控件演示"
        verbose_name_plural = "配置表控件演示"

    def __str__(self):
        return str(self.pk)
```

*admin.py*

```
from django import forms
from django.contrib import admin

from django_power_admin.widgets import ConfigTable

class ConfigTableExampleModelForm(forms.ModelForm):
    class Meta:
        widgets = {
            "config": ConfigTable(),
        }

class ConfigTableExampleModelAdmin(admin.ModelAdmin):
    form = ConfigTableExampleModelForm

admin.site.register(ConfigTableExampleModel, ConfigTableExampleModelAdmin)
```

### <a name="django_power_admin.widgets.AllUsersSelect"></a>django_power_admin.widgets.AllUsersSelect

#### django_power_admin.widgets.AllUsersSelect预览效果

![django_power_admin.widgets.AllUsersSelect效果预览图](https://github.com/zencore-dobetter/pypi-images/raw/main/django-power-admin/widgets/AllUsersSelect/AllUsersSelect.png)


#### django_power_admin.widgets.AllUsersSelect使用方法

*models.py*

```
from django.db import models

class Project(models.Model):
    
    owner = models.ForeignKey(global_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+", verbose_name=_("Owner"))

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return str(self.pk)
```

*admin.py*

```
from django import forms
from django.contrib import admin
from django_power_admin.widgets import AllUsersSelect
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        widgets = {
            "owner": AllUsersSelect(),
        }

class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm

admin.site.register(Project, ProjectAdmin)
```

### <a name="django_power_admin.filters.TextInputFieldFilter"></a>django_power_admin.widgets.TextInputFieldFilter

#### django_power_admin.filters.TextInputFieldFilter预览效果

![django_power_admin.filters.TextInputFieldFilter预览效果](https://github.com/zencore-dobetter/pypi-images/raw/main/django-power-admin/filters/TextInputFieldFilter/TextInputFieldFilter.png)


#### django_power_admin.filters.TextInputFieldFilter使用方法

```
from django.contrib import admin
from django_power_admin.filters import TextInputFieldFilter

class ExampleAdmin(admin.ModelAdmin):
    list_filter = [
        ("title", TextInputFieldFilter),
        "description",
        "enable",
    ]
    list_display = ["title", "description", "enable"]
```

#### <a name="django_power_admin.filters.TextInputFieldFilter实现原理"></a>django_power_admin.filters.TextInputFieldFilter实现原理

使用了django_power_admin引入的ListFilter Media机制，
通过在类内部定义`class Media`，
导入ListFilter需要使用到的js/css文件，
导入的js文件，可以按django标准media文件引入机制进行自动化的去重和依赖排序。


```
from django.contrib.admin import FieldListFilter

class TextInputFieldFilter(FieldListFilter):
    template = 'django_power_admin/filters/TextInputFieldFilter.html'

    ...

    class Media:
        css = {
            "all": [
                "django_power_admin/filters/TextInputFieldFilter/css/TextInputFieldFilter.css",
            ]
        }
        js = [
            "django_power_admin/assets/js/parseParam.js",
            "admin/js/vendor/jquery/jquery.js",
            "django_power_admin/filters/TextInputFieldFilter/js/TextInputFieldFilter.js",
            "admin/js/jquery.init.js",
        ]

```

### <a name="django_power_admin.filters.DateRangeFilter"></a>django_power_admin.filters.DateRangeFilter

#### django_power_admin.filters.DateRangeFilter效果预览

![django_power_admin.filters.DateRangeFilter](https://github.com/zencore-dobetter/pypi-images/raw/main/django-power-admin/filters/DateRangeFilter/DateRangeFilter.png)


#### django_power_admin.filters.DateRangeFilter使用方式

```
from django.contrib import admin
from django_power_admin.filters import DateRangeFilter

class ExampleAdmin(admin.ModelAdmin):
    list_filter = [
        "username",
        ("date_join", DateRangeFilter),
        "is_active",
    ]
    list_display = ["username", "date_join", "is_active"]
```

### Admin样式类

- inline-narror-input

    TabularInline字符串输入框改为小框。

    *使用范围：*

    - 可加在TabularInline类的claases属性中。

- related-actions-hidden

    隐藏外键的增改删按钮。

    *使用范围：*

    - 可加在fieldsets的classes属性中。
    - 可以加在TabularInline类的claases属性中。

- inline-original-hidden

    隐藏TabularInline及StackInline中的orininal显示。

    *使用范围：*

    - 可加在TabularInline类的claases属性中。
    - 可加在StackInline类的claases属性中。

- form-row-c2

    FormChange表单两例显示，同时控制textarea的宽度。

    *使用范围：*

    - 可加在fieldsets的classes属性中。

### Admin全局控制

- DJANGO_ADMIN_USE_FIXED_WIDTH_LAYOUT

    当DJANGO_ADMIN_USE_FIXED_WIDTH_LAYOUT=True，Admin管理后台设置为固定宽度，且居中显示。可通过以下设置控制宽度及背景色。

    *关联设置项：*

    - DJANGO_ADMIN_USE_FIXED_WIDTH_LAYOUT = False
    - DJANGO_ADMIN_WIDTH = 1280px
    - DJANGO_ADMIN_BACKGROUND_COLOR = "#f5f6f8"
    - DJANGO_ADMIN_FOOTER_COLOR = "#c5cbd2"


## 版本记录

### v0.1.7

- 项目启动。
- 框架搭建。
- PowerAdmin类基本完成。

### v0.1.10

- get_extra_views更名为get_extra_view_urls，避免与其它方法名冲突。
- view_action更名为read_xxx。xxx_action更名为xxx_button。
- 在list_display中追加change_list_object_toolbar字段。

### v0.1.12

- 增加has_change_permission_real, has_delete_permission_real方法，解决read/change机制导致的原始权限判断丢失的情况。
- 增加get_messages方法， 用于获取站点当前的messages队列。
- 增加get_power_admin_class，用于统一扩展所有PowerAdmin的子类。

### v0.1.18

- 修正get_changelist_object_row_classes_javascript方法在遇到其它错误时导致的异常行为。
- ChangelistObjectToolbarButton可以直接引用extra view（需要为extra view添加按钮额外属性，如：short_description、icon、classes等）。
- change_list_xxx更名为changelist_xxx（注意：可能引起新旧版本的不兼容，特别是子类配置的change_list_toolbar_buttons属性需要改名为changelist_toolbar_buttons）。
- 引入ChangelistToolbar机制，用于添加额外的列表页顶部按钮。

### v0.1.20

- 添加简易数据分享机制的支持（simple share model）。
- 添加数据导出功能。

### v0.1.21

- 添加适用于TextField使用的“键值对”控件。
- PowerAdmin中方法名加上django_power_admin_前缀，避免与其它扩展类冲突。

### v0.1.23

- 修正Select2、SelectMultiple2、ConfigTable在inline表单中的使用问题。
- 新增django_power_admin.widgets.AllUsersSelect。

### v0.1.24

- 新增django_power_admin.filters.TextInputFieldFilter。
- 新增list_filter类通过定义内部的`Media:`引入额外的js/css文件的机制。

### v0.1.25

- 新增django_power_admin.filters.DateRangeFilter。

### v0.1.27

- 修正ChangelistObjectToolbar按钮换行的问题。

### v0.1.29

- 兼容django 4.x。
- 兼容python 2.7。
- 修正排序Admin未设置ordering时的异常。

### v0.1.30

- 修正get_ordering强制添加display_order字段导致的问题。

### v0.1.31

- 修正ChangelistObjectToolBarButton的默认target=self问题，修正后的默认target=_self。
- 使用zenutils依赖包以简化不必要的依赖关系。

### v0.1.35

- 修正DateRangeFilter结束日期框搜索条件名称错误的问题。

### v0.1.36

- 增加站点固定宽度居中。
- 增加Admin样式类：form-row-c2、inline-original-hidden、related-actions-hidden、inline-narror-input。
- 增加PopupConfigTable控件。

### v0.1.37

- 文档更新。
