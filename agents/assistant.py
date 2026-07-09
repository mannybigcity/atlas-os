# agents/assistant.py â€” PUTER's agent brain

import json
import re
from openai import OpenAI
from dotenv import load_dotenv

from memory.memory import load_memory, remember_fact
from skills.datetime_skill import get_current_time
from skills.calculator_skill import calculate
from skills.sales_coach_skill import sales_coach
from skills.quote_skill import create_quote
from skills.atlas_skill import run_diagnostics
from skills.morning_report import alfred_morning_report
from skills.agent_registry import show_agents
from skills.assign_agent_task import assign_agent_task
from skills.priority_report import alfred_priority_report
from skills.complete_agent_task import complete_agent_task
from skills.available_agents import show_available_agents
from skills.auto_delegate_report import alfred_auto_delegate_report
from skills.agent_reports import get_agent_report
from skills.deliverables import create_deliverable
from skills.mason_auto_builder_skill import mason_auto_builder_task

from .sales_agent import sales_agent
from .crm_agent import crm_agent
from .content_agent import content_agent
from .operations_agent import operations_agent
from .mission_agent import mission_agent

from crm.crm_skill import add_prospect, show_prospects
from crm.update_prospect import update_prospect_status
from crm.filter_prospects import filter_prospects_by_status
from crm.followups import set_follow_up, show_follow_ups

from orders.order_skill import create_order, show_orders
from orders.update_order import update_order_status

from missions.mission_skill import add_mission, show_missions, complete_mission

from revenue.revenue_skill import add_revenue_opportunity, show_revenue_report
from revenue.cleanup_revenue import cleanup_zero_revenue_items
from brain.intent_router import detect_intent, is_conversation_followup
from brain.intent_router import detect_intent

load_dotenv("config/.env")
client = OpenAI()


