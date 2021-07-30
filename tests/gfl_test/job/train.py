import multiprocessing

import torch
from torch.utils.data import DataLoader

from tests.gfl_test.model import Net, MnistOptimizer, CrossEntropyLoss
from tests.gfl_test.dataset import mnist_dataset


GPU = "cuda:0"


def train(step):
    print("Start step %d" % step)
    model = Net().to(GPU)
    optimizer = MnistOptimizer(model.parameters(), lr=0.01)
    loss_f = CrossEntropyLoss()
    dataloader = DataLoader(mnist_dataset, batch_size=32, shuffle=True)

    for e in range(3):
        correct = 0
        total = 0
        loss_v = 0
        iter_num = 0

        for i, data in enumerate(dataloader):
            inputs, labels = data
            inputs = inputs.to(GPU)
            labels = labels.to(GPU)

            optimizer.zero_grad()

            outputs = model(inputs)
            loss = loss_f(outputs, labels)

            if torch.is_grad_enabled():
                loss.backward()
                optimizer.step()

            loss_v += loss.item()
            iter_num += 1

            _, pred = torch.max(outputs, 1)
            c = (pred == labels).squeeze()
            for i, lb in enumerate(labels):
                correct += c[i].item()
                total += 1

        print("[%d] EPOCH %d OF %d" % (step, e, 3))
        print("[%d] \tLoss: %s, Acc: %s" % (step, loss_v / iter_num, correct / total))

    print("End step %d" % step)


if __name__ == "__main__":
    """
    t1 = threading.Thread(target=train, args=(1, ))
    t2 = threading.Thread(target=train, args=(2, ))
    t3 = threading.Thread(target=train, args=(3, ))
    """
    t1 = multiprocessing.Process(target=train, args=(1, ))
    t2 = multiprocessing.Process(target=train, args=(2, ))
    t3 = multiprocessing.Process(target=train, args=(3, ))
    t1.start()
    t2.start()
    t3.start()
    """
    t1.join()
    t2.join()
    t3.join()
    """

    # train(1)
    pass
