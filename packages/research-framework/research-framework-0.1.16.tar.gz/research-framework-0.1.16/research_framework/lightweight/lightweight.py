from typing import Any, Dict
from research_framework.base.flyweight.base_flyweight import BaseFlyweight
from research_framework.lightweight.model.item_model import ItemModel
from research_framework.lightweight.model.item_dao import ItemDao
from research_framework.container.container import Container

import json
import hashlib
import traceback


KW_MODEL = "Model"
KW_DATA = "Data"


class FlyWeight(BaseFlyweight):

    @staticmethod
    def hashcode_from_name(name):
        hashable = f'{name}'.encode('utf-8')
        return hashlib.sha1(hashable).hexdigest()
    
    @staticmethod
    def hashcode_from_config(clazz, params):
        hashable = f'{clazz}{json.dumps(params)}'.encode('utf-8')
        return hashlib.sha1(hashable).hexdigest()
         
    @staticmethod
    def append_to_hashcode(hashcode, hashcode2, is_model=False):
        hashable = f'{hashcode}_{hashcode2}[{KW_MODEL if is_model else KW_DATA}]'.encode('utf-8')
        return hashlib.md5(hashable).hexdigest()
    
    def get_item(self, hash_code):
        response = ItemDao.findOneByHashCode(hash_code)
        if response != None:
            doc = ItemModel(**response)
            return doc
        return None
    
    def get_wrapped_data_from_item(self, item):
        #Este devuelve el Wrapper +  el plugin
        return Container.get_filter(item.clazz, item.params)
    
    def get_data_from_item(self, item):
        #Este devuelve solo el plugin
        return Container.get_model(item.clazz, item.params).predict(None)
    
    def set_item(self, name:str, hashcode:str, data:Any, overwrite:bool=False):
        with Container.client.start_session() as session:
            with session.start_transaction():
                try:
                    item = ItemModel(
                        name=name,
                        hash_code= hashcode,
                        clazz="SaaSPlugin",
                        params={
                            "drive_ref": hashcode,
                        }
                    )
                    
                    if not overwrite:
                        result = ItemDao.create(item, session=session)
                        if result.inserted_id is not None:
                            Container.storage.upload_file(file=data, file_name=item.hash_code)
                            session.commit_transaction()
                            return True
                        else:
                            print("Item already exists")
                            return False
                    else:
                        Container.storage.upload_file(file=data, file_name=item.hash_code)
                        return True
                        
                except Exception as ex:
                    print(traceback.print_exc())
                    try:
                        session.abort_transaction()
                        Container.storage.delete_file(hashcode)
                    except Exception as ex2:
                        print(ex2)
                        return False
                    print(ex)
                    return False
                
    def unset_item(self, hashcode:str):
        with Container.client.start_session() as session:
            with session.start_transaction():
                try:
                    result = ItemDao.deleteByHashcode(hashcode, session=session)
                    if result.deleted_count >= 1:
                        Container.storage.delete_file(hashcode)
                        session.commit_transaction()
                        return True
                    else:
                        print("Item couldn't be deleted")
                        return False
                except Exception as ex:
                    try:
                        session.abort_transaction()
                    except Exception as ex2:
                        print(ex2)
                        return False
                    print(ex)
                    return False
                    

    
    
        
                        
                    
    
            
            
        