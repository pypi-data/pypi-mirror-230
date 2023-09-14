from typing import Any

from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, Extra

from xprompt_common.base_service import BaseService


class PromptParser(BaseModel):
    prompt: str
    soup: BeautifulSoup = None

    tag_to_service: dict[str, BaseService.__class__] = None

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.soup = BeautifulSoup(self.prompt, "html.parser")

    def get_service(self, tag: Tag) -> BaseService:
        return self.tag_to_service[tag.name].create_from_tag(tag)

    @staticmethod
    def handle_missing_tag(tag: Tag):
        pass

    def run_services(self):
        tags: list[Tag] = self.soup.find_all()
        # TODO: running services for parsing tags concurrently
        for tag in tags:
            if tag.name in self.tag_to_service:
                service: BaseService = self.get_service(tag=tag)
                text = service.run()
                tag.replace_with(text)

            else:
                self.handle_missing_tag(tag=tag)

        return self.soup.prettify()
