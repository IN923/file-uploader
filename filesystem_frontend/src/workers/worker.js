console.log("Worker file started");

import { expose } from "threads/worker";
import api from '../api/axios';

console.log("Imports completed");

const chunkSize = 1024;
let uploaded_file_id = null;
const files_loadedbytes = {}; //contains loaded bytes of file

async function uploadChunk(
    file,
    chunkId,
    totalChunks,
    filename,
    filesize
) {
    const start = chunkId * chunkSize;
    console.log("chunkId=",chunkId);
    const chunk = file.slice(
        start,
        start + chunkSize
    );

    const formData = new FormData();

    formData.append("file", chunk);

    if (uploaded_file_id === null) {
        formData.append("filename", filename);
        formData.append("file_size", filesize);
        formData.append("total_chunks", totalChunks);
    }

    formData.append("chunk_number", chunkId);

    if (uploaded_file_id) {
        formData.append(
            "uploadfile",
            uploaded_file_id
        );
    }

    console.log("API URL:", import.meta.env.VITE_API_URL);
    console.log("Axios baseURL:", api.defaults.baseURL);
    console.log("file:",file,chunk.size);
    if(files_loadedbytes.hasOwnProperty(file.name)){
        files_loadedbytes[file.name] = files_loadedbytes[file.name]+chunk.size;
    }
    else{
        files_loadedbytes[file.name]=chunk.size;
    }
    console.log("files_loadedbytes:",files_loadedbytes);
    // const response = await fetch(
    //     "http://127.0.0.1:8000/upload/filechunk/",
    //     {
    //         method: "POST",
    //         body: formData,
    //         cache: "no-cache"
    //     }
    // );
    let response;
    try{
        response = await api.post('/upload/filechunk/',formData,{
            onUploadProgress:(ProgressEvent)=>{
                let {loaded,total} = ProgressEvent;
                loaded = files_loadedbytes[file.name];
                total = file.size;
                console.log(`loaded=${loaded},total=${total}`)
                if(total){
                    let percentage = Math.round((loaded * 100) / total);
                    console.log(`Upload Progress: ${percentage}%`);
                    // setProgress(percentage);
                }
            }
        })
    }
    catch(error){
        console.error(error.response?.status);
        console.error(error.response?.data);
        console.error(error.config?.baseURL + error.config?.url);
        console.error('axios error:',error);
        throw error;
    };

    console.log("response=",response);
    

    const data = response.data;

    if (data.uploaded_file_id) {
        uploaded_file_id = data.uploaded_file_id;
    }

    return data;
}

expose({
    uploadChunk
}
);

console.log("Expose called");