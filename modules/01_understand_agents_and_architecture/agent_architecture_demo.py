"""
Module 01: Understand Google Cloud Agents & Architecture
Demonstrates the architectural comparison between:
1. Low-Code Deterministic State Machine (Pages, Transition Routes, Event Handlers)
2. Autonomous Agentic Reasoning Loop (Perception, Tool Invocation, Reflection)
"""

import os
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==============================================================================
# 1. Low-Code State Machine Simulator (CX Agent Studio Concept)
# ==============================================================================

@dataclass
class Page:
    name: str
    entry_fulfillment: str
    transition_routes: Dict[str, str] = field(default_factory=dict)
    event_handlers: Dict[str, str] = field(default_factory=dict)

class DeterministicStateMachine:
    """Simulates a Dialogflow CX / Customer Experience Agent Studio State Machine."""
    def __init__(self):
        self.pages: Dict[str, Page] = {
            "START": Page(
                name="START",
                entry_fulfillment="Welcome! How can I assist you with your order?",
                transition_routes={"intent:track_order": "ORDER_LOOKUP", "intent:return_item": "RETURN_POLICY"},
                event_handlers={"sys.no-match-1": "FALLBACK_1", "sys.no-match-2": "ESCALATION"}
            ),
            "ORDER_LOOKUP": Page(
                name="ORDER_LOOKUP",
                entry_fulfillment="Please provide your Order ID.",
                transition_routes={"param:order_valid": "ORDER_STATUS"},
                event_handlers={"sys.no-input": "REPROMPT_ORDER"}
            ),
            "ORDER_STATUS": Page(
                name="ORDER_STATUS",
                entry_fulfillment="Your order #1084 is currently Out for Delivery.",
                transition_routes={"intent:done": "END"}
            ),
            "FALLBACK_1": Page(
                name="FALLBACK_1",
                entry_fulfillment="I didn't quite get that. Could you please rephrase or specify your request?",
                transition_routes={"intent:track_order": "ORDER_LOOKUP", "intent:return_item": "RETURN_POLICY"},
                event_handlers={"sys.no-match-2": "ESCALATION"}
            ),
            "ESCALATION": Page(
                name="ESCALATION",
                entry_fulfillment="Transferring you to a live human agent immediately.",
                transition_routes={}
            )
        }
        self.current_page = "START"
        self.session_params: Dict[str, Any] = {}
        self.no_match_count = 0

    def process_event(self, trigger: str) -> Dict[str, Any]:
        page = self.pages.get(self.current_page)
        if not page:
            return {"status": "error", "message": "Unknown page state."}

        # Check transition routes
        if trigger in page.transition_routes:
            self.current_page = page.transition_routes[trigger]
            self.no_match_count = 0
            new_page = self.pages[self.current_page]
            return {
                "current_page": self.current_page,
                "fulfillment": new_page.entry_fulfillment,
                "action": "TRANSITION_SUCCESS"
            }

        # Trigger event handlers
        self.no_match_count += 1
        event_key = f"sys.no-match-{self.no_match_count}"
        if event_key in page.event_handlers:
            self.current_page = page.event_handlers[event_key]
            new_page = self.pages[self.current_page]
            return {
                "current_page": self.current_page,
                "fulfillment": new_page.entry_fulfillment,
                "action": "EVENT_HANDLER_TRIGGERED"
            }

        return {
            "current_page": self.current_page,
            "fulfillment": "I didn't understand that. Can you rephrase?",
            "action": "DEFAULT_FALLBACK"
        }

# ==============================================================================
# 2. Autonomous Agentic Reasoning Loop (Gemini 3.7 Flash Architecture)
# ==============================================================================

