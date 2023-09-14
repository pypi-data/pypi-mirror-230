from abc import abstractmethod

from bs4 import Tag
from pydantic import BaseModel


class BaseService(BaseModel):
    @classmethod
    def create_from_tag(cls, tag: Tag, **kwargs):
        """create class based on bs4 tag"""
        creation_dict = tag.attrs
        creation_dict.update(**kwargs)

        return cls(**creation_dict)

    @abstractmethod
    def run(self) -> str:
        """replace the tag with string"""
