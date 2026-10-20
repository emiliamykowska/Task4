import pandas as pd
import yaml
import re
import dateparser
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import argparse
from pathlib import Path
import tqdm


def get_args():
    parser = argparse.ArgumentParser(
        "data_processing.py", "Program to process and save cleaned data"
    )
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--output_dir", type=str)

    return parser.parse_args()


def convert_price(price):
    if "$" in price or "USD" in price:
        match = re.search(r"\d+\.?\d+", price)
        return round(float(match.group()), 2)

    match = re.search(r"\d+\.?\d+", price)
    return round(float(match.group()) * 1.2, 2)


def convert_phone(phone):
    match = re.search(r"(\d+)[^\d]*(\d+)[^\d]*(\d+)", phone)

    return "".join(match.groups())


def main():
    args = get_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_dir / "books.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    orders = pd.read_parquet(input_dir / "orders.parquet")
    users = pd.read_csv(input_dir / "users.csv")
    books = pd.DataFrame(data)

    orders.replace(["NULL", "", "NaN", "None", "-", " ", "	"], np.nan, inplace=True)
    users.replace(["NULL", "", "NaN", "None", "-", " ", "	"], np.nan, inplace=True)
    books.replace(["NULL", "", "NaN", "None", "-", " ", "	"], np.nan, inplace=True)

    books.columns = ["id", "title", "author", "genre", "publisher", "year"]

    orders["unit_price"] = orders["unit_price"].apply(convert_price)
    orders.rename(columns={"unit_price": "unit_price_USD"}, inplace=True)

    orders["timestamp"] = orders["timestamp"].apply(dateparser.parse)

    orders.drop_duplicates(inplace=True)

    orders["paid_price"] = orders["quantity"] * orders["unit_price_USD"]
    orders["date"] = orders["timestamp"].dt.date

    users["phone"] = users["phone"].apply(convert_phone)

    users.drop_duplicates(subset=["name", "address", "phone", "email"], inplace=True)

    books["year"] = pd.to_numeric(books["year"], errors="coerce")
    books["year"] = books["year"].where(books["year"] > 0, np.nan)
    books["year"] = books["year"].astype("Int32")

    books.drop_duplicates(
        subset=["title", "author", "genre", "publisher", "year"], inplace=True
    )

    users.to_csv(output_dir / "users.csv", index=False)
    books.to_csv(output_dir / "books.csv", index=False)
    orders.to_csv(output_dir / "orders.csv", index=False)

    orders["daily_revenue"] = (
        orders.groupby("date")["paid_price"].transform("sum").round(2)
    )
    best_days = (
        orders[["date", "daily_revenue"]]
        .drop_duplicates()
        .sort_values("daily_revenue", ascending=False)
        .head(5)
    )
    best_days.to_csv(output_dir / "best_days.csv", index=False)

    order_to_plot = (
        orders[["date", "daily_revenue"]].drop_duplicates().sort_values("date")
    )

    plt.figure(figsize=(16, 9))
    plt.plot(order_to_plot["date"], order_to_plot["daily_revenue"])
    plt.xlabel("Date")
    plt.ylabel("Daily revenue [USD]")
    plt.savefig(output_dir / "daily_revenue_fig.png")

    books["author_set"] = books["author"].apply(
        lambda x: frozenset(name.strip() for name in str(x).split(","))
    )

    orders_and_books = pd.merge(
        books, orders, "inner", left_on="id", right_on="book_id"
    )

    author_revenue = (
        orders_and_books.groupby(["author_set"])["paid_price"]
        .aggregate("sum")
        .round(2)
        .sort_values(ascending=False)
    )

    G = nx.Graph()
    G.add_nodes_from(users["id"])

    for i in tqdm.tqdm(range(users.shape[0])):
        for j in range(i + 1, users.shape[0]):
            if (users.iloc[i][1:].values != users.iloc[j][1:].values).sum() < 2:
                G.add_edge(users.iat[i, 0], users.iat[j, 0])

    unique_accounts = list(nx.connected_components(G))

    spendings = {}

    for ids in unique_accounts:
        ids_tuple = tuple(ids)
        spendings[ids_tuple] = 0

        for id in ids_tuple:
            spendings[ids_tuple] += orders[orders["user_id"] == id]["paid_price"].sum()

    best_buyer = max(spendings, key=spendings.get)
    best_buyer_str = "; ".join(str(int(i)) for i in best_buyer)

    with open(output_dir / "summary.csv", "w") as f:
        f.writelines(
            [
                "unique_users_count, unique_authors_count, best_author, best_customer\n",
                f"{len(unique_accounts)}, {books['author_set'].nunique()}, {next(iter(author_revenue.index[0]))}, {best_buyer_str}",
            ]
        )


if __name__ == "__main__":
    main()
