import os


def generate_model_id(user_id: str, filename: str, method: str) -> str:
    """
    Convert:
        user123 + customer_train.csv

    into:
        user123_customer

    Also works for:
        customer_test.csv
    """
    name = os.path.splitext(filename)[0]  # remove extension
    print("File extension removed : ", name)

    if method == "train":
        if "_train_" in name:
            name = name.split("_train_", 1)[0]

        elif name.endswith("_train"):
            name = name[:-6]

    if method == "test":
        if "_test_" in name:
            name = name.split("_test_", 1)[0]

        elif name.endswith("_test"):
            name = name[:-5]

    print ("Name fixed : ", name)
    return f"{user_id}_{name}"
