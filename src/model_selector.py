"""Model Selector and Registry for DataPilot AI."""

from __future__ import annotations

from typing import Any, Dict, List
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


def get_candidate_models(
    problem_type: str,
    dataset_size: int,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Returns an appropriately tuned dictionary of Scikit-Learn models based on problem type and volume."""
    is_large = dataset_size > 20000
    n_trees = 50 if is_large else 100

    if "Classification" in problem_type:
        return {
            "Logistic Regression": LogisticRegression(
                max_iter=1000,
                random_state=random_state,
                solver="lbfgs",
            ),
            "Decision Tree": DecisionTreeClassifier(
                max_depth=10,
                min_samples_split=5,
                random_state=random_state,
            ),
            "Random Forest": RandomForestClassifier(
                n_estimators=n_trees,
                max_depth=12,
                min_samples_split=4,
                n_jobs=1,
                random_state=random_state,
            ),
            "Gradient Boosting": GradientBoostingClassifier(
                n_estimators=min(80, n_trees),
                learning_rate=0.1,
                max_depth=5,
                random_state=random_state,
            ),
            "K-Nearest Neighbors": KNeighborsClassifier(
                n_neighbors=min(5, max(3, int(dataset_size**0.5))),
                n_jobs=1,
            ),
        }

    elif "Regression" in problem_type:
        return {
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(alpha=1.0, random_state=random_state),
            "Decision Tree": DecisionTreeRegressor(
                max_depth=10,
                min_samples_split=5,
                random_state=random_state,
            ),
            "Random Forest": RandomForestRegressor(
                n_estimators=n_trees,
                max_depth=12,
                min_samples_split=4,
                n_jobs=-1,
                random_state=random_state,
            ),
            "Gradient Boosting": GradientBoostingRegressor(
                n_estimators=min(80, n_trees),
                learning_rate=0.1,
                max_depth=5,
                random_state=random_state,
            ),
        }

    elif "Unsupervised" in problem_type:
        return {
            "K-Means": KMeans(n_clusters=3, n_init=10, random_state=random_state),
            "PCA": PCA(n_components=2, random_state=random_state),
        }

    return {}


def get_model_descriptions() -> Dict[str, str]:
    """Returns human-readable descriptions for educational clarity."""
    return {
        "Logistic Regression": "Generalized Linear Model utilizing sigmoid/softmax activation. Fast, highly interpretable baseline with probability calibration.",
        "Linear Regression": "Ordinary Least Squares (OLS) fitting an optimal linear hyperplane minimizing residual sum of squares.",
        "Ridge Regression": "Linear regression augmented with L2 Tikhonov regularization, preventing coefficient explosion under multicollinearity.",
        "Decision Tree": "Non-parametric hierarchical partitioning based on Gini Impurity (classification) or MSE reduction (regression).",
        "Random Forest": "Ensemble bagging method constructing uncorrelated decision trees over bootstrap samples, drastically reducing variance.",
        "Gradient Boosting": "Sequential boosting ensemble where each subsequent tree fits the negative gradient of the loss function.",
        "K-Nearest Neighbors": "Instance-based lazy learning classifying points via majority voting among closest Euclidean distance neighbors.",
        "K-Means": "Centroid-based iterative partitioning clustering algorithm optimizing within-cluster sum of squares (inertia).",
        "PCA": "Orthogonal linear transformation projecting data onto principal eigenvectors capturing maximum variance.",
    }
