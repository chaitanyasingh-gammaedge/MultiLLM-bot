import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from vectorstore import VectorStore
from PyPDF2 import PdfReader
from docx import Document

rag_bp = Blueprint("rag", __name__)

# global cached vectorstore
_vs = None

def get_vs():
    """Return cached or new VectorStore instance."""
    global _vs
    cfg = current_app.config
    if _vs is None:
        _vs = VectorStore(cfg["EMBEDDING_MODEL"], cfg["FAISS_INDEX_PATH"], cfg["DOC_STORE_PATH"])
    return _vs


@rag_bp.route("/add", methods=["POST"])
def add_docs():
    """Add text documents via JSON."""
    data = request.get_json(force=True)
    docs = data.get("docs", [])
    if not docs:
        return jsonify({"error": "no docs"}), 400

    vs = get_vs()
    tuples = [(d["id"], d["text"], d.get("meta", {})) for d in docs]
    vs.add_documents(tuples)
    return jsonify({"status": "ok", "count": len(docs)})


@rag_bp.route("/query", methods=["POST"])
def query_docs():
    """Query FAISS index for relevant chunks."""
    data = request.get_json(force=True)
    q = data.get("query", "")
    k = int(data.get("top_k", 3))

    vs = get_vs()
    results = vs.query(q, top_k=k)
    return jsonify(results)


@rag_bp.route("/upload", methods=["POST"])
def upload_docs():
    """Upload and index a .txt, .pdf, or .docx document file."""
    if "file" not in request.files:
        return jsonify({"error": "no file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "empty filename"}), 400

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()

    # extract text
    try:
        if ext == ".txt":
            text = file.read().decode("utf-8", errors="ignore")
        elif ext == ".pdf":
            pdf = PdfReader(file)
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        elif ext == ".docx":
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            return jsonify({"error": "unsupported file type"}), 400
    except Exception as e:
        return jsonify({"error": f"failed to read file: {e}"}), 500

    # split into smaller chunks
    step = 500
    chunks = []
    for i in range(0, len(text), step):
        chunk_text = text[i:i + step].strip()
        if chunk_text:
            chunks.append((i, chunk_text, {"src": filename}))

    if not chunks:
        return jsonify({"error": "no text extracted"}), 400

    vs = get_vs()
    vs.add_documents(chunks)
    return jsonify({"status": "ok", "file": filename, "count": len(chunks)})


@rag_bp.route("/remove", methods=["POST"])
def remove_doc():
    """Remove specific document by filename from FAISS + doc store."""
    global _vs
    data = request.get_json(force=True)
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "filename required"}), 400

    cfg = current_app.config
    index_path = cfg["FAISS_INDEX_PATH"]
    doc_store_path = cfg["DOC_STORE_PATH"]

    # Rebuild store excluding that document
    if not os.path.exists(doc_store_path):
        return jsonify({"error": "no documents found"}), 404

    import pickle
    import faiss

    with open(doc_store_path, "rb") as f:
        doc_store = pickle.load(f)

    # Filter docs
    new_docs = {k: v for k, v in doc_store.items() if v["meta"].get("src") != filename}
    removed_count = len(doc_store) - len(new_docs)

    if removed_count == 0:
        return jsonify({"message": f"No entries found for {filename}"}), 404

    # Rebuild FAISS index
    model = get_vs().model
    texts = [v["text"] for v in new_docs.values()]
    ids = list(new_docs.keys())
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexIDMap(faiss.IndexFlatIP(dim))
    index.add_with_ids(embeddings, np.array(ids, dtype="int64"))
    faiss.write_index(index, index_path)

    # Save new doc store
    with open(doc_store_path, "wb") as f:
        pickle.dump(new_docs, f)

    # Reset memory cache
    _vs = None
    return jsonify({"status": "ok", "removed": removed_count, "filename": filename})


@rag_bp.route("/clear", methods=["POST"])
def clear_docs():
    """Completely clear FAISS index and doc store (both memory + disk)."""
    global _vs
    cfg = current_app.config
    index_path = cfg["FAISS_INDEX_PATH"]
    doc_store_path = cfg["DOC_STORE_PATH"]

    try:
        if os.path.exists(index_path):
            os.remove(index_path)
        if os.path.exists(doc_store_path):
            os.remove(doc_store_path)

        # Clear memory
        _vs = None
        return jsonify({"status": "ok", "message": "All documents cleared from memory and disk."})
    except Exception as e:
        return jsonify({"error": f"Failed to clear documents: {e}"}), 500
