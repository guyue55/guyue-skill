#!/usr/bin/env python3
import os
import sys
import json
import argparse

def extract_claude_chat(jsonl_path, limit=50, keyword=None):
    if not os.path.exists(jsonl_path):
        print(f"Error: JSONL file not found at {jsonl_path}", file=sys.stderr)
        return

    try:
        # Check file size. If very large, we read from bottom or just sequentially safely
        file_size = os.path.getsize(jsonl_path)
        print(f"=== Claude Chat Extraction for {jsonl_path} ({file_size/1024/1024:.1f} MB) ===\n")
        
        extracted_count = 0
        
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if extracted_count >= limit and not keyword:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                    
                # Keyword filter without parsing JSON first to save CPU
                if keyword and keyword.lower() not in line.lower():
                    continue
                    
                try:
                    data = json.loads(line)
                    # Try to extract the user or assistant message
                    msg_type = data.get("type", "unknown")
                    source = data.get("source", "unknown")
                    content = data.get("content", "")
                    
                    # Truncate content if too long to prevent context explosion
                    if len(str(content)) > 2000:
                        content_str = str(content)[:2000] + "\n... [Content Truncated] ..."
                    else:
                        content_str = str(content)
                        
                    print(f"[{msg_type} | {source}]")
                    print(content_str)
                    print("-" * 40)
                    
                    extracted_count += 1
                except json.JSONDecodeError:
                    print("[RAW JSONL]")
                    print(line[:1000])
                    print("-" * 40)
                    extracted_count += 1
                    
        print(f"\nExtraction complete. Extracted {extracted_count} matching entries.")
                
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safely extract chat history from Claude Code JSONL files.")
    parser.add_argument("jsonl_path", help="Path to the .jsonl file")
    parser.add_argument("--limit", type=int, default=50, help="Limit the number of messages to extract (default 50)")
    parser.add_argument("--keyword", type=str, help="Only extract messages containing this keyword")
    args = parser.parse_args()
    
    extract_claude_chat(args.jsonl_path, args.limit, args.keyword)
