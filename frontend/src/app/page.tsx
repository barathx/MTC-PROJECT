"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { loginUser, registerUser } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    fullName: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      let data;
      if (isRegister) {
        data = await registerUser(form.username, form.email, form.password, form.fullName);
      } else {
        data = await loginUser(form.username, form.password);
      }

      // Store token and user info
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));

      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "20px" }}>
      <div style={{ width: "100%", maxWidth: 460 }}>
        {/* Logo / Brand */}
        <div style={{ textAlign: "center", marginBottom: 40 }} className="animate-fade-in-up">
          <div style={{
            width: 72, height: 72, borderRadius: 18,
            background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 20px", fontSize: 32, fontWeight: 900,
            boxShadow: "0 8px 30px rgba(59,130,246,0.3)"
          }}>
            ⚗️
          </div>
          <h1 style={{ fontSize: "1.8rem", fontWeight: 800, marginBottom: 8, letterSpacing: "-0.5px" }}>
            MTC Verification
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
            AI-Powered Material Test Certificate Analysis
          </p>
        </div>

        {/* Auth Card */}
        <div className="glass-card animate-fade-in-up" style={{ padding: "36px 32px", animationDelay: "0.1s" }}>
          {/* Tab Toggle */}
          <div style={{
            display: "flex", background: "var(--bg-secondary)", borderRadius: 12,
            padding: 4, marginBottom: 28, gap: 4
          }}>
            <button
              onClick={() => { setIsRegister(false); setError(""); }}
              style={{
                flex: 1, padding: "10px 0", borderRadius: 10, border: "none",
                fontWeight: 600, fontSize: "0.9rem", cursor: "pointer",
                transition: "all 0.3s ease",
                background: !isRegister ? "linear-gradient(135deg, #3b82f6, #8b5cf6)" : "transparent",
                color: !isRegister ? "white" : "var(--text-secondary)",
              }}
            >
              Sign In
            </button>
            <button
              onClick={() => { setIsRegister(true); setError(""); }}
              style={{
                flex: 1, padding: "10px 0", borderRadius: 10, border: "none",
                fontWeight: 600, fontSize: "0.9rem", cursor: "pointer",
                transition: "all 0.3s ease",
                background: isRegister ? "linear-gradient(135deg, #3b82f6, #8b5cf6)" : "transparent",
                color: isRegister ? "white" : "var(--text-secondary)",
              }}
            >
              Register
            </button>
          </div>

          {error && (
            <div style={{
              background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
              borderRadius: 10, padding: "12px 16px", marginBottom: 20,
              color: "#f87171", fontSize: "0.85rem"
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6 }}>
                Username
              </label>
              <input
                className="input-field"
                type="text"
                placeholder="Enter username"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                required
              />
            </div>

            {isRegister && (
              <>
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6 }}>
                    Email
                  </label>
                  <input
                    className="input-field"
                    type="email"
                    placeholder="Enter email"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6 }}>
                    Full Name
                  </label>
                  <input
                    className="input-field"
                    type="text"
                    placeholder="Enter full name (optional)"
                    value={form.fullName}
                    onChange={(e) => setForm({ ...form, fullName: e.target.value })}
                  />
                </div>
              </>
            )}

            <div>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6 }}>
                Password
              </label>
              <input
                className="input-field"
                type="password"
                placeholder="Enter password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: 8, width: "100%" }}>
              {loading ? (
                <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
                  <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
                  Processing...
                </span>
              ) : isRegister ? "Create Account" : "Sign In"}
            </button>
          </form>
        </div>

        <p style={{ textAlign: "center", marginTop: 24, color: "var(--text-muted)", fontSize: "0.8rem" }}>
          Secure material compliance verification platform
        </p>
      </div>
    </div>
  );
}
