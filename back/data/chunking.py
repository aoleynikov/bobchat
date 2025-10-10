from llm import llm

def chunk_text(text: str, max_tokens: int = 400, overlap_tokens: int = 40) -> list:
    if not text.strip():
        return []
    
    token_count = llm.count_tokens(text)
    if token_count <= max_tokens:
        return [text]
    
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for sentence in sentences:
        sentence_tokens = llm.count_tokens(sentence)
        
        if current_tokens + sentence_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk.strip())
            
            if overlap_tokens > 0:
                overlap_text = get_overlap_text(current_chunk, overlap_tokens)
                current_chunk = overlap_text + " " + sentence
                current_tokens = llm.count_tokens(current_chunk)
            else:
                current_chunk = sentence
                current_tokens = sentence_tokens
        else:
            if current_chunk:
                current_chunk += ". " + sentence
            else:
                current_chunk = sentence
            current_tokens += sentence_tokens
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def get_overlap_text(text: str, overlap_tokens: int) -> str:
    if not text.strip():
        return ""
    
    words = text.split()
    overlap_words = []
    current_tokens = 0
    
    for word in reversed(words):
        word_tokens = llm.count_tokens(word)
        if current_tokens + word_tokens > overlap_tokens:
            break
        overlap_words.insert(0, word)
        current_tokens += word_tokens
    
    return " ".join(overlap_words)
