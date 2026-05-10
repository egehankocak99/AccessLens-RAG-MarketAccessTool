"""Fire targeted queries via the live API to seed G-BA/AMNOG content into Qdrant."""
import requests

QUERIES = [
    "G-BA AMNOG benefit assessment oncology drugs evidence requirements",
    "AMNOG Germany reimbursement cancer RCT dossier endpoints",
    "G-BA HTA oncology overall survival progression free survival endpoints",
    "NICE technology appraisal cancer evidence requirements threshold",
    "HAS France SMR ASMR clinical benefit oncology assessment",
    "EMA conditional marketing authorisation oncology clinical data",
    "European HTA bodies reimbursement oncology immuno-oncology checkpoint inhibitors",
]

BASE = "http://localhost:8000"

for q in QUERIES:
    print(f"Querying: {q[:60]}...")
    try:
        r = requests.post(f"{BASE}/query", json={"question": q, "top_k": 3}, timeout=120)
        d = r.json()
        sources = len(d.get("sources", []))
        latency = d.get("latency_ms", 0)
        print(f"  -> {sources} sources, {latency}ms")
    except Exception as e:
        print(f"  -> ERROR: {e}")

# Check final count
r = requests.get(f"{BASE}/health")
print("\nHealth:", r.json())
