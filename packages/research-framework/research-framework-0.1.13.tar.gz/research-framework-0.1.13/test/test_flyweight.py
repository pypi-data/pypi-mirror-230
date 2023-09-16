import pytest
from typing import Any, Tuple
from research_framework.base.wrappers.filter_wrapper import BaseFilterWrapper
from research_framework.container.container import Container
from research_framework.lightweight.model.item_model import ItemModel
from research_framework.lightweight.model.item_dao import ItemDao
from research_framework.lightweight.lightweight import FlyWeight
from test.plugins.test_plugin import TestPassThroughFilterWrapper

@pytest.fixture
def test_save_new_item():
    Container.fly = FlyWeight()
    
    wrapper = Container.get_filter(TestPassThroughFilterWrapper.__name__, {})
    
    data_hashcode, _, data = wrapper.predict("Test_HASHCODE", "Test_NAME", {})

    if callable(data):
        print("is callable()")
        data = data()
    
    assert data == TestPassThroughFilterWrapper().predict(None)
    
    assert True == Container.storage.check_if_exists(data_hashcode)
    assert data == Container.storage.download_file(data_hashcode)
    stored = ItemModel(**ItemDao.findOneByHashCode(data_hashcode))
    
    assert stored.hash_code == data_hashcode
    
    return  wrapper, data_hashcode


@pytest.fixture
def save_new_item_delete_at_the_end(test_save_new_item:Tuple[BaseFilterWrapper, str], request):
    _, data_hashcode = test_save_new_item
    request.addfinalizer(lambda: Container.fly.unset_item(data_hashcode))
    return test_save_new_item


def test_save_existing_item(save_new_item_delete_at_the_end: Tuple[BaseFilterWrapper, str]):
    wrapper, data_hashcode = save_new_item_delete_at_the_end
    
    new_data_hashcode, _, new_data = wrapper.predict("Test_HASHCODE", "Test_NAME", {})
    
    assert callable(new_data)
    assert new_data_hashcode == data_hashcode    
    assert 1 == len(list(ItemDao.findByHashCode(data_hashcode)))
    
def test_delete_existing_item(test_save_new_item: Tuple[BaseFilterWrapper, str]):
    _, data_hashcode =  test_save_new_item
    
    Container.fly.unset_item(data_hashcode)
    
    assert ItemDao.findOneByHashCode(data_hashcode) == None
    assert Container.storage.check_if_exists(data_hashcode) == False
    
    
    
    

    
    
    