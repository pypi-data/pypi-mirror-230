from research_framework.container.container import Container

to_delete = ["600c845eb1ae710f10956c9bdace4529"]


for hashcode in to_delete:
    Container.fly.unset_item(hashcode)
    