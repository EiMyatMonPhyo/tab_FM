import os


def generate_model_id(user_id: str, filename: str) -> str:
    """
    Convert:
        user123 + customer_train.csv

    into:
        user123_customer

    Also works for:
        customer_test.csv
    """
    name = os.path.splitext(filename)[0]  # remove .csv

    if name.endswith("_train"):
        name = name[:-6]
    

    elif name.endswith("_test"):
        name = name[:-5]

    return f"{user_id}_{name}"
