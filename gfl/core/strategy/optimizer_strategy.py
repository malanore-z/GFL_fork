from enum import Enum

class OptimizerStrategy(Enum):

    SGD = "SGD"
    ASGD = "ASGD"
    RPROP = "Rprop"
    ADAGRAD = "Adagrad"
    ADADELTA = "Adadelta"
    RMSprop = "RMSprop"
    ADAM = "Adam"
    ADAMW = "AdamW"
    ADAMAX = "Adamax"
    SPARSE_ADAM = "SparseAdam"
    LBFGS = "LBFGS"
