'use client';

import { useState } from 'react';
import DocumentUpload from '@/app/components/DocumentUpload';
import ChatInterface from '@/app/components/ChatInterface';
import Sidebar from '@/app/components/Sidebar';
import { FileText } from 'lucide-react';

export default function Home() {
  const [documents, setDocuments] = useState<Array<{ name: string; id: string }>>([]);
  const [activeDocument, setActiveDocument] = useState<string | null>(null);

  function handleDocumentUpload (doc: { name: string; id: string }) {
    setDocuments((prev) => [...prev, doc]);
    setActiveDocument(doc.id);
  };

  function handleDocumentDelete (id: string) {
    setDocuments((prev) => prev.filter((doc) => doc.id !== id));
    if (activeDocument === id) {
      setActiveDocument(null);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Sidebar */}
      <Sidebar
        documents={documents}
        activeDocument={activeDocument}
        onDocumentSelect={setActiveDocument}
        onDocumentDelete={handleDocumentDelete}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">MyDocWhisper</h1>
              <p className="text-sm text-slate-400">
                Chat with your documents using AI
              </p>
            </div>
          </div>
        </header>

        {/* Main Area */}
        <div className="flex-1 overflow-hidden">
          {!activeDocument ? (
            <div className="h-full flex items-center justify-center p-8">
              <DocumentUpload onUploadSuccess={handleDocumentUpload} />
            </div>
          ) : (
            <ChatInterface
              documentId={activeDocument}
              documentName={documents.find((d) => d.id === activeDocument)?.name || ''}
            />
          )}
        </div>
      </div>
    </div>
  );
}