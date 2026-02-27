
import { useState } from "react";
import axios from 'axios';

function FileUploader(){
    const [file,setFile] = useState(null);
    const [status,setStatus] = useState('idle');

    function handleFileChange(e) {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    }

    async function handleFileUpload() {
        if (!file) return;
        setStatus('uploading');
        const formData = new FormData();
        formData.append('file', file);
        try {
            await axios.post(`${import.meta.env.VITE_API_URL}/jazz`, formData, {
                headers: {
                    'Content-Type' : 'multipart/form-data',
                }
            });
            setStatus('success');
        } catch{
            setStatus('error');
        };

    }
    return (
        <div>
            <input type = "file" accept="audio/wav" onChange={handleFileChange}></input>
            {file && (
                <div>
                    <p>File Name : {file.name}</p>
                    <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
                    <p>File Type: {file.type}</p>
                </div>
            )}
            {file && status !== 'uploading' && <button onClick = {handleFileUpload}>Upload</button>}
            {status === 'success' && <p>Audio uploaded successfully!</p>}
            {status === 'error' && <p>Upload failed. Please try again.</p>}
        </div>
    )
}

export default FileUploader;