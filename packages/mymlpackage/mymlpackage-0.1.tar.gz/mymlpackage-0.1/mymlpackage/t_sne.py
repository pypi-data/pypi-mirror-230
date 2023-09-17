import numpy as np


def compute_pairwise_distances(X):
    # Compute pairwise Euclidean distances between data points
    n = X.shape[0]
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            distances[i, j] = np.linalg.norm(X[i] - X[j])
    return distances


def compute_similarity_matrix(distances, perplexity):
    # Compute the conditional probability similarity matrix P
    n = distances.shape[0]
    P = np.zeros((n, n))
    for i in range(n):
        # Binary search for the perplexity value
        beta_min = -np.inf
        beta_max = np.inf
        tol = 1e-5
        beta = 1.0

        while True:
            # Compute conditional probability matrix
            exp_distances = np.exp(-distances[i] * beta)
            sum_exp_distances = np.sum(exp_distances)
            P[i] = exp_distances / sum_exp_distances

            # Compute the Shannon entropy of P[i]
            entropy = -np.sum(P[i] * np.log2(P[i] + 1e-12))

            # Adjust beta based on the entropy
            entropy_diff = entropy - np.log2(perplexity)
            if np.abs(entropy_diff) < tol:
                break
            if entropy_diff > 0:
                beta_min = beta
                if beta_max == np.inf:
                    beta *= 2
                else:
                    beta = (beta + beta_max) / 2
            else:
                beta_max = beta
                if beta_min == -np.inf:
                    beta /= 2
                else:
                    beta = (beta + beta_min) / 2

    return P


def t_sne(X, perplexity=30, num_iterations=1000, learning_rate=200):
    # Initialize variables
    n, m = X.shape
    Y = np.random.randn(n, 2)  # Initialize Y randomly
    dY = np.zeros((n, 2))
    iY = np.zeros((n, 2))
    gains = np.ones((n, 2))

    # Compute pairwise distances and the similarity matrix P
    distances = compute_pairwise_distances(X)
    P = compute_similarity_matrix(distances, perplexity)
    P = 0.5 * (P + P.T)  # Make P symmetric

    # Perform t-SNE iterations
    for iteration in range(num_iterations):
        # Compute pairwise affinities Q
        sum_Y = np.sum(np.square(Y), axis=1)
        num = 1 / (1 + np.add(np.add(-2 * np.dot(Y, Y.T), sum_Y).T, sum_Y))
        np.fill_diagonal(num, 0)
        Q = num / np.sum(num)
        Q = np.maximum(Q, 1e-12)  # Avoid division by zero

        # Compute gradient and update Y
        PQ_diff = P - Q
        for i in range(n):
            dY[i] = 4 * np.sum(
                np.tile(PQ_diff[:, i] * num[:, i], (2, 1)).T * (Y[i] - Y), axis=0
            )
        Y_grad = (PQ_diff.T.dot(Y - Y[:, np.newaxis])).flatten()
        dY += Y_grad

        # Update gains
        gains = (gains + 0.2) * ((dY > 0) != (iY > 0)) + (gains * 0.8) * (
            (dY > 0) == (iY > 0)
        )
        gains[gains < 0.01] = 0.01

        # Update Y with momentum
        iY = learning_rate * iY - gains * dY
        Y += iY

        # Normalize Y to prevent exploding gradients
        Y -= np.mean(Y, axis=0)

        # Print progress
        if (iteration + 1) % 100 == 0:
            cost = np.sum(P * np.log(P / Q))
            print(f"Iteration {iteration + 1}, Cost: {cost:.2f}")

    return Y
