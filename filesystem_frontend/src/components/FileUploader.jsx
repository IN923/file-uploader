import React from 'react';
import { useState } from 'react';
import api from '../api/axios'
import { Pool, spawn, Worker } from "threads";
import ProgressBar from "./ProgressBar";

function FileUploader() {

    const [errors, setErrors] = useState({})
    const maxFileSize = 1024 * 1024 * 1024
    let filesize = 0;
    let filename = null;
    const [progress, setProgress] = useState(0);

    const apiURL = import.meta.env.VITE_API_URL;

    function validateFile(event) {
        const file = event.target.files[0]
        const newErrors = {}
        if (file.size > maxFileSize) {
            newErrors.fileError = "Maximum file size :1GB"
        }

        filesize = file.size;
        filename = file.filename;
        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    // const handleImageChange = async (event) => {
    //     event.preventDefault()
    //     const file = document.getElementById('file-upload').files[0]
    //     console.log("Selected file:", file.size);

    //     const maxFileSize = 1024 * 1024 * 1024
    //     console.log(maxFileSize);
    //     // if (file && file.size > maxFileSize) {
    //     //     return "Maximum file size:1GB"
    //     // }

    //     const chunkSize = 1024
    //     const totalChunks = Math.ceil(file.size / chunkSize)
    //     // console.log('totalChunks:', totalChunks)
    //     let chunk_number = 0 // chunk index
    //     let uploaded_file_id = null
    //     async function fileChunking() {
    //         for (let start = 0; start < file.size; start += chunkSize) {
    //             const chunk = file.slice(start, start + chunkSize);
    //             // console.log("file chunk:", chunk);
    //             // console.log('chunknumber', chunk_number)
    //             // console.log('file size', file.size)
    //             const data = await uploadChunk(chunk, chunk_number, file.name, file.size, totalChunks, uploaded_file_id)

    //             uploaded_file_id = data

    //             chunk_number += 1

    //             // if (chunk_number === 3) {
    //             //     break
    //             // }

    //         }

    //     }
    //     await fileChunking()
    //     console.log("uploading file identifier",uploaded_file_id)
    //     const merge_file = await fileMerge(uploaded_file_id)
    // }

    // async function uploadChunk(chunk, chunk_number, filename, file_size, totalChunks, uploaded_file_id) {
    //     // console.log("uploaded file id:", uploaded_file_id)

    //     const formData = new FormData()
    //     formData.append('file', chunk)
    //     if (uploaded_file_id === null) {
    //         formData.append('filename', filename)
    //         formData.append('file_size', file_size)
    //         formData.append('total_chunks', totalChunks)
    //         formData.append('chunk_number', chunk_number)
    //     }
    //     else {
    //         formData.append('chunk_number', chunk_number)
    //         formData.append('uploadfile', uploaded_file_id)
    //     }

    //     const response = await fetch('http://127.0.0.1:8000/upload/filechunk/', {
    //         method: 'POST',
    //         body: formData,
    //     })

    //     let { uploaded_file_id: saved_file_id } = await response.json()
    //     // console.log("saved file id:", saved_file_id)
    //     return saved_file_id
    // }

    // async function fileMerge(uploaded_file_id) {
    //     const response = await fetch('http://127.0.0.1:8000/upload/filemerge/', {
    //         method: 'POST',
    //         headers:{
    //             'Content-Type':'application/json'
    //         },
    //         body: JSON.stringify({'uploaded_file_id':uploaded_file_id}),
    //     })

    //     const data = await response.json()
    //     return data
    // }
    const chunkSize = 10 * 1024 * 1024;
    let uploaded_file_id = null;
    const chunksQueue = [];

    async function handleImageUpload(event) {
        event.preventDefault();
        const file = document.getElementById("file-upload").files[0];

        if (!file) return;

        const totalChunks = Math.ceil(file.size / chunkSize);
        console.log("total chunks=",totalChunks);
        const pool = Pool(
            () => spawn(new Worker("src/workers/worker.js", {
                type: "module"
            })),
            4
        );

        const tasks = [];

        for (let chunkId = 0; chunkId < totalChunks; chunkId++) {
            tasks.push(
                pool.queue(async worker => {

                    return worker.uploadChunk(
                        file,
                        chunkId,
                        totalChunks,
                        file.name,
                        file.size
                    );
                })
            );
        }

        const result = await Promise.all(tasks);
        console.log("result=", result);
        await pool.terminate();

        console.log("Upload completed");
    }

    async function fileMerge(uploaded_file_id) {
        // const response = await fetch(`{apiURL}/upload/filemerge/`, {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json'
        //     },
        //     body: JSON.stringify({ 'uploaded_file_id': uploaded_file_id }),
        // })

        try {
            const response = await axios.post('upload/filemerge/',
                JSON.stringify({ 'uploaded_file_id': uploaded_file_id })
            )
        }
        catch (error) {
            console.log('axios error:', error)
        }

        const data = await response.json()
        return data
    }

    return (
        <>
            <div className="container file-upload-container">
                <form method='POST' onSubmit={handleImageUpload} className="w-50" encType="multipart/form-data">

                    <label htmlFor="file-upload" className="mb-3">Upload File</label>
                    <input id="file-upload" className="form-control" type="file" name="uploaded_file" />
                    {errors.fileError && <span className='error mt-1'>{errors.fileError}</span>}
                    <div className="d-flex justify-content-center align-items-center mt-4 mb-2">
                        <input type="submit" value="Upload" className="px-3" />
                    </div>

                </form>

                <ProgressBar
        progress={progress}
        uploadedSize="450 MB"
        totalSize="1 GB"
        status="Uploading"
      />
            </div>
        </>
    )
}

export default FileUploader;

