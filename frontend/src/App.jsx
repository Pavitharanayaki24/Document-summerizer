import { useState } from "react";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");

  const askQuestion = async () => {
    if (!question) return;

    try {
      const response = await axios.post("http://127.0.0.1:8000/ask", {
        question: question,
      });

      setAnswer(response.data.answer);
    } catch (error) {
      console.error("Error:", error);
      setAnswer("Something went wrong.");
    }
  };

  const uploadFile = async () => {
    if (!file) {
      setUploadStatus("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploadStatus("Uploading...");

      await axios.post("http://127.0.0.1:8000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setUploadStatus("✅ File uploaded successfully!");
    } catch (error) {
      console.error(error);
      setUploadStatus("❌ Upload failed.");
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h2 style={styles.title}>Document Summarizer</h2>

        
        <div style={styles.uploadSection}>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <button onClick={uploadFile} style={styles.uploadButton}>
            Upload PDF
          </button>

          <p style={styles.status}>{uploadStatus}</p>
        </div>

       
        <div style={styles.inputSection}>
          <input
            type="text"
            placeholder="Ask your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            style={styles.input}
          />

          <button onClick={askQuestion} style={styles.button}>
            Ask
          </button>
        </div>

        
        <div style={styles.answerBox}>
          <strong>Answer:</strong>
          <p>{answer}</p>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#e4e7eb",
    fontFamily: "Arial, sans-serif",
  },
  card: {
    backgroundColor: "#61dac1",
    padding: "40px",
    borderRadius: "12px",
    boxShadow: "0 8px 20px rgba(0,0,0,0.1)",
    width: "500px",
    textAlign: "center",
  },
  title: {
    marginBottom: "20px",
  },
  uploadSection: {
    marginBottom: "20px",
  },
  uploadButton: {
    marginLeft: "10px",
    padding: "8px 12px",
    borderRadius: "6px",
    border: "none",
    backgroundColor: "#28a745",
    color: "white",
    cursor: "pointer",
  },
  status: {
    marginTop: "8px",
    fontSize: "14px",
  },
  inputSection: {
    display: "flex",
    justifyContent: "center",
    gap: "10px",
    marginBottom: "20px",
  },
  input: {
    flex: 1,
    padding: "10px",
    borderRadius: "6px",
    border: "1px solid #ccc",
  },
  button: {
    padding: "10px 16px",
    borderRadius: "6px",
    border: "none",
    backgroundColor: "#4670e5",
    color: "white",
    cursor: "pointer",
  },
  answerBox: {
    marginTop: "10px",
    textAlign: "left",
    backgroundColor: "#f9fafb",
    padding: "15px",
    borderRadius: "8px",
    minHeight: "80px",
  },
};

export default App;