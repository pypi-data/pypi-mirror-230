import json
import base64
import zlib
import binascii
import logging

from zenutils import strutils
from zenutils import fsutils
from zenutils import dictutils
from xlsxhelper import load_data_from_workbook


from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from django_safe_fields.fields import SafeCharField
from django_safe_fields.fields import SafeTextField

from .settings import DJANGO_DATA_IMPORT_MANAGEMENT_DATA_FILE_UPLOAD_TO
from .settings import SAFE_FIELD_PASSWORDS

DJANGO_DATA_IMPORT_WORKFLOWS = {}


logger = logging.getLogger(__name__)


class ParsedItem(object):
    """导入数据解析后的条目。"""

    def __init__(self, success=None, info=None, data=None):
        self.success = success
        self.info = info
        self.data = data

    def mark_success(self, info, data):
        """标记本条目解析正确。"""
        self.success = True
        self.info = info
        self.data = data

    def mark_failed(self, error_message, error_data=None):
        """标记本条目解析失败。"""
        self.success = False
        self.info = error_message
        self.data = error_data


class DjangoDataImportWorkflow(object):
    """数据导入流程。"""

    def __init__(self, datafile_field):
        if isinstance(datafile_field, str):
            self.datafile_field = None
            self.datafile = datafile_field
        else:
            self.datafile_field = datafile_field
            try:
                self.datafile = datafile_field.path
            except:  # pylint: disable=bare-except
                self.datafile = None

    def do_parse(self):
        """返回所有解析条目。"""
        raise NotImplementedError()

    def do_import(self, imported_items):
        """导入所有解析成功的条目。返回导入成功的条目列表。"""
        raise NotImplementedError()

    @classmethod
    def get_code(cls):
        """返回模块编码。"""
        return ".".join([cls.__module__, cls.__name__])


def json_decode(value, field_name, field_settings, **kwargs):
    """对数据进行json解析。"""
    # pylint: disable=unused-argument
    return json.loads(value)


def compressed_json_decode(value, field_name, field_settings, **kwargs):
    """对经过zlib压缩以及b64safe编码的json数据进行解析。"""
    # pylint: disable=unused-argument
    value = strutils.force_bytes(value)
    value_compressed = base64.urlsafe_b64decode(value)
    json_text = zlib.decompress(value_compressed)
    return json.loads(json_text)


def hexlified_compressed_json_decode(value, field_name, field_settings, **kwargs):
    """对经过zlib压缩以及hexlify编码的json数据进行解析。"""
    value_compressed = binascii.unhexlify(value)
    json_text = zlib.decompress(value_compressed)
    return json.loads(json_text)


def base64encoded_compressed_json_decode(value, field_name, field_settings, **kwargs):
    """对经过zlib压缩以及base64编码的json数据进行解析。"""
    value = strutils.force_bytes(value)
    value_compressed = base64.decodebytes(value)
    json_text = zlib.decompress(value_compressed)
    return json.loads(json_text)


