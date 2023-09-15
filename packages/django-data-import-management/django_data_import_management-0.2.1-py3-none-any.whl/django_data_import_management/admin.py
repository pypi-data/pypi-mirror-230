from django import forms
from django.contrib import admin, messages
from django.urls import reverse
from django.urls import path
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django_changelist_toolbar_admin.admin import DjangoChangelistToolbarAdmin
from django_object_toolbar_admin.admin import DjangoObjectToolbarAdmin

from .models import (
    DJANGO_DATA_IMPORT_WORKFLOWS,
    DjangoDataImportCase,
    DjangoDataImportItem,
    get_django_data_import_workflow_choices,
)


def django_data_import_do_parse(modeladmin, request, queryset):
    for case in queryset.all():
        try:
            case.do_parse()
            modeladmin.message_user(
                request,
                _("Parse data file of case {case} success.").format(case=case.title),
                messages.SUCCESS,
            )
        except Exception as error:
            modeladmin.message_user(
                request,
                _("Parse data file of case {case} failed: {message}").format(
                    case=case.title, message=str(error)
                ),
                messages.ERROR,
            )


django_data_import_do_parse.short_description = _("Parse selected data files.")


def django_data_import_do_import(modeladmin, request, queryset):
    for case in queryset.all():
        try:
            items = case.do_import()
            ok = 0
            failed = 0
            for item in items:
                if item.success:
                    ok += 1
                else:
                    failed += 1
            modeladmin.message_user(
                request,
                _(
                    "Import data file of case {case} done, {ok} items success, {failed} items failed."
                ).format(case=case.title, ok=ok, failed=failed),
                messages.SUCCESS,
            )
        except Exception as error:
            modeladmin.message_user(
                request,
                _("Import data file of case {case} failed: {message}").format(
                    case=case.title, message=str(error)
                ),
                messages.ERROR,
            )


django_data_import_do_import.short_description = _("Import selected data files.")


def django_data_import_do_item_import(modeladmin, request, queryset):
    success_count = 0
    failed_count = 0
    for item in queryset.prefetch_related("case").all():
        try:
            success = item.do_import()
            if success:
                success_count += 1
            else:
                failed_count += 1
        except Exception as error:
            modeladmin.message_user(
                request,
                _("Import item {item} failed: {message}").format(
                    item=item.pk, messages=str(error)
                ),
                messages.ERROR,
            )
            failed_count += 1

    if success_count:
        modeladmin.message_user(
            request,
            _("{success} items successfully imported.").format(success=success_count),
            messages.SUCCESS,
        )
    if failed_count:
        modeladmin.message_user(
            request,
            _("{failed} items import failed.").format(failed=failed_count),
            messages.ERROR,
        )


django_data_import_do_item_import.short_description = _("Import selected items.")


