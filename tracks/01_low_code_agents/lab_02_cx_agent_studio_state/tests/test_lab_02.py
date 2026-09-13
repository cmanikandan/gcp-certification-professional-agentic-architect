import pytest
import sys
import pathlib

lab_dir = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(lab_dir))

import lab

def test_happy_path_transition():
    """Verify that fulfilling a route condition transitions correctly."""
    start = lab.Page("Start")
    target = lab.Page("Target")
    
    start.add_route(lab.TransitionRoute(
        condition=lambda p: p.get("ready") == True,
        target_page="Target"
    ))
    
    sim = lab.CXSimulator(start)
    sim.add_page(target)
    
    sim.session_params["ready"] = True
    sim.process_turn("go")
    
    assert sim.current_page.name == "Target"

def test_event_handler_fallback():
    """Verify that an unhandled route triggers the event handler."""
    start = lab.Page("Start")
    escalate = lab.Page("Escalation")
    
    # Route that never matches
    start.add_route(lab.TransitionRoute(
        condition=lambda p: False,
        target_page="Nowhere"
    ))
    
    # Event handler for no-match
    start.add_event_handler(lab.EventHandler(
        event_name="sys.no-match-default",
        target_page="Escalation"
    ))
    
    sim = lab.CXSimulator(start)
    sim.add_page(escalate)
    
    sim.process_turn("invalid input")
    
    assert sim.current_page.name == "Escalation"

def test_offline_run_does_not_crash(capsys):
    """The offline run must complete successfully without network calls."""
    lab.run_offline()
    captured = capsys.readouterr()
    assert "All 2 checks passed" in captured.out
