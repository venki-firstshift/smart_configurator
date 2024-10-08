from langchain_openai import ChatOpenAI

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

from langchain_core.messages import HumanMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.output_parsers.json import SimpleJsonOutputParser

DATA_DIR = '/tmp/smart_configurator'

llm_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)

sample_csv_prompt = """
    Use the following CSV data to answer questions:
    {csv_data}
"""
entity_question = """
    Return a JSON object with a `entity` key that answers the following question: What is a possible table name for given CSV data? 
"""
product_dim_question = """
    Return a JSON object with a `product` key that answers the following question with true of false: Is {entity_name} a product or something which can be sold? 
"""
customer_dim_question = """
    Return a JSON object with a `customer` key that answers the following question with true of false: Is {entity_name} stand for a customer or someone who buys a product or service? 
"""
location_dim_question = """
    Return a JSON object with a `location` key that answers the following question with true of false: does the given CSV describe sites, locations or warehouses? 
"""
cols_question = """
    Return a JSON object with a `columns` key that answers the following question: What are the columns and their data types  given CSV data?
"""
db_cols_question = """
    For given CSV data convert each column name to compatible with MySQL in upper case with spaces replaced with underscore and with no
     trailing underscore. Return a JSON object with a original column name as key and converted column name as value."
"""
# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

chat_prompt = ChatPromptTemplate([
    ("system", "You are going to analyze given CSV Data and answer some questions"),
    MessagesPlaceholder(variable_name="messages")
])


# Define the function that calls the model
def call_model(state: MessagesState):
    # Return a JSON object which stands for the inferred entity
    # csv_prompt = PromptTemplate.from_template(sample_csv_prompt)
    json_parser = SimpleJsonOutputParser()
    # | json_parser
    chat_chain = chat_prompt | llm_model
    response = chat_chain.invoke(state)

    return {"messages": response}


# Define the (single) node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def discover_config_entity(file_name: str, client_id: str) -> dict:
    data_file_path = f"{DATA_DIR}/{file_name}"
    max_lines = 25
    with open(data_file_path) as f:
        lines = []
        for _ in range(max_lines):
            l = f.readline()
            lines.append(l)
            if l == '': break
        csv_data = ''.join(lines)
        # print(csv_data)
    config = {"configurable": {"thread_id": client_id}}

    json_parser = SimpleJsonOutputParser()

    csv_msg = sample_csv_prompt.format(csv_data=csv_data)

    input_messages = [HumanMessage(csv_msg), HumanMessage(entity_question)]
    output = app.invoke({"messages": input_messages}, config)
    last_msg = output["messages"][-1]
    entity_dict = json_parser.parse(last_msg.content)
    # entity details
    entity_details = {"ENTITY_NAME": entity_dict['entity']}

    input_messages = [HumanMessage(csv_msg), HumanMessage(product_dim_question.format(entity_name=entity_dict['entity']))]
    output = app.invoke({"messages": input_messages}, config)
    last_msg = output["messages"][-1]
    prod_dict = json_parser.parse(last_msg.content)

    input_messages = [HumanMessage(csv_msg), HumanMessage(customer_dim_question.format(entity_name=entity_dict['entity']))]
    output = app.invoke({"messages": input_messages}, config)
    last_msg = output["messages"][-1]
    cust_dict = json_parser.parse(last_msg.content)

    input_messages = [HumanMessage(csv_msg),
                      HumanMessage(location_dim_question.format(entity_name=entity_dict['entity']))]
    output = app.invoke({"messages": input_messages}, config)
    last_msg = output["messages"][-1]
    location_dict = json_parser.parse(last_msg.content)

    config_dict = dict()

    if prod_dict['product']:
        entity_details["ENTITY_NAME"] = 'Product'
        entity_details["ENTITY_TYPE"] = "DIMENSION_MASTER_MANAGEMENT"
        entity_details["DIMENSION_SEQUENCE"] = 1
        entity_details["DD1_PK"] = 'Product'
        entity_details["SOURCE_SCHEMA"] = "PRODUCT_MASTER"
        entity_details["STAGE_SCHEMA"] = "DIMENSION_MASTER"

    if cust_dict['customer']:
        entity_details["ENTITY_NAME"] = 'Customer'
        entity_details["ENTITY_TYPE"] = "DIMENSION_MASTER_MANAGEMENT"
        entity_details["DIMENSION_SEQUENCE"] = 2
        entity_details["DD2_PK"] = 'Customer'
        entity_details["SOURCE_SCHEMA"] = "CUSTOMER_MASTER"
        entity_details["STAGE_SCHEMA"] = "DIMENSION_MASTER"

    if location_dict['location']:
        entity_details["ENTITY_NAME"] = 'Location'
        entity_details["ENTITY_TYPE"] = "DIMENSION_MASTER_MANAGEMENT"
        entity_details["DIMENSION_SEQUENCE"] = 3
        entity_details["DD2_PK"] = 'Location'
        entity_details["SOURCE_SCHEMA"] = "LOCATION_MASTER"
        entity_details["STAGE_SCHEMA"] = "DIMENSION_MASTER"

    config_dict['CONFIG_DATA_ENTITY'] = entity_details

    return config_dict

def discover_column_mappings(client_id: str) -> dict:
    config = {"configurable": {"thread_id": client_id}}
    json_parser = SimpleJsonOutputParser()

    input_messages = [HumanMessage(cols_question)]
    output = app.invoke({"messages": input_messages}, config)
    last_msg = output["messages"][-1]
    type_dict = json_parser.parse(last_msg.content)
    type_dict = type_dict['columns']

    input_messages = [HumanMessage(db_cols_question)]
    output = app.invoke({"messages": input_messages}, config)
    last_msg = output["messages"][-1]
    db_dict = json_parser.parse(last_msg.content)
    # print(db_dict)

    # now construct all
    config_dict = dict()
    cols = []
    for key, val in type_dict.items():
        cols.append(dict(DISPLY_NAME=key, SOURCE_TABLE_COLUMN=db_dict[key], DATA_TYPE=type_dict[key]))
    config_dict['CONFIG_DATA_ENTITY_MAP'] = cols

    return config_dict