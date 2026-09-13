#!/usr/bin/env python3
"""Lab 2: CX Agent Studio State (State-Machine Simulator)"""

import sys
from typing import Callable

from common import load_config, require_live
from common.labkit import LabReport, banner, section, step, detail

# ---------------------------------------------------------------------------
# State-Machine Simulator
#
# The exam asks about CX Agent Studio primitives: pages, transition routes,
# and event handlers. Since CX is a console product, we simulate its semantics
# here in plain Python so you can see exactly how the state machine behaves.
# ---------------------------------------------------------------------------

class Event(Exception):
    """An event raised during a turn, like NO_INPUT or NO_MATCH."""
    pass


class EventHandler:
    def __init__(self, event_name: str, target_page: str = None, message: str = None):
        self.event_name = event_name
        self.target_page = target_page
        self.message = message


class TransitionRoute:
    def __init__(self, condition: Callable[[dict], bool], target_page: str, intent_match: str = None):
        self.condition = condition
        self.target_page = target_page
        self.intent_match = intent_match


class Page:
    def __init__(self, name: str, entry_message: str = ""):
        self.name = name
        self.entry_message = entry_message
        self.routes: list[TransitionRoute] = []
        self.event_handlers: dict[str, EventHandler] = {}
        # Simple parameter filling simulation
        self.required_parameters: list[str] = []

    def add_route(self, route: TransitionRoute):
        self.routes.append(route)

    def add_event_handler(self, handler: EventHandler):
        self.event_handlers[handler.event_name] = handler


class CXSimulator:
    def __init__(self, start_page: Page):
        self.pages: dict[str, Page] = {start_page.name: start_page}
        self.current_page = start_page
        self.session_params = {}
        self.history = []

    def add_page(self, page: Page):
        self.pages[page.name] = page

    def log(self, msg: str):
        self.history.append(msg)
        detail(msg)

    def process_turn(self, user_input: str, intent: str = None):
        self.log(f"User: {user_input} [Intent: {intent}]")
        
        # 1. Parameter collection (simplified)
        for param in self.current_page.required_parameters:
            if param not in self.session_params and user_input:
                self.session_params[param] = user_input
                self.log(f"System: Collected parameter '{param}' = '{user_input}'")
                user_input = "" # Consumed

        # 2. Transition Route evaluation
        for route in self.current_page.routes:
            if (route.intent_match and route.intent_match == intent) or route.condition(self.session_params):
                self.log(f"System: Route matched -> transitioning to {route.target_page}")
                self.transition_to(route.target_page)
                return

        # 3. No match / Event handling
        self.trigger_event("sys.no-match-default")

    def trigger_event(self, event_name: str):
        handler = self.current_page.event_handlers.get(event_name)
        if not handler:
            self.log(f"System: Unhandled event '{event_name}', conversation ended in error.")
            return

        if handler.message:
            self.log(f"Agent: {handler.message}")
            
        if handler.target_page:
            self.log(f"System: Event triggered transition to {handler.target_page}")
            self.transition_to(handler.target_page)

    def transition_to(self, page_name: str):
        self.current_page = self.pages[page_name]
        if self.current_page.entry_message:
            self.log(f"Agent: {self.current_page.entry_message}")


def run_offline():
    banner("Lab 2: CX Agent Studio State", "Pages, Transition Routes, and Event Handlers")

    # Define the Flow: Product Return Process
    start = Page("Start", "Welcome. What would you like to do?")
    
    get_order = Page("GetOrderNumber", "Please provide your 5-digit order number.")
    get_order.required_parameters = ["order_number"]
    
    process_return = Page("ProcessReturn", "Generating your return label...")
    
    escalate = Page("Escalation", "Transferring you to a human agent...")

    # Wire the transition routes
    start.add_route(TransitionRoute(
        condition=lambda p: False, 
        intent_match="return_product", 
        target_page="GetOrderNumber"
    ))
    
    get_order.add_route(TransitionRoute(
        condition=lambda p: "order_number" in p and len(p["order_number"]) == 5, 
        target_page="ProcessReturn"
    ))

    # Add Event Handlers (No-Match Fallback)
    get_order.add_event_handler(EventHandler(
        event_name="sys.no-match-default",
        message="That doesn't look like a valid order number.",
        target_page="Escalation" # Fail fast for demo purposes
    ))

    sim = CXSimulator(start)
    sim.add_page(get_order)
    sim.add_page(process_return)
    sim.add_page(escalate)

    section("Scenario A: The Happy Path")
    sim.transition_to("Start")
    sim.process_turn("I want to return a product", intent="return_product")
    sim.process_turn("12345")
    
    happy_path_success = sim.current_page.name == "ProcessReturn"

    section("Scenario B: The Unhappy Path (Event Handler Escalation)")
    sim.session_params.clear()
    sim.transition_to("Start")
    sim.process_turn("I want to return a product", intent="return_product")
    sim.process_turn("abc") # Invalid order number format
    
    unhappy_path_success = sim.current_page.name == "Escalation"
    
    # Check
    report = LabReport("State Machine Semantics")
    report.check("Transition route mapped intent to page", happy_path_success)
    report.check("Event handler triggered escalation on invalid input", unhappy_path_success)
    report.summary()

def main():
    config = load_config(sys.argv[1:])

    # CX Agent Studio is a console product: the state machine you build there is
    # configuration, not an API you call. There is therefore nothing to bill and
    # nothing to authenticate against, so both paths run the same simulator.
    # require_live() is still honoured so that `--live` reports consistently
    # across all eighteen labs instead of being silently ignored here.
    if require_live(config):
        print("Live mode requested. CX Agent Studio state machines are authored in the")
        print("console, so there is no live API surface for this concept — running the")
        print("same deterministic simulator, at no cost.\n")

    run_offline()


if __name__ == "__main__":
    main()