class DjangoSimpleExportedDataImportWorkflow(DjangoDataImportWorkflow):
    """数据导入工作流定义。

    field_cols example:
        field_cols = {
            "id": 1,                        # simple one cell field value
            "users_list": [2,3,4,5],        # complex multiple cells field value
        }
    foreignkey_settings example:
        foreignkey_settings = {
            "server": {
                "keyfield": "uid",
                "model": Server,
            }
        }
    manytomanyfield_settings example:
        manytomanyfield_settings = {
            "users": {
                "keyfield": "username",
                "model": User,
                "separator": ",",
            },
            "groups": {
                "keyfield": "uid",
                "model": Group,
                "decode": json_decode,
            }
        }
    """

    model = None
    start_row = 2
    copy_datafile = True
    keyfield = "id"
    field_cols = {}
    foreignkey_settings = {}
    manytomanyfield_settings = {}

    def get_keyfield_value(self, row):
        if isinstance(row, (list, tuple)):
            field_col = self.field_cols[self.keyfield]
            value = row[field_col]
        elif isinstance(row, dict):
            value = row[self.keyfield]
        else:
            value = getattr(row, self.keyfield)
        if not isinstance(value, (str, int)):
            value = str(value)
        return value

    def get_data(self, row):
        data = {}
        for field_name, field_col in self.field_cols.items():
            if isinstance(field_col, (list, tuple)):
                data[field_name] = ""
                for col in field_col:
                    data[field_name] += row[col]
            elif isinstance(field_col, set):
                field_col = sorted(list(field_col))
                for col in field_col:
                    data[field_name] += row[col]
            else:
                data[field_name] = row[field_col]
        return data

    def get_compare_field_names(self):
        field_names = list(self.field_cols)
        if self.keyfield in field_names:
            field_names.remove(self.keyfield)
        for field_name in self.manytomanyfield_settings.keys():
            if field_name in field_names:
                field_names.remove(field_name)
        return field_names

    def get_manytomanyfield_values(self, value, field_name, field_settings):
        if not value:
            return []

        decode = field_settings.get("decode", None)
        if decode:
            return decode(value, field_name, field_settings)
        else:
            sep = field_settings.get("separator", ",")
            value = str(value)
            return value.split(sep)

    def check_foreignkey_change(self, obj, data, field_name, field_settings):
        data_key_value = str(data[field_name])
        related_object = getattr(obj, field_name)
        if related_object:
            related_keyfield = field_settings["keyfield"]
            obj_key_value = getattr(related_object, related_keyfield)
        else:
            obj_key_value = None
        result = data_key_value != obj_key_value
        return result

    def check_manytomanyfield_change(self, obj, data, field_name, field_settings):
        related_keyfield = field_settings["keyfield"]
        data_m2m_keys = sorted(
            self.get_manytomanyfield_values(
                data[field_name], field_name, field_settings
            )
        )
        obj_m2m_keys = sorted(
            [str(getattr(x, related_keyfield)) for x in getattr(obj, field_name).all()]
        )
        return data_m2m_keys != obj_m2m_keys

    def get_queryset(self):
        related_fields = list(self.manytomanyfield_settings.keys())
        queryset = self.model.objects
        if related_fields:
            queryset = queryset.prefetch_related(*related_fields)
        return queryset

    def update_manytomanyfield(self, obj, data, field_name, field_settings):
        model = field_settings["model"]
        related_keyfield = field_settings["keyfield"]

        related_obj_mapping = {}
        for related_obj in model.objects.all():
            keyword = getattr(related_obj, related_keyfield)
            related_obj_mapping[keyword] = related_obj

        data_relates = {}
        for keyword in self.get_manytomanyfield_values(
            data[field_name], field_name, field_settings
        ):
            data_relates[keyword] = related_obj_mapping[keyword]

        obj_relates = {}
        for related_obj in getattr(obj, field_name).all():
            keyword = getattr(related_obj, related_keyfield)
            obj_relates[keyword] = related_obj

        created_keys, _, deleted_keys = dictutils.diff(obj_relates, data_relates)

        if created_keys:
            getattr(obj, field_name).add(
                *[related_obj_mapping[x] for x in created_keys]
            )

        if deleted_keys:
            getattr(obj, field_name).remove(
                *[related_obj_mapping[x] for x in deleted_keys]
            )

        if created_keys or deleted_keys:
            return True
        else:
            return False

    def update_foreignkey(self, obj, data, field_name, field_settings):
        pass

    def do_parse(self):
        load_rows = f"{self.start_row}-"
        try:
            if self.copy_datafile or (self.datafile is None):
                temp_datafile = fsutils.TemporaryFile(
                    content=self.datafile_field.read(), filename_suffix=".xlsx"
                )
                rows = load_data_from_workbook(temp_datafile.filepath, rows=load_rows)
            else:
                rows = load_data_from_workbook(self.datafile, rows=load_rows)
        except Exception as error:
            raise RuntimeError(
                _("Load data from excel file failed: {message}").format(
                    message=str(error)
                )
            ) from error

        obj_mapping = {}
        for obj in self.get_queryset().all():
            keyword = self.get_keyfield_value(obj)
            obj_mapping[keyword] = obj

        compare_field_names = self.get_compare_field_names()
        items = []
        for row in rows:
            item = ParsedItem()
            try:
                keyword = self.get_keyfield_value(row)
                data = self.get_data(row)
                if keyword in obj_mapping:
                    obj = obj_mapping[keyword]
                    changed, changed_fields = dictutils.changes(
                        obj,
                        data,
                        keys=compare_field_names,
                        return_changed_keys=True,
                        do_update=False,
                        ignore_empty_value=True,
                    )

                    for field_name, field_settings in self.foreignkey_settings.items():
                        foreignkey_changed = self.check_foreignkey_change(
                            obj, data, field_name, field_settings
                        )
                        if foreignkey_changed:
                            changed = True
                            changed_fields.append(field_name)

                    for (
                        field_name,
                        field_settings,
                    ) in self.manytomanyfield_settings.items():
                        manytomanyfield_changed = self.check_manytomanyfield_change(
                            obj, data, field_name, field_settings
                        )
                        if manytomanyfield_changed:
                            changed = True
                            changed_fields.append(field_name)

                    if changed:
                        info = _(
                            "Parse line of {verbose_name} success, keyword={keyword},  changed_fields={changed_fields}".format(
                                verbose_name=self.model._meta.verbose_name,
                                keyword=keyword,
                                changed_fields=changed_fields,
                            )
                        )
                    else:
                        info = _(
                            "Parse line of {verbose_name} success without any change, keyword={keyword}".format(
                                verbose_name=self.model._meta.verbose_name,
                                keyword=keyword,
                            )
                        )
                    item.mark_success(info, data)
                    items.append(item)
                    continue
                else:
                    info = _(
                        "Parse line of {verbose_name} success, create a new object with keyword={keyword}".format(
                            verbose_name=self.model._meta.verbose_name, keyword=keyword
                        )
                    )
                    item.mark_success(info, data)
                    items.append(item)
                    continue
            except Exception as error:
                info = _(
                    "Parse line of {verbose_name} failed: error_message={error_message}".format(
                        verbose_name=self.model._meta.verbose_name,
                        error_message=str(error),
                    )
                )
                logger.exception(info)
                item.mark_failed(info, row)
                items.append(item)
                continue
        return items

    def do_import(self, imported_items):
        obj_mapping = {}
        for obj in self.get_queryset().all():
            obj_mapping[self.get_keyfield_value(obj)] = obj

        compare_field_names = self.get_compare_field_names()
        for item in imported_items:
            try:
                keyword = self.get_keyfield_value(item.data)

                if keyword in obj_mapping:
                    obj = obj_mapping[keyword]
                    create_flag = False
                else:
                    obj = self.model()
                    setattr(obj, self.keyfield, keyword)
                    create_flag = True

                changed, changed_fields = dictutils.changes(
                    obj,
                    item.data,
                    keys=compare_field_names,
                    return_changed_keys=True,
                    do_update=True,
                    ignore_empty_value=True,
                )

                if changed or create_flag:
                    obj.save()

                for field_name, field_settings in self.manytomanyfield_settings.items():
                    manytomanyfield_changed = self.update_manytomanyfield(
                        obj, item.data, field_name, field_settings
                    )
                    if manytomanyfield_changed:
                        changed = True
                        changed_fields.append(field_name)

                if changed:
                    info = _(
                        "Import {verbose_name} item success, keyword={keyword}, changed_fields={changed_fields}".format(
                            verbose_name=self.model._meta.verbose_name,
                            keyword=keyword,
                            changed_fields=changed_fields,
                        )
                    )
                else:
                    info = _(
                        "Import {verbose_name} item success without any change, keyword={keyword}".format(
                            verbose_name=self.model._meta.verbose_name, keyword=keyword
                        )
                    )
                item.mark_success(info)
                continue
            except Exception as error:
                info = _(
                    "import {verbose_name} item failed, error_message={error_message}"
                ).format(
                    verbose_name=self.model._meta.verbose_name, error_message=str(error)
                )
                logger.exception(info)
                item.mark_failed(info)
                continue

        return imported_items


