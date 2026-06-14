import React from "react";

const ProgressBar = ({
  progress = 0,
  uploadedSize = "",
  totalSize = "",
  status = "Uploading",
}) => {
  return (
    <div className="mt-3">
      <div className="d-flex justify-content-between mb-1">
        <span>{status}</span>
        <span>{progress}%</span>
      </div>

      <div className="progress" style={{ height: "25px" }}>
        <div
          className={`progress-bar ${
            status === "Completed"
              ? "bg-success"
              : status === "Failed"
              ? "bg-danger"
              : "progress-bar-striped progress-bar-animated"
          }`}
          role="progressbar"
          style={{ width: `${progress}%` }}
          aria-valuenow={progress}
          aria-valuemin="0"
          aria-valuemax="100"
        >
          {progress}%
        </div>
      </div>

      <div className="mt-2 text-muted">
        {uploadedSize && totalSize && (
          <small>
            {uploadedSize} / {totalSize}
          </small>
        )}
      </div>

      {status === "Completed" && (
        <div className="mt-2 text-success fw-bold">
          ✓ Upload Completed
        </div>
      )}

      {status === "Failed" && (
        <div className="mt-2 text-danger fw-bold">
          ✗ Upload Failed
        </div>
      )}
    </div>
  );
};

export default ProgressBar;