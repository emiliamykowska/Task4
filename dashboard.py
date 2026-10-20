import streamlit as st
import pandas as pd
from openai import OpenAI
import json
from tools import TOOLS, CONDITIONS

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

first_prompt = """
You are an analitycal assistant for 5 stores. Use avaiable tools to answer questions. 
Do not invent data and answer questions using data from these 5 stores.
If you can't find the data, ask for clarification question instead of guessing.
If a user does not specify the store number, ask for it.
If a user declares a store number, use it as store_num parameter. 
Multiple values are passed as one string separated by " or ".
After filter_dataset and clear_filters the dashboard updates automatically.
When you need to use a tool, directly apply it ang give only the answer, don't say that you need to use a particular tool.

Available datasets:
1. books
Contains information about books: id, title, author, genre, publisher and year

2. users
Contains information about users: id, name, address, phone and email

3. orders
Contains information about orders: id, user_id, book_id, quantity, unit_price_USD, timestamp, shipping, paid_price, date

4. best_days
Contains information about dates with the highest revenue: date, daily_revenue
"""


@st.cache_data
def load_store_data(store_num: int, file_type: str):
    if file_type == "summary":
        return pd.read_csv(f"data/clean/STORE{store_num}/summary.csv")
    elif file_type == "best_days":
        return pd.read_csv(f"data/clean/STORE{store_num}/best_days.csv")
    else:
        return pd.read_csv(f"data/clean/STORE{store_num}/{file_type}.csv")


def get_sorted_data(
    store_num: int = 1,
    file_type: str = None,
    column_name: str = None,
    n: int = 3,
    is_ascending: bool = False,
):
    if store_num not in range(1, 6):
        return "Wrong store number, available ones are 1 - 5"

    if file_type not in ["users", "books", "orders", "best_days"]:
        return "Please tell if you want to get information about books, orders or users"

    df = load_store_data(store_num, file_type)

    if column_name not in df.columns:
        return f"Column was not found. Available columns: are {df.columns.tolist()}"

    sorted_df = df.sort_values(by=column_name, ascending=is_ascending).head(n)
    return sorted_df.to_string(index=False)


def get_most_popular(
    store_num: int = 1, file_type: str = None, column_name: str = None, n: int = 3
):
    if store_num not in range(1, 6):
        return "Wrong store number, available ones are 1 - 5"

    if file_type not in ["users", "books", "orders"]:
        return "Please tell if you want to get information about books, orders or users"

    df = load_store_data(store_num, file_type)

    if column_name not in df.columns:
        return f"Column was not found. Available columns: are {df.columns.tolist()}"

    return df[column_name].value_counts().head(n).to_string()


def get_unique_users(store_num: int = 1):
    if store_num not in range(1, 6):
        return "Wrong store number, available ones are 1 - 5"

    df = load_store_data(store_num, "summary")
    return str(df.iat[0, 0])


def get_unique_authors(store_num: int = 1):
    if store_num not in range(1, 6):
        return "Wrong store number, available ones are 1 - 5"

    df = load_store_data(store_num, "summary")
    return str(df.iat[0, 1])


def get_best_author(store_num: int = 1):
    if store_num not in range(1, 6):
        return "Wrong store number, available ones are 1 - 5"

    df = load_store_data(store_num, "summary")
    return str(df.iat[0, 2])


def get_best_customer_ids(store_num: int = 1):
    if store_num not in range(1, 6):
        return "Wrong store number, available ones are 1 - 5"

    df = load_store_data(store_num, "summary")
    return str(df.iat[0, 3])


def count_entities(entity: str, store_num: int = 1):
    if store_num not in range(1, 6):
        return "Wrong store number, available ones are 1 - 5"

    if entity not in ["users", "books", "orders"]:
        return "Please tell if you want to count books, orders or users"

    entities = load_store_data(store_num, entity)
    return len(entities)


def filter_dataset(dataset: str, column_name: str, condition: str, value: str):
    if dataset not in st.session_state.filters:
        return "Valid datasets are books, users and orders"

    available_columns = load_store_data(1, dataset).columns
    if column_name not in available_columns:
        return (
            f"Column was not found. Available columns are {available_columns.tolist()}"
        )

    if condition not in CONDITIONS:
        return f"Valid conditions are {CONDITIONS}"

    st.session_state.filters[dataset].append(
        {"column_name": column_name, "condition": condition, "value": value}
    )
    st.session_state["view"] = dataset

    return f"Filter with condition {condition} and value {value} was applied on {dataset}.{column_name}"


def clear_filters(dataset: str):
    if dataset == "all":
        for key in st.session_state.filters:
            st.session_state.filters[key] = []

        return "All filters were cleared"

    if dataset not in st.session_state.filters:
        return "Valid datasets are books, users, orders or all 3 datasets"

    st.session_state.filters[dataset] = []
    st.session_state["view"] = dataset
    return f"Filters on {dataset} dataset were cleared"


st.html("""
    <style>
        .stMainBlockContainer {
            max-width:70rem;
        }
    </style>
    """)

