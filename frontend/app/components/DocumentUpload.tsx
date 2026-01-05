'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Loader2 } from 'lucide-react';

interface DocumentUploadProps {
  onUploadSuccess: (doc: { name: string; id: string }) => void;
}

export default function DocumentUpload({ onUploadSuccess }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      setUploading(true);
      setProgress(0);

      const formData = new FormData();
      formData.append('file', file);

      try {
        // Simulate progress
        const progressInterval = setInterval(() => {
          setProgress((prev) => {
            if (prev >= 90) {
              clearInterval(progressInterval);
              return 90;
            }
            return prev + 10;
          });
        }, 200);

        const response = await fetch('http://localhost:8000/upload', {
          method: 'POST',
          body: formData,
        });

        clearInterval(progressInterval);
        setProgress(100);

        if (!response.ok) {
          throw new Error('Upload failed');
        }

        const data = await response.json();

        setTimeout(() => {
          onUploadSuccess({
            name: file.name,
            id: data.documentId || Date.now().toString(),
          });
          setUploading(false);
          setProgress(0);
        }, 500);
      } catch (error) {
        console.error('Upload error:', error);
        setUploading(false);
        setProgress(0);
        alert('Failed to upload document. Please check:\n• Backend is running on port 8000\n• File is a valid PDF\n• File is under 50MB');
      }
    },
    [onUploadSuccess]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div className="w-full max-w-2xl">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer
          transition-all duration-300 ease-in-out
          ${
            isDragActive
              ? 'border-blue-500 bg-blue-500/10 scale-105'
              : 'border-slate-600 bg-slate-800/50 hover:border-blue-400 hover:bg-slate-800'
          }
          ${uploading ? 'pointer-events-none opacity-60' : ''}
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-4">
          {uploading ? (
            <>
              <Loader2 className="w-16 h-16 text-blue-500 animate-spin" />
              <div className="w-full max-w-xs">
                <div className="bg-slate-700 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-600 h-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="text-slate-400 text-sm mt-2">{progress}% uploaded</p>
              </div>
            </>
          ) : (
            <>
              <div className="bg-gradient-to-br from-blue-500/20 to-purple-600/20 p-6 rounded-full">
                {isDragActive ? (
                  <Upload className="w-12 h-12 text-blue-400" />
                ) : (
                  <FileText className="w-12 h-12 text-blue-400" />
                )}
              </div>

              <div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {isDragActive ? 'Drop your PDF here' : 'Upload a PDF Document'}
                </h3>
                <p className="text-slate-400">
                  Drag and drop your PDF file here, or click to browse
                </p>
              </div>

              <div className="flex gap-2 text-xs text-slate-500">
                <span className="bg-slate-700/50 px-3 py-1 rounded-full">PDF only</span>
                <span className="bg-slate-700/50 px-3 py-1 rounded-full">Max 50MB</span>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="mt-6 text-center text-sm text-slate-500">
        <p>Your documents are processed locally and never stored permanently</p>
      </div>
    </div>
  );
}