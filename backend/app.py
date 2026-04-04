from flask import Flask, request, jsonify
from flask_cors import CORS
from Fetching.query import ask_question

import os
from Fetching.query import ask_question
from Fetching.gather import load_document, chunk_documents, create_embeddings
from langchain_community.vectorstores import FAISS


app = Flask(__name__)
CORS(app) 

VECTOR_STORE_PATH = "Fetching/vector_store"

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
        filename = file.filename
        temp_path = f"temp_{filename}"
        file.save(temp_path)

        documents = load_document(temp_path)
        chunks = chunk_documents(documents)
        embeddings = create_embeddings()

        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(VECTOR_STORE_PATH)

        os.remove(temp_path)

        return jsonify({"message": "Document uploaded successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



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