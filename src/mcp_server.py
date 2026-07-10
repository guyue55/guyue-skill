import json
import datetime
import re
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("guyue")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = WORKSPACE_ROOT / ".guyue_memory"
INDEX_FILE = MEMORY_DIR / "index.json"
MANIFEST_FILE = WORKSPACE_ROOT / "skills_manifest.json"
MAX_MEMORY_RESULTS = 20

SENSITIVE_MEMORY_PATTERNS = [
    ("API key or token", re.compile(r"(?i)(?:api[_ -]?key|access[_ -]?token|secret)\s*[:=]\s*[^\s,;]+")),
    ("bearer token", re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}")),
    ("provider credential", re.compile(r"(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})")),
    ("personal absolute path", re.compile(r"(?:/(?:Users|home)/[^/\s]+/|[A-Za-z]:\\\\Users\\\\[^\\\s]+\\\\)")),
]


def load_memory_index() -> dict:
    """Load memory index and normalize legacy list-shaped indexes."""
    if not INDEX_FILE.exists():
        return {"memories": []}

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        memories = data.get("memories", [])
        normalized = [item for item in memories if isinstance(item, dict)] if isinstance(memories, list) else []
        return {"memories": normalized}

    if isinstance(data, list):
        normalized = []
        for item in data:
            if not isinstance(item, dict):
                continue
            normalized.append({
                "filename": item.get("filename") or item.get("file", ""),
                "tags": item.get("tags", []),
                "summary": item.get("summary", ""),
                "timestamp": item.get("timestamp", ""),
            })
        return {"memories": normalized}

    return {"memories": []}


def find_sensitive_memory_content(values: list[str]) -> str | None:
    """Return the first sensitive-content category found in memory input."""
    content = "\n".join(values)
    for label, pattern in SENSITIVE_MEMORY_PATTERNS:
        if pattern.search(content):
            return label
    return None


@mcp.tool()
def guyue_list_skills() -> str:
    """Read skills_manifest.json to report available skills."""
    if not MANIFEST_FILE.exists():
        return "skills_manifest.json not found. Ensure you are running in the guyue workspace."
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return f.read()

@mcp.tool()
def guyue_read_memory(query: str) -> str:
    """Read the memory index and return relevant past lessons based on a keyword query."""
    normalized_query = query.strip().casefold()
    if not normalized_query:
        return "Memory query must contain a non-whitespace keyword."

    if not INDEX_FILE.exists():
        return "No memory bank index found."

    try:
        memories = load_memory_index().get("memories", [])
    except json.JSONDecodeError:
        return "Failed to parse memory index."
            
    results = []
    for mem in memories:
        # Simple text matching across tags and summary
        tags_str = " ".join(mem.get("tags", []))
        summary_str = mem.get("summary", "")
        if normalized_query in tags_str.casefold() or normalized_query in summary_str.casefold():
            results.append(mem)
            if len(results) >= MAX_MEMORY_RESULTS:
                break
            
    if not results:
        return f"No memories found for query: {query}"
        
    return json.dumps(results, ensure_ascii=False, indent=2)

@mcp.tool()
def guyue_write_memory(symptom: str, root_cause: str, solution: str, tags: list[str]) -> str:
    """Write a new lesson into the double-track memory bank."""
    normalized_tags = [str(tag).strip() for tag in (tags or []) if str(tag).strip()]
    sensitive_label = find_sensitive_memory_content(
        [symptom, root_cause, solution, *normalized_tags]
    )
    if sensitive_label:
        return f"Refused to store memory containing {sensitive_label}. Redact it and try again."

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"memory_{timestamp}.md"
    filepath = MEMORY_DIR / filename
    
    # Write markdown detail
    md_content = f"# Memory: {timestamp}\n\n## Symptom\n{symptom}\n\n## Root Cause\n{root_cause}\n\n## Solution\n{solution}\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    try:
        index_data = load_memory_index()
    except json.JSONDecodeError:
        index_data = {"memories": []}
                
    new_entry = {
        "filename": filename,
        "tags": normalized_tags,
        "summary": root_cause[:100] + ("..." if len(root_cause) > 100 else ""),
        "timestamp": timestamp
    }
    index_data.setdefault("memories", []).append(new_entry)
    
    temporary_index = INDEX_FILE.with_name(f".{INDEX_FILE.name}.{timestamp}.tmp")
    with open(temporary_index, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    temporary_index.replace(INDEX_FILE)
        
    return f"Successfully saved memory to {filename} and updated the index.json."

if __name__ == "__main__":
    mcp.run()
