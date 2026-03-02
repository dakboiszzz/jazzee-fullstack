
import { useState } from "react";
import axios from 'axios';

function FileUploader(){
    const [ytbUrl, setYtbUrl] = useState('');
    const [status,setStatus] = useState('idle');
    const [audioUrl, setAudioUrl] = useState(null);

    function handleInputChange(e) {
        if (e.target.value) {
            setYtbUrl(e.target.value);
            setAudioUrl(null);
            setStatus('idle');
        }
    }

    async function handleConvert() {
        if (!ytbUrl) return;
        setStatus('processing');
        try {
            const response = await axios.post(`${import.meta.env.VITE_API_URL}/jazz`,{
                url : ytbUrl
            }, {
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
            <input type = "text" onChange={handleInputChange} placeholder="Enter a Youtube Url"></input>
            {ytbUrl && status !== 'processing' && <button onClick = {handleConvert}>Upload</button>}
            {status === 'processing' && <p>Processing through AI model... Please wait.</p>}
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