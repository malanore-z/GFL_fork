from torchvision import datasets, transforms


class MnistDataset(datasets.MNIST):

    def __init__(self, root):
        super(MnistDataset, self).__init__(root, download=True, train=True, transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.13066062,), (0.30810776,))
        ]))


mnist_dataset = MnistDataset("C:/Users/malanore/Documents/PycharmProjects/GFL_fork/dataset")


if __name__ == "__main__":
    import gfl_test
    mnist = MnistDataset("dataset")
