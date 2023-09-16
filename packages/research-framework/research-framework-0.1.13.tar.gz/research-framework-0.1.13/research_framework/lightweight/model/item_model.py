from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from research_framework.base.model.base_utils import PyObjectId


class ItemTypeModel(BaseModel):
    name: str
    clazz: str

class ItemModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    hash_code: str
    clazz: str
    params: Dict[str, Any]
    type: Optional[ItemTypeModel] = None

    model_config = ConfigDict(
        arbitrary_types_allowed = True,
        populate_by_name = True
    )