def register_django_data_import_workflow(name, workflow_class):
    """注册导入工作流。"""
    code = workflow_class.get_code()
    DJANGO_DATA_IMPORT_WORKFLOWS[code] = {
        "code": code,
        "name": name,
        "workflow_class": workflow_class,
    }


def get_django_data_import_workflow_choices():
    """生成导入工作流选项列表。"""
    choices = [
        (None, "-" * 40),
    ]
    for _, info in DJANGO_DATA_IMPORT_WORKFLOWS.items():
        choices.append((info["code"], info["name"]))
    return choices


class DjangoDataImportCase(models.Model):
    """数据导入工作实例数据模型。"""

    SUCCESS = 10
    FAILED = 20
    PARTLY_FAILED = 30

    RESULT_CHOICES = [
        (SUCCESS, _("Success")),
        (FAILED, _("Failed")),
        (PARTLY_FAILED, _("Partly Failed")),
    ]

    import_workflow = SafeCharField(
        max_length=512,
        verbose_name=_("Import Workflow"),
        password=SAFE_FIELD_PASSWORDS[
            "django_data_import_management.DjangoDataImportCase.import_workflow"
        ],
    )
    datafile = models.FileField(
        upload_to=DJANGO_DATA_IMPORT_MANAGEMENT_DATA_FILE_UPLOAD_TO,
        verbose_name=_("Data File"),
    )
    title = SafeCharField(
        max_length=512,
        null=True,
        blank=True,
        verbose_name=_("Title"),
        password=SAFE_FIELD_PASSWORDS[
            "django_data_import_management.DjangoDataImportCase.title"
        ],
    )
    add_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Add Time"))
    mod_time = models.DateTimeField(auto_now=True, verbose_name=_("Modify Time"))

    parse_result = models.IntegerField(
        choices=RESULT_CHOICES, null=True, blank=True, verbose_name=_("Parse Result")
    )
    parse_time = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Parse Time")
    )
    parse_error = SafeTextField(
        null=True,
        blank=True,
        verbose_name=_("Parse Error"),
        password=SAFE_FIELD_PASSWORDS[
            "django_data_import_management.DjangoDataImportCase.parse_error"
        ],
    )

    import_result = models.IntegerField(
        choices=RESULT_CHOICES, null=True, blank=True, verbose_name=_("Import Result")
    )
    import_time = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Import Time")
    )
    import_error = SafeTextField(
        null=True,
        blank=True,
        verbose_name=_("Import Error"),
        password=SAFE_FIELD_PASSWORDS[
            "django_data_import_management.DjangoDataImportCase.import_error"
        ],
    )

    class Meta:
        ordering = ["-pk"]
        verbose_name = _("Django Data Import Case")
        verbose_name_plural = _("Django Data Import Cases")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.title is None:
            nowtime = timezone.now().strftime("%Y%m%d-%H%M%S")
            workflow_name = DJANGO_DATA_IMPORT_WORKFLOWS.get(
                self.import_workflow, {}
            ).get("name", "-")
            self.title = f"{workflow_name}-{nowtime}"
        return super().save(*args, **kwargs)

    def get_workflow_class(self):
        info = DJANGO_DATA_IMPORT_WORKFLOWS.get(self.import_workflow, None)
        if info:
            return info["workflow_class"]
        else:
            return None

    def get_workflow(self):
        workflow_class = self.get_workflow_class()
        if not workflow_class:
            raise RuntimeError(_("Unknown import workflow!"))
        workflow = workflow_class(self.datafile)
        return workflow

    def do_parse(self):
        try:
            workflow = self.get_workflow()
            rows = workflow.do_parse()
            DjangoDataImportItem.objects.filter(case=self).delete()
            items = []
            success_count = 0
            failed_count = 0
            for row in rows:
                item = DjangoDataImportItem()
                item.case = self
                item.success = row.success
                item.info = row.info
                item.data = row.data
                items.append(item)
                if row.success:
                    success_count += 1
                else:
                    failed_count += 1
            DjangoDataImportItem.objects.bulk_create(items, batch_size=200)
            if success_count and failed_count:
                self.parse_result = self.PARTLY_FAILED
            elif failed_count:
                self.parse_result = self.FAILED
            else:
                self.parse_result = self.SUCCESS
            self.parse_time = timezone.now()
            self.parse_error = None
            self.save()
        except Exception as error:
            self.parse_result = self.FAILED
            self.parse_time = timezone.now()
            self.parse_error = str(error)
            self.save()
        return True

    def do_import(self, items=None):
        workflow = self.get_workflow()
        import_items = items or list(self.items.filter(success=True).all())
        try:
            workflow.do_import(import_items)
            DjangoDataImportItem.objects.bulk_update(
                import_items,
                ["import_success", "import_error", "import_time"],
                batch_size=200,
            )
            success_count = 0
            failed_count = 0
            for item in import_items:
                if item.import_success:
                    success_count += 1
                else:
                    failed_count += 1
            if success_count and failed_count:
                self.import_result = self.PARTLY_FAILED
            elif failed_count:
                self.import_result = self.FAILED
            else:
                self.import_result = self.SUCCESS
            self.import_time = timezone.now()
            self.import_error = None
            self.save()
        except Exception as error:
            self.import_result = self.FAILED
            self.import_time = timezone.now()
            self.import_error = str(error)
            self.save()
        return import_items


