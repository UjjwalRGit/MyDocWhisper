# MyDocWhisper 🗣️📄

> Transform static PDFs into interactive conversations with AI-powered document analysis

An intelligent RAG (Retrieval-Augmented Generation) application that allows users to upload PDF documents and chat with them using natural language. Built with Next.js, FastAPI, and OpenAI's GPT-4.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/yourusername/mydocwhisper)

---

## 🎯 What It Does

**The Problem**: Knowledge is trapped in documents. Standard search (Ctrl+F) only finds keywords, not answers. ChatGPT is great, but it doesn't know your private data.

**The Solution**: MyDocWhisper bridges that gap by:
- 📤 Accepting your PDF documents
- 🧠 Understanding the content using AI
- 💬 Answering questions in natural language with real-time streaming
- 📝 Citing exact page numbers for every answer
- 🛡️ Preventing AI hallucinations through grounding
- 🔄 Remembering conversation context for natural follow-ups

---

## ✨ Features

### Core Capabilities ✅
- **Drag-and-Drop Upload**: Intuitive PDF document upload interface
- **Intelligent Chunking**: Documents split into meaningful segments (1000 chars, 200 overlap)
- **Vector Search**: Semantic understanding beyond keyword matching
- **AI-Powered Answers**: GPT-4o-mini generates accurate responses
- **Source Citations**: Every answer includes page references with hoverable previews
- **Document Management**: Sidebar for managing multiple documents
- **Modern UI**: Dark-themed, responsive interface with Tailwind CSS

### Advanced Features (v2.0) ⚡
- **🚀 Streaming Responses**: Real-time "typewriter effect" as AI generates answers
- **🧠 Chat History**: Context-aware conversations - AI remembers previous questions
- **📚 Enhanced Citations**: Hover over sources to see document excerpts and page numbers
- **📋 Copy to Clipboard**: One-click copying of AI responses
- **💬 Multi-turn Conversations**: Natural follow-up questions without repeating context
- **✨ Animated UI**: Smooth transitions and visual feedback throughout

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Lucide React Icons
- **Markdown**: React Markdown with remark-gfm
- **File Upload**: React Dropzone

### Backend
- **Framework**: FastAPI (Python)
- **AI/LLM**: OpenAI GPT-4o-mini with streaming support
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Database**: ChromaDB
- **Orchestration**: LangChain
- **PDF Processing**: pypdf
- **Environment**: python-dotenv

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18.0 or higher
- **Python** 3.9 or higher
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/MyDocWhisper.git
cd MyDocWhisper
```

#### 2. Backend Setup

```cmd
cd backend

REM Install Python dependencies
pip install -r requirements.txt

REM Create .env file
echo OPENAI_API_KEY=your_actual_api_key_here > .env

REM Start the backend server
python main.py
```

The backend will run on `http://localhost:8000`

#### 3. Frontend Setup

```cmd
cd frontend

REM Install Node dependencies
npm install

REM Start the development server
npm run dev
```

The frontend will run on `http://localhost:3000`

---

## 📖 Usage

1. **Start Both Servers**: Make sure backend (port 8000) and frontend (port 3000) are running
2. **Open Browser**: Navigate to `http://localhost:3000`
3. **Upload Document**: Drag and drop a PDF file (max 50MB)
4. **Wait for Processing**: The document will be chunked and embedded (~5-10 seconds)
5. **Start Chatting**: Ask questions and watch responses stream in real-time
6. **View Citations**: Hover over page badges to see source excerpts
7. **Ask Follow-ups**: Continue the conversation naturally - the AI remembers context

### Example Conversations

**Initial Question:**
```
You: "What is this document about?"
AI: "This document discusses machine learning fundamentals, covering 
     supervised learning, neural networks, and practical applications."
     📄 Sources: Page 3, 7, 12
```

**Contextual Follow-up:**
```
You: "Can you explain more about neural networks?"
AI: "Neural networks, as mentioned earlier, are computational models 
     inspired by biological neurons..."
     📄 Sources: Page 7, 8
```

*Notice how the AI understands "neural networks" refers to the topic from the previous answer!*

### Pro Tips
- 💡 **Copy Responses**: Hover over AI messages to reveal the copy button
- 📚 **View Sources**: Hover over source badges to see document excerpts
- 🔄 **Context Aware**: Ask follow-up questions without repeating information
- ⚡ **Streaming**: Watch answers appear in real-time as they're generated

---

## 📂 Project Structure

```
MyDocWhisper/
├── frontend/                   # Next.js application
│   ├── app/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx      # Streaming chat UI
│   │   │   ├── DocumentUpload.tsx     # Upload component
│   │   │   └── Sidebar.tsx            # Document list sidebar
│   │   ├── globals.css                # Global styles
│   │   ├── layout.tsx                 # Root layout
│   │   └── page.tsx                   # Home page
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                    # FastAPI application
│   ├── main.py                        # API endpoints with streaming
│   ├── rag_pipeline.py                # RAG logic with chat history
│   ├── vector_store.py                # Vector DB abstraction
│   ├── requirements.txt               # Python dependencies
│   └── .env                           # Environment variables (not in Git)
│
├── .gitignore
├── README.md
└── CHANGELOG.md
```

---

## 🔧 API Endpoints

