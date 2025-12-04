# diag_agent_module.py
import importlib, inspect, sys, traceback

def diag(module_name):
    print("=== DIAGNOSTIC for module:", module_name, "===")
    try:
        m = importlib.import_module(module_name)
    except Exception as e:
        print("IMPORT ERROR:")
        traceback.print_exc()
        return

    print("\n-- Classes defined in module (name -> module) --")
    classes = [(name, obj) for name,obj in inspect.getmembers(m, inspect.isclass) if obj.__module__ == module_name]
    if not classes:
        print("  (no classes defined directly in this module)")
    for name, obj in classes:
        print(f"  - {name}  (type: {type(obj)})")

    print("\n-- All classes in module (including imported) --")
    for name,obj in inspect.getmembers(m, inspect.isclass):
        print(f"  - {name}  (from {obj.__module__})")

    # check BaseAgent subclassing
    try:
        from agents.base_agent import BaseAgent
        subs = [name for name,obj in classes if issubclass(obj, BaseAgent) and obj is not BaseAgent]
        print("\n-- Subclasses of agents.base_agent.BaseAgent found in module:", subs)
    except Exception as e:
        print("\nCould not import agents.base_agent.BaseAgent (error below):")
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diag_agent_module.py <module.name>  (e.g. agents.order_agent.agent)")
        sys.exit(1)
    diag(sys.argv[1])
