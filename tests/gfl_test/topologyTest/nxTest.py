import unittest

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


class TestMethod(unittest.TestCase):

    def setUp(self) -> None:
        self.n = 8
        self.undirected_neighbor_num = 4

    def test_start(self):
        # ws = nx.watts_strogatz_graph(8, 6, 0)
        # # plt.subplot(121)
        # nx.draw(ws, with_labels=True, font_weight='bold')
        # plt.show()
        # first generate a ring topology

        # ws = nx.watts_strogatz_graph(self.n, 2, 0)
        # nx.draw(ws, with_labels=True, font_weight='bold')
        # plt.show()
        # topology_ring = np.array(nx.to_numpy_matrix(ws, dtype=np.float32))
        # print(topology_ring)
        #
        # # randomly add some links for each manager (symmetric)
        # k = int(self.neighbor_num)
        # print("undirected_neighbor_num = " + str(k))
        # topology_random_link = np.array(nx.to_numpy_matrix(nx.watts_strogatz_graph(self.n, k, 0)), dtype=np.float32)
        # print("randomly add some links for each manager (symmetric): ")
        # print(topology_random_link)
        #
        # # generate symmetric topology
        # topology_symmetric = topology_ring.copy()
        # for i in range(self.n):
        #     for j in range(self.n):
        #         if topology_symmetric[i][j] == 0 and topology_random_link[i][j] == 1:
        #             topology_symmetric[i][j] = topology_random_link[i][j]
        # np.fill_diagonal(topology_symmetric, 1)
        # print("symmetric topology:")
        # print(topology_symmetric)
        #
        # for i in range(self.n):
        #     row_len_i = 0
        #     for j in range(self.n):
        #         if topology_symmetric[i][j] == 1:
        #             row_len_i += 1
        #     topology_symmetric[i] = topology_symmetric[i] / row_len_i
        # print("weighted symmetric confusion matrix:")
        # print(topology_symmetric)
        # randomly add some links for each manager (symmetric)
        k = self.undirected_neighbor_num
        print("neighbors = " + str(k))
        sw1 = nx.watts_strogatz_graph(self.n, k, 0)
        topology_random_link = np.array(nx.to_numpy_matrix(sw1), dtype=np.float32)
        print("randomly add some links for each manager (symmetric): ")
        print(topology_random_link)

        # first generate a ring topology
        topology_ring = np.array(nx.to_numpy_matrix(nx.watts_strogatz_graph(self.n, 2, 0)), dtype=np.float32)

        for i in range(self.n):
            for j in range(self.n):
                if topology_ring[i][j] == 0 and topology_random_link[i][j] == 1:
                    topology_ring[i][j] = topology_random_link[i][j]

        np.fill_diagonal(topology_ring, 1)

        print("asymmetric topology1:")
        print(topology_ring)

        # k_d = self.out_directed_neighbor
        # Directed graph
        # Undirected graph
        # randomly delete some links
        out_link_set = set()
        for i in range(self.n):
            len_row_zero = 0
            for j in range(self.n):
                if topology_ring[i][j] == 0:
                    len_row_zero += 1
            random_selection = np.random.randint(2, size=len_row_zero)
            # print(random_selection)
            index_of_zero = 0
            for j in range(self.n):
                out_link = j * self.n + i
                if topology_ring[i][j] == 0:
                    if random_selection[index_of_zero] == 1 and out_link not in out_link_set:
                        topology_ring[i][j] = 1
                        out_link_set.add(i * self.n + j)
                    index_of_zero += 1

        print("asymmetric topology2:")
        print(topology_ring)

        for i in range(self.n):
            row_len_i = 0
            for j in range(self.n):
                if topology_ring[i][j] == 1:
                    row_len_i += 1
            topology_ring[i] = topology_ring[i] / row_len_i

        print("weighted asymmetric confusion matrix:")
        print(topology_ring)


if __name__ == "__main__":
    unittest.main()
