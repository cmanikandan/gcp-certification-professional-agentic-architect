#!/usr/bin/env python3
"""
Google Cloud Certified Professional Agentic Architect — Interactive CLI & Exam Suite
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MODULE_DIRECTORIES = {
    1: ("modules/01_understand_agents_and_architecture", "agent_architecture_demo.py", "Understand Google Cloud Agents & Architecture"),
    2: ("modules/02_antigravity_and_coding_agents", "coding_agent_sandbox.py", "Antigravity SDK & Coding Agents"),
    3: ("modules/03_agentic_strategy_and_prototyping", "model_selection_matrix.py", "Agentic Strategy & Model Selection"),
    4: ("modules/04_optimizing_agent_behavior", "prompt_optimizer.py", "Optimizing Agent Behavior & Loop Prevention"),
    5: ("modules/05_agent_development_kit_adk", "custom_adk_agent.py", "Engineer AI Agents with ADK (Gemini 3.7 Flash)"),
    6: ("modules/06_agent_memory_and_state", "memory_bank_manager.py", "Manage Agent Memory, State & Sessions"),
    7: ("modules/07_agent_tools_and_capabilities", "tool_orchestrator.py", "Add Agent Capabilities With Tools"),
    8: ("modules/08_custom_skills_plugins_and_hooks", "skills_and_hooks_manager.py", "Build Custom Agent Skills, Plugins & Hooks"),
    9: ("modules/09_enterprise_rag_and_vector_search", "vector_search_rag.py", "Enterprise RAG & Vector Search 1.0"),
    10: ("modules/10_enterprise_databases_and_mcp", "mcp_database_server.py", "Build AI Agents with Enterprise Databases & MCP"),
    11: ("modules/11_multi_agent_orchestration_a2a", "multi_agent_system.py", "Multi-Agent Architectures & Agent2Agent (A2A)"),
    12: ("modules/12_agentops_evaluation_and_monitoring", "agent_evaluator.py", "AgentOps: Evaluation & Observability"),
    13: ("modules/13_production_deployment_and_security", "security_guardrails.py", "Production Deployment, Security & Governance")
}

PRACTICE_QUESTIONS = [
    {
        "domain": "Domain 1: Low-Code Tools",
        "question": "In CX Agent Studio, which component manages retry counts for invalid user inputs and triggers automatic escalation to human agents?",
        "options": {
            "A": "Inline Python cloud functions in webhook memory",
            "B": "Event Handlers with sys.no-match counts transitioning to an escalation page",
            "C": "LLM prompt system instructions asking the model to count turns",
            "D": "Agent Search data store zero-shot classifiers"
        },
        "answer": "B",
        "rationale": "Event Handlers (e.g. sys.no-match-2) provide deterministic state transitions for escalation in CX Agent Studio."
    },
    {
        "domain": "Domain 2: Coding Agents",
        "question": "Which sandboxing configuration ensures that Antigravity coding agents can safely test untrusted code without host filesystem compromise?",
        "options": {
            "A": "Standard Sandbox Mode with GKE Sandbox (gVisor runsc) and workspace isolation",
            "B": "BypassSandbox: true with developer OS firewall rules",
            "C": "Root Docker container mounting the /Users directory",
            "D": "Read-only mode with manual copy-pasting"
        },
        "answer": "A",
        "rationale": "Standard Sandbox Mode coupled with gVisor container runtime (runsc) enforces user-space kernel syscall interception and directory boundaries."
    },
    {
        "domain": "Domain 3: Custom Agents",
        "question": "Which model and parameter configuration is optimal for an enterprise agent requiring ultra-low latency, dynamic reasoning, and structured API outputs?",
        "options": {
            "A": "Gemini 2.5 Pro with 32,000 static thinking tokens",
            "B": "Gemini 3.7 Flash with dynamic thinking budget (1024-2048 tokens) and Pydantic response_schema",
            "C": "Gemma 2 2B without function calling",
            "D": "Gemini 2.5 Flash-Lite with unstructured text outputs"
        },
        "answer": "B",
        "rationale": "Gemini 3.7 Flash provides the optimal blend of speed, cost, thinking reasoning capabilities, and deterministic schema enforcement."
    },
    {
        "domain": "Domain 4: Evaluation & Ops",
        "question": "Which framework on Google Cloud provides automated evaluation of multi-turn tool calling against curated historical cases?",
        "options": {
            "A": "Manual transcript review in Cloud Logging",
            "B": "ADK evaluation tooling (evalset) with Golden Datasets and Gemini 3.7 Flash Autorater",
            "C": "BLEU / ROUGE n-gram lexical overlap metrics",
            "D": "Basic HTTP 200 health check status verification"
        },
        "answer": "B",
        "rationale": "ADK evalset combined with Golden Datasets and LLM autoraters accurately measures tool selection accuracy and retrieval faithfulness."
    },
    {
        "domain": "Domain 5: Security & Governance",
        "question": "Which multi-layer security configuration protects agents against prompt injections, scopes IAM reach, and prevents high-stakes unauthorized actions?",
        "options": {
            "A": "Model Armor on Agent Gateway, Principal Access Boundary (PAB) via Agent Identity, and Human-in-the-Loop (HITL) gates",
            "B": "Custom Python regex string searching on public Cloud Run URLs",
            "C": "Admin Service Accounts with password prompts in user chat",
            "D": "Disabling IAM authentication and running on private compute"
        },
        "answer": "A",
        "rationale": "Model Armor intercepts malicious injection payloads, PAB scopes the Agent Identity IAM boundary, and HITL gates enforce human sign-off."
    }
]

def print_banner():
    banner = """
