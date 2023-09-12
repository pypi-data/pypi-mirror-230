import uuid
from enum import Enum
from .api_dto import ApiDto


class Category(ApiDto):

    def __init__(self,
                 category_id: uuid.UUID = None,
                 name: str = None):
        if category_id is None:
            self.category_id = uuid.uuid4()
        else:
            self.category_id = category_id
        self.name = name

    def api_id(self) -> str:
        return str(self.category_id).upper()

    def endpoint(self) -> str:
        return "Categories"

    def from_json(self, obj):
        if "id" in obj.keys():
            self.category_id = uuid.UUID(obj["id"])

        if "name" in obj.keys():
            self.name = obj["name"]

    def to_json(self):
        obj = {
            "id": str(self.category_id)
        }
        if self.name is not None and self.name != '':
            obj["name"] = self.name
        return obj


class Label(ApiDto):

    def __init__(self,
                 label_id: uuid.UUID = None,
                 name: str = None):
        if label_id is None:
            self.label_id = uuid.uuid4()
        else:
            self.label_id = label_id
        self.name = name

    def api_id(self) -> str:
        return str(self.label_id).upper()

    def endpoint(self) -> str:
        return "Labels"

    def from_json(self, obj):
        if "id" in obj.keys():
            self.label_id = uuid.UUID(obj["id"])

        if "name" in obj.keys():
            self.name = obj["name"]

    def to_json(self):
        obj = {
            "id": str(self.label_id)
        }
        if self.name is not None and self.name != '':
            obj["name"] = self.name
        return obj


class Unit(ApiDto):

    def __init__(self,
                 unit_id: uuid.UUID = None,
                 short_name: str = None):
        if unit_id is None:
            self.unit_id = uuid.uuid4()
        else:
            self.unit_id = unit_id
        self.short_name = short_name

    def api_id(self) -> str:
        return str(self.unit_id).upper()

    def endpoint(self) -> str:
        return "Units"

    def from_json(self, obj):
        """
        Load the datapoint entity from a dictionary.

        :param obj: Dict version of the datapoint.
        """
        if "id" in obj.keys():
            self.unit_id = uuid.UUID(obj["id"])

        if "shortName" in obj.keys():
            self.short_name = obj["shortName"]

    def to_json(self):
        obj = {
            "id": str(self.unit_id)
        }
        if self.short_name is not None and self.short_name != '':
            obj["shortName"] = self.short_name
        return obj


class BusinessType(Enum):
    TELEMETRY = "telemetry"
    SET_POINTS = "setPoint"
    LOGICAL = "logical"
    MEASUREMENT = "measurement"


class DataPoint(ApiDto):
    """
    A datapoint reference a time-series tag stored on DB.

    :ivar hardware_id: The unique logical hardware Id of the datapoint.
    """

    def __init__(self,
                 datapoint_id=None,
                 hardware_id=None,
                 business_type: BusinessType = None,
                 name=None,
                 twin_id=None,
                 unit_id=None,
                 category_id=None,
                 description=None):
        if datapoint_id is None:
            self.datapoint_id = uuid.uuid4()
        else:
            self.datapoint_id = datapoint_id
        self.hardware_id = hardware_id
        self.name = name
        self.business_type = business_type
        self.twin_id = twin_id
        self.unit_id = unit_id
        self.category_id = category_id
        self.description = description

    def api_id(self) -> str:
        """
        Id of the datapoint (datapoint_id)

        :return: string formatted UUID of the DataPoint.
        """
        return str(self.datapoint_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate execution.
        :return: Endpoint name.
        """
        return "DataPoints"

    def from_json(self, obj):
        """
        Load the datapoint entity from a dictionary.

        :param obj: Dict version of the datapoint.
        """
        if "id" in obj.keys():
            self.datapoint_id = uuid.UUID(obj["id"])

        if "hardwareId" in obj.keys():
            self.hardware_id = obj["hardwareId"]

        if "name" in obj.keys():
            self.name = obj["name"]

        if "businessType" in obj.keys():
            self.business_type = BusinessType(str(obj["businessType"]))

        if "twinId" in obj.keys() and obj["twinId"] is not None:
            self.twin_id = uuid.UUID(obj["twinId"])

        if "unitId" in obj.keys() and obj["unitId"] is not None:
            self.unit_id = uuid.UUID(obj["unitId"])

        if "categoryId" in obj.keys() and obj["categoryId"] is not None:
            self.category_id = uuid.UUID(obj["categoryId"])

        if "description" in obj.keys() and obj["description"] is not None:
            self.description = obj["description"]

    def to_json(self):
        """
        Convert the datapoint to a dictionary compatible to JSON format.

        :return: dictionary representation of the datapoint object.
        """
        obj = {
            "id": str(self.datapoint_id),
            "hardwareId": str(self.hardware_id)
        }
        if self.business_type is not None and isinstance(self.business_type, BusinessType):
            obj["businessType"] = self.business_type.value
        if self.twin_id is not None:
            obj["twinId"] = self.twin_id
        if self.unit_id is not None:
            obj["unitId"] = self.unit_id
        if self.category_id is not None:
            obj["categoryId"] = self.category_id
        if self.description is not None and self.description != "":
            obj["description"] = self.description
        if self.name is not None and self.name != "":
            obj["name"] = self.name
        return obj
