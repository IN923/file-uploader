import React from "react";

function formatBytes(bytes) {
  if (!bytes) return "0 B";

  const units = [
    "B",
    "KB",
    "MB",
    "GB",
    "TB",
  ];

  const index = Math.floor(
    Math.log(bytes) / Math.log(1024)
  );

  return `${(
    bytes / Math.pow(1024, index)
  ).toFixed(2)} ${units[index]}`;
}

export default function ProgressBar({
  progress,
  uploadedBytes,
  totalBytes,
  status,
}) {
  return (
    <div className="mt-4">
      <div className="d-flex justify-content-between">
        <span>{status}</span>
        <span>{progress}%</span>
      </div>

      <div
        className="progress"
        style={{ height: "25px" }}
      >
        <div
          className={`progress-bar ${
            status === "Completed"
              ? "bg-success"
              : "progress-bar-striped progress-bar-animated"
          }`}
          style={{
            width: `${progress}%`,
          }}
        >
          {progress}%
        </div>
      </div>

      <small>
        {formatBytes(uploadedBytes)}
        {" / "}
        {formatBytes(totalBytes)}
      </small>
    </div>
  );
}