import { expose } from "threads/worker";
import axios from "../api/axios";

async function uploadChunk({
  uploadId,
  chunk,
  chunkNumber,
  totalChunks,
  file
}) {
  const formData = new FormData();

  formData.append("file", chunk);
  formData.append("uploadfile", uploadId);
  formData.append('filename',file.name);
  formData.append(
    "chunk_number",
    chunkNumber
  );
  formData.append(
    "total_chunks",
    totalChunks
  );

  await axios.post(
    "/upload/filechunk/",
    formData
  );

  return {
    uploadedBytes: chunk.size,
    chunkNumber,
  };
}

expose({
  uploadChunk,
});

