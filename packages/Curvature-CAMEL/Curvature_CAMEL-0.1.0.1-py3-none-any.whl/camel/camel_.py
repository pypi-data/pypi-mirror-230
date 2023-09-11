from numba import jit, prange
import numpy as np
from sklearn.utils.validation import check_array
from sklearn.decomposition import PCA
from scipy.sparse import issparse, csr_matrix
from scipy.sparse.csgraph import laplacian
from scipy.sparse.linalg import eigsh
from pynndescent import NNDescent
from sklearn.base import BaseEstimator

MAX_VAL = 1e10  # Large value to substitute for np.inf


@jit(nopython=True)
def euclidean_dist(x, y):
    return np.linalg.norm(x - y)


@jit(nopython=True)
def cosine_dist(x, y):
    return 1 - np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))


@jit(nopython=True)
def manhattan_dist(x, y):
    return np.sum(np.abs(x - y))


@jit(nopython=True)
def clip(arr):
    """
    Clip the values in the array to be within the range [a_min, a_max].
    """
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if arr[i, j] < -4:
                arr[i, j] = -4
            elif arr[i, j] > 4:
                arr[i, j] = 4
    return arr


@jit(nopython=True, parallel=True)
def smooth_knn_dist(distances, k=15, n_iter=64, local_connectivity=1.0):
    target = np.log2(k) * 3 / 4
    num_points = distances.shape[0]
    rho = np.zeros(num_points)
    sigma = np.zeros(num_points)

    for i in prange(num_points):
        lo = 0.0
        hi = MAX_VAL
        mid = 1.0
        rho[i] = distances[i, 0]
        for n in range(n_iter):
            psum = np.sum(np.exp(-(distances[i] - rho[i]) / mid))
            if np.fabs(psum - target) < local_connectivity:
                break
            if psum < target:
                hi = mid
                mid = (lo + hi) / 2.0
            else:
                lo = mid
                if hi == MAX_VAL:
                    mid *= 2.0
                else:
                    mid = (lo + hi) / 2.0
        sigma[i] = mid

    return sigma, rho


@jit(nopython=True, parallel=True)
def _compute_gradient_and_update(embedding,
                                 indices,
                                 weights,
                                 curvatures,
                                 alpha, lambda1,
                                 learning_rate,
                                 epsilon=1e-5, num_negative_samples=5, dist_func=euclidean_dist):
    """Compute the gradient for embedding and update it using attractive and repulsive forces."""
    num_samples = embedding.shape[0]
    n_components = embedding.shape[1]

    for i in prange(num_samples):
        gradient_attractive = np.zeros((1, n_components))
        gradient_repulsive = np.zeros((1, n_components))

        # Combined loop for both attractive and repulsive forces from the local neighborhood
        for idx, j in enumerate(indices[i]):
            diff = embedding[i] - embedding[j]
            dist = dist_func(embedding[i], embedding[j])

            if dist > epsilon:  # To avoid division by zero
                weight = weights[i, idx]

                # Attractive force gradient
                gradient_attractive[0] += 2 * alpha * np.tanh(dist ** 2 - 1) * diff / (dist ** 2)

                # Repulsive force gradient
                gradient_repulsive[0] -= 2 * lambda1 * diff / dist ** 2 / (np.tanh(dist ** 2 + 1) ** 2) * curvatures[i]

        # Update embedding using the attractive force gradient
        gradient_attractive = clip(gradient_attractive)

        for dim in range(n_components):
            embedding[i, dim] -= learning_rate * gradient_attractive[0, dim]

        # Update embedding using the local repulsive force gradient
        gradient_repulsive = clip(gradient_repulsive)

        for dim in range(n_components):
            embedding[i, dim] -= 0.2 * learning_rate * gradient_repulsive[0, dim]

        gradient_global_repulsive = np.zeros((1, n_components))
        # Negative sampling for far away points (global repulsive force)
        for _ in range(num_negative_samples):
            j = np.random.randint(num_samples)
            while j in indices[i]:  # Ensure it's not in the local neighborhood
                j = np.random.randint(num_samples)

            diff = embedding[i] - embedding[j]
            dist = dist_func(embedding[i], embedding[j])
            if dist > epsilon:
                gradient_global_repulsive[0] -= lambda1 * diff / (dist ** 2)

        # Update embedding using the global repulsive force gradient
        gradient_global_repulsive = clip(gradient_global_repulsive)

        for dim in range(n_components):
            embedding[i, dim] -= learning_rate * gradient_global_repulsive[0, dim]

    return embedding


