"""
Trajectopy - Trajectory Evaluation in Python

Gereon Tombrink, 2023
mail@gtombrink.de
"""
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import seaborn as sns

from trajectopy.alignment.parameters import AlignmentParameters


def plot_correlation_heatmap(estimated_parameters: AlignmentParameters, enabled_only: bool = True) -> Figure:
    """Plots the correlation heatmap of a covariance matrix.

    Args:
        covariance (np.ndarray): Covariance matrix.

    Returns:
        plt.Figure: Correlation heatmap figure.
    """
    covariance_matrix = estimated_parameters.get_covariance_matrix(enabled_only=enabled_only)
    std_devs = np.sqrt(np.diag(covariance_matrix))
    correlation_matrix = covariance_matrix / np.outer(std_devs, std_devs)
    np.fill_diagonal(correlation_matrix, np.nan)
    fig, ax = plt.subplots()
    ax.grid(False)
    sns.heatmap(correlation_matrix, ax=ax, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f", cbar=False)
    ax.set_xticklabels(estimated_parameters.params_labels(enabled_only=enabled_only, lower_case=True), rotation=45)
    ax.set_yticklabels(estimated_parameters.params_labels(enabled_only=enabled_only, lower_case=True), rotation=0)
    plt.tight_layout()
    return fig


def plot_covariance_heatmap(estimated_parameters: AlignmentParameters, enabled_only: bool = True) -> Figure:
    """Plots the covariance heatmap of a covariance matrix.

    Args:
        covariance (np.ndarray): Covariance matrix.

    Returns:
        plt.Figure: Covariance heatmap figure.
    """
    covariance_matrix = estimated_parameters.get_covariance_matrix(enabled_only=enabled_only)
    fig, ax = plt.subplots()
    ax.grid(False)
    ax.set_xlabel("DOF")
    ax.set_ylabel("DOF")
    sns.heatmap(covariance_matrix, ax=ax, annot=True, cmap="coolwarm", fmt=".3f", cbar=False)
    ax.set_xticklabels(estimated_parameters.params_labels(enabled_only=enabled_only, lower_case=True), rotation=45)
    ax.set_yticklabels(estimated_parameters.params_labels(enabled_only=enabled_only, lower_case=True), rotation=0)
    plt.tight_layout()
    return fig
