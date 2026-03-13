"use client";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const stored = localStorage.getItem("user");
    if (stored) setUser(JSON.parse(stored));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/");
  };

  const navItems = [
    { label: "Dashboard", path: "/dashboard", icon: "📊" },
    { label: "Upload", path: "/upload", icon: "📄" },
  ];

  return (
    <nav style={{
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "16px 32px",
      background: "var(--glass-bg)",
      backdropFilter: "blur(20px)",
      borderBottom: "1px solid var(--glass-border)",
      position: "sticky", top: 0, zIndex: 50,
    }}>
      {/* Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, cursor: "pointer" }} onClick={() => router.push("/dashboard")}>
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 18
        }}>
          ⚗️
        </div>
        <span style={{ fontWeight: 800, fontSize: "1.1rem", letterSpacing: "-0.3px" }}>
          MTC<span style={{ color: "var(--accent-blue)" }}>Verify</span>
        </span>
      </div>

      {/* Nav Links */}
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        {navItems.map((item) => {
          const isActive = pathname === item.path;
          return (
            <button
              key={item.path}
              onClick={() => router.push(item.path)}
              style={{
                display: "flex", alignItems: "center", gap: 8,
                padding: "8px 18px", borderRadius: 10,
                border: "none", cursor: "pointer",
                fontWeight: 600, fontSize: "0.88rem",
                transition: "all 0.2s ease",
                background: isActive ? "rgba(59,130,246,0.15)" : "transparent",
                color: isActive ? "var(--accent-blue)" : "var(--text-secondary)",
              }}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          );
        })}
      </div>

      {/* User Menu */}
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        {user && (
          <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            👤 {user.full_name || user.username}
          </span>
        )}
        <button onClick={handleLogout} className="btn-secondary" style={{ padding: "8px 18px", fontSize: "0.82rem" }}>
          Logout
        </button>
      </div>
    </nav>
  );
}