### Backend API (`http://localhost:8000`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check and stats |
| `POST` | `/upload` | Upload and process PDF |
| `POST` | `/chat` | Ask questions (non-streaming) |
| `POST` | `/chat/stream` | Ask questions with streaming response ⚡ |
| `DELETE` | `/document/{documentId}` | Delete a document |
| `GET` | `/documents` | List all documents |
| `GET` | `/stats` | Get system statistics |
| `DELETE` | `/reset` | Clear all documents |

---

## 🧪 How It Works (RAG Pipeline)

```
┌─────────────┐
│ Upload PDF  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Extract Text    │  (pypdf)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Chunk Text      │  (1000 chars, 200 overlap)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Create Vectors  │  (OpenAI embeddings)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Store in DB     │  (ChromaDB)
└─────────────────┘

┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Vector Search   │  (Top 5 similar chunks)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Build Prompt    │  (Context + Chat History + Question)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Stream Answer   │  (GPT-4o-mini, token-by-token)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Return + Cite   │  (Answer + Page numbers + Excerpts)
└─────────────────┘
```

### Key Innovations

1. **Streaming Architecture**: Uses Server-Sent Events (SSE) for real-time response delivery
2. **Context Management**: Last 3 exchanges included in prompts for natural conversations
3. **Citation Enhancement**: Sources include page numbers, filenames, and text excerpts
4. **Error Resilience**: Graceful degradation with helpful error messages

---

## 🔒 Privacy & Security

- **Local Processing**: Documents are processed on your machine
- **Temporary Storage**: No permanent document storage
- **API Keys**: Never committed to Git (`.env` is ignored)
- **No Tracking**: No analytics or user tracking
- **ChromaDB**: Local vector database - your data never leaves your machine

---

## 🎓 What Makes This Special

### For Developers
- ✅ **Modern Stack**: Next.js 14, TypeScript, FastAPI
- ✅ **Best Practices**: Clean code, type safety, error handling
- ✅ **Streaming Implementation**: Real-time SSE with async generators
- ✅ **Context Aware**: Efficient chat history management
- ✅ **Production Ready**: Comprehensive error handling and logging

### For Users
- ⚡ **Instant Feedback**: See responses as they're generated
- 🧠 **Natural Conversations**: No need to repeat context
- 📚 **Transparent Sources**: Always know where information comes from
- 🎨 **Polished UX**: Smooth animations and intuitive interface

---

## 🛠 Troubleshooting

### Backend won't start
- ✅ Check if Python 3.9+ is installed: `python --version`
- ✅ Verify OpenAI API key in `.env` file
- ✅ Install dependencies: `pip install -r requirements.txt`
- ✅ Check for import errors: `python -c "from typing import AsyncGenerator"`

### Frontend won't start
- ✅ Check if Node.js 18+ is installed: `node --version`
- ✅ Delete `node_modules` and reinstall: `npm install`
- ✅ Clear Next.js cache: `rm -rf .next`

### "Backend not responding" error
- ✅ Verify backend is running on port 8000
- ✅ Check CORS settings in `main.py`
- ✅ Look for errors in backend terminal
- ✅ Test endpoint: `curl http://localhost:8000/`

### Streaming not working
- ✅ Ensure using `/chat/stream` endpoint (not `/chat`)
- ✅ Check browser console for JavaScript errors
- ✅ Verify `ChatInterface.tsx` has streaming implementation
- ✅ Test with a simple question first

### Chat history not working
- ✅ Check that history array is being sent in API request
- ✅ Verify backend logs show history being processed
- ✅ Test with: "Who is mentioned?" then "Tell me more about them"

### Documents not uploading
- ✅ Check file size (max 50MB)
- ✅ Verify file is a valid PDF
- ✅ Check backend `uploads/` directory permissions
- ✅ Look for processing errors in backend logs

---

## 📊 Performance

- **Time to First Token**: ~1.5 seconds
- **Full Response Time**: ~8 seconds (depending on answer length)
- **Chunk Size**: 1000 characters (200 overlap)
- **Top-K Retrieval**: 5 most relevant chunks
- **Chat History**: Last 3 exchanges (optimized for cost/performance)
- **Embedding Model**: text-embedding-3-small (1536 dimensions)
- **LLM Model**: GPT-4o-mini (fast and cost-effective)

---

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Ujjwal Raghuvanshi**

Built MyDocWhisper to demonstrate:
- ✅ **Full-Stack Development** (React/Next.js + FastAPI)
- ✅ **AI Engineering** (RAG, Vector Databases, LLM Streaming)
- ✅ **System Design** (Backend architecture, API design)
- ✅ **Product Thinking** (User experience, feature prioritization)
- ✅ **Modern Practices** (TypeScript, async programming, real-time features)

*Portfolio Project showcasing production-ready RAG implementation with advanced features*

---

## 🙏 Acknowledgments

- [LangChain](https://www.langchain.com/) for RAG orchestration
- [OpenAI](https://openai.com/) for GPT-4 and embeddings
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Next.js](https://nextjs.org/) for the frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework

---

## 📧 Contact

Questions or feedback? Feel free to reach out or open an issue!

---

**Status**: ✅ Production Ready (v2.0) | All Features Complete

*Last Updated: January 2025*