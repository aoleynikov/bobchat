#!/usr/bin/env python3

import sys
import os
from pathlib import Path
from main import file_processor_factory
from data.storage import DataChunk, repopulate_data_chunks
from data.chunking import chunk_text
from llm import llm
from template_manager import TemplateManager
from rag import RAGProcessor

def ingest_command(data_directory):
    """Handle the ingest command."""
    if not data_directory.is_dir():
        print(f"Error: Directory not found: {data_directory}")
        sys.exit(1)

    files = [f for f in data_directory.iterdir() if f.is_file() and not f.name.startswith('.')]
    
    if not files:
        print("No files found in the directory")
        return
    
    total_files = len(files)
    total_items = 0
    all_data_chunks = []
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{total_files}] Processing: {file_path.name}")
        
        try:
            processor = file_processor_factory.get_processor_for_file(str(file_path))
        except ValueError as e:
            print(f"  Skipping unsupported file type: {e}")
            continue
        
        with open(file_path, 'rb') as f:
            results = processor.process_file(f)
        
        item_count = len(results)
        total_items += item_count
        
        print(f"  ✓ Extracted {item_count} items")
        
        global_chunk_index = 0
        for item_index, item_text in enumerate(results):
            text_chunks = chunk_text(item_text, max_tokens=400, overlap_tokens=40)
            
            for chunk_index, chunk_content in enumerate(text_chunks):
                embedding = llm.generate_embedding(chunk_content)
                
                data_chunk = DataChunk(
                    filename=file_path.name,
                    chunk_index=global_chunk_index,
                    chunk_text=chunk_content,
                    embedding=embedding
                )
                all_data_chunks.append(data_chunk)
                global_chunk_index += 1
        
        if results:
            print(f"  Preview:")
            for j, item in enumerate(results[:3]):
                preview = item[:100] + '...' if len(item) > 100 else item
                print(f"    {j+1}: {preview}")
            if len(results) > 3:
                print(f"    ... and {len(results) - 3} more items")
    
    print("\n" + "=" * 50)
    print(f"SUMMARY:")
    print(f"  Total files processed: {total_files}")
    print(f"  Total items extracted: {total_items}")
    print(f"  Total data chunks created: {len(all_data_chunks)}")
    print(f"  Average items per file: {total_items / total_files:.1f}")
    print(f"  Average chunks per item: {len(all_data_chunks) / total_items:.1f}" if total_items > 0 else "  Average chunks per item: 0")
    
    if all_data_chunks:
        print(f"\nRepopulating database with {len(all_data_chunks)} data chunks...")
        repopulate_data_chunks(all_data_chunks)
        print("✓ Database successfully updated with data chunks")
    else:
        print("No data chunks to store in database")

def ask_command(prompt):
    """Handle the ask command."""
    template_manager = TemplateManager()
    rag_processor = RAGProcessor(llm, template_manager)
    
    print(f"Question: {prompt}")
    print("=" * 60)
    
    answer = rag_processor.process(prompt)
    
    print("Answer:")
    print("-" * 40)
    print(answer)
    print("=" * 60)

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <command> [args]")
        print("Commands:")
        print("  ingest <directory>  - Process files and populate database")
        print("  ask <prompt>         - Ask a question using RAG")
        sys.exit(1)

    command = sys.argv[1]
    
    if command == 'ingest':
        if len(sys.argv) < 3:
            print("Usage: python cli.py ingest <directory>")
            sys.exit(1)
        data_directory = Path(sys.argv[2])
        ingest_command(data_directory)
    
    elif command == 'ask':
        if len(sys.argv) < 3:
            print("Usage: python cli.py ask <prompt>")
            sys.exit(1)
        prompt = ' '.join(sys.argv[2:])
        ask_command(prompt)
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: ingest, ask")
        sys.exit(1)

if __name__ == '__main__':
    main()