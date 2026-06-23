import React, { useState, useEffect } from "react";
import { Pool, spawn, Worker } from "threads";
import axios from "../api/axios";
import ProgressBar from "./ProgressBar";
import MultipleProgressBar from "./MultipleProgressBar";

const CHUNK_SIZE = 10 * 1024 * 1024; // 10 MB
const CONCURRENCY = 4;

export default function FileUploader() {
  const [progress, setProgress] = useState(0);
  const [uploadedBytes, setUploadedBytes] = useState(0);
  const [totalBytes, setTotalBytes] = useState(0);
  const [status, setStatus] = useState("Idle");
  const [socket, setSocket] = useState(null);
  const [fileswithprogress, setFiles] = useState([]);
  useEffect(() => {
    return () => {
      if (socket) socket.close();
    };
  }, [socket]);
  const handleUpload = async (e) => {
    e.preventDefault();

    const file = document.getElementById("file-upload").files[0];

    if (!file) return;

    setStatus("Uploading");
    setProgress(0);
    setUploadedBytes(0);
    setTotalBytes(file.size);

    try {
      // Create upload record first
      const startResponse = await axios.post(
        "/upload/start/",
        {
          filename: file.name,
          file_size: file.size,
        }
      );

      const uploadId = startResponse.data.uploaded_file_id;
      console.log("uploadId=", uploadId, startResponse.data);

      console.log("upload id on frontend:", uploadId)
      const totalChunks = Math.ceil(
        file.size / CHUNK_SIZE
      );

      const pool = Pool(
        () =>
          spawn(
            new Worker(
              new URL(
                "../workers/worker.js",
                import.meta.url
              ),
              { type: "module" }
            )
          ),
        CONCURRENCY
      );

      const tasks = [];

      for (
        let chunkNumber = 0;
        chunkNumber < totalChunks;
        chunkNumber++
      ) {
        const start = chunkNumber * CHUNK_SIZE;

        const chunk = file.slice(
          start,
          start + CHUNK_SIZE
        );

        tasks.push(
          pool.queue(async (worker) => {
            const result =
              await worker.uploadChunk({
                uploadId,
                chunk,
                chunkNumber,
                totalChunks,
                file
              });

            setUploadedBytes((prev) => {
              const uploaded =
                prev + result.uploadedBytes;

              setProgress(
                Math.round(
                  (uploaded * 100) / file.size
                )
              );

              return uploaded;
            });

            return result;
          })
        );
      }

      await Promise.all(tasks);

      await axios.post("upload/filemerge/", {
        upload_id: uploadId,
      });

      setProgress(100);
      setStatus("Completed");

      await pool.terminate();
    } catch (error) {
      console.error(error);
      setStatus("Failed");
    }
  };


  function connectWebSocket(jobId) {
    const ws = new WebSocket(
      `ws://127.0.0.1:8000/ws/progress/${jobId}/`
    );

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("event data=", event.data)
      setFiles((prevFiles) => {
        const updatedFiles = prevFiles.map((file) =>
          file.id === data.id
            ? { ...file, ...data }
            : file
        );

        const allCompleted =
          updatedFiles.length > 0 &&
          updatedFiles.every(
            (file) => file.status === "completed"
          );

        if (allCompleted) {
          setTimeout(() => {
            setFiles([]);
          }, 3000);
        }

        return updatedFiles;
      });


      // if (data.status === "completed") {
      //   ws.close();
      // }
    };

    ws.onclose = () => {
      console.log("WebSocket closed");
    };

    ws.onerror = (err) => {
      console.error("WebSocket error", err);
    };

    setSocket(ws);
  }


  async function handleMultipleUpload(event) {
    event.preventDefault();
    const link = document.getElementById("file-multiple-upload").value;

    try {
      const response = await axios.post("upload/get-files/", { link });
      const jobId = response.data["job_id"];
      // const socket = new WebSocket(`ws://127.0.0.1:8000/ws/progress/${jobId}/`)
      setFiles(
        response.data.files.map(file => ({
          ...file,
          progress: file.progress ?? 0,
          status: file.status ?? "Pending",
        }))
      );
      connectWebSocket(jobId)
      // socket.onmessage = (event) => {
      //   const data = JSON.parse(event.data);

      //   connectWebSocket(jobId)
      //   if (data.status === "completed") {
      //     socket.close();
      //   }
      // };

    } catch (error) {
      console.error(error);
      setStatus("Failed");
    }
  }

  return (
    <>
      <div className="container mt-4">
        <form onSubmit={handleUpload}>
          <input
            id="file-upload"
            type="file"
            className="form-control"
          />

          <button
            className="btn btn-primary mt-3"
            type="submit"
          >
            Upload
          </button>
        </form>

        <ProgressBar
          progress={progress}
          uploadedBytes={uploadedBytes}
          totalBytes={totalBytes}
          status={status}
        />
      </div>

      <div className="container mt-4">
        <form onSubmit={handleMultipleUpload}>
          <input
            id="file-multiple-upload"
            type="text"
            className="form-control"
          />

          <button
            className="btn btn-primary mt-3"
            type="submit"
          >
            submit
          </button>
        </form>

        {/* <ProgressBar
          progress={progress}
          uploadedBytes={uploadedBytes}
          totalBytes={totalBytes}
          status={status}
        /> */}
      </div>

      {fileswithprogress.length > 0 && (<MultipleProgressBar files={fileswithprogress} />)}
    </>
  );
}