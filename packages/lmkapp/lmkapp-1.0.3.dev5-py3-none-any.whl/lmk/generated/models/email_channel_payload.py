# coding: utf-8

"""
    LMK API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.1
    Generated by: https://openapi-generator.tech
"""


from __future__ import annotations
from inspect import getfullargspec
import pprint
import re  # noqa: F401
import json



from pydantic import BaseModel, Field, StrictStr, validator

class EmailChannelPayload(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """
    type: StrictStr = ...
    email_address: StrictStr = Field(..., alias="emailAddress")
    __properties = ["type", "emailAddress"]

    @validator('type')
    def type_validate_enum(cls, v):
        if v not in ('email'):
            raise ValueError("must validate the enum values ('email')")
        return v

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> EmailChannelPayload:
        """Create an instance of EmailChannelPayload from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> EmailChannelPayload:
        """Create an instance of EmailChannelPayload from a dict"""
        if obj is None:
            return None

        if type(obj) is not dict:
            return EmailChannelPayload.parse_obj(obj)

        _obj = EmailChannelPayload.parse_obj({
            "type": obj.get("type"),
            "email_address": obj.get("emailAddress")
        })
        return _obj

