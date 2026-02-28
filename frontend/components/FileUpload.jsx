
import { useState } from "react";
import axios from 'axios';

function FileUploader(){
    const [file,setFile] = useState(null);
    const [status,setStatus] = useState('idle');
    const [audioUrl, setAudioUrl] = useState(null);

    function handleFileChange(e) {
        if (e.target.files) {
            setFile(e.target.files[0]);
            setAudioUrl(null);
            setStatus('idle');
        }
    }

    async function handleFileUpload() {
        if (!file) return;
        setStatus('uploading');
        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await axios.post(`${import.meta.env.VITE_API_URL}/jazz`, formData, {
                headers: {
                    'Content-Type' : 'multipart/form-data',
                },
                responseType: 'blob',
            });
            const newAudioUrl = URL.createObjectURL(response.data);
            setAudioUrl(newAudioUrl);
            setStatus('success');
        } catch(error){
            console.log(error);
            setStatus('error');
        };

    }
    return (
        <div>
            <h2>Pop to Jazz Converter</h2>
            <input type = "file" accept="audio/wav" onChange={handleFileChange}></input>
            {file && (
                <div>
                    <p>File Name : {file.name}</p>
                    <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
                    <p>File Type: {file.type}</p>
                </div>
            )}
            {file && status !== 'uploading' && <button onClick = {handleFileUpload}>Upload</button>}
            {status === 'uploading' && <p>Processing through AI model... Please wait.</p>}
            {status === 'success' && <p>Audio uploaded successfully!</p>}
            {status === 'error' && <p>Upload failed. Please try again.</p>}
            {audioUrl && (
                <div style={{ marginTop: '20px' }}>
                    <h3>Your Generated Track:</h3>
                    <audio src={audioUrl} controls></audio>
                </div>
            )}
        </div>
    )
}

export default FileUploader;