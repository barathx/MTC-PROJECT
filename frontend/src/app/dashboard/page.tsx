"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import { getDocumentHistory } from "@/lib/api";

interface DocumentItem {
  id: number;
  original_filename: string;
  file_type: string;
  status: string;
  uploaded_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const stored = localStorage.getItem("user");
    if (!token) { router.push("/"); return; }
    if (stored) setUser(JSON.parse(stored));

    getDocumentHistory(token)
      .then(setDocuments)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const statusBadge = (status: string) => {
    const map: Record<string, string> = {
      completed: "badge-pass",
      processing: "badge-pending",
      failed: "badge-fail",
      uploaded: "badge-warning",
    };
    return map[status] || "badge-na";
  };

  const completedDocs = documents.filter(d => d.status === "completed").length;
  const failedDocs = documents.filter(d => d.status === "failed").length;

  return (
    <div style={{ minHeight: "100vh" }}>
      <Navbar />
      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "32px 24px" }}>
        {/* Welcome Header */}
        <div className="animate-fade-in-up" style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: "1.8rem", fontWeight: 800, marginBottom: 6 }}>
            Welcome back, <span style={{ color: "var(--accent-blue)" }}>{user?.full_name || user?.username || "Engineer"}</span>
          </h1>
          <p style={{ color: "var(--text-secondary)" }}>Material Test Certificate verification dashboard</p>
        </div>

        {/* Stats Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 36 }}
             className="animate-fade-in-up" >
          <div className="glass-card stat-card">
            <span className="stat-value">{documents.length}</span>
            <span className="stat-label">Total Documents</span>
          </div>
          <div className="glass-card stat-card">
            <span className="stat-value" style={{ background: "linear-gradient(135deg, #10b981, #34d399)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              {completedDocs}
            </span>
            <span className="stat-label">Completed</span>
          </div>
          <div className="glass-card stat-card">
            <span className="stat-value" style={{ background: "linear-gradient(135deg, #ef4444, #f87171)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              {failedDocs}
            </span>
            <span className="stat-label">Failed</span>
          </div>
          <div className="glass-card stat-card" style={{ cursor: "pointer" }} onClick={() => router.push("/upload")}>
            <span style={{ fontSize: "2rem" }}>📄</span>
            <span className="stat-label" style={{ color: "var(--accent-blue)", fontWeight: 700 }}>Upload New MTC ↗</span>
          </div>
        </div>

        {/* Documents Table */}
        <div className="glass-card animate-fade-in-up" style={{ animationDelay: "0.2s", overflow: "hidden" }}>
          <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--border-color)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2 style={{ fontSize: "1.1rem", fontWeight: 700 }}>Recent Verifications</h2>
            <button className="btn-primary" onClick={() => router.push("/upload")} style={{ padding: "8px 20px", fontSize: "0.82rem" }}>
              + Upload MTC
            </button>
          </div>

          {loading ? (
            <div style={{ display: "flex", justifyContent: "center", padding: 60 }}>
              <div className="spinner" />
            </div>
          ) : documents.length === 0 ? (
            <div style={{ textAlign: "center", padding: "60px 20px" }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>📋</div>
              <p style={{ color: "var(--text-secondary)", marginBottom: 20 }}>No documents uploaded yet</p>
              <button className="btn-primary" onClick={() => router.push("/upload")}>
                Upload Your First MTC
              </button>
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id}>
                    <td style={{ fontWeight: 600 }}>{doc.original_filename}</td>
                    <td><span style={{ color: "var(--text-secondary)", textTransform: "uppercase", fontSize: "0.8rem", fontWeight: 700 }}>{doc.file_type}</span></td>
                    <td><span className={`badge ${statusBadge(doc.status)}`}>{doc.status}</span></td>
                    <td style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                      {new Date(doc.uploaded_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" })}
                    </td>
                    <td>
                      {doc.status === "completed" && (
                        <button
                          className="btn-secondary"
                          style={{ padding: "6px 14px", fontSize: "0.78rem" }}
                          onClick={() => router.push(`/results/${doc.id}`)}
                        >
                          View Results
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  );
}
