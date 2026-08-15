from dotenv import load_dotenv
load_dotenv()

from app.graph.graph import build_graph
from langchain_core.messages import HumanMessage

graph = build_graph()
config = {"configurable": {"thread_id": "cli"}}

while True:
    q = input("You: ")
    result = graph.invoke(
        {
            "messages": [HumanMessage(content=q)],
            "employee_id": "EMP-1234",
            "llm_calls": 0
        },
        config=config,
    )
    msg = result["messages"][-1]
    content = msg.content
    if isinstance(content, list):
        content = "".join(b.get("text", "") for b in content if isinstance(b, dict))
    print(content)