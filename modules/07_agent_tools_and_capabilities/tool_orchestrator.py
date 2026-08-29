"""
Module 07: Add Agent Capabilities With Tools
Demonstrates:
1. Dynamic Tool Registration via Python Type-Hint Introspection
2. OpenAPI / Google GenAI Function Declaration Generation
3. Type-Safe Parameter Validation & Automatic Error Recovery
"""

import os
import inspect
from typing import Callable, Dict, Any, List, Optional, get_type_hints

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class ToolRegistry:
    """Manages agent tool functions, schema introspection, and execution."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}

    def register(self, description: Optional[str] = None):
        """Decorator to register a Python function as an agent tool."""
        def decorator(func: Callable):
            name = func.__name__
            doc = description or inspect.getdoc(func) or f"Tool for {name}"
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)

            properties = {}
            required = []

            for param_name, param in sig.parameters.items():
                if param_name in ("self", "cls"):
                    continue
                param_type = type_hints.get(param_name, str)
                type_name = "string"
                if param_type in (int, float):
                    type_name = "number" if param_type is float else "integer"
                elif param_type is bool:
                    type_name = "boolean"
                elif param_type in (list, List):
                    type_name = "array"

                properties[param_name] = {
                    "type": type_name,
                    "description": f"Parameter {param_name}"
                }
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)

            schema = {
                "name": name,
                "description": doc,
                "parameters": {
                    "type": "OBJECT",
                    "properties": properties,
                    "required": required
                }
            }

            self._tools[name] = func
            self._schemas[name] = schema
            return func
        return decorator

    def get_function_declarations(self) -> List[Dict[str, Any]]:
        """Returns OpenAPI / Google GenAI compatible declarations."""
        return list(self._schemas.values())

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a registered tool with type validation and error handling."""
        if tool_name not in self._tools:
            return {"status": "error", "error_code": "TOOL_NOT_FOUND", "message": f"Tool '{tool_name}' not registered."}

        func = self._tools[tool_name]
        try:
            # Type casting / coercion for robust tool calls
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)
            coerced_args = {}

            for k, v in arguments.items():
                if k in type_hints:
                    target_type = type_hints[k]
                    try:
                        if target_type is int and isinstance(v, str):
                            coerced_args[k] = int(v)
                        elif target_type is float and isinstance(v, (str, int)):
                            coerced_args[k] = float(v)
                        elif target_type is bool and isinstance(v, str):
                            coerced_args[k] = v.lower() in ("true", "1")
                        else:
                            coerced_args[k] = v
                    except Exception:
                        coerced_args[k] = v
                else:
                    coerced_args[k] = v

            result = func(**coerced_args)
            return {"status": "success", "tool": tool_name, "output": result}
        except TypeError as te:
            return {"status": "error", "error_code": "INVALID_ARGUMENTS", "message": str(te)}
        except Exception as e:
            return {"status": "error", "error_code": "EXECUTION_FAILURE", "message": str(e)}

# ==============================================================================
# Sample Enterprise Tools
# ==============================================================================

registry = ToolRegistry()

@registry.register(description="Queries Cloud Storage bucket metrics such as total object count and storage size.")
def get_bucket_metrics(bucket_name: str, region: str = "us-central1") -> Dict[str, Any]:
    return {
        "bucket": bucket_name,
        "region": region,
        "object_count": 48200,
        "size_gigabytes": 328.45,
        "storage_class": "STANDARD"
    }

@registry.register(description="Restarts a Cloud Run microservice service instance.")
def restart_cloud_run_service(service_name: str, project_id: str, force: bool = False) -> Dict[str, Any]:
    return {
        "service": service_name,
        "project": project_id,
        "status": "RESTARTED",
        "timestamp": "2026-08-29T12:00:00Z",
        "force_restart": force
    }

def main():
    print("====================================================================")
    print("Module 07: Dynamic Agent Tools & OpenAPI Function Declarations")
    print("====================================================================\n")

    print("--- 1. Generated Function Declarations for Gemini 3.7 Flash ---")
    declarations = registry.get_function_declarations()
    import json
    print(json.dumps(declarations, indent=2))

    print("\n--- 2. Executing Tool with Automatic Type Coercion ---")
    # Simulate LLM returning boolean as string "true"
    result = registry.execute("restart_cloud_run_service", {
        "service_name": "agent-gateway-api",
        "project_id": "gcp-prod-arch-2026",
        "force": "true"
    })
    print("Execution Result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
