"use client";
import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import { getResults, getAuditTrail } from "@/lib/api";

interface FieldResult {
  value: number | null;
  min: number | null;
  max: number | null;
  status: string;
  unit: string;
}

export default function ResultsPage() {
  const router = useRouter();
  const params = useParams();
  const documentId = Number(params.id);

  const [data, setData] = useState<any>(null);
  const [audit, setAudit] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"chemical" | "mechanical" | "audit">("chemical");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/"); return; }

    Promise.all([
      getResults(documentId, token),
      getAuditTrail(documentId, token).catch(() => []),
    ])
      .then(([results, auditData]) => {
        setData(results);
        setAudit(auditData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [documentId, router]);

  const getBadgeClass = (status: string) => {
    const map: Record<string, string> = {
      PASS: "badge-pass",
      FAIL: "badge-fail",
      WARNING: "badge-warning",
      "N/A": "badge-na",
      "NOT FOUND": "badge-na",
      PENDING: "badge-pending",
    };
    return map[status] || "badge-na";
  };

  const renderTable = (results: Record<string, FieldResult> | null, title: string) => {
    if (!results || Object.keys(results).length === 0) {
      return (
        <div style={{ textAlign: "center", padding: 40, color: "var(--text-secondary)" }}>
          No {title.toLowerCase()} data available
        </div>
      );
    }

    return (
      <table className="data-table">
        <thead>
          <tr>
            <th>Property</th>
            <th>Extracted Value</th>
            <th>Min Limit</th>
            <th>Max Limit</th>
            <th>Unit</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(results).map(([key, field]) => (
            <tr key={key}>
              <td style={{ fontWeight: 600 }}>{key}</td>
              <td style={{
                fontWeight: 700, fontFamily: "monospace", fontSize: "0.95rem",
                color: field.status === "FAIL" ? "#f87171" : field.status === "PASS" ? "#34d399" : "var(--text-primary)"
              }}>
                {field.value !== null && field.value !== undefined ? field.value : "—"}
              </td>
              <td style={{ color: "var(--text-secondary)", fontFamily: "monospace" }}>
                {field.min !== null && field.min !== undefined ? field.min : "—"}
              </td>
              <td style={{ color: "var(--text-secondary)", fontFamily: "monospace" }}>
                {field.max !== null && field.max !== undefined ? field.max : "—"}
              </td>
              <td style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                {field.unit || "—"}
              </td>
              <td>
                <span className={`badge ${getBadgeClass(field.status)}`}>
                  {field.status === "PASS" ? "✓ " : field.status === "FAIL" ? "✗ " : ""}{field.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  if (loading) {
    return (
      <div style={{ minHeight: "100vh" }}>
        <Navbar />
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh" }}>
          <div style={{ textAlign: "center" }}>
            <div className="spinner" style={{ margin: "0 auto 16px" }} />
            <p style={{ color: "var(--text-secondary)" }}>Loading verification results...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ minHeight: "100vh" }}>
        <Navbar />
        <div style={{ maxWidth: 600, margin: "60px auto", textAlign: "center" }}>
          <div className="glass-card" style={{ padding: 40 }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
            <h2 style={{ marginBottom: 8 }}>Error Loading Results</h2>
            <p style={{ color: "#f87171", marginBottom: 20 }}>{error}</p>
            <button className="btn-primary" onClick={() => router.push("/dashboard")}>
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  const validation = data?.validation;
  const extracted = data?.extracted_data;
  const doc = data?.document;

  return (
    <div style={{ minHeight: "100vh" }}>
      <Navbar />
      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "32px 24px" }}>
        {/* Header */}
        <div className="animate-fade-in-up" style={{ marginBottom: 32 }}>
          <button
            onClick={() => router.push("/dashboard")}
            style={{
              background: "none", border: "none", color: "var(--text-secondary)",
              cursor: "pointer", fontSize: "0.85rem", fontWeight: 600, marginBottom: 12,
              display: "flex", alignItems: "center", gap: 6,
            }}
          >
            ← Back to Dashboard
          </button>
          <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
            <h1 style={{ fontSize: "1.6rem", fontWeight: 800 }}>Verification Results</h1>
            {validation && (
              <span className={`badge ${getBadgeClass(validation.overall_status)}`} style={{ fontSize: "0.9rem", padding: "8px 20px" }}>
                {validation.overall_status === "PASS" ? "✓ COMPLIANT" :
                 validation.overall_status === "FAIL" ? "✗ NON-COMPLIANT" :
                 validation.overall_status}
              </span>
            )}
          </div>
        </div>

        {/* Top Info Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 16, marginBottom: 28 }}
             className="animate-fade-in-up">
          {/* Document Info */}
          <div className="glass-card" style={{ padding: 20 }}>
            <h3 style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--text-secondary)", marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.5px" }}>
              Document Info
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: "0.9rem" }}>
              <div><span style={{ color: "var(--text-muted)" }}>File:</span> <span style={{ fontWeight: 600 }}>{doc?.original_filename}</span></div>
              <div><span style={{ color: "var(--text-muted)" }}>Type:</span> <span style={{ fontWeight: 600, textTransform: "uppercase" }}>{doc?.file_type}</span></div>
              <div><span style={{ color: "var(--text-muted)" }}>Uploaded:</span> <span style={{ fontWeight: 600 }}>{doc?.uploaded_at ? new Date(doc.uploaded_at).toLocaleString() : "—"}</span></div>
            </div>
          </div>

          {/* Material Info */}
          <div className="glass-card" style={{ padding: 20 }}>
            <h3 style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--text-secondary)", marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.5px" }}>
              Material Identification
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: "0.9rem" }}>
              <div><span style={{ color: "var(--text-muted)" }}>Heat No:</span> <span style={{ fontWeight: 600 }}>{extracted?.material_identification?.heat_number || "—"}</span></div>
              <div><span style={{ color: "var(--text-muted)" }}>Batch No:</span> <span style={{ fontWeight: 600 }}>{extracted?.material_identification?.batch_number || "—"}</span></div>
              <div><span style={{ color: "var(--text-muted)" }}>Grade:</span> <span style={{ fontWeight: 600 }}>{extracted?.material_identification?.material_grade || "—"}</span></div>
              <div><span style={{ color: "var(--text-muted)" }}>Spec:</span> <span style={{ fontWeight: 600 }}>{extracted?.material_identification?.specification || "—"}</span></div>
            </div>
          </div>

          {/* Validation Summary */}
          <div className="glass-card" style={{ padding: 20 }}>
            <h3 style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--text-secondary)", marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.5px" }}>
              Validation Summary
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: "0.9rem" }}>
              <div><span style={{ color: "var(--text-muted)" }}>Standard:</span> <span style={{ fontWeight: 600 }}>{validation?.standard_used || "—"}</span></div>
              <div style={{ display: "flex", gap: 16, marginTop: 4 }}>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "#34d399" }}>{validation?.passed_checks ?? 0}</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Passed</div>
                </div>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "#f87171" }}>{validation?.failed_checks ?? 0}</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Failed</div>
                </div>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "#fbbf24" }}>{validation?.warning_checks ?? 0}</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Warnings</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="glass-card animate-fade-in-up" style={{ animationDelay: "0.2s", overflow: "hidden" }}>
          <div style={{ display: "flex", borderBottom: "1px solid var(--border-color)", padding: "0 8px" }}>
            {([
              { key: "chemical" as const, label: "Chemical Composition", icon: "⚗️" },
              { key: "mechanical" as const, label: "Mechanical Properties", icon: "🔧" },
              { key: "audit" as const, label: "Audit Trail", icon: "📋" },
            ]).map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                style={{
                  padding: "16px 20px",
                  border: "none", borderBottom: activeTab === tab.key ? "2px solid var(--accent-blue)" : "2px solid transparent",
                  background: "none",
                  color: activeTab === tab.key ? "var(--accent-blue)" : "var(--text-secondary)",
                  fontWeight: 700, fontSize: "0.9rem",
                  cursor: "pointer", transition: "all 0.2s",
                  display: "flex", alignItems: "center", gap: 8,
                }}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          <div style={{ padding: 4 }}>
            {activeTab === "chemical" && renderTable(validation?.chemical_results, "Chemical Composition")}
            {activeTab === "mechanical" && renderTable(validation?.mechanical_results, "Mechanical Properties")}
            {activeTab === "audit" && (
              <div style={{ padding: "8px 14px" }}>
                {audit.length === 0 ? (
                  <div style={{ textAlign: "center", padding: 40, color: "var(--text-secondary)" }}>
                    No audit records available
                  </div>
                ) : (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Action</th>
                        <th>Details</th>
                        <th>Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {audit.map((log) => (
                        <tr key={log.id}>
                          <td>
                            <span className={`badge ${
                              log.action === "upload" ? "badge-pending" :
                              log.action === "validate" ? "badge-pass" :
                              log.action === "extract" ? "badge-warning" : "badge-na"
                            }`}>
                              {log.action}
                            </span>
                          </td>
                          <td style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                            {log.details ? JSON.stringify(log.details) : "—"}
                          </td>
                          <td style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                            {new Date(log.timestamp).toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
