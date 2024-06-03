from abc import ABC, abstractmethod

class onnx_model(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def preprocess(self):
        pass

    @abstractmethod
    def predict(self):
        pass

    @abstractmethod
    def load_model(self):
        pass
