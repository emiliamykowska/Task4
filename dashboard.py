import streamlit as st
import pandas as pd
from openai import OpenAI
import json

@st.cache_data
def load_store_data(store_num: int, file_type: str):
    if file_type == "summary":
        return pd.read_csv(f"STORE{store_num}/summary.csv")
    elif file_type == "best_days":
        return pd.read_csv(f"STORE{store_num}/best_days")
    else:
        return pd.read_csv(f"STORE{store_num}/clean/{file_type}.csv")

st.html("""
    <style>
        .stMainBlockContainer {
            max-width:70rem;
        }
    </style>
    """
)

tabs = st.tabs([f"Store {i}" for i in range(1, 6)])

for i, tab in enumerate(tabs, start = 1):
    with tab:
        df_summ = load_store_data(i, "summary")
        df_best_days = load_store_data(i, "best_days")
        path_image = f"STORE{i}/STORE{i}_fig.png"

        df_summ.columns = ["Number of unique users", "Number of unique authors", "Most popular author", "Top customer ids"]
        df_best_days.columns = ["Date", "Daily revenue"]

        st.subheader("Data after preprocessing")
        option = st.selectbox("Select which data you want to see", ["books", "users", "orders"], key=f"key_{i}")
        df_entity = load_store_data(i, option)
        
        st.dataframe(df_entity, hide_index=True)
        st.subheader("Summary table")
        st.dataframe(df_summ, hide_index=True)
        st.subheader("Dates with the highest revenue")
        st.dataframe(df_best_days, hide_index=True)
        st.subheader("Plot illustrating dependence of daily revenue on date")
        st.image(path_image, width="stretch")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_sorted_data",
            "description": "Get rows with top records from users, books and orders or days with highest revenue",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_type": {"type": "string", "enum": ["users", "books", "orders", "best_days"], "description": "users, books, orders or best_days"},
                    "store_num": {"type": "integer", "enum": [1, 2, 3, 4, 5], "description": "Store number from 1 to 5"},
                    "column_name": {"type": "string", "description": "Column name to sort by"},
                    "n": {"type": "integer", "minimum": 1, "maximum": 100, "description": "Number of rows to return (default 3)"}                    
                },
                "required": ["file_type", "column_name"]
            },
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_most_popular",
            "description": "Get the most popular records from users, books or orders",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_type": {"type": "string", "enum": ["users", "books", "orders"], "description": "users, books or orders"},
                    "store_num": {"type": "integer", "enum": [1, 2, 3, 4, 5], "description": "Store number from 1 to 5"},
                    "column_name": {"type": "string", "description": "Column name to find the most popular record in"},
                    "n": {"type": "integer", "minimum": 1, "description": "Number of rows to return (default 3)"}                    
                },
                "required": ["file_type", "column_name"]
            },
        }
    },

    {
        "type": "function",
        "function":{
            "name": "get_unique_users",
                "description": "Get number of unique users",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "store_num": {"type": "integer", "enum": [1, 2, 3, 4, 5], "description": "Store number from 1 to 5"}
                    },
                },
        }        
    },
    {
        "type": "function",
        "function":{
            "name": "get_unique_authors",
            "description": "Get number of unique authors",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_num": {"type": "integer", "enum": [1, 2, 3, 4, 5], "description": "Store number from 1 to 5"}
                },
            },
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_best_author",
            "description": "Get name of top selling author(s)",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_num": {"type": "integer", "enum": [1, 2, 3, 4, 5], "description": "Store number from 1 to 5"}
                },
            },
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_best_customer_ids",
            "description": "Get ids belonging to the top customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_num": {"type": "integer", "enum": [1, 2, 3, 4, 5], "description": "Store number from 1 to 5"}
                },
            },
        }
    },

    {
        "type": "function",
        "function": {
            "name": "count_entities",
            "description": "Count users, book or orders in chosen store",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity": {"type": "string", "enum": ["users", "books", "orders"], "description": "users, books, or orders"},
                    "store_num": {"type": "integer", "enum": [1, 2, 3, 4, 5], "description": "Store number from 1 to 5"}
                },
                "required": ["entity"]
            },
        }
    },
]

def get_sorted_data(store_num: int = 1, file_type: str = None, column_name: str = None, n: int = 3):
    if store_num not in range(1, 6):
        return "Wrong store number, available ones are 1 - 5"

    if file_type not in ["users", "books", "orders", "best_days"]:
            return "Please tell if you want to get information about books, orders or users"

    df = load_store_data(store_num, file_type)

    if column_name not in df.columns:
            return (
                f"Column was not found. Available columns: are {df.columns.tolist()}"
            )
    
    sorted_df = df.sort_values(by=column_name, ascending=False).head(n)
    return sorted_df.to_string()
        
    

def get_most_popular(store_num: int = 1, file_type: str = None, column_name: str = None, n: int = 3):
    if store_num not in range(1, 6):
            return "Wrong store number, available ones are 1 - 5"

    if file_type not in ["users", "books", "orders"]:
            return "Please tell if you want to get information about books, orders or users"

    
    df = load_store_data(store_num, file_type)

    if column_name not in df.columns:
            return (
                f"Column was not found. Available columns: are {df.columns.tolist()}"
            )

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


first_prompt = """
You are an analitycal assistant for 5 stores. Use avaiable tools to answer questions. 
Do not invent data and answer questions using data from these 5 stores.
If you can't find the data, ask for clarification question instead of guessing.
If a user declares a store number, use it as store_num parameter. 

Available datasets:
1. books
Contains information about books: id, title, author, genre, publisher and year

2. users
Contains information about users: id, name, address, phone and email

3. orders
Contains information about orders: id, user_id, book_id, quantity, unit_price_USD, timestamp, shipping, paid_price, date
"""

st.subheader("Chat bot")

# client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
client = OpenAI(
            api_key="sk-no-key-required", 
            base_url="http://192.168.5.30:8080/v1"
        )

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "qwen 3.6"

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
        messages = [{"role": "system", "content": first_prompt}] + [{"role": message["role"], "content":message["content"]} for message in st.session_state.messages]

        try:
            with st.spinner("Analyzing the request"):
                response = client.chat.completions.create(
                    model = st.session_state["openai_model"],
                    messages = messages,
                    tools = tools,
                    timeout = 60)

                response_message = response.choices[0].message

        except Exception as e:
            st.error(f"Could not analyze the request: {e}")
            st.stop()

        if response_message.tool_calls:            
            messages.append(response_message)

            existing_functions = {
                        "get_sorted_data": get_sorted_data,
                        "get_most_popular": get_most_popular,
                        "get_unique_users": get_unique_users,
                        "get_unique_authors": get_unique_authors,
                        "get_best_author": get_best_author,
                        "get_best_customer_ids": get_best_customer_ids,
                        "count_entities": count_entities,
                    }

            for tool_call in response_message.tool_calls:               

                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                function_response = existing_functions[function_name](**arguments)

                messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    })

        try:
            with st.spinner("Generating the answer"):
                stream = client.chat.completions.create(
                        model = st.session_state["openai_model"],
                        messages = messages,
                        tools=tools,
                        stream = True,
                        timeout = 60)
                
                response = st.write_stream(stream)

        except Exception as e:
            st.error(f"Could not generate the answer: {e}")            

        st.session_state.messages.append({"role": "assistant", "content": response})