class AutonomousAgentSimulator:
    """Simulates an autonomous goal-driven agent with perception, reasoning, and tool calls."""
    def __init__(self, model_name: str = "gemini-3.7-flash"):
        self.model_name = os.getenv("GEMINI_MODEL", model_name)
        self.tools = {
            "query_order_db": self._tool_query_order_db,
            "calculate_refund": self._tool_calculate_refund
        }

    def _tool_query_order_db(self, order_id: str) -> Dict[str, Any]:
        database = {
            "ORD-991": {"status": "Delivered", "items": ["Wireless Headphones"], "amount": 129.99, "returnable": True},
            "ORD-404": {"status": "In Transit", "items": ["Laptop"], "amount": 1499.00, "returnable": False}
        }
        return database.get(order_id, {"error": "Order not found"})

    def _tool_calculate_refund(self, amount: float, restocking_fee_pct: float = 0.05) -> Dict[str, Any]:
        refund_amount = round(amount * (1 - restocking_fee_pct), 2)
        return {"original_amount": amount, "refund_amount": refund_amount, "restocking_fee": round(amount * restocking_fee_pct, 2)}

    def execute_goal(self, user_goal: str, order_id: str) -> Dict[str, Any]:
        """Executes multi-step reasoning with tool invocation."""
        steps = []
        # Step 1: Observable decision summary (not a private reasoning trace)
        decision_1 = f"Check order status for {order_id} before calculating any refund."
        steps.append({"step": 1, "decision_summary": decision_1, "action": "CALL_TOOL", "tool": "query_order_db"})

        # Step 2: Tool Execution
        order_info = self.tools["query_order_db"](order_id)
        steps.append({"step": 2, "observation": order_info})

        if "error" in order_info:
            final_response = f"I could not locate order {order_id}. Please check your order number."
            return {"status": "completed", "steps": steps, "final_response": final_response}

        # Step 3: Reflection & Next Action
        if order_info.get("returnable"):
            decision_2 = f"Order {order_id} is returnable; calculate the policy-defined refund."
            steps.append({"step": 3, "decision_summary": decision_2, "action": "CALL_TOOL", "tool": "calculate_refund"})
            refund_calc = self.tools["calculate_refund"](order_info["amount"])
            steps.append({"step": 4, "observation": refund_calc})

            final_response = (
                f"Your order {order_id} for {', '.join(order_info['items'])} is eligible for a return. "
                f"Your estimated refund is ${refund_calc['refund_amount']} after a ${refund_calc['restocking_fee']} restocking fee."
            )
        else:
            final_response = f"Order {order_id} is currently '{order_info['status']}' and is not yet eligible for a return."

        return {
            "status": "completed",
            "model": self.model_name,
            "steps": steps,
            "final_response": final_response
        }


# ============================================================================
# 3. Gemini Enterprise data-connection planning (Exam objective 1.2)
# ============================================================================

@dataclass(frozen=True)
class EnterpriseDataSource:
    name: str
    modality: str
    location: str
    contains_sensitive_data: bool = False


class EnterpriseDataConnectionPlanner:
    """Plans grounding and ingestion controls for proprietary multimodal data."""

    SUPPORTED_MODALITIES = {"text", "pdf", "image", "audio", "video"}

    def plan(self, sources: List[EnterpriseDataSource]) -> Dict[str, Any]:
        unsupported = sorted({source.modality for source in sources} - self.SUPPORTED_MODALITIES)
        if unsupported:
            raise ValueError(f"Unsupported modalities: {unsupported}")
        controls = ["Agent Identity least-privilege connector access", "Grounded citations"]
        if any(source.contains_sensitive_data for source in sources):
            controls.extend(["Sensitive Data Protection inspection", "Access-filtered retrieval"])
        return {
            "ingestion_target": "Gemini Enterprise / Agent Search",
            "modalities": sorted({source.modality for source in sources}),
            "source_count": len(sources),
            "security_controls": controls,
        }

# ==============================================================================
# Execution Entrypoint
# ==============================================================================

def main():
    print("====================================================================")
    print("Module 01: Google Cloud Agent Architectures Comparison")
    print("====================================================================\n")

    print("--- 1. Testing Deterministic State Machine (CX Agent Studio) ---")
    sm = DeterministicStateMachine()
    print("Initial Page:", sm.current_page)
    res1 = sm.process_event("intent:track_order")
    print("Event 'intent:track_order' ->", res1)
    res2 = sm.process_event("param:order_valid")
    print("Event 'param:order_valid'  ->", res2)

    # Test Event Handler Escalation
    print("\nSimulating unhandled inputs (Event Handler Escalation):")
    sm_err = DeterministicStateMachine()
    print("Attempt 1 Error ->", sm_err.process_event("unknown_input"))
    print("Attempt 2 Error ->", sm_err.process_event("unknown_input"))

    print("\n--- 2. Testing Autonomous Agent Loop (Gemini 3.7 Flash Architecture) ---")
    agent = AutonomousAgentSimulator()
    result = agent.execute_goal(user_goal="Process return and calculate refund", order_id="ORD-991")
    print(json.dumps(result, indent=2))

    print("\n--- 3. Planning Secure Multimodal Enterprise Grounding ---")
    planner = EnterpriseDataConnectionPlanner()
    data_plan = planner.plan([
        EnterpriseDataSource("Policy PDFs", "pdf", "Cloud Storage", True),
        EnterpriseDataSource("Support recordings", "audio", "Cloud Storage", True),
        EnterpriseDataSource("Product images", "image", "Cloud Storage"),
    ])
    print(json.dumps(data_plan, indent=2))

if __name__ == "__main__":
    main()
