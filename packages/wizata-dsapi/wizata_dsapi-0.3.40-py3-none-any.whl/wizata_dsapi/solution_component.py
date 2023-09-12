import uuid
from .api_dto import ApiDto
from enum import Enum
import json


class SolutionType(Enum):
    GRAFANA_DASHBOARD = "grafana_dashboard"


class SolutionComponent(ApiDto):
    """
    A solution components handle an element giving to end-users to interact with solution.
    Currently supporting:
        - Grafana Dashboard
    """

    def __init__(self, solution_component_id=None, category=None, sub_category=None, solution_type=None, content=None,
                 category_order=None, sub_category_order=None,
                 twin_id=None, template_id=None):
        if solution_component_id is None:
            self.solution_component_id = uuid.uuid4()
        else:
            self.solution_component_id = solution_component_id
        self.category = category
        self.category_order = category_order
        self.sub_category = sub_category
        self.sub_category_order = sub_category_order
        self.solution_type = solution_type
        self.content = content
        self.twin_id = twin_id
        self.template_id = template_id

    def api_id(self) -> str:
        return str(self.solution_component_id).upper()

    def endpoint(self) -> str:
        return "SolutionComponents"

    def to_json(self):
        obj = {
            "id": str(self.solution_component_id)
        }
        if self.category is not None:
            obj["category"] = self.category
        if self.category_order is not None:
            obj["categoryOrder"] = self.category_order
        if self.sub_category is not None:
            obj["subCategory"] = str(self.sub_category)
        if self.sub_category_order is not None:
            obj["subCategoryOrder"] = str(self.sub_category_order)
        if self.content is not None:
            obj["content"] = self.content
        if self.solution_type is not None and isinstance(self.solution_type, SolutionType):
            obj["type"] = self.solution_type.value
        if self.twin_id is not None:
            obj["twinId"] = str(self.twin_id)
        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)
        return obj

    def from_json(self, obj):
        if "id" in obj.keys():
            self.solution_component_id = uuid.UUID(obj["id"])
        if "category" in obj.keys() and obj["category"] is not None:
            self.category = obj["category"]
        if "categoryOrder" in obj.keys() and obj["categoryOrder"] is not None:
            self.category_order = obj["categoryOrder"]
        if "subCategory" in obj.keys() and obj["subCategory"] is not None:
            self.sub_category = obj["subCategory"]
        if "subCategoryOrder" in obj.keys() and obj["subCategoryOrder"] is not None:
            self.sub_category_order = obj["subCategoryOrder"]
        if "content" in obj.keys() and obj["content"] is not None:
            self.content = obj["content"]
        if "type" in obj.keys():
            self.solution_type = SolutionType(str(obj["type"]))
        if "twinId" in obj.keys() and obj["twinId"] is not None:
            self.twin_id = uuid.UUID(obj["twinId"])
        if "templateId" in obj.keys() and obj["templateId"] is not None:
            self.template_id = uuid.UUID(obj["templateId"])