class DjangoDataImportItem(models.Model):
    """解析导入用例生成的导入数据条目。"""

    case = models.ForeignKey(
        DjangoDataImportCase,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Django Data Import Case"),
    )

    success = models.BooleanField(
        null=True, blank=True, verbose_name=_("Parse Success")
    )
    info = SafeCharField(
        max_length=512,
        null=True,
        blank=True,
        verbose_name=_("Item Information"),
        password=SAFE_FIELD_PASSWORDS[
            "django_data_import_management.DjangoDataImportItem.info"
        ],
    )
    add_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Parsed Time"))
    json_data = SafeTextField(
        null=True,
        blank=True,
        verbose_name=_("Data"),
        password=SAFE_FIELD_PASSWORDS[
            "django_data_import_management.DjangoDataImportItem.json_data"
        ],
    )

    import_success = models.BooleanField(
        null=True, blank=True, default=None, verbose_name=_("Import Success")
    )
    import_error = SafeTextField(
        null=True,
        blank=True,
        verbose_name=_("Import Error Message"),
        password=SAFE_FIELD_PASSWORDS[
            "django_data_import_management.DjangoDataImportItem.import_error"
        ],
    )
    import_time = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Import Time")
    )

    class Meta:
        verbose_name = _("Django Data Import Item")
        verbose_name_plural = _("Django Data Import Items")

    def get_json_data(self):
        if not self.json_data:
            return {}
        else:
            return json.loads(self.json_data)

    def set_json_data(self, value):
        self.json_data = json.dumps(value)

    data = property(get_json_data, set_json_data)

    def mark_success(self, message=None):
        self.import_success = True
        self.import_time = timezone.now()
        self.import_error = message

    def mark_failed(self, error):
        self.import_success = False
        self.import_time = timezone.now()
        self.import_error = str(error)

    def do_import(self):
        self.case.do_import([self])
        return self.import_success