class DjangoDataImportCaseForm(forms.ModelForm):
    """导入案例表单。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["import_workflow"] = forms.ChoiceField(
            choices=get_django_data_import_workflow_choices(),
            label=_("Import Workflow"),
        )

    class Meta:
        model = DjangoDataImportCase
        fields = "__all__"


class DjangoDataImportCaseAdmin(DjangoObjectToolbarAdmin, admin.ModelAdmin):
    """导入案例管理。"""

    form = DjangoDataImportCaseForm
    list_display = [
        "title",
        "import_workflow_display",
        "parse_result",
        "import_result",
        "django_object_toolbar",
    ]
    list_filter = ["import_workflow"]
    fieldsets = [
        (
            _("Import Settings"),
            {
                "fields": ["import_workflow", "datafile", "title"],
                "classes": ["django-data-import-case-admin-import-settings"],
            },
        ),
        (
            _("Parse Resslt"),
            {
                "fields": ["parse_result", "parse_time", "parse_error"],
                "classes": ["django-data-import-case-admin-parse-result"],
            },
        ),
        (
            _("Import Result"),
            {
                "fields": ["import_result", "import_time", "import_error"],
                "classes": ["django-data-import-case-admin-import-result"],
            },
        ),
    ]
    readonly_fields = [
        "parse_result",
        "parse_time",
        "parse_error",
        "import_result",
        "import_time",
        "import_error",
    ]
    actions = [
        django_data_import_do_parse,
        django_data_import_do_import,
    ]

    class Media:
        css = {
            "all": [
                "jquery-ui/jquery-ui.min.css",
            ]
        }
        js = [
            "admin/js/vendor/jquery/jquery.js",
            "jquery-ui/jquery-ui.min.js",
            "django_data_import_management/js/django_data_import_management.js",
            "admin/js/jquery.init.js",
        ]

    def get_urls(self):
        return [
            path(
                "django_data_import_management_case_do_parse",
                self.admin_site.admin_view(self.do_parse_view),
                name="django_data_import_management_case_do_parse",
            ),
            path(
                "django_data_import_management_case_do_import",
                self.admin_site.admin_view(self.do_import_view),
                name="django_data_import_management_case_do_import",
            ),
        ] + super().get_urls()

    def do_parse_view(self, request):
        """案例解析请求。"""
        case_id = int(request.GET.get("case_id"))
        case = DjangoDataImportCase.objects.get(id=case_id)
        case.do_parse()
        return JsonResponse(
            {
                "code": 0,
                "message": _("Parse Done!"),
                "result": True,
            },
            json_dumps_params={
                "ensure_ascii": False,
            },
        )

    def do_import_view(self, request):
        """案例导入请求。"""
        case_id = int(request.GET.get("case_id"))
        case = DjangoDataImportCase.objects.get(id=case_id)
        case.do_import()
        return JsonResponse(
            {
                "code": 0,
                "message": _("Import Done!"),
                "result": True,
            },
            json_dumps_params={
                "ensure_ascii": False,
            },
        )

    def do_parse_button(self, obj):
        """案例解析按钮。"""
        return (
            reverse("admin:django_data_import_management_case_do_parse")
            + "?case_id="
            + str(obj.pk)
        )

    do_parse_button.icon = "fas fa-book"
    do_parse_button.title = _("Parse Case")
    do_parse_button.klass = "django_data_import_management_do_parse_button"

    def do_import_button(self, obj):
        """案例导入按钮。"""
        return (
            reverse("admin:django_data_import_management_case_do_import")
            + "?case_id="
            + str(obj.pk)
        )

    do_import_button.icon = "fas fa-upload"
    do_import_button.title = _("Import Case")
    do_import_button.klass = "django_data_import_management_do_import_button"

    def show_items_button(self, obj):
        """显示导入案例的条目列表。"""
        return (
            reverse(
                "admin:django_data_import_management_djangodataimportitem_changelist"
            )
            + "?case__id__exact="
            + str(obj.pk)
        )

    show_items_button.icon = "fas fa-list"
    show_items_button.title = _("Show Items")

    def import_workflow_display(self, obj):
        info = DJANGO_DATA_IMPORT_WORKFLOWS.get(obj.import_workflow, None)
        if info:
            return info["name"]
        else:
            return "-"

    import_workflow_display.short_description = _("Import Workflow")
    import_workflow_display.admin_order_field = "import_workflow"

    django_object_toolbar_buttons = [
        "do_parse_button",
        "do_import_button",
        "show_items_button",
    ]


class DjangoDataImportItemAdmin(DjangoChangelistToolbarAdmin, admin.ModelAdmin):
    list_display = ["id", "success", "info", "import_success", "case"]
    list_filter = ["case", "success", "import_success"]
    search_fields = ["info", "json_data"]
    actions = [
        django_data_import_do_item_import,
    ]
    readonly_fields = [
        "case",
        "success",
        "info",
        "add_time",
        "json_data",
        "import_success",
        "import_time",
        "import_error",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("case")

    django_changelist_toolbar_buttons = [
        "show_cases",
    ]

    def show_cases(self, request):
        return reverse(
            "admin:django_data_import_management_djangodataimportcase_changelist"
        )

    show_cases.icon = "fa fa-list"
    show_cases.title = _("Goto Case Changelist")


admin.site.register(DjangoDataImportCase, DjangoDataImportCaseAdmin)
admin.site.register(DjangoDataImportItem, DjangoDataImportItemAdmin)
