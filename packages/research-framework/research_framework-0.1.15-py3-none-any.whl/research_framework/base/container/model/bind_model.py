from pydantic import BaseModel, ConfigDict
from bson.objectid import ObjectId
from typing import Optional, Type
from research_framework.base.plugin.base_plugin import BasePlugin
from research_framework.base.wrappers.filter_wrapper import BaseFilterWrapper

class BindModel(BaseModel):
    wrapper: Optional[Type[BaseFilterWrapper]] = None
    plugin: Optional[Type[BasePlugin]] = None
    
    model_config = ConfigDict(
        arbitrary_types_allowed = True,
        populate_by_name = True
    )
    
    