class CAMEL(BaseEstimator):
    """CAMEL: A Custom Embedding Algorithm.

    Parameters:
    - n_neighbors (int): Number of neighbors for k-NN graph.
    - n_components (int): Dimension of the embedding space.
    - alpha (float): Parameter for the attractive force.
    - lambda1 (float): Parameter for the repulsive force.
    - learning_rate (float): Learning rate for optimization.
    - max_iter (int, optional): Maximum number of iterations for optimization.
    - metric (str): Metric for k-NN search (used in high-dimensional space).
    - embedding_metric (str): Metric used in the embedded space.
    - verbose (bool): Whether to print progress or not.
    - init (str): Initialization strategy ('pca', 'random', or 'spectral').
    - precomputed_knn (tuple, optional): Precomputed k-NN graph (indices, distances).

    Returns:
    - Instance of the CAMEL class.
    """

    def __init__(self, n_neighbors=5,
                 n_components=2,
                 alpha=10,
                 lambda1=0.9,
                 learning_rate=0.9,
                 max_iter=None,
                 metric='euclidean',
                 embedding_metric='euclidean',
                 verbose=False,
                 init='random',
                 precomputed_knn=None):

        self.n_neighbors = n_neighbors
        self.n_components = n_components
        self.alpha = alpha
        self.lambda1 = lambda1
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.embedding_ = None
        self.metric = metric
        self.embedding_metric = embedding_metric
        self.verbose = verbose
        self.init = init
        self.precomputed_knn = precomputed_knn

    def fit(self, X):
        X = check_array(X, accept_sparse=['csr', 'csc'], ensure_min_samples=2, ensure_min_features=1, estimator=self)
        if issparse(X):
            X = X.tocsr()

        if self.precomputed_knn is not None:
            indices, distances = self.precomputed_knn
        else:
            index = NNDescent(X, n_neighbors=self.n_neighbors, metric=self.metric)
            indices, distances = index.query(X, k=self.n_neighbors)

        sigma, rho = smooth_knn_dist(distances)

        row, col = indices.shape
        weights = np.zeros((row, col))
        for i in range(row):
            for j in range(col):
                if i != j:
                    weights[i, j] = np.exp(-(distances[i, j] - rho[i]) / sigma[i])

        self.embedding_ = self._initialize_embedding(X, indices)
        if self.verbose:
            print(f"Initial embedding computed using {self.init}.")

        weights = np.exp(-distances ** 2)
        curvatures = 1 - np.sum(weights, axis=1) / (np.max(weights, axis=1) * self.n_neighbors)

        if not self.max_iter:
            if X.shape[1] > 10000:
                self.max_iter = 200
            else:
                self.max_iter = 500

        # Decide the distance function
        if self.embedding_metric == 'euclidean':
            dist_func = euclidean_dist
        elif self.embedding_metric == 'cosine':
            dist_func = cosine_dist
        elif self.embedding_metric == 'manhattan':
            dist_func = manhattan_dist
        else:
            raise ValueError("Invalid embedding metric")

        # Iteratively optimize the embedding
        initial_lambda = self.lambda1
        for iteration in range(self.max_iter):
            # Dynamic alpha
            alpha_dynamic = self.alpha * (1.0 - (float(iteration) / float(self.max_iter)))
            # Dynamic lambda1
            lambda_dynamic = initial_lambda * (1.0 - (float(iteration) / float(self.max_iter)))

            # Update embedding based on the loss gradient
            self.embedding_ = _compute_gradient_and_update(self.embedding_, indices, weights, curvatures, alpha_dynamic,
                                                           lambda_dynamic, self.learning_rate, dist_func=dist_func)

            if self.verbose and (iteration % 10 == 0 or iteration == self.max_iter - 1):
                print(f"Iteration {iteration + 1}/{self.max_iter} complete.")

        return self

    def _initialize_embedding(self, X, indices=None):
        if self.init == 'pca':
            pca = PCA(n_components=self.n_components)
            return pca.fit_transform(X)
        elif self.init == 'random':
            return np.random.rand(X.shape[0], self.n_components)
        elif self.init == 'spectral':
            if indices is None:
                raise ValueError("For spectral initialization, k-NN indices must be provided.")
            adj_matrix = np.zeros((X.shape[0], X.shape[0]))
            for i in range(X.shape[0]):
                for j in indices[i]:
                    adj_matrix[i, j] = 1
            lap = laplacian(adj_matrix, normed=True)
            _, vec = eigsh(lap, k=self.n_components + 1, which='SM')
            return vec[:, 1:self.n_components + 1]
        else:
            raise ValueError("Invalid initialization method")

    def fit_transform(self, X):
        self.fit(X)
        return self.get_embedding()

    def get_embedding(self):
        return self.embedding_