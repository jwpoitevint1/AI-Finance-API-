import os
import yaml

def load_policy(path: str = "fintech-policy.yaml") -> dict:
    """Load the fintech governance policy from YAML file."""
    try:
        with open(os.path.abspath(path), "r") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error loading policy: {e}")
        return {}

# Example usage
if __name__ == "__main__":
    policy = load_policy()
    print("Loaded policy:", policy)
