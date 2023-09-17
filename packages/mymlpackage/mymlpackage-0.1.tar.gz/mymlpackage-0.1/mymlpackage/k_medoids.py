""" K-Medoids clustering algorithm. """
import random
import numpy as np
from scipy.sparse import csr_matrix


class KMedoids:
    """
    Initialize K-Medoids clustering.

    Parameters:
    - n_clusters: Number of clusters.
    - max_iterations: Maximum number of iterations.
    - tolerance: Tolerance for convergence.
    - start_prob: Start probability for selecting distant medoids.
    - end_prob: End probability for selecting distant medoids.
    """

    def __init__(
        self,
        n_clusters=2,
        max_iterations=10,
        tolerance=0.1,
        start_prob=0.8,
        end_prob=0.99,
    ):
        if not 0 <= start_prob < end_prob <= 1:
            raise ValueError("Invalid input probabilities")
        self.n_clusters = n_clusters
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.start_prob = start_prob
        self.end_prob = end_prob

        self.medoids = []
        self.clusters = {}
        self.cluster_distances = {}
        self.tol_reached = float("inf")
        self.current_distance = 0

        self.__data = None
        self.__is_csr = None
        self.__rows = 0
        self.__columns = 0

    def fit(self, data):
        """
        Fit the K-Medoids clustering algorithm to the input data.

        Parameters:
        - data: Input data, either a list of data points or a CSR matrix.

        Returns:
        - self
        """
        self.__data = data
        self.__set_data_type()
        self.__start_algorithm()
        return self

    def __start_algorithm(self):
        self.__initialize_medoids()
        self.clusters, self.cluster_distances = self.__calculate_clusters(self.medoids)
        self.__update_clusters()

    def __update_clusters(self):
        for _ in range(self.max_iterations):
            cluster_dist_with_new_medoids = self.__swap_and_recalculate_clusters()
            if self.__is_new_cluster_dist_small(cluster_dist_with_new_medoids):
                self.clusters, self.cluster_distances = self.__calculate_clusters(
                    self.medoids
                )
            else:
                break

    def __is_new_cluster_dist_small(self, cluster_dist_with_new_medoids):
        existing_dist = self.calculate_distance_of_clusters()
        new_dist = self.calculate_distance_of_clusters(cluster_dist_with_new_medoids)

        if existing_dist > new_dist and (existing_dist - new_dist) > self.tolerance:
            self.medoids = list(cluster_dist_with_new_medoids.keys())
            return True
        return False

    def calculate_distance_of_clusters(self, cluster_dist=None):
        if cluster_dist is None:
            cluster_dist = self.cluster_distances
        return sum(cluster_dist.values())

    def __swap_and_recalculate_clusters(self):
        cluster_dist = {}
        for medoid in self.medoids:
            is_shortest_medoid_found = False
            for data_index in self.clusters[medoid]:
                if data_index != medoid:
                    cluster_list = list(self.clusters[medoid])
                    cluster_list[self.clusters[medoid].index(data_index)] = medoid
                    new_distance = self.calculate_inter_cluster_distance(
                        data_index, cluster_list
                    )
                    if new_distance < self.cluster_distances[medoid]:
                        cluster_dist[data_index] = new_distance
                        is_shortest_medoid_found = True
                        break
            if not is_shortest_medoid_found:
                cluster_dist[medoid] = self.cluster_distances[medoid]
        return cluster_dist

    def calculate_inter_cluster_distance(self, medoid, cluster_list):
        distances = [
            self.__get_distance(medoid, data_index) for data_index in cluster_list
        ]
        return sum(distances) / len(cluster_list)

    def __calculate_clusters(self, medoids):
        clusters = {medoid: [] for medoid in medoids}
        cluster_distances = {medoid: 0 for medoid in medoids}

        for row in range(self.__rows):
            nearest_medoid, nearest_distance = self.__get_shortest_distance_to_medoid(
                row, medoids
            )
            cluster_distances[nearest_medoid] += nearest_distance
            clusters[nearest_medoid].append(row)

        for medoid in medoids:
            cluster_distances[medoid] /= len(clusters[medoid])

        return clusters, cluster_distances

    def __get_shortest_distance_to_medoid(self, row_index, medoids):
        min_distance = float("inf")
        current_medoid = None

        for medoid in medoids:
            current_distance = self.__get_distance(medoid, row_index)
            if current_distance < min_distance:
                min_distance = current_distance
                current_medoid = medoid
        return current_medoid, min_distance

    def __initialize_medoids(self):
        self.medoids.append(random.randint(0, self.__rows - 1))
        while len(self.medoids) != self.n_clusters:
            self.medoids.append(self.__find_distant_medoid())

    def __find_distant_medoid(self):
        distances = []
        indices = list(range(self.__rows))
        for row in range(self.__rows):
            distances.append(
                self.__get_shortest_distance_to_medoid(row, self.medoids)[1]
            )
        distances_index = np.argsort(distances)
        choosen_dist = self.__select_distant_medoid(distances_index)
        return indices[choosen_dist]

    def __select_distant_medoid(self, distances_index):
        start_index = round(self.start_prob * len(distances_index))
        end_index = round(self.end_prob * (len(distances_index) - 1))
        return distances_index[random.randint(start_index, end_index)]

    def __get_distance(self, x1, x2):
        a = self.__data[x1].toarray() if self.__is_csr else np.array(self.__data[x1])
        b = self.__data[x2].toarray() if self.__is_csr else np.array(self.__data[x2])
        return np.linalg.norm(a - b)

    def __set_data_type(self):
        """to check whether the given input is of type "list" or "csr" """
        if isinstance(self.__data, csr_matrix):
            self.__is_csr = True
            self.__rows = self.__data.shape[0]
            self.__columns = self.__data.shape[1]

        elif isinstance(self.__data, list):
            self.__is_csr = False
            self.__rows = len(self.__data)
            self.__columns = len(self.__data[0])
        else:
            raise ValueError("Invalid input")

    def predict(self, new_data):
        """
        Predict cluster labels for new data points.

        Parameters:
        - new_data: New data points, either a list of data points or a CSR matrix.

        Returns:
        - cluster_labels: Cluster labels for the new data.
        """
        if self.__data is None:
            raise ValueError("Fit the model before making predictions.")

        if len(new_data) == 0:
            return []

        new_data = new_data if self.__is_csr else np.array(new_data)

        cluster_labels = []
        for data_point in new_data:
            min_distance = float("inf")
            nearest_medoid = None

            for medoid in self.medoids:
                current_distance = self.__get_distance(medoid, data_point)
                if current_distance < min_distance:
                    min_distance = current_distance
                    nearest_medoid = medoid

            cluster_labels.append(nearest_medoid)

        return cluster_labels

    def get_medoids(self):
        """
        Get the medoids of each cluster.

        Returns:
        - medoids: List of medoid indices.
        """
        return self.medoids
