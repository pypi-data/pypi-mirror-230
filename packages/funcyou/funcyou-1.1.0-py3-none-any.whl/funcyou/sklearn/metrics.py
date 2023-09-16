import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
    roc_auc_score,
)


def all_metrics(y_true, y_pred, heatmap=True):
    import os

    os.system("pip install scikit-learn seaborn")

    print("f1 score: ", f1_score(y_true, y_pred))
    print("precision score: ", precision_score(y_true, y_pred))
    print("recall score: ", recall_score(y_true, y_pred))
    auc = roc_auc_score(y_true, y_pred)
    print("AUC: %.3f" % auc)
    if heatmap:
        sns.heatmap(confusion_matrix(y_true, y_pred), annot=True, cmap="Blues", fmt="g")
    else:
        print(confusion_matrix(y_true, y_pred))


def make_cm(ytrue, ypred, title=None, figsize=(12, 4)):
    # Create a confusion matrix
    cm = confusion_matrix(ytrue, ypred)

    # Create a figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Plot the confusion matrix in the first subplot
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axes[0])
    axes[0].set_xlabel("Predicted Labels")
    axes[0].set_ylabel("True Labels")
    axes[0].set_title("Confusion Matrix" if title is None else title)

    # Calculate and display performance metrics in the second subplot
    accuracy = accuracy_score(ytrue, ypred)
    precision = precision_score(ytrue, ypred, average="binary")
    recall = recall_score(ytrue, ypred, average="binary")
    f1 = f1_score(ytrue, ypred, average="binary")

    # Set the x and y coordinates for each text label
    x_pos = 0.2  # Adjust these coordinates as needed
    y_pos = 0.6

    # Print the text on the plot without x-label and y-label
    axes[1].text(x_pos, y_pos, f"Accuracy: {accuracy:.4f}", fontsize=12)
    axes[1].text(x_pos, y_pos - 0.1, f"Precision: {precision:.4f}", fontsize=12)
    axes[1].text(x_pos, y_pos - 0.2, f"Recall: {recall:.4f}", fontsize=12)
    axes[1].text(x_pos, y_pos - 0.3, f"F1 Score: {f1:.4f}", fontsize=12)

    # Remove x-label and y-label from the second subplot
    axes[1].axes.get_xaxis().set_visible(False)
    axes[1].axes.get_yaxis().set_visible(False)

    # Adjust the layout of subplots
    plt.tight_layout()

    # Show the plot
    plt.show()


# Function to evaluate: accuracy, precision, recall, f1-score
def calculate_results(y_true, y_pred, model_name: str = None, discription: str = None):
    """
    Calculates model accuracy, precision, recall and f1 score of a binary classification model.
    Args:
        y_true: true labels in the form of a 1D array
        y_pred: predicted labels in the form of a 1D array
    Returns a dictionary of accuracy, precision, recall, f1-score.
    """
    # Calculate model accuracy
    model_accuracy = accuracy_score(y_true, y_pred) * 100
    # Calculate model precision, recall and f1 score using "weighted average
    model_precision, model_recall, model_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted"
    )
    return {
        "model": model_name,
        "accuracy": model_accuracy,
        "precision": model_precision,
        "recall": model_recall,
        "f1": model_f1,
        "discription": discription,
    }


def main():
    pass


if __name__ == "__main__":
    main()
