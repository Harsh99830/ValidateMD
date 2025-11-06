import React, { useState } from 'react';
import axios from 'axios';
const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const FileUpload = ({ onValidationComplete, onValidationError, onLoading }) => {
  const [file, setFile] = useState(null);
  const [useAI, setUseAI] = useState(true);
  const [limit, setLimit] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && (selectedFile.type === 'text/csv' || selectedFile.type === 'application/pdf')) {
      setFile(selectedFile);
    } else {
      alert('Please select a CSV or PDF file');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      onValidationError('Please select a CSV or PDF file');
      return;
    }

    onLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('use_ai', useAI ? 'true' : 'false');
    const numericLimit = Number(limit);
    const validLimit = Number.isFinite(numericLimit) && numericLimit > 0 ? String(Math.floor(numericLimit)) : null;
    if (validLimit) {
      formData.append('limit', validLimit);
    }

    try {
      console.log('[FileUpload] Submitting validation request', {
        use_ai: useAI,
        limit: validLimit,
        fileName: file?.name,
        fileSize: file?.size
      });

      const response = await axios.post(`${API_BASE}/api/validate`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000,
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
      });

      console.log('[FileUpload] Response received', {
        status: response.status,
        typeofData: typeof response.data,
      });

      // Handle stringified or non-compliant JSON payloads
      const safeParseJson = (input) => {
        if (typeof input !== 'string') return input;
        try {
          return JSON.parse(input);
        } catch (e1) {
          // Replace unquoted NaN/Infinity with null
          const sanitized = input
            .replace(/(?<=[:\s\[,])NaN(?=\s*[,\]}])/g, 'null')
            .replace(/(?<=[:\s\[,])Infinity(?=\s*[,\]}])/g, 'null')
            .replace(/(?<=[:\s\[,])-Infinity(?=\s*[,\]}])/g, 'null');
          try {
            return JSON.parse(sanitized);
          } catch (e2) {
            const start = sanitized.indexOf('{');
            const end = sanitized.lastIndexOf('}');
            if (start !== -1 && end !== -1 && end > start) {
              const slice = sanitized.slice(start, end + 1);
              try {
                return JSON.parse(slice);
              } catch (e3) {
                console.error('[FileUpload] Failed to parse sliced response', e3);
              }
            }
            console.error('[FileUpload] Failed to parse string response', e2, { preview: input.slice(0, 200) + '...' });
            return null;
          }
        }
      };

      let payload = safeParseJson(response.data);
      if (!payload) payload = response.data; // fallback to raw

      if (payload && payload.success) {
        onValidationComplete(payload);
      } else {
        const msg = payload?.error || 'Validation failed';
        console.error('[FileUpload] Validation not successful', { msg, data: payload });
        onValidationError(msg);
      }
    } catch (error) {
      const status = error.response?.status;
      const serverMsg = error.response?.data?.error || error.response?.data?.message;
      const clientMsg = error.message;
      const composed = serverMsg || clientMsg || 'Failed to connect to validation service. Please try again.';
      console.error('[FileUpload] Request failed', { status, serverMsg, clientMsg, error });
      onValidationError(status ? `[HTTP ${status}] ${composed}` : composed);
    } finally {
      onLoading(false);
    }
  };

  const handleDemoData = async () => {
    onLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/validate-sample?use_ai=true&limit=5`);
      if (response.data.success) {
        onValidationComplete(response.data);
      }
    } catch (error) {
      onValidationError('Failed to load demo data');
    } finally {
      onLoading(false);
    }
  };

  return (
    <div className="rounded-md border bg-white p-4 shadow-sm">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-1">
            <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700">Upload File (CSV or PDF)</label>
            <input
              type="file"
              id="file-upload"
              accept=".csv,.pdf"
              onChange={handleFileChange}
              required
              className="block w-full rounded-md border border-gray-300 bg-white text-sm file:mr-4 file:rounded-md file:border-0 file:bg-blue-50 file:px-3 file:py-2 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <label className="inline-flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={useAI}
                onChange={(e) => setUseAI(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              🧠 Enable AI Validation
            </label>

            <div className="space-y-1">
              <label htmlFor="limit" className="block text-sm font-medium text-gray-700">Limit (optional)</label>
              <input
                type="number"
                id="limit"
                value={limit}
                onChange={(e) => setLimit(e.target.value)}
                placeholder="All records"
                min="1"
                max="1000"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button type="submit" disabled={!file} className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50">
            🚀 Validate Providers
          </button>
         
        </div>
      </form>
    </div>
  );
};

export default FileUpload;