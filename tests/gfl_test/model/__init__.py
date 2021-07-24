from .mnist_model import Net

from torch.optim import SGD
from torch.nn import CrossEntropyLoss


class MnistOptimizer(SGD):
    pass


model = Net()

sgd111 = SGD(model.parameters(), lr=0.1)