tools = [
    {"type": "function", "function": {"name": "mason_auto_builder_task", "description": "Give Mason a coding, build, debug, inspect, test, or system improvement task using Hermes skills without giant prompts.", "parameters": {"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"]}}},
    {"type": "function", "function": {"name": "create_deliverable", "description": "Create an agent deliverable, such as David drafting a follow-up message for a prospect.", "parameters": {"type": "object", "properties": {"agent_name": {"type": "string"}, "deliverable_type": {"type": "string"}, "target": {"type": "string"}}, "required": ["agent_name", "deliverable_type", "target"]}}},
    {"type": "function", "function": {"name": "get_agent_report", "description": "Get a report from an Agent City agent such as Micah, Gideon, David, or Amanda.", "parameters": {"type": "object", "properties": {"agent_name": {"type": "string"}}, "required": ["agent_name"]}}},
    {"type": "function", "function": {"name": "alfred_auto_delegate_report", "description": "Automatically delegate the next best task to an available agent and show available agents.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "show_available_agents", "description": "Show standby Agent City agents available for assignment.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "complete_agent_task", "description": "Complete an Agent City task and return the agent to standby.", "parameters": {"type": "object", "properties": {"agent_name": {"type": "string"}}, "required": ["agent_name"]}}},
    {"type": "function", "function": {"name": "alfred_priority_report", "description": "Show Alfred's real priority report and next recommended action using revenue, follow-ups, and agents.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "assign_agent_task", "description": "Assign a task to an Agent City agent.", "parameters": {"type": "object", "properties": {"agent_name": {"type": "string"}, "task": {"type": "string"}}, "required": ["agent_name", "task"]}}},
    {"type": "function", "function": {"name": "run_diagnostics", "description": "Alfred inspects PUTER's files and databases.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "alfred_morning_report", "description": "Generate Alfred's Batcave morning report.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "show_agents", "description": "Show Agent City registry, including agents, roles, rooms, tasks, and reports.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "show_revenue_report", "description": "Show Alfred's revenue report and money opportunities.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "cleanup_zero_revenue_items", "description": "Remove zero-dollar revenue items from Alfred's revenue system.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "add_revenue_opportunity", "description": "Add a revenue opportunity, paid invoice, outstanding invoice, or potential sale.", "parameters": {"type": "object", "properties": {"customer": {"type": "string"}, "source": {"type": "string"}, "amount": {"type": "number"}, "status": {"type": "string"}}, "required": ["customer", "source", "amount", "status"]}}},

    {"type": "function", "function": {"name": "show_prospects", "description": "Show all saved prospects.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "show_orders", "description": "Show all saved customer orders.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "show_missions", "description": "Show all Batcave missions.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "show_follow_ups", "description": "Show all saved follow-ups.", "parameters": {"type": "object", "properties": {}, "required": []}}},

    {"type": "function", "function": {"name": "add_prospect", "description": "Save a sales prospect.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "business": {"type": "string"}, "product": {"type": "string"}, "status": {"type": "string"}}, "required": ["name", "business", "product", "status"]}}},
    {"type": "function", "function": {"name": "update_prospect_status", "description": "Update prospect status.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "new_status": {"type": "string"}}, "required": ["name", "new_status"]}}},
    {"type": "function", "function": {"name": "filter_prospects_by_status", "description": "Show prospects by status.", "parameters": {"type": "object", "properties": {"status": {"type": "string"}}, "required": ["status"]}}},
    {"type": "function", "function": {"name": "set_follow_up", "description": "Set follow-up for a prospect.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "follow_up_date": {"type": "string"}}, "required": ["name", "follow_up_date"]}}},
    {"type": "function", "function": {"name": "create_quote", "description": "Create a quote.", "parameters": {"type": "object", "properties": {"customer": {"type": "string"}, "product": {"type": "string"}, "quantity": {"type": "number"}, "price_each": {"type": "number"}}, "required": ["customer", "product", "quantity", "price_each"]}}},
    {"type": "function", "function": {"name": "create_order", "description": "Create order.", "parameters": {"type": "object", "properties": {"customer": {"type": "string"}, "product": {"type": "string"}, "quantity": {"type": "number"}, "total": {"type": "number"}}, "required": ["customer", "product", "quantity", "total"]}}},
    {"type": "function", "function": {"name": "update_order_status", "description": "Update order status.", "parameters": {"type": "object", "properties": {"customer": {"type": "string"}, "new_status": {"type": "string"}}, "required": ["customer", "new_status"]}}},
    {"type": "function", "function": {"name": "add_mission", "description": "Add mission.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "category": {"type": "string"}, "priority": {"type": "string"}}, "required": ["title", "category", "priority"]}}},
    {"type": "function", "function": {"name": "complete_mission", "description": "Complete mission.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}},

    {"type": "function", "function": {"name": "get_current_time", "description": "Get the current date and time.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "calculate", "description": "Do basic arithmetic.", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}, "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]}}, "required": ["a", "b", "operation"]}}},
    {"type": "function", "function": {"name": "remember_fact", "description": "Save an important fact about Manny.", "parameters": {"type": "object", "properties": {"fact": {"type": "string"}}, "required": ["fact"]}}},
    {"type": "function", "function": {"name": "sales_coach", "description": "Provide sales coaching.", "parameters": {"type": "object", "properties": {"industry": {"type": "string"}, "situation": {"type": "string"}}, "required": ["industry", "situation"]}}},
    {"type": "function", "function": {"name": "sales_agent", "description": "Create sales messages.", "parameters": {"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"]}}},
    {"type": "function", "function": {"name": "crm_agent", "description": "CRM helper.", "parameters": {"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"]}}},
    {"type": "function", "function": {"name": "content_agent", "description": "Create marketing content.", "parameters": {"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"]}}},
    {"type": "function", "function": {"name": "operations_agent", "description": "Operations helper.", "parameters": {"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"]}}},
    {"type": "function", "function": {"name": "mission_agent", "description": "Mission board helper.", "parameters": {"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"]}}}
]


available_functions = {
    "mason_auto_builder_task": mason_auto_builder_task,
    "create_deliverable": create_deliverable,
    "get_agent_report": get_agent_report,
    "alfred_auto_delegate_report": alfred_auto_delegate_report,
    "show_available_agents": show_available_agents,
    "complete_agent_task": complete_agent_task,
    "alfred_priority_report": alfred_priority_report,
    "assign_agent_task": assign_agent_task,
    "run_diagnostics": run_diagnostics,
    "alfred_morning_report": alfred_morning_report,
    "show_agents": show_agents,
    "show_revenue_report": show_revenue_report,
    "cleanup_zero_revenue_items": cleanup_zero_revenue_items,
    "add_revenue_opportunity": add_revenue_opportunity,

    "show_prospects": show_prospects,
    "show_orders": show_orders,
    "show_missions": show_missions,
    "show_follow_ups": show_follow_ups,
    "add_prospect": add_prospect,
    "update_prospect_status": update_prospect_status,
    "filter_prospects_by_status": filter_prospects_by_status,
    "set_follow_up": set_follow_up,
    "create_quote": create_quote,
    "create_order": create_order,
    "update_order_status": update_order_status,
    "add_mission": add_mission,
    "complete_mission": complete_mission,

    "get_current_time": get_current_time,
    "calculate": calculate,
    "remember_fact": remember_fact,
    "sales_coach": sales_coach,
    "sales_agent": sales_agent,
    "crm_agent": crm_agent,
    "content_agent": content_agent,
    "operations_agent": operations_agent,
    "mission_agent": mission_agent,
}


def parse_assignment_command(text):
    cleaned = text.strip()

    patterns = [
        r"assign\s+([a-zA-Z]+)\s+to\s+(.+)",
        r"tell\s+([a-zA-Z]+)\s+to\s+(.+)",
        r"have\s+([a-zA-Z]+)\s+(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            agent_name = match.group(1).strip()
            task = match.group(2).strip().rstrip(".")
            return agent_name, task

    return None, None


def parse_complete_agent_command(text):
    patterns = [
        r"complete\s+([a-zA-Z]+)(?:'s)?\s+task",
        r"finish\s+([a-zA-Z]+)(?:'s)?\s+task",
        r"mark\s+([a-zA-Z]+)(?:'s)?\s+task\s+complete",
        r"set\s+([a-zA-Z]+)\s+to\s+standby",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def parse_agent_report_command(text):
    patterns = [
        r"get\s+([a-zA-Z]+)(?:'s)?\s+report",
        r"show\s+([a-zA-Z]+)(?:'s)?\s+report",
        r"pull\s+([a-zA-Z]+)(?:'s)?\s+report",
        r"report\s+from\s+([a-zA-Z]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def parse_deliverable_command(text):

    collection_patterns = [
        r"draft\s+a?\s*collection\s+message\s+for\s+(.+)",
        r"create\s+a?\s*collection\s+message\s+for\s+(.+)",
        r"draft\s+a?\s*payment\s+reminder\s+for\s+(.+)",
        r"create\s+a?\s*payment\s+reminder\s+for\s+(.+)",
        r"collect\s+from\s+(.+)",
    ]

    for pattern in collection_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            target = match.group(1).strip().rstrip(".")
            return "Gideon", "collection", target

    followup_patterns = [
        r"draft\s+a?\s*follow[- ]?up\s+for\s+(.+)",
        r"write\s+a?\s*follow[- ]?up\s+for\s+(.+)",
        r"create\s+a?\s*follow[- ]?up\s+for\s+(.+)",
        r"make\s+a?\s*follow[- ]?up\s+for\s+(.+)",
        r"draft\s+a?\s*message\s+for\s+(.+)",
        r"write\s+a?\s*message\s+for\s+(.+)",
    ]

    for pattern in followup_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            target = match.group(1).strip().rstrip(".")
            return "David", "follow-up", target

    return None, None, None

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            target = match.group(1).strip().rstrip(".")
            return "David", "follow-up", target

    return None, None, None


def instant_alfred_command(latest_message):
    text = latest_message.lower().strip()

    intent = detect_intent(latest_message)

    if intent == "conversation":
        return None

    if is_conversation_followup(latest_message):
        return None

    intent = detect_intent(latest_message)

    if intent == "conversation":
        return None
    text = latest_message.lower().strip()

    deliverable_agent, deliverable_type, deliverable_target = parse_deliverable_command(latest_message)
    if deliverable_agent and deliverable_type and deliverable_target:
        return create_deliverable(deliverable_agent, deliverable_type, deliverable_target)

    report_agent_name = parse_agent_report_command(latest_message)
    if report_agent_name:
        return get_agent_report(report_agent_name)

    completed_agent_name = parse_complete_agent_command(latest_message)
    if completed_agent_name:
        return complete_agent_task(completed_agent_name)

    agent_name, task = parse_assignment_command(latest_message)
    if agent_name and task:
        return assign_agent_task(agent_name, task)

    if any(phrase in text for phrase in [
        "auto delegate",
        "auto-delegate",
        "delegate next task",
        "auto delegate next task",
        "assign next best task",
        "assign the next best task",
        "delegate work",
        "delegate the work"
    ]):
        return alfred_auto_delegate_report()

    if any(phrase in text for phrase in [
        "who is available",
        "who's available",
        "show available agents",
        "available agents",
        "show standby agents",
        "standby agents",
        "who is on standby",
        "who's on standby"
    ]):
        return show_available_agents()

    if any(phrase in text for phrase in [
        "what should i work on next",
        "priority report",
        "next move",
        "what is the priority",
        "what's the priority",
        "what should i do next",
        "what needs my attention",
        "what should i focus on",
        "what is most important right now",
        "what's most important right now"
    ]):
        return alfred_priority_report()

    if any(phrase in text for phrase in [
        "good morning",
        "morning report",
        "start my day",
        "what's on my plate",
        "what should i work on today",
        "daily report"
    ]):
        return alfred_morning_report()

    if any(phrase in text for phrase in [
        "show agent city",
        "agent city",
        "show agents",
        "agent registry",
        "who are the agents",
        "show the agents",
        "what is micah working on",
        "what's micah working on",
        "what is gideon working on",
        "what's gideon working on",
        "what is alfred working on",
        "what's alfred working on",
        "what is amanda working on",
        "what's amanda working on",
        "what is david working on",
        "what's david working on"
    ]):
        return show_agents()

    if any(phrase in text for phrase in [
        "cleanup revenue",
        "clean up revenue",
        "clean revenue",
        "remove zero revenue",
        "remove zero-dollar revenue",
        "remove zero dollar revenue",
        "fix revenue",
        "fix the money",
        "clean up the money",
        "remove bad revenue"
    ]):
        return cleanup_zero_revenue_items()

    if any(phrase in text for phrase in [
        "where is the money",
        "money report",
        "show revenue",
        "revenue report",
        "open money",
        "paid money",
        "income opportunities",
        "show me the money"
    ]):
        return show_revenue_report()

    if any(phrase in text for phrase in [
        "run diagnostics",
        "inspect the cave",
        "check the system",
        "check puter",
        "is puter healthy",
        "system health"
    ]):
        return run_diagnostics()

    if any(phrase in text for phrase in [
        "show prospects",
        "show my prospects",
        "prospect list",
        "crm list"
    ]):
        return show_prospects()

    if any(phrase in text for phrase in [
        "show orders",
        "show my orders",
        "order list"
    ]):
        return show_orders()

    if any(phrase in text for phrase in [
        "show missions",
        "mission board",
        "show mission board",
        "open missions"
    ]):
        return show_missions()

    if any(phrase in text for phrase in [
        "show follow ups",
        "show follow-ups",
        "follow up list",
        "follow-up list",
        "who do i need to follow up with"
    ]):
        return show_follow_ups()

    return None


def ask_puter(history):
    latest_message = history[-1]["content"] if history else ""

    instant_response = instant_alfred_command(latest_message)
    if instant_response is not None:
        return instant_response

    facts = load_memory()
    memory_text = "\n".join(facts) if facts else "Nothing yet."

    system_prompt = (
        "You are PUTER, Manny Big City Ramirez's RAMFAM KINGDOM AI command system.\n"
        "You speak as ATLAS, the RAMFAM KINGDOM Chief of Staff, unless a specific tool or agent is responding.\n"
        "ATLAS coordinates Manny's Kingdom agents, protects Manny's time, watches revenue, and gives practical next steps.\n\n"

        "IMPORTANT IDENTITY RULES:\n"
        "- Never refer to the system as Agent City.\n"
        "- Never refer to Alfred as the current Chief of Staff.\n"
        "- The current command identity is ATLAS.\n"
        "- The current system name is RAMFAM KINGDOM.\n"
        "- If an old tool name still contains 'alfred', treat it as a legacy function name only.\n"
        "- Speak in RAMFAM KINGDOM language.\n\n"

        "KINGDOM BRAIN FALLBACK RULE:\n"
        "If Manny asks for a plan, strategy, recommendation, or next step and there is no exact documented playbook, "
        "do not say you cannot assist. Instead say: "
        "'I do not see a specific playbook for that yet, but based on the Kingdom Vision, agent roles, and current priorities, here is my recommended plan.' "
        "Then create a practical best-effort plan using available memory and agent roles.\n\n"

        "TOOL ROUTING RULES:\n"
        "When Manny asks to draft, write, create, or make a follow-up or message for a prospect, use create_deliverable.\n"
        "When Manny asks to get, show, pull, or receive an agent report, use get_agent_report.\n"
        "When Manny asks to auto delegate, delegate work, or assign the next best task, use alfred_auto_delegate_report.\n"
        "When Manny asks who is available, who is on standby, or asks for available agents, use show_available_agents.\n"
        "When Manny asks to complete, finish, or mark an agent's task complete, use complete_agent_task.\n"
        "When Manny asks what he should work on next, what needs attention, asks for the next move, or asks for a priority report, use alfred_priority_report.\n"
        "When Manny asks ATLAS to assign, tell, or have an agent do something, use assign_agent_task.\n"
        "When Manny asks where the money is, asks for revenue, money report, open money, paid money, or income opportunities, use show_revenue_report.\n"
        "When Manny asks to clean up revenue, fix revenue, clean up the money, remove zero-dollar revenue, or remove bad revenue, use cleanup_zero_revenue_items.\n"
        "When Manny asks to add revenue, log money, add a paid order, add an invoice, or add a sales opportunity, use add_revenue_opportunity.\n"
        "When Manny asks to see RAMFAM KINGDOM agents, show agents, see the agent registry, or asks who the agents are, use show_agents.\n"
        "When Manny says good morning, morning report, start my day, what's on my plate today, what should I work on today, daily report, or asks ATLAS for a report, use alfred_morning_report.\n"
        "When Manny asks ATLAS to inspect the system, run diagnostics, check the system, or check if PUTER is healthy, use run_diagnostics.\n"
        "Use the correct tool for CRM, follow-ups, quotes, orders, missions, diagnostics, revenue, priority reports, agents, deliverables, and business help.\n\n"

        "Memory:\n"
        f"{memory_text}\n\n"

        "SPEECH AND SPEED RULE:\n"
"When Manny asks about speech speed, voice speed, response speed, or says you are slow, do not give generic productivity advice. "
"Explain plainly that response speed and speech pace are controlled by the app code, model choice, retrieval, and text-to-speech settings. "
"Tell Manny that Hermes/Mason can help write the fix, but Manny still needs to apply or run the code changes in VS Code. "
"Keep this answer short and practical.\n\n"

"DEFAULT RESPONSE STYLE:\n"
"For normal conversation, keep replies short: 2 to 5 sentences. "
"For voice use, avoid long lists unless Manny asks. "
"Answer the question first, then give one next step. "
"If Manny asks for details, expand.\n\n"

"Be clear, confident, practical, ethical, revenue-aware, Kingdom-aligned, and next-step focused."
    )

    messages = [{"role": "system", "content": system_prompt}] + history

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
    )

    ai_message = response.choices[0].message

    if ai_message.tool_calls:
        messages.append(ai_message)

        for tool_call in ai_message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            result = available_functions[name](**args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

        final = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        return final.choices[0].message.content

    return ai_message.content

    messages = [{"role": "system", "content": system_prompt}] + history

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
    )

    ai_message = response.choices[0].message

    if ai_message.tool_calls:
        messages.append(ai_message)

        for tool_call in ai_message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            result = available_functions[name](**args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

        final = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        return final.choices[0].message.content

    return ai_message.content

