
class SelfInput:
    def __init__(self, train_name, train_clazz, train_params):
        self.train_name = train_name
        self.train_clazz = train_clazz
        self.train_params = train_params
        

class SupervisedInput(SelfInput):
    def __init__(self, test_name, test_clazz, test_params, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_name = test_name
        self.test_clazz = test_clazz
        self.test_params = test_params
        
        

