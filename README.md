# 🧠🚀 AstroBio Explorer

AstroBio Explorer is our AI-powered research assistant built for the **NASA Space Apps Challenge 2025**.
It helps anyone explore NASA’s space biology research in a simple, conversational, and interactive way.

---

## 🌟 Inspiration

NASA has been studying how life behaves beyond Earth for decades. From how plants grow in space to how microgravity affects the human body, the knowledge is incredible.
But it’s buried inside hundreds of research papers that are hard to search and connect.

We wanted to make that exploration feel natural, like having a conversation with a scientist who knows exactly where to look. That’s why we built AstroBio Explorer.

---

## 🧭 What It Does

AstroBio Explorer turns complex scientific literature into a friendly research companion. Here’s what you can do inside it:

* 🧠 **Ask research questions** in plain language and get clear, well-grounded answers from NASA bioscience papers
* 🔗 **See inline citations** with clickable links to original publications
* 📄 **Explore related Google Scholar papers** using SerpAPI
* 🖼 **View relevant images** tied to your question in a sidebar
* 💬 **Keep multiple research threads open** using multi-session chat

It doesn’t just give you a block of text. It brings together papers, citations, images, and related work so you can truly explore a topic.

---

## 🛠 How We Built It

We structured AstroBio Explorer into three main parts working together.

### 🧠 Backend (RAG + AI)

* Built with **FastAPI**, **LangChain**, and **Gemini 2.5 Flash**
* Parsed and chunked **606 NASA bioscience articles** at the sentence level
* Generated dense and sparse embeddings and stored them in **Qdrant** for fast retrieval
* Used a small agent system to combine the RAG pipeline with **Google Scholar** and **image search**, merging multiple sources for each response

### 🖥 Frontend (UI/UX)

* Built with **Next.js** and **Tailwind CSS**
* Clean chat interface with **SCSS and Haml animations** for a smooth space-themed feel
* Citations appear inline inside chat bubbles
* Images are shown in a sidebar for visual context
* Includes a “Google Scholar” button to fetch related papers
* Supports multiple chat sessions so users can explore different topics simultaneously

### 🧱 Data Layer

* Vector DB: **Qdrant**, storing each chunk with metadata like paper ID, section, and URL for precise citation linking
* Context + session storage: **Supabase Postgres**, for multi-turn conversations and persistent threads

---

## 🪄 Pipeline Overview

<img width="520" height="422" alt="nasa" src="https://github.com/user-attachments/assets/054bfeea-19e5-4a84-9cf4-f53ab66b06fb" />

---

## 🚧 Challenges We Ran Into

* Finding the **right chunk size** to keep answers precise without slowing the system
* Placing **inline citations** at exactly the right spots in the generated text
* Coordinating **Gemini**, **Qdrant**, and **SerpAPI** in a single pipeline
* Designing a **UI** that could handle citations, media, and multiple threads without feeling cluttered

---

## 🏆 Accomplishments We're Proud Of

* Built a working research assistant that connects **NASA data**, **Google Scholar**, and **images** in one conversational interface
* Added **inline citations** that link directly to real papers
* Enabled **multi-session research chats** for parallel exploration
* Designed a **modular backend** that can easily be extended with more tools later

---

## 📚 What We Learned

* How to combine different AI components into a smooth, useful experience
* The importance of **chunking and retrieval** when working with real scientific literature
* How to shape LLM outputs into structured answers that are actually useful for research
* How to design frontend components that gracefully handle citations, references, and visual content

---

## 🚀 What’s Next for AstroBio Explorer

* A **Research Mode** with longer, more detailed answers and expanded context
* **Visual knowledge graphs** that show how concepts connect across studies
* **Hypothesis generation** and **exportable research briefs**
* Direct integration with NASA’s open data repositories for richer exploration

---

## 🧰 Built With

* Next.js
* Tailwind CSS
* SCSS + Haml animations
* FastAPI
* LangChain
* Gemini 2.5 Flash
* Qdrant
* Supabase
* SerpAPI (Google Scholar + Images)

---

## 🧪 Evaluation Overview

We tested AstroBio Explorer on **real NASA space biology literature** to measure how well it retrieves, cites, and answers scientific questions.

* **181 questions**
* **42 research papers**
* Evaluation measured **retrieval**, **answer quality**, and **citation accuracy**

### Results

* **Overall Score:** 72%
  (Weighted across retrieval, answer quality, and citation accuracy)

| Component         | Score | Notes                                           |
| ----------------- | ----- | ----------------------------------------------- |
| Answer Quality    | 83%   | Excellent factual alignment with expert answers |
| Citation Accuracy | 70%   | Good relevance and proper linking               |
| Retrieval Quality | 59%   | Good but room for broader document recall       |

**Formula:**

```
Overall = 35% × Retrieval + 45% × Answer Quality + 20% × Citations
```

### Performance by Question Type

| Question Type        | Score |
| -------------------- | ----- |
| Specific questions   | 79%   |
| Comparative analysis | 77%   |
| Factual queries      | 73%   |
| Complex reasoning    | 69%   |
| Broad overviews      | 60%   |

AstroBio Explorer excels at **targeted scientific questions**, which is where researchers benefit most.

### Top Performance Areas

* Medical case studies – 89%
* Space agriculture research – 86%
* Plant imaging systems – 88%
* FAIR data systems – 88%

---

## 🧭 How to Run the Project

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

* Backend runs on `http://localhost:8000`
* Frontend runs on `http://localhost:3000`

---

## 📂 Project Structure

```
.
├── backend        # FastAPI + LangChain + Gemini chatbot + RAG pipeline
├── frontend       # Next.js + Tailwind CSS UI
├── evaluation     # Evaluation scripts, metrics, and results
```

---

## 👨‍🚀 Meet AstroBio Explorer

AstroBio Explorer is more than a chatbot. It’s a research companion designed to make space bioscience accessible and explorable.
Whether you’re a scientist, a student, or just curious about how life thrives beyond Earth, AstroBio Explorer lets you **ask real questions and get meaningful, research-backed answers**.

