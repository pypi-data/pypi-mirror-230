from research_framework.base.model.base_dao import BaseDao
from research_framework.container.container import Container
from typing import Any

@Container.register_dao('item_collection')
class ItemDao(BaseDao):
    database:Any = None
    
    @classmethod
    def findByHashCode(cls, hash_code):
        if cls.database != None:
            return cls.database.find({'hash_code': hash_code})
        else:
            raise Exception("Dao Not propertly initialized")
        
        
    @classmethod
    def findOneByHashCode(cls, hash_code):
        if cls.database != None:
            return cls.database.find_one({'hash_code': hash_code})
        else:
            raise Exception("Dao Not propertly initialized")
        
    
    @classmethod
    def deleteByHashcode(cls, hash_code, *args, **kwargs) -> Any:
        if cls.database != None:
            return cls.database.delete_one({'hash_code': hash_code}, *args, **kwargs)
        else:
            raise Exception("Dao Not propertly initialized")