================================================================================
  Google Cloud Certified Professional Agentic Architect — CLI & Exam Hub
================================================================================
    """
    print(banner)

def run_module(module_num: int):
    if module_num not in MODULE_DIRECTORIES:
        print(f"❌ Error: Invalid module number {module_num}. Choose 1-13.")
        return

    mod_dir, script, title = MODULE_DIRECTORIES[module_num]
    script_path = Path(mod_dir) / "run_lab.sh"

    print(f"\n🚀 Launching Module {module_num:02d}: {title}")
    print(f"📁 Path: {script_path}\n" + "-"*80)

    res = subprocess.run(["bash", str(script_path)])
    print("-"*80)
    if res.returncode == 0:
        print(f"✅ Module {module_num:02d} executed successfully.")
    else:
        print(f"❌ Module {module_num:02d} exited with error code {res.returncode}.")

def run_all_tests():
    print("\n🧪 Running Pytest across all 13 modules...\n" + "="*80)
    res = subprocess.run([sys.executable, "-m", "pytest", "modules/", "-v"])
    print("="*80)
    if res.returncode == 0:
        print("🎉 ALL 13 MODULE TEST SUITES PASSED (100% SUCCESS)!")
    else:
        print("⚠️ Some tests failed. Please inspect the output above.")
    return res.returncode

def run_exam_simulator():
    print("\n📋 Starting Interactive Practice Exam Simulator (5 Questions Sample)")
    print("="*80)
    score = 0

    for i, q in enumerate(PRACTICE_QUESTIONS, 1):
        print(f"\n[Question {i}/5] — {q['domain']}")
        print(f"{q['question']}\n")
        for key in sorted(q["options"].keys()):
            print(f"  ({key}) {q['options'][key]}")

        while True:
            choice = input("\nYour answer (A/B/C/D): ").strip().upper()
            if choice in ("A", "B", "C", "D"):
                break
            print("Please enter A, B, C, or D.")

        if choice == q["answer"]:
            print(f"✅ CORRECT! ({choice})")
            score += 1
        else:
            print(f"❌ INCORRECT. You answered ({choice}). The correct answer is ({q['answer']}).")
        print(f"💡 Rationale: {q['rationale']}")
        print("-" * 80)

    pct = (score / len(PRACTICE_QUESTIONS)) * 100
    print(f"\n🎯 Final Score: {score}/{len(PRACTICE_QUESTIONS)} ({pct:.1f}%)")
    if pct >= 75:
        print("🏆 Result: PASS! You have strong grasp of Agentic Architect principles.")
    else:
        print("📚 Result: NEEDS REVIEW. Study the relevant modules in this repository.")

def run_cleanup():
    print("\n🧹 Launching GCP Lab Resource Teardown & Cache Cleanup...")
    cleanup_script = Path("scripts/cleanup_gcp_resources.sh")
    if cleanup_script.exists():
        res = subprocess.run(["bash", str(cleanup_script)])
        return res.returncode
    else:
        print("❌ Cleanup script not found at scripts/cleanup_gcp_resources.sh")
        return 1


def cleanup_module(module_num: int):
    if module_num not in MODULE_DIRECTORIES:
        print(f"❌ Error: Invalid module number {module_num}. Choose 1-13.")
        return 1
    mod_dir, _, title = MODULE_DIRECTORIES[module_num]
    cleanup_script = Path(mod_dir) / "cleanup.sh"
    print(f"\n🧹 Cleaning Module {module_num:02d}: {title}")
    return subprocess.run(["bash", str(cleanup_script)]).returncode

def check_environment():
    print("\n🔍 Verifying Environment & Google Cloud Configuration")
    print("="*80)
    project_id = os.getenv("GCP_PROJECT_ID", "Not Configured")
    gemini_key = os.getenv("GEMINI_API_KEY")
    masked_key = f"{gemini_key[:6]}...{gemini_key[-4:]}" if gemini_key else "Not Configured (Using Mock Fallback)"
    model = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
    budget = os.getenv("GEMINI_THINKING_BUDGET", "2048")

    print(f"• GCP_PROJECT_ID          : {project_id}")
    print(f"• GEMINI_API_KEY          : {masked_key}")
    print(f"• GEMINI_MODEL            : {model}")
    print(f"• GEMINI_THINKING_BUDGET  : {budget} tokens")
    print(f"• Python Version          : {sys.version.split()[0]}")
    print("="*80)
    print("✅ Environment check complete. All labs run with or without live API keys via built-in mocks.")

def interactive_menu():
    while True:
        print_banner()
        print("Select an option:")
        print("  1. 🚀 Run a Specific Hands-On Module (1-13)")
        print("  2. 🧪 Run All Automated Tests (Pytest across all 13 modules)")
        print("  3. 📋 Take the Interactive Practice Exam Simulator")
        print("  4. 🔍 Check Environment & Gemini 3.7 Flash Configuration")
        print("  5. 🧹 Clean Up a Specific Module")
        print("  6. 🧹 Global GCP Resource Teardown")
        print("  7. 🚪 Exit\n")

        choice = input("Enter choice (1-6): ").strip()
        if choice == "1":
            print("\nAvailable Modules:")
            for num, (_, _, title) in MODULE_DIRECTORIES.items():
                print(f"  {num:2d}. Module {num:02d}: {title}")
            mod_choice = input("\nEnter module number (1-13): ").strip()
            if mod_choice.isdigit():
                run_module(int(mod_choice))
            else:
                print("Invalid input.")
            input("\nPress Enter to return to menu...")
        elif choice == "2":
            run_all_tests()
            input("\nPress Enter to return to menu...")
        elif choice == "3":
            run_exam_simulator()
            input("\nPress Enter to return to menu...")
        elif choice == "4":
            check_environment()
            input("\nPress Enter to return to menu...")
        elif choice == "5":
            mod_choice = input("Enter module number to clean (1-13): ").strip()
            if mod_choice.isdigit():
                cleanup_module(int(mod_choice))
            else:
                print("Invalid input.")
            input("\nPress Enter to return to menu...")
        elif choice == "6":
            run_cleanup()
            input("\nPress Enter to return to menu...")
        elif choice == "7":
            print("\nGood luck with your Google Cloud Certified Professional Agentic Architect exam! 🚀")
            break
        else:
            print("Invalid selection. Try again.")

def main():
    parser = argparse.ArgumentParser(description="Google Cloud Professional Agentic Architect CLI")
    parser.add_argument("--run-module", type=int, help="Run a specific module (1-13)")
    parser.add_argument("--test-all", action="store_true", help="Run pytest across all modules")
    parser.add_argument("--exam", action="store_true", help="Run the practice exam simulator")
    parser.add_argument("--check-env", action="store_true", help="Verify environment setup")
    parser.add_argument("--cleanup", action="store_true", help="Clean up GCP resources and local caches")
    parser.add_argument("--cleanup-module", type=int, help="Clean one module's local artifacts (1-13)")

    args = parser.parse_args()

    if args.run_module:
        run_module(args.run_module)
    elif args.test_all:
        sys.exit(run_all_tests())
    elif args.exam:
        run_exam_simulator()
    elif args.check_env:
        check_environment()
    elif args.cleanup:
        sys.exit(run_cleanup())
    elif args.cleanup_module:
        sys.exit(cleanup_module(args.cleanup_module))
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
