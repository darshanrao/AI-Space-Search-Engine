# 🌌 AstroBio Explorer

Welcome to **AstroBio Explorer**, our submission for the **2025 NASA Space Apps Challenge** (Build a Space Biology Knowledge Engine).
Our project is designed to help scientists, researchers and space enthusiasts explore decades of NASA’s bioscience research through a smart, conversational interface.

---

## 🌟 Inspiration

Space biology research is full of valuable knowledge, but it’s scattered across hundreds of dense publications. Finding the right information or making sense of it quickly can be overwhelming.

We wanted to build something that feels like **talking to a knowledgeable research assistant**. You ask a question and instead of giving you a vague summary, the assistant provides context-rich answers with proper citations, relevant images and links to papers.

The goal was simple: make space bioscience literature **easier to explore, understand and build upon**.

---

## 🧠 What It Does

AstroBio Explorer is a **conversational research assistant** for space biology.

* You ask scientific questions in natural language.
* It finds relevant NASA bioscience papers, retrieves key information using a RAG pipeline and generates detailed, citation-backed answers.
* Each answer includes inline citations with clickable links so you can jump straight to the source.
* Related images are fetched dynamically and displayed in a sidebar.
* You can open **multiple chat sessions**, save context, and explore follow-up questions just like you would with a human expert.
* A special **Google Scholar mode** finds similar papers using SERP API, giving you an extra layer of relevant academic context.
* All interactions are stored so the assistant can maintain context over longer sessions.

---

## 🏗 How We Built It

We designed a clear pipeline to keep things modular and efficient.

### ✨ Core Stack

* **Frontend:** Next.js + Tailwind CSS + SCSS animations for a smooth and space-themed UI
* **Backend:** FastAPI + LangChain + Gemini 2.5 Flash model for fast and contextual responses
* **Vector Store:** Qdrant for chunk storage and semantic retrieval
* **APIs:**

  * SERP API for Google Scholar paper recommendations
  * SERP Image API for relevant images
* **Database:** Supabase Postgres for storing user sessions and chat context

### 🧰 Pipeline

1. **User Query** → comes from the frontend chat UI
2. **RAG Pipeline** → query is embedded, searched in Qdrant, and relevant chunks are retrieved
3. **LLM Response** → LangChain + Gemini model generate a passage-style answer with inline citations
4. **Enrichment** → Google Scholar API fetches similar papers, SERP image API fetches relevant visuals
5. **Frontend Display** → answer + citations inline, related images in a sidebar, scholar links in a separate tab

 <!-- Replace with actual image path -->
 <img width="520" height="422" alt="nasa" src="https://github.com/user-attachments/assets/599bf7a1-f250-438e-9bbf-e350a0f7e21b" />


---

## ⚡ Challenges We Ran Into

One of the biggest challenges was **making the chatbot feel genuinely useful for researchers**. It wasn’t enough to just retrieve data. We had to get **citations right**, display images properly, maintain session context, and make sure the RAG pipeline produced meaningful long-form answers.

Handling citation linking and ensuring images didn’t break the layout took careful planning on the frontend. We also faced issues with connection pooling (PgBouncer) when scaling the chatbot, which led us to rethink database connection management for production.

---

## 🏆 Accomplishments We’re Proud Of

* Built a fully working research chatbot with context storage and multi-session support
* Achieved **83% answer quality** in our evaluation
* Designed a UI that makes scientific exploration feel natural and interactive
* Integrated SERP APIs to extend beyond just NASA papers
* Added inline citations and image sidebars that make responses richer and more trustworthy

---

## 📚 What We Learned

We learned how to combine RAG pipelines with conversational UI in a way that feels natural to scientists. Storing session context in Supabase made it possible to build genuine back-and-forth conversations.

We also realized the importance of **good retrieval**. Answer quality depends heavily on what documents you find, so tuning chunking and vector search parameters became a major focus.

---

## 🚀 What’s Next

* A **Research Mode** with deeper context windows, longer answers, and advanced scholar recommendations
* Integration of **knowledge graphs** for better relationship exploration
* Support for richer media like interactive figures or tables from papers
* Improving retrieval quality using better chunking strategies and hybrid search
* Deploying the system so anyone can try it during and after the hackathon

---

## 🧪 Evaluation Overview

We tested AstroBio Explorer on **real scientific literature**, not just toy data.

* **181 questions** tested
* Across **42 space biology research papers**
* Evaluation covered **retrieval**, **answer quality**, and **citations**

### Results

* **Overall Score:** 72%
  (Weighted across retrieval, answer quality, and citation accuracy)

| Component         | Score | Notes                                              |
| ----------------- | ----- | -------------------------------------------------- |
| Answer Quality    | 83%   | Excellent factual alignment with expert answers    |
| Citation Accuracy | 70%   | Sources are relevant and properly linked           |
| Retrieval Quality | 59%   | Good, but has room to improve on broader questions |

**Formula:**

```
Overall = 35% × Retrieval + 45% × Answer Quality + 20% × Citations
```

---

### Performance by Question Type

| Question Type        | Score |
| -------------------- | ----- |
| Specific questions   | 79%   |
| Comparative analysis | 77%   |
| Factual queries      | 73%   |
| Complex reasoning    | 69%   |
| Broad overviews      | 60%   |

It performs best on targeted scientific questions, which is exactly where researchers need strong support.

---

### Top Performance Areas

* Medical case studies – 89%
* Space agriculture research – 86%
* Plant imaging systems – 88%
* FAIR data systems – 88%

---

## 🧰 Built With

* **Next.js**
* **Tailwind CSS**
* **SCSS animations**
* **FastAPI**
* **LangChain**
* **Gemini 2.5 Flash Model**
* **Qdrant**
* **Supabase**
* **SERP API (Google Scholar & Images)**

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

This starts the FastAPI server at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

This starts the frontend on `http://localhost:3000`. Open this URL in your browser to chat with AstroBio Explorer.

---

## 📂 Project Structure

```
.
├── backend        # FastAPI + LangChain + Gemini chatbot + RAG pipeline
├── frontend       # Next.js + Tailwind CSS UI
├── evaluation     # Evaluation scripts, metrics, and results
```

---

## 👩‍🚀 Meet AstroBio Explorer

AstroBio Explorer is more than a chatbot. It’s a research companion built for space biology. Whether you’re a scientist, student, or just curious about life beyond Earth, you can ask real questions and get meaningful, well-cited answers.