if "filters" not in st.session_state:
    st.session_state.filters = {"books": [], "users": [], "orders": []}

tabs = st.tabs([f"Store {i}" for i in range(1, 6)])
view = st.session_state.pop("view", None)

for i, tab in enumerate(tabs, start=1):
    with tab:
        df_summ = load_store_data(i, "summary")
        df_best_days = load_store_data(i, "best_days")
        path_image = f"data/clean/STORE{i}/daily_revenue_fig.png"

        df_summ.columns = [
            "Number of unique users",
            "Number of unique authors",
            "Most popular author",
            "Top customer ids",
        ]
        df_best_days.columns = ["Date", "Daily revenue"]

        st.subheader("Data after preprocessing")

        if view in ("books", "users", "orders"):
            st.session_state[f"key_{i}"] = view

        option = st.selectbox(
            "Select which data you want to see",
            ["books", "users", "orders"],
            key=f"key_{i}",
        )
        df_entity = load_store_data(i, option)

        if option in st.session_state.filters:
            for fil in st.session_state.filters[option]:
                column = fil["column_name"]
                condition = fil["condition"]
                value = fil["value"]

                if column in df_entity.columns:
                    series = df_entity[column].astype("string")
                    value_lowercase = str(value).lower()
                    values = tuple(
                        v.strip()
                        for v in value_lowercase.replace(" or ", ",").split(",")
                    )

                    if condition == "startswith":
                        df_entity = df_entity[series.str.lower().str.startswith(values)]
                    elif condition == "contains":
                        reg = pattern = "|".join(values)
                        df_entity = df_entity[
                            series.str.contains(reg, case=False, regex=True)
                        ]
                    elif condition == "endswith":
                        df_entity = df_entity[series.str.lower().str.endswith(values)]
                    elif condition == "equals":
                        if len(values) > 1:
                            df_entity = df_entity[series.str.lower().isin(values)]
                        else:
                            df_entity = df_entity[
                                series.str.lower() == str(value).lower()
                            ]
                    elif condition == "not_startswith":
                        df_entity = df_entity[
                            ~series.str.lower().str.startswith(values)
                        ]
                    elif condition == "not_contains":
                        reg = pattern = "|".join(values)
                        df_entity = df_entity[
                            ~series.str.contains(reg, case=False, regex=True)
                        ]
                    elif condition == "not_endswith":
                        df_entity = df_entity[~series.str.lower().str.endswith(values)]
                    elif condition == "not_equals":
                        if len(values) > 1:
                            df_entity = df_entity[~series.str.lower().isin(values)]
                        else:
                            df_entity = df_entity[
                                ~(series.str.lower() == str(value).lower())
                            ]
                    elif condition == "greater_than":
                        try:
                            series = pd.to_numeric(series)
                            df_entity = df_entity[series > float(value)]
                        except Exception:
                            pass
                    elif condition == "less_than":
                        try:
                            series = pd.to_numeric(series)
                            df_entity = df_entity[series < float(value)]
                        except Exception:
                            pass

        st.dataframe(df_entity, hide_index=True)
        st.subheader("Summary table")
        st.dataframe(df_summ, hide_index=True)
        st.subheader("Dates with the highest revenue")
        st.dataframe(df_best_days, hide_index=True)
        st.subheader("Plot illustrating dependence of daily revenue on date")
        st.image(path_image, width="stretch")


st.subheader("Chat bot")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "openai/gpt-oss-120b"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask something"):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        messages = [{"role": "system", "content": first_prompt}] + [
            {"role": message["role"], "content": message["content"]}
            for message in st.session_state.messages
        ]

        existing_functions = {
            "get_sorted_data": get_sorted_data,
            "get_most_popular": get_most_popular,
            "get_unique_users": get_unique_users,
            "get_unique_authors": get_unique_authors,
            "get_best_author": get_best_author,
            "get_best_customer_ids": get_best_customer_ids,
            "count_entities": count_entities,
            "filter_dataset": filter_dataset,
            "clear_filters": clear_filters,
        }

        try:
            with st.spinner("Analyzing the request"):
                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=messages,
                    tools=TOOLS,
                    timeout=120,
                )

                response_message = response.choices[0].message

        except Exception as e:
            st.error(f"Could not analyze the request: {e}")
            st.stop()

        if response_message.tool_calls:
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                function_response = existing_functions[function_name](**arguments)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )

                if function_name in ["filter_dataset", "clear_filters"]:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": str(function_response)}
                    )
                    st.rerun()

        try:
            with st.spinner("Generating the answer"):
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=messages,
                    stream=True,
                    tools=TOOLS,
                    timeout=120,
                )

                response = st.write_stream(stream)

                if not response.strip():
                    st.markdown(
                        "I couldn't generate the answer, please specify your request: store number, columns etc."
                    )

        except Exception as e:
            st.error(f"Could not generate the answer: {e}")

        st.session_state.messages.append({"role": "assistant", "content": response})
