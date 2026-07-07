import { expose } from "threads/worker";
import axios from "../api/axios";

async function uploadChunk({
  selectedFile,
  file_unique_name,
  chunk,
  chunkNumber,
}) {
  const formData = new FormData();

  const renamedChunk = new File([chunk], selectedFile.name, {
    type: selectedFile.type
  })

  console.log("fffffff=",file_unique_name);
  formData.append("chunk_file",renamedChunk);
  formData.append("file", file_unique_name);
  formData.append(
    "chunk_number",
    chunkNumber
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

