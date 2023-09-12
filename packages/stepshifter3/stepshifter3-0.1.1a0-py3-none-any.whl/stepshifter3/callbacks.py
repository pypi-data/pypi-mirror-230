"""
A good practise for writing callbacks is to inherit from the Callback class in the framework you are using.
For example, if
"""


from keras.callbacks import Callback
from sklearn.base import clone


class MyCallback(Callback):
    def __init__(self, model):
        self.model = model
        self.models = {}

    def on_step_end(self, model, step, logs):
        self.models[step] = clone(model)

    def get_step_number(self, step_number):
        return self.models.get(step_number)
