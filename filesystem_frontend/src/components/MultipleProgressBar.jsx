import React from "react";

// const { useState } = require("react");
function MultipleProgressBar({files}) {
  // const [files,setFiles] = useState([]);
  // const files = [{
  //   'id': 1,
  //   'progress': 45,
  //   'status': 'completed',
  //   'file': 'AB'
  // }]

  // console.log("files=",files)
  return (
    <div style={{ padding: "20px" }}>
      {files.map((file) => (
        <div key={file.id} style={{ marginBottom: "15px" }}>
          <div>{file.name} ({file.status??"pending"})</div>
          <div className="d-flex align-items-center align-content-center justify-items-center column-gap-2">
            {/* Progress Bar */}
            <div
              style={{
                width: "300px",
                height: "10px",
                background: "black",
                borderRadius: "5px",
                overflow: "hidden",
                marginTop: "5px",
                color: "red"
              }}
            >
              <div
                style={{
                  width: `${file.progress?? 0}%`,
                  height: "100%",
                  background:
                    file.status === "completed" ? "green" : "blue",
                  transition: "width 0.3s ease",
                }}
              />
            </div>

            <div>
              {file.progress??0}%
            </div>

          </div>
        </div>
      ))}
    </div>
  );
}

export default MultipleProgressBar;