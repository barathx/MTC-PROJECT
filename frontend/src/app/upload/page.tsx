"use client";
import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import { uploadDocument } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");

  const allowedTypes = [
    "application/pdf",
    "image/png", "image/jpg", "image/jpeg", "image/tiff",
  ];
  const allowedExtensions = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"];

  const validateFile = (f: File): boolean => {
    const ext = "." + f.name.split(".").pop()?.toLowerCase();
    if (!allowedExtensions.includes(ext)) {
      setError(`Unsupported file type: ${ext}. Allowed: ${allowedExtensions.join(", ")}`);
      return false;
    }
    if (f.size > 50 * 1024 * 1024) {
      setError("File too large. Maximum size: 50MB");
      return false;
    }
    setError("");
    return true;
  };

  const handleFile = (f: File) => {
    if (validateFile(f)) setFile(f);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) handleFile(dropped);
  }, []);

  const handleUpload = async () => {
    if (!file) return;
    const token = localStorage.getItem("token");
    if (!token) { router.push("/"); return; }

    setUploading(true);
    setProgress(10);

    // Simulate progress while processing
    const progressInterval = setInterval(() => {
      setProgress((p) => Math.min(p + 8, 85));
    }, 500);

    try {
      const result = await uploadDocument(file, token);
      clearInterval(progressInterval);
      setProgress(100);

      // Navigate to results page
      setTimeout(() => {
        router.push(`/results/${result.document.id}`);
      }, 500);
    } catch (err: any) {
      clearInterval(progressInterval);
      setError(err.message || "Upload failed");
      setUploading(false);
      setProgress(0);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <div style={{ minHeight: "100vh" }}>
      <Navbar />
      <main style={{ maxWidth: 800, margin: "0 auto", padding: "40px 24px" }}>
        <div className="animate-fade-in-up" style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 800, marginBottom: 8 }}>
            Upload MTC Document
          </h1>
          <p style={{ color: "var(--text-secondary)" }}>
            Upload a Material Test Certificate for AI-powered extraction and validation
          </p>
        </div>

        {/* Upload Zone */}
        <div className="glass-card animate-fade-in-up" style={{ padding: 32, animationDelay: "0.1s" }}>
          {!file ? (
            <div
              className={`upload-zone ${dragging ? "dragging" : ""}`}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
            >
              <div style={{ fontSize: 56, marginBottom: 16 }}>
                {dragging ? "📥" : "📄"}
              </div>
              <h3 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: 8 }}>
                {dragging ? "Drop your file here" : "Drag & drop your MTC document"}
              </h3>
              <p style={{ color: "var(--text-secondary)", marginBottom: 20 }}>
                or click to browse files
              </p>
              <div style={{
                display: "inline-flex", gap: 8, flexWrap: "wrap", justifyContent: "center"
              }}>
                {["PDF", "PNG", "JPG", "JPEG", "TIFF"].map((ext) => (
                  <span key={ext} style={{
                    padding: "4px 12px", borderRadius: 8,
                    background: "var(--bg-secondary)", border: "1px solid var(--border-color)",
                    fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)",
                    letterSpacing: "0.5px"
                  }}>
                    .{ext}
                  </span>
                ))}
              </div>
              <p style={{ color: "var(--text-muted)", fontSize: "0.8rem", marginTop: 12 }}>
                Maximum file size: 50MB
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.png,.jpg,.jpeg,.tiff,.tif"
                onChange={(e) => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }}
                style={{ display: "none" }}
              />
            </div>
          ) : (
            <div>
              {/* File Preview */}
              <div style={{
                display: "flex", alignItems: "center", gap: 16,
                padding: 20, borderRadius: 14,
                background: "var(--bg-secondary)", border: "1px solid var(--border-color)",
                marginBottom: 24,
              }}>
                <div style={{
                  width: 52, height: 52, borderRadius: 12,
                  background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 24, flexShrink: 0,
                }}>
                  {file.type === "application/pdf" ? "📕" : "🖼️"}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontWeight: 700, marginBottom: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {file.name}
                  </p>
                  <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                    {formatSize(file.size)} • {file.type || "Unknown type"}
                  </p>
                </div>
                {!uploading && (
                  <button
                    onClick={() => { setFile(null); setError(""); }}
                    style={{
                      background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
                      borderRadius: 10, padding: "8px 16px", color: "#f87171",
                      cursor: "pointer", fontWeight: 600, fontSize: "0.82rem",
                    }}
                  >
                    Remove
                  </button>
                )}
              </div>

              {/* Progress Bar */}
              {uploading && (
                <div style={{ marginBottom: 24 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                    <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)" }}>
                      {progress < 30 ? "Uploading document..." :
                       progress < 60 ? "Running OCR extraction..." :
                       progress < 85 ? "Validating against standards..." :
                       "Finalizing results..."}
                    </span>
                    <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--accent-blue)" }}>
                      {progress}%
                    </span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${progress}%` }} />
                  </div>
                </div>
              )}

              {/* Upload Button */}
              {!uploading && (
                <button
                  onClick={handleUpload}
                  className="btn-primary"
                  style={{ width: "100%", padding: "16px", fontSize: "1rem" }}
                >
                  🚀 Start AI Verification
                </button>
              )}

              {uploading && progress < 100 && (
                <div style={{ display: "flex", justifyContent: "center", padding: 10 }}>
                  <div className="spinner" />
                </div>
              )}
            </div>
          )}

          {error && (
            <div style={{
              background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
              borderRadius: 10, padding: "12px 16px", marginTop: 20,
              color: "#f87171", fontSize: "0.85rem"
            }}>
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Info Section */}
        <div className="animate-fade-in-up" style={{ animationDelay: "0.2s", marginTop: 32 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
            {[
              { icon: "🔍", title: "OCR Extraction", desc: "Advanced text recognition from PDFs and images" },
              { icon: "⚗️", title: "AI Analysis", desc: "Structured extraction of chemical & mechanical data" },
              { icon: "✅", title: "Validation", desc: "Automated compliance check against ASTM/ASME standards" },
              { icon: "📊", title: "Reporting", desc: "Detailed pass/fail results with audit trail" },
            ].map((item) => (
              <div key={item.title} className="glass-card" style={{ padding: "20px 18px", textAlign: "center" }}>
                <div style={{ fontSize: 28, marginBottom: 8 }}>{item.icon}</div>
                <h4 style={{ fontWeight: 700, fontSize: "0.9rem", marginBottom: 4 }}>{item.title}</h4>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
