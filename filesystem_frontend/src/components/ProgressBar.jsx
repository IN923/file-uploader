import React from "react";

const ProgressBar = ({
  file_unique_name,
  progress,
  uploaded,
  total,
  progress_status,
  name
}) => {
  const done = progress_status == "COMPLETED";
  const error = progress_status == "FAILED";

  return (
    <div
      style={{
        maxWidth: "500px",
        margin: "0 auto 10px auto",
        padding: "10px 12px",
        border: "1px solid #eef2f6",
        borderRadius: "12px",
        background: "#fff",
        boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
      }}
    >
      {/* TOP ROW */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "10px",
        }}
      >
        {/* FILE INFO */}
        <div style={{ minWidth: 0, flex: 1 }}>
          <div
            style={{
              fontSize: "13px",
              fontWeight: 600,
              color: "#111827",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {name}
          </div>

          <div
            style={{
              fontSize: "11px",
              color: "#6b7280",
              marginTop: "2px",
            }}
          >
            {uploaded} / {total} bytes
          </div>
        </div>

        {/* STATUS */}
        <div style={{ fontSize: "12px", fontWeight: 600 }}>
          {done && <span style={{ color: "#16a34a" }}>✔ Done</span>}
          {error && <span style={{ color: "#dc2626" }}>✖ Failed</span>}
          {!done && !error && (
            <span style={{ color: "#374151" }}>{progress}%</span>
          )}
        </div>
      </div>

      {/* PROGRESS BAR */}
      <div
        style={{
          marginTop: "8px",
          height: "6px",
          width: "100%",
          background: "#e5e7eb",
          borderRadius: "999px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${progress}%`,
            background: error
              ? "#ef4444"
              : done
              ? "#22c55e"
              : "linear-gradient(90deg, #3b82f6, #6366f1)",
            transition: "width 0.25s ease",
          }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;