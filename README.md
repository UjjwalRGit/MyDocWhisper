# MyDocWhisper 🗣️📄

> Transform static PDFs into interactive conversations with AI-powered document analysis

An intelligent RAG (Retrieval-Augmented Generation) application that allows users to upload PDF documents and chat with them using natural language. Built with Next.js, FastAPI, and OpenAI's GPT-4.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)

---

## 🎯 What It Does

**The Problem**: Knowledge is trapped in documents. Standard search (Ctrl+F) only finds keywords, not answers. ChatGPT is great, but it doesn't know your private data.

**The Solution**: MyDocWhisper bridges that gap by:
- 📤 Accepting your PDF documents
- 🧠 Understanding the content using AI
- 💬 Answering questions in natural language
- 📍 Citing exact page numbers for every answer
- 🛡️ Preventing AI hallucinations through grounding

---

## ✨ Features

### Phase 1 (Current) ✅
- **Drag-and-Drop Upload**: Intuitive PDF document upload interface
- **Intelligent Chunking**: Documents split into meaningful segments
- **Vector Search**: Semantic understanding beyond keyword matching
- **AI-Powered Answers**: GPT-4o-mini generates accurate responses
- **Source Citations**: Every answer includes page references
- **Document Management**: Sidebar for managing multiple documents
- **Modern UI**: Dark-themed, responsive interface with Tailwind CSS

### Phase 2 (Planned) 🚧
- **Streaming Responses**: Real-time "typewriter effect" for answers
- **Enhanced Citations**: Click to highlight source text
- **Chat History**: Context-aware conversations
- **Multi-turn Conversations**: AI remembers previous questions

### Phase 3 (Future) 📅
- **Source Control Dashboard**: Manage documents in vector database
- **Prompt Inspection**: Debug mode to view retrieval context
- **Hybrid Search**: Combine keyword + semantic search
- **Production Database**: Migration from ChromaDB to Supabase

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
- **AI/LLM**: OpenAI GPT-4o-mini
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
4. **Wait for Processing**: The document will be chunked and embedded
5. **Start Chatting**: Ask questions about your document
6. **View Citations**: Click on page badges to see sources

### Example Questions
- "What is this document about?"
- "Summarize the key points"
- "What does it say about [specific topic]?"
- "Who are the main stakeholders mentioned?"

---

## 📂 Project Structure

```
MyDocWhisper/
├── frontend/                   # Next.js application
│   ├── app/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx      # Chat UI component
│   │   │   ├── DocumentUpload.tsx     # Upload component
│   │   │   └── Sidebar.tsx            # Document list sidebar
│   │   ├── globals.css                # Global styles
│   │   ├── layout.tsx                 # Root layout
│   │   └── page.tsx                   # Home page
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                    # FastAPI application
│   ├── main.py                        # API endpoints
│   ├── rag_pipeline.py                # RAG logic
│   ├── vector_store.py                # Vector DB abstraction
│   ├── requirements.txt               # Python dependencies
│   └── .env                           # Environment variables (not in Git)
│
├── .gitignore
└── README.md
```

---

## 🔧 API Endpoints

### Backend API (`http://localhost:8000`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check and stats |
| `POST` | `/upload` | Upload and process PDF |
| `POST` | `/chat` | Ask questions about documents |
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
│ Build Prompt    │  (Context + Question)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Generate Answer │  (GPT-4o-mini)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Return + Cite   │  (Answer + Page numbers)
└─────────────────┘
```

---

## 🔒 Privacy & Security

- **Local Processing**: Documents are processed on your machine
- **Temporary Storage**: No permanent document storage
- **API Keys**: Never committed to Git (`.env` is ignored)
- **No Tracking**: No analytics or user tracking

---

## 🎓 Development Roadmap

- [x] **Phase 1**: Core RAG pipeline ✅
  - [x] PDF upload and processing
  - [x] Text extraction and chunking
  - [x] Vector embeddings and storage
  - [x] Basic Q&A with citations
  - [x] Modern UI/UX

- [ ] **Phase 2**: Intelligence Layer 🚧
  - [ ] Streaming responses (typewriter effect)
  - [ ] Enhanced citations (clickable, highlighted)
  - [ ] Chat history (context awareness)
  - [ ] Multi-turn conversations

- [ ] **Phase 3**: Production Ready 📅
  - [ ] Document management dashboard
  - [ ] Prompt inspection/debugging
  - [ ] Hybrid search (keyword + semantic)
  - [ ] Supabase integration
  - [ ] Deployment (Vercel + Railway)

---

## 🐛 Troubleshooting

### Backend won't start
- ✅ Check if Python 3.9+ is installed: `python --version`
- ✅ Verify OpenAI API key in `.env` file
- ✅ Install dependencies: `pip install -r requirements.txt`

### Frontend won't start
- ✅ Check if Node.js 18+ is installed: `node --version`
- ✅ Delete `node_modules` and reinstall: `npm install`
- ✅ Clear Next.js cache: `rm -rf .next`

### "Backend not responding" error
- ✅ Verify backend is running on port 8000
- ✅ Check CORS settings in `main.py`
- ✅ Look for errors in backend terminal

### Documents not uploading
- ✅ Check file size (max 50MB)
- ✅ Verify file is a valid PDF
- ✅ Check backend `uploads/` directory permissions

---

## 📊 Performance

- **Time to First Token**: < 2 seconds
- **Chunk Size**: 1000 characters (200 overlap)
- **Top-K Retrieval**: 5 most relevant chunks
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

**Bhaskar (Ujjwal Raghuvanshi)**

Building MyDocWhisper as a portfolio project to demonstrate:
- ✅ Full-Stack Development (React/Next.js + FastAPI)
- ✅ AI Engineering (RAG, Vector Databases, LLMs)
- ✅ System Design (Backend architecture, API design)
- ✅ Product Thinking (User experience, feature prioritization)

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

**Status**: Phase 1 Complete ✅ | Phase 2 In Planning 🚧

*Last Updated: January 2026*