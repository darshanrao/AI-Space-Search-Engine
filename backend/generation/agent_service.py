"""
Agent Service - LangChain ReAct Agent for intelligent RAG usage.
This service decides when to use RAG and when to rely on LLM knowledge.
"""

from typing import Dict, Any, List, Tuple, Optional
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage

from models import RAGResponse, ImageCitation
from settings import settings
from .rag_tool import RAGSearchTool


class AgentService:
    """Service that uses LangChain ReAct agent to intelligently decide when to use RAG."""
    
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1,  # Lower temperature for more consistent reasoning
            max_output_tokens=settings.MAX_RESPONSE_TOKENS  # Use full token limit
        )
        
        # Create the RAG tool
        self.rag_tool = RAGSearchTool()
        
        # Create the ReAct agent
        self.agent = self._create_agent()
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=[self.rag_tool],
            verbose=False,  # Disable verbose to reduce output
            max_iterations=3,  # Balanced iterations
            early_stopping_method="generate",  # Use generate for better responses
            handle_parsing_errors=True,
            max_execution_time=20  # Reduced time limit for faster responses
        )
    
    def _create_agent(self):
        """Create the ReAct agent with custom prompt."""
        
        # Custom prompt template for space biology context
        prompt = PromptTemplate.from_template("""
You are a Space Biology Research Assistant with access to a specialized research database. Your role is to help researchers with questions about space biology, including effects of microgravity, space radiation, life support systems, and biological experiments in space.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT GUIDELINES:
1. FIRST, analyze the question to determine if you already know the answer from your training data.
2. Use the search tool ONLY when:
   - You need specific research findings from published space biology studies
   - The question asks for experimental data, results, or methodologies from research papers
   - You need citations from the 608 PubMed Central space biology publications (2010-present)
   - The question is about specific organisms, experiments, or studies in space biology
   - You need authoritative sources from peer-reviewed research

3. DO NOT use the search tool for:
   - General scientific concepts you already know well (e.g., "What is DNA?", "What is gravity?")
   - Basic definitions or fundamental principles
   - Simple factual questions you can answer confidently
   - Questions about general space exploration or NASA history
   - Follow-up questions where you already have sufficient context from previous responses

4. Provide complete but concise answers. Be thorough enough to fully address the question without unnecessary details.

5. When you do use the search tool, provide a complete answer with proper citations.

Current conversation context:
{chat_history}

Question: {input}
Thought: I need to think about whether this question requires searching the space biology corpus or if I can answer it from my existing knowledge.
{agent_scratchpad}
""")
        
        return create_react_agent(
            llm=self.llm,
            tools=[self.rag_tool],
            prompt=prompt
        )
    
    def generate_answer(self, question: str, context: Dict[str, Any], conversation_history: List[Tuple[str, str]] = None) -> RAGResponse:
        """
        Generate an answer using the ReAct agent that decides when to use RAG.
        
        Args:
            question: User's question
            context: Additional context (organism, focus area, etc.)
            conversation_history: Previous conversation messages
            
        Returns:
            RAGResponse with answer and metadata
        """
        try:
            # Format conversation history for the agent
            chat_history = ""
            if conversation_history:
                chat_history_parts = []
                for role, content in conversation_history[-5:]:  # Last 5 messages for context
                    if role == "user":
                        chat_history_parts.append(f"Human: {content}")
                    elif role == "assistant":
                        chat_history_parts.append(f"Assistant: {content}")
                chat_history = "\n".join(chat_history_parts)
            
            # Add context information to the question
            contextualized_question = question
            if context.get("organism"):
                contextualized_question = f"[Context: {context['organism']}] {question}"
            if context.get("focus"):
                contextualized_question = f"[Focus: {context['focus']}] {contextualized_question}"
            
            # Run the agent
            result = self.agent_executor.invoke({
                "input": contextualized_question,
                "chat_history": chat_history
            })
            
            # Extract the final answer
            final_answer = result.get("output", "")
            
            # Parse the agent's response to extract citations if any
            citations = []
            image_citations = []
            confidence_score = 85  # Default confidence for agent responses
            
            # Look for citations in the response
            if "SOURCES" in final_answer:
                # Extract citations from the search results
                lines = final_answer.split('\n')
                in_sources = False
                for line in lines:
                    if line.startswith("SOURCES"):
                        in_sources = True
                        continue
                    elif in_sources and line.strip().startswith('[') and ']' in line:
                        # Extract URL from citation line like "[1] https://..."
                        try:
                            url = line.split(']', 1)[1].strip()
                            if url.startswith('http'):
                                citations.append(url)
                        except:
                            pass
                    elif in_sources and line.strip() and not line.startswith('['):
                        # End of sources section
                        break
            
            # Clean up the answer by removing search metadata
            clean_answer = final_answer
            if "SEARCH RESULTS:" in clean_answer:
                clean_answer = clean_answer.split("SEARCH RESULTS:", 1)[1]
            if "SOURCES" in clean_answer:
                clean_answer = clean_answer.split("SOURCES")[0].strip()
            if "Confidence Score:" in clean_answer:
                clean_answer = clean_answer.split("Confidence Score:")[0].strip()
            
            # Remove any remaining agent reasoning artifacts
            clean_answer = clean_answer.replace("Thought:", "").replace("Action:", "").replace("Observation:", "")
            clean_answer = clean_answer.strip()
            
            return RAGResponse(
                answer_markdown=clean_answer,
                citations=citations,
                image_citations=image_citations,
                image_urls=[],  # Agent doesn't handle image search directly
                confidence_score=confidence_score
            )
            
        except Exception as e:
            print(f"Agent execution failed: {str(e)}")
            # Fallback to direct RAG if agent fails
            return self._fallback_to_rag(question, context, conversation_history)
    
    def _fallback_to_rag(self, question: str, context: Dict[str, Any], conversation_history: List[Tuple[str, str]] = None) -> RAGResponse:
        """Fallback to direct RAG if agent fails."""
        try:
            # Import here to avoid circular imports
            from .api import query_rag_json
            
            result = query_rag_json(question)
            
            citations = result.get("citations", [])
            image_citations = []
            for img_citation in result.get("image_citations", []):
                image_citations.append(ImageCitation(
                    id=img_citation.get("id", ""),
                    url=img_citation.get("url", ""),
                    why_relevant=img_citation.get("why_relevant", "")
                ))
            
            return RAGResponse(
                answer_markdown=result.get("answer_markdown", ""),
                citations=citations,
                image_citations=image_citations,
                image_urls=result.get("image_urls", []),
                confidence_score=result.get("confidence_score", 0)
            )
            
        except Exception as e:
            # Ultimate fallback
            return RAGResponse(
                answer_markdown=f"I apologize, but I'm having trouble generating a response right now. Please try again later. Error: {str(e)}",
                citations=[],
                image_citations=[],
                image_urls=[],
                confidence_score=0
            )


# Global agent service instance
agent_service = AgentService()
