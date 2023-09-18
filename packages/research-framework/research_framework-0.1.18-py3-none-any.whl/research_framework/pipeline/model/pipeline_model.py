from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
from research_framework.base.model.base_utils import PyObjectId
from research_framework.lightweight.model.item_model import ItemModel

class GridSearchFilterModel(BaseModel):
    clazz: str
    params: Dict[str, List[Any]]
        
class FilterModel(BaseModel):
    clazz: str
    params: Dict[str, Any]
    item: Optional[ItemModel] = None
    
class MetricModel(BaseModel):
    clazz: str
    value: Optional[str] = None

class InputFilterModel(FilterModel):
    name: str
    items: Optional[List[ItemModel]] = []
    
class PipelineModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    train_input: InputFilterModel
    test_input: InputFilterModel
    filters: List[FilterModel]
    metrics: Optional[List[MetricModel]] = None
    params: Optional[Dict[str, Any]] = None
    scoring: Optional[str] = None
    
    model_config = ConfigDict(
        arbitrary_types_allowed = True,
        populate_by_name = True
    )