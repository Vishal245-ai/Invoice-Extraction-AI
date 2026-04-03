import { useState } from "react";
import { uploadInvoices } from "../services/api";

export default function Upload({ refresh }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  // ----------------------------
  // FILE VALIDATION
  // ----------------------------
  const validateFiles = (fileList) => {
    const validTypes = ["application/pdf", "image/png", "image/jpeg"];
    const maxSize = 5 * 1024 * 1024; // 5MB

    return Array.from(fileList).filter((file) => {
      if (!validTypes.includes(file.type)) {
        alert(`${file.name} is not a valid file type`);
        return false;
      }
      if (file.size > maxSize) {
        alert(`${file.name} exceeds 5MB`);
        return false;
      }
      return true;
    });
  };

  // ----------------------------
  // HANDLE UPLOAD
  // ----------------------------
  const handleUpload = async () => {
    if (!files.length) return;

    try {
      setLoading(true);

      const data = await uploadInvoices(files);

      alert(`Processed ${data?.total_files ?? files.length} file(s)`);

      await refresh?.();
      setFiles([]);

    } catch (err) {
      console.error("Upload error:", err);
      alert(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  // ----------------------------
  // FILE INPUT
  // ----------------------------
  const handleChange = (e) => {
    const validated = validateFiles(e.target.files || []);
    setFiles(validated);
  };

  // ----------------------------
  // DRAG & DROP
  // ----------------------------
  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);

    const validated = validateFiles(e.dataTransfer.files || []);
    setFiles(validated);
  };

  // ----------------------------
  // REMOVE FILE
  // ----------------------------
  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // ----------------------------
  // CLEAR ALL
  // ----------------------------
  const clearAll = () => setFiles([]);

  return (
    <div style={{ marginBottom: "25px" }}>

      {/* Drag Area */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        style={{
          border: "2px dashed",
          borderColor: dragActive ? "#2563eb" : "#555",
          background: dragActive ? "#f0f6ff" : "transparent",
          padding: "24px",
          textAlign: "center",
          borderRadius: "12px",
          marginBottom: "12px",
          cursor: "pointer",
        }}
      >
        📂 Drag & Drop Invoices or Click Below
      </div>

      {/* File Input */}
      <input
        type="file"
        multiple
        onChange={handleChange}
        accept=".pdf,.png,.jpg,.jpeg"
      />

      {/* File List */}
      {files.length > 0 && (
        <div style={{ marginTop: "12px" }}>
          <ul style={{ textAlign: "left" }}>
            {files.map((f, i) => (
              <li key={f.name + f.size}>
                {f.name} ({(f.size / 1024).toFixed(1)} KB)
                <button
                  onClick={() => removeFile(i)}
                  style={{
                    marginLeft: "10px",
                    color: "red",
                    border: "none",
                    cursor: "pointer",
                    background: "none",
                  }}
                >
                  ❌
                </button>
              </li>
            ))}
          </ul>

          <button onClick={clearAll} style={{ marginTop: "8px" }}>
            Clear All
          </button>
        </div>
      )}

      {/* Upload Button */}
      <button
        onClick={handleUpload}
        disabled={loading || files.length === 0}
        style={{
          marginTop: "12px",
          padding: "10px 14px",
          borderRadius: "8px",
          border: "none",
          background: loading || files.length === 0 ? "#999" : "#2563eb",
          color: "white",
          cursor: loading || files.length === 0 ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "Processing..." : `Upload ${files.length} file(s)`}
      </button>
    </div>
  );
}