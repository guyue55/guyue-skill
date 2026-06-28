#!/usr/bin/env python3
import os
import sys
import sqlite3
import json
import argparse

def extract_cursor_chat(db_path, limit=5, keyword=None):
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}", file=sys.stderr)
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query keys that typically contain chat or composer data
        query = "SELECT key, value FROM ItemTable WHERE key LIKE '%chat%' OR key LIKE '%composer%' OR key LIKE '%aiService%'"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("No chat-related keys found in this workspace.", file=sys.stderr)
            return

        print(f"=== Cursor Chat Extraction for {db_path} ===\n")
        
        extracted_count = 0
        for key, value in rows:
            if extracted_count >= limit and not keyword:
                break
                
            try:
                # Value is stored as BLOB/TEXT, usually JSON string
                if isinstance(value, bytes):
                    value_str = value.decode('utf-8', errors='ignore')
                else:
                    value_str = str(value)
                
                # Check keyword
                if keyword and keyword.lower() not in value_str.lower():
                    continue

                print(f"--- Key: {key} ---")
                
                # Try to parse and pretty-print JSON if possible
                try:
                    data = json.loads(value_str)
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
                    if len(json.dumps(data)) > 2000:
                        print("\n... [Content Truncated] ...")
                except json.JSONDecodeError:
                    # If not valid JSON, just print the raw string safely
                    print(value_str[:2000])
                    if len(value_str) > 2000:
                        print("\n... [Content Truncated] ...")
                print("\n")
                extracted_count += 1
                
            except Exception as e:
                print(f"Error processing key {key}: {e}", file=sys.stderr)
                
    except sqlite3.Error as e:
        print(f"SQLite error: {e}", file=sys.stderr)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safely extract chat history from Cursor state.vscdb SQLite database.")
    parser.add_argument("db_path", help="Path to the state.vscdb file")
    parser.add_argument("--limit", type=int, default=10, help="Limit the number of keys to extract (default 10)")
    parser.add_argument("--keyword", type=str, help="Only extract keys where the value contains this keyword")
    args = parser.parse_args()
    
    extract_cursor_chat(args.db_path, args.limit, args.keyword)
