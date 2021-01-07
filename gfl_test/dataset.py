import os

from torchvision import datasets, transforms


class MnistDataset(datasets.MNIST):

    def __init__(self, root):
        super(MnistDataset, self).__init__(root, download=True, train=True, transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.13066062,), (0.30810776,))
        ]))


abs_path = os.path.abspath("dataset")
mnist_dataset = MnistDataset(abs_path)
