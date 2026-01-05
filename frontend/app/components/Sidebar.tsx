'use client';

import { FileText, Trash2, Plus } from 'lucide-react';

interface SidebarProps {
  documents: Array<{ name: string; id: string }>;
  activeDocument: string | null;
  onDocumentSelect: (id: string) => void;
  onDocumentDelete: (id: string) => void;
}

export default function Sidebar({
  documents,
  activeDocument,
  onDocumentSelect,
  onDocumentDelete,
}: SidebarProps) {
  return (
    <div className="w-80 bg-slate-800/50 backdrop-blur-sm border-r border-slate-700 flex flex-col">
      {/* Sidebar Header */}
      <div className="p-4 border-b border-slate-700">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Documents
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          {documents.length} {documents.length === 1 ? 'document' : 'documents'} loaded
        </p>
      </div>

      {/* Documents List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {documents.length === 0 ? (
          <div className="text-center py-12">
            <div className="bg-slate-700/30 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3">
              <Plus className="w-8 h-8 text-slate-500" />
            </div>
            <p className="text-slate-500 text-sm">No documents yet</p>
            <p className="text-slate-600 text-xs mt-1">Upload a PDF to get started</p>
          </div>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.id}
              className={`
                group relative p-3 rounded-lg cursor-pointer transition-all
                ${
                  activeDocument === doc.id
                    ? 'bg-gradient-to-r from-blue-500/20 to-purple-600/20 border border-blue-500/50'
                    : 'bg-slate-700/30 hover:bg-slate-700/50 border border-transparent'
                }
              `}
              onClick={() => onDocumentSelect(doc.id)}
            >
              <div className="flex items-start gap-3">
                <div
                  className={`
                  p-2 rounded-md
                  ${
                    activeDocument === doc.id
                      ? 'bg-blue-500/20'
                      : 'bg-slate-600/30 group-hover:bg-slate-600/50'
                  }
                `}
                >
                  <FileText
                    className={`w-4 h-4 ${
                      activeDocument === doc.id ? 'text-blue-400' : 'text-slate-400'
                    }`}
                  />
                </div>

                <div className="flex-1 min-w-0">
                  <p
                    className={`text-sm font-medium truncate ${
                      activeDocument === doc.id ? 'text-white' : 'text-slate-300'
                    }`}
                  >
                    {doc.name}
                  </p>
                  <p className="text-xs text-slate-500 mt-0.5">Ready to chat</p>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm(`Delete "${doc.name}"?`)) {
                      onDocumentDelete(doc.id);
                    }
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1.5 rounded-md hover:bg-red-500/20 transition-all"
                >
                  <Trash2 className="w-4 h-4 text-red-400" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700">
        <div className="text-xs text-slate-500 space-y-1">
          <p>💡 Tip: Ask specific questions</p>
          <p className="text-slate-600">Citations will be provided</p>
        </div>
      </div>
    </div>
  );
}