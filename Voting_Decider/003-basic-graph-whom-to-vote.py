import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
openai_api_key = os.environ["OPENAI_API_KEY"]

from langchain_openai import ChatOpenAI

chatModel35 = ChatOpenAI(model="gpt-3.5-turbo-0125")
chatModel4o = ChatOpenAI(model="gpt-4o")

from typing_extensions import TypedDict

class State(TypedDict):
    graph_state: str

def node_1(state):
    print("---Node 1---")
    return {"graph_state": state['graph_state'] + " Based on this, I will vote for"}


def node_2(state):
    print("---Node 2---")
    return {"graph_state": state['graph_state'] +" Donald Trump."}

def node_3(state):
    print("---Node 3---")
    return {"graph_state": state['graph_state'] +" Kamala Harris."}

import random
from typing import Literal
import matplotlib.pyplot as plt

def decide_vote(state) -> Literal["node_2", "node_3"]:
    policy_context = """
Donald Trump:
- Wants to reduce U.S. involvement in foreign wars (e.g., Ukraine)
- Supports stricter immigration enforcement and border security
- Advocates for crypto freedom and deregulation
- Emphasizes lower taxes, domestic oil/gas, and manufacturing

Kamala Harris:
- Advocates for immigration reform and DACA protections
- Supports social safety nets (healthcare, food, rent)
- Favors strong climate action and clean energy investment
- Promotes NATO, Ukraine aid, and international cooperation
"""

    prompt = (
        f"{policy_context}\n\n"
        f"Voter Info:\n{state['graph_state']}\n\n"
        "Analyze this person's values and priorities. Then rate each candidate from 0 to 100 "
        "based on how likely the person is to vote for them.\n"
        "Format:\n"
        "Reasoning: <brief explanation>\n"
        "Trump: <score>\n"
        "Harris: <score>"
    )

    response = chatModel35.invoke(prompt)
    full_output = response.content.strip()

    print("\n🧠 GPT's reasoning and scores:\n" + full_output + "\n")

    # Score parsing
    trump_score = 0
    harris_score = 0
    for line in full_output.splitlines():
        if line.lower().startswith("trump:"):
            try:
                trump_score = int(line.split(":")[1].strip())
            except:
                pass
        elif line.lower().startswith("harris:"):
            try:
                harris_score = int(line.split(":")[1].strip())
            except:
                pass

    # 🎨 Plotting
    candidates = ["Donald Trump", "Kamala Harris"]
    scores = [trump_score, harris_score]

    plt.figure(figsize=(6, 4))
    bars = plt.bar(candidates, scores)
    plt.ylim(0, 100)
    plt.ylabel("Likelihood of Voting (%)")
    plt.title("Candidate Preference Based on Voter Info")

    # Add score labels on top
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 1, f"{int(height)}%", ha="center", fontsize=10)

    plt.tight_layout()
    plt.show()

    # Decision routing
    if trump_score >= harris_score:
        return "node_2"
    else:
        return "node_3"


def is_meaningful_input(text: str) -> bool:
    prompt = (
        f"A user gave the following response about how they feel about the country:\n\n"
        f"\"{text}\"\n\n"
        "Even if it's informal, ungrammatical, or written in a rush, does this response contain enough meaningful political opinion, "
        "concern, or sentiment that could help predict voting preference?\n"
        "Respond only with 'yes' or 'no'."
    )
    response = chatModel35.invoke(prompt)
    answer = response.content.strip().lower()
    return "yes" in answer



from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

# Build graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Add the logic of the graph
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_vote)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Compile the graph
graph = builder.compile()

# Step 1: Ask the user for input
name = input("What's your name? ")
user_state = input("Which state do you live in? ")

while True:
    opinion = input("How do you feel about the current state of the country? ")
    if is_meaningful_input(opinion):
        break
    print("⚠️ That input doesn't seem meaningful. Please try again using a more complete or clear sentence.")


# Step 2: Combine into a single message
intro_message = (
    f"My name is {name}. I live in {user_state}. "
    f"Here's what I think about the country: {opinion}"
)

# Step 3: Start the graph with this info
response = graph.invoke({"graph_state": intro_message})

# response = graph.invoke({"graph_state" : "Hi, this is Joe Biden."})


print("\n----------\n")

print(response["graph_state"])

print("\n----------\n")

