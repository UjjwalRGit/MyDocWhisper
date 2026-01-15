'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, FileText, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ page: number; text: string; filename: string; }>;
  isStreaming?: boolean;
}

interface ChatInterfaceProps {
  documentId: string;
  documentName: string;
}

export default function ChatInterface({ documentId, documentName }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  function scrollToBottom() {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  async function copyToClipboard(text: string, index: number) {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }

  async function handleSubmitStreaming(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim()
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const assistantMessageIndex = messages.length + 1;
    setMessages((prev) => [
      ...prev,
      {
        role: 'assistant',
        content: '',
        isStreaming: true
      }
    ]);

    try {
      const response = await fetch(`${API_URL}/chat/stream`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: input.trim(),
            documentId: documentId,
            history: messages.map((m) => ({
              role: m.role,
              content: m.content
            }))
          })
        });

      if (!response.ok) {
        throw new Error('Stream request failed');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available');
      }

      let totalAnswer = '';
      let sources: Array<{ page: number; text: string; filename: string }> = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter((line) => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);

            if (data.type == 'answer') {
              totalAnswer += data.content;

              // Update the streaming message
              setMessages((prev) => {
                const newMessages = [...prev];
                newMessages[assistantMessageIndex] = {
                  role: 'assistant',
                  content: totalAnswer,
                  isStreaming: true
                };
                return newMessages;
              })
            } else if (data.type === 'sources') {
              sources = data.sources;
            }
          } catch (err) {
            console.error('Error parsing chunk: ', err);
          }
        }
      }

      // Finalize message
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[assistantMessageIndex] = {
          role: 'assistant',
          content: totalAnswer,
          sources: sources,
          isStreaming: false
        };
        return newMessages
      });
    } catch (error) {
      console.error('Stream error: ', error);

      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[assistantMessageIndex] = {
          role: 'assistant',
          content: '❌ Sorry, I encountered an error. Please make sure the backend is running.',
          isStreaming: false
        };
        return newMessages;
      });
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }


  // async function handleSubmit(e: React.FormEvent) {
  //   e.preventDefault();
  //   if (!input.trim() || isLoading) return;

  //   const userMessage: Message = {
  //     role: 'user',
  //     content: input.trim(),
  //   };

  //   setMessages((prev) => [...prev, userMessage]);
  //   setInput('');
  //   setIsLoading(true);

  //   try {
  //     const response = await fetch('http://localhost:8000/chat', {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify({
  //         message: input.trim(),
  //         documentId: documentId,
  //         history: messages.map((m) => ({
  //           role: m.role,
  //           content: m.content,
  //         })),
  //       }),
  //     });

  //     if (!response.ok) {
  //       throw new Error('Chat request failed');
  //     }

  //     const data = await response.json();

  //     const assistantMessage: Message = {
  //       role: 'assistant',
  //       content: data.answer,
  //       sources: data.sources,
  //     };

  //     setMessages((prev) => [...prev, assistantMessage]);
  //   } catch (error) {
  //     console.error('Chat error:', error);
  //     const errorMessage: Message = {
  //       role: 'assistant',
  //       content: '❌ Sorry, I encountered an error. Please make sure the backend is running.',
  //     };
  //     setMessages((prev) => [...prev, errorMessage]);
  //   } finally {
  //     setIsLoading(false);
  //     inputRef.current?.focus();
  //   }
  // };

  return (
    <div className="flex flex-col h-full">
      {/* Document Info Banner */}
      <div className="bg-slate-800/30 px-6 py-3 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm">
            <FileText className="w-4 h-4 text-blue-400" />
            <span className="text-slate-300">Chatting with:</span>
            <span className="text-white font-medium">{documentName}</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/10 rounded-full">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-xs text-green-400">Streaming Active</span>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="bg-gradient-to-br from-blue-500/10 to-purple-600/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="w-10 h-10 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              Start a Conversation
            </h3>
            <p className="text-slate-400 max-w-md mx-auto mb-6">
              Ask questions about your document. I'll provide answers with citations from the source.
            </p>
            <div className="space-y-2">
              <button
                onClick={() => setInput('What is this document about?')}
                className="block w-full max-w-sm mx-auto text-left px-4 py-3 bg-slate-700/30 hover:bg-slate-700/50 rounded-lg text-slate-300 text-sm transition-colors"
              >
                💡 What is this document about?
              </button>
              <button
                onClick={() => setInput('Summarize the key points')}
                className="block w-full max-w-sm mx-auto text-left px-4 py-3 bg-slate-700/30 hover:bg-slate-700/50 rounded-lg text-slate-300 text-sm transition-colors"
              >
                📝 Summarize the key points
              </button>
              <button
                onClick={() => setInput('What are the main takeaways?')}
                className="block w-full max-w-sm mx-auto text-left px-4 py-3 bg-slate-700/30 hover:bg-slate-700/50 rounded-lg text-slate-300 text-sm transition-colors"
              >
                🎯 What are the main takeaways?
              </button>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
          >
            <div
              className={`group relative max-w-3xl ${message.role === 'user'
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                : 'bg-slate-800/50 text-slate-100'
                } rounded-2xl px-6 py-4`}
            >
              {/* Copy button */}
              {message.role === 'assistant' && !message.isStreaming && (
                <button
                  onClick={() => copyToClipboard(message.content, index)}
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1.5 rounded-md hover:bg-slate-700/50 transition-all"
                  title="Copy to clipboard"
                >
                  {copiedIndex === index ? (
                    <Check className="w-4 h-4 text-green-400" />
                  ) : (
                    <Copy className="w-4 h-4 text-slate-400" />
                  )}
                </button>
              )}

              <div className="prose prose-invert prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              </div>

              {/* Streaming indicator */}
              {message.isStreaming && (
                <div className="flex items-center gap-2 mt-2 text-xs text-slate-400">
                  <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></div>
                    <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span>Thinking...</span>
                </div>
              )}

              {/* Sources */}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <p className="text-xs text-slate-400 mb-2 font-medium">
                    📚 Sources ({message.sources.length}):
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {message.sources.map((source, idx) => (
                      <button
                        key={idx}
                        className="group/source relative text-xs bg-slate-700/50 hover:bg-slate-700 px-3 py-1.5 rounded-full text-blue-300 transition-colors"
                        title={source.text}
                      >
                        📄 Page {source.page}

                        {/* Tooltip */}
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover/source:block w-64 p-2 bg-slate-900 text-slate-300 text-xs rounded-lg shadow-xl z-10">
                          {<p className="font-semibold mb-1">{source.filename}</p>}
                          <p className="text-slate-400">{source.text}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
          <div className="flex justify-start">
            <div className="bg-slate-800/50 rounded-2xl px-6 py-4">
              <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-700 p-6">
        <form onSubmit={handleSubmitStreaming} className="flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your document..."
            className="flex-1 bg-slate-800/50 border border-slate-700 rounded-xl px-6 py-4 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-8 py-4 rounded-xl font-medium transition-all flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Send className="w-5 h-5" />
                Send
              </>
            )}
          </button>
        </form>

        {/* Context indicator */}
        {messages.length > 0 && (
          <div className="mt-3 text-xs text-slate-500 flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>
              Chat history active - I remember our conversation ({messages.filter(m => m.role === 'user').length} messages)
            </span>
          </div>
        )}
      </div>
    </div>
  );
}