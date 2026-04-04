from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

import os
from Fetching.query import ask_question
from Fetching.gather import load_document, chunk_documents, create_embeddings
from langchain_community.vectorstores import FAISS


app = Flask(__name__)
CORS(app)

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_STORE_PATH = os.path.join(BACKEND_DIR, "Fetching", "vector_store")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask backend is running"})


@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty file"}), 400

    try:
        safe_name = secure_filename(file.filename)
        if not safe_name:
            return jsonify({"error": "Invalid filename"}), 400
        temp_path = os.path.join(BACKEND_DIR, f"temp_{safe_name}")
        file.save(temp_path)

        ext = os.path.splitext(safe_name)[1].lower()
        documents = load_document(temp_path)
        has_text = any((doc.page_content or "").strip() for doc in documents)
        if not has_text:
            if ext == ".pdf":
                return jsonify(
                    {
                        "error": (
                            "This PDF has no extractable text. It may be scanned or image-only. "
                            "Try a text-based PDF or add OCR support."
                        )
                    }
                ), 400
            return jsonify({"error": "This file has no extractable text."}), 400

        chunks = chunk_documents(documents)
        if not chunks:
            return jsonify({"error": "Could not extract any searchable text from the file."}), 400
        embeddings = create_embeddings()

        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(VECTOR_STORE_PATH)

        return jsonify({"message": "Document uploaded successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if "temp_path" in locals() and os.path.exists(temp_path):
            os.remove(temp_path)



@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({"error": "Question is required"}), 400

    question = data["question"]

    try:
        answer = ask_question(question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error":str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True, port=8000)
