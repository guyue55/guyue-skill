import json
import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("guyue")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = WORKSPACE_ROOT / ".guyue_memory"
INDEX_FILE = MEMORY_DIR / "index.json"
MANIFEST_FILE = WORKSPACE_ROOT / "skills_manifest.json"


def load_memory_index() -> dict:
    """Load memory index and normalize legacy list-shaped indexes."""
    if not INDEX_FILE.exists():
        return {"memories": []}

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        memories = data.get("memories", [])
        return {"memories": memories if isinstance(memories, list) else []}

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
        if query.lower() in tags_str.lower() or query.lower() in summary_str.lower():
            results.append(mem)
            
    if not results:
        return f"No memories found for query: {query}"
        
    return json.dumps(results, ensure_ascii=False, indent=2)

@mcp.tool()
def guyue_write_memory(symptom: str, root_cause: str, solution: str, tags: list[str]) -> str:
    """Write a new lesson into the double-track memory bank."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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
        "tags": tags,
        "summary": root_cause[:100] + ("..." if len(root_cause) > 100 else ""),
        "timestamp": timestamp
    }
    index_data.setdefault("memories", []).append(new_entry)
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
        
    return f"Successfully saved memory to {filename} and updated the index.json."

if __name__ == "__main__":
    mcp.run()
