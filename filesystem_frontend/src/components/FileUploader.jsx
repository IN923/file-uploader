import React, { useState, useEffect } from "react";
import { Pool, spawn, Worker } from "threads";
import axios from "../api/axios";
import ProgressBar from "./ProgressBar";

const CHUNK_SIZE = 10 * 1024 * 1024; // 10 MB
const CONCURRENCY = 4;

export default function FileUploader() {
  const MAX_FILE_SIZE = 1000000000; // 1 MB
  // const [file, setFile] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState("");
  const [filesProgress, setFilesProgress] = useState([]);
  let [source, setSource] = useState(null);
  const [urlInput, seturlInput] = useState(null)

  const socket_name = crypto.randomUUID();
  async function handleFileUpload(e) {
    e.preventDefault();
    setSource("single-file")

    if(!selectedFile){
      setError("Please select a file.");
      return;
    }
    console.log("name=", selectedFile);

    let total_chunks = 0;
    if (selectedFile && selectedFile.size <= CHUNK_SIZE) {
      total_chunks = 1
      console.log("total_chunks=", total_chunks)
    }
    else {
      total_chunks = Math.ceil(selectedFile.size / CHUNK_SIZE);
    }
    console.log("total_chunks1111=", total_chunks)
    let file_unique_name = null;
    try {
      const startResponse = await axios.post("/upload/start/",
        {
          name: selectedFile.name,
          // file_size: selectedFile.size,
          total_chunks: total_chunks
        }
      );

      file_unique_name = startResponse.data.file_unique_name;

      setFilesProgress((prev) => [
        ...prev,
        {
          file_unique_name,
          progress: 0,
          uploaded: 0,
          total: selectedFile.size,
          progress_status: "pending",
          name: selectedFile.name
        },
      ]);

    } catch (err) {
      // console.log("error data=", err.response.data)
      const errors = err.response.data
      if (errors.name[0]) {
        setError(errors.name[0])
      }
      return;
    }

    // const file_unique_name = startResponse.data.file_unique_name;
    console.log("iiiiiiiii=", file_unique_name);

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

    for (let chunkNumber = 0; chunkNumber < total_chunks; chunkNumber++
    ) {
      const start = chunkNumber * CHUNK_SIZE;

      const chunk = selectedFile.slice(start, start + CHUNK_SIZE);

      tasks.push(
        pool.queue(async (worker) => {
          const result =
            await worker.uploadChunk({
              selectedFile,
              file_unique_name,
              chunk,
              chunkNumber,
            });

          return result;
        })
      );

    }

    await Promise.all(tasks);
    connectSocket(socket_name);
    await axios.post("upload/filemerge/", {
      file_unique_name: file_unique_name,
      'socketname': socket_name
    });

    await pool.terminate();
  }

  function connectSocket(socket_name) {
    let socket_conn = new WebSocket(`ws://127.0.0.1:8000/ws/progress/${socket_name}/`);
    socket_conn.onmessage = function (event) {
      const data = JSON.parse(event.data);

      setFilesProgress((prev) =>
        prev.map((file) =>
          file.file_unique_name === data.file_unique_name
            ? { ...file, progress: data.progress, name: selectedFile?.name ?? file.name, uploaded: data.uploaded, progress_status: data.progress_status }
            : file
        )
      );
    }
  }

  const handleFileChange = (e) => {
    e.preventDefault();
    const selectedFile = e.target.files[0];
    console.log("selected file=", selectedFile);

    setError("");
    // setFile(null);

    // Required validation
    if (!selectedFile) {
      setError("Please select a file.");
      return;
    }

    // File size validation
    if (selectedFile.size > MAX_FILE_SIZE) {
      setError("File size must not exceed 1 MB.");
      return;
    }

    // setFile(selectedFile);
    setSelectedFile(selectedFile);
  }

  function handleUrlField(e) {
    e.preventDefault();
    setSource("import-url")
    const selectedUrl = e.target.value;

    setError("");
    // setFile(null);
    console.log("1111111111111111111111")
    // Required validation
    if (!selectedUrl) {
      console.log("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
      setError("Please write a URL");
      return;
    }

    seturlInput(selectedUrl);
  }

  async function handleURLUpload(e) {
    e.preventDefault();
    console.log("abbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
    if(!urlInput){
      setError("Please write a URL");
      return;
    }
    try{
    const result= await axios.post('/upload/get-files/',{
      link:urlInput,
      socketname:socket_name
    })

    const result_data = result.data

    if(result_data.length===0){
      alert("upload files size should be less than 1GB")
      return
    }

    setFilesProgress(result_data);
    connectSocket(socket_name);
    console.log(result.data)
  }
  catch(err){
    console.log(err)
  }
  }


  console.log("hhhhhhhhh", filesProgress);
  return (
    <>
      <div
        className="container d-flex flex-column justify-content-center align-items-center"
        style={{ height: "100vh" }}
      >
        <form onSubmit={handleFileUpload} className="w-50 mt-3 mb-4">
          <label htmlFor="upload_file_box" className="form-label">
            Upload File
          </label>
          <input
            type="file"
            id="upload_file_box"
            className="form-control"
            onChange={handleFileChange}
          />

          {source == "single-file" &&
            error && (
              <p style={{ color: "red", marginTop: "8px" }}>
                {error}
              </p>
            )}

          <div className="d-flex justify-content-center mt-3">
            <input type="submit" value="Upload" className="btn btn-primary" />
          </div>

        </form>

        {
          source == "single-file" && (
            <div className="container mt-4">
              {filesProgress.map((file) => (
                <ProgressBar key={file.file_unique_name} {...file} />
              ))}
            </div>)
        }

        <form onSubmit={handleURLUpload} className="w-50">
          <label htmlFor="import_url_box" className="form-label">
            Import Files
          </label>
          <input
            type="text"
            id="import_url_box"
            className="form-control"
            onChange={handleUrlField}
            placeholder="Paste URL"
          />
          {source == "input-url" &&
            error && (
              <p style={{ color: "red", marginTop: "8px" }}>
                {error}
              </p>
            )}

          <div className="d-flex justify-content-center mt-3">
            <input type="submit" value="Import" className="btn btn-primary" />
          </div>
        </form>

        {source == "import-url" && (
          <div className="container mt-4">
            {filesProgress.map((file) => (
              <ProgressBar key={file.file_unique_name} {...file} />
            ))}
          </div>)
        }



      </div>
    </>
  )
}
