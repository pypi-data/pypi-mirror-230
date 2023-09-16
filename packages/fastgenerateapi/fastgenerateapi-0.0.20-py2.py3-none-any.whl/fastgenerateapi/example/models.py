import datetime
from typing import Optional

from pydantic.fields import FieldInfo
from tortoise import Model, fields


class StaffInfo(Model):
    """
        员工信息
    """
    is_active: bool = fields.BooleanField(default=True, description="是否有效")
    name: Optional[str] = fields.CharField(description="名字", max_length=255)
    age: Optional[int] = fields.IntField(description="年龄", default=None, null=True)
    created_at: Optional[datetime.datetime] = fields.DatetimeField(null=True, auto_now_add=True, description="创建时间")
    company: fields.ForeignKeyNullableRelation["CompanyInfo"] = fields.ForeignKeyField(
        'models.CompanyInfo', related_name="staff", on_delete=fields.SET_NULL, default=None, null=True)

    @property
    def test(self):
        return "test"

    class PydanticMeta:
        exclude = ["created_at"]
        get_one_include = [
            "name",
            "company__name",
            ("test", Optional[str], FieldInfo(default="", description="测试字段")),
        ]
        # get_all_include = []
        # create_include = []
        # update_include = []


class CompanyInfo(Model):
    """
        公司信息
    """
    is_active: bool = fields.BooleanField(default=True, description="是否有效")
    name: str = fields.CharField(description="岗位名称", max_length=255)
    boss_name: str = fields.CharField(description="老板名字", max_length=255)
    parent: fields.ForeignKeyNullableRelation["CompanyInfo"] = fields.ForeignKeyField(
        'models.CompanyInfo',
        null=True,
        on_delete=fields.SET_NULL,
        db_constraint=False,
        description='父级')



