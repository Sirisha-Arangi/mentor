# backend/app/services/academic/flashcard_generator.py

import logging
from typing import List, Dict, Any, Optional
from app.services.rag.langchain_rag import LangChainRAG

logger = logging.getLogger(__name__)


class FlashcardGenerator:
    def __init__(self, rag_service: LangChainRAG):
        self.rag_service = rag_service
        logger.info("Initialized FlashcardGenerator")

    def generate_flashcards(
        self,
        topic: str,
        num_cards: int = 10,
        difficulty: str = "medium",
        card_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate flashcards for a specific topic from document content.
        """
        if card_types is None:
            card_types = ["definition", "concept", "application"]

        logger.info(f"Generating {num_cards} flashcards for topic: {topic}")

        # ------------------ SEARCH PHASE ------------------
        search_queries = [
            f"{topic} definitions concepts",
            f"{topic} key terms terminology",
            f"{topic} applications examples",
            f"{topic} important principles"
        ]

        all_results = []
        for query in search_queries:
            results = self.rag_service.search(query, k=5)
            all_results.extend(results)

        # ------------------ REMOVE DUPLICATES ------------------
        unique_results = []
        seen_texts = set()

        for result in all_results:
            text = result.get("text", "").strip()
            if text and text not in seen_texts:
                unique_results.append(result)
                seen_texts.add(text)

        results = unique_results[:15]

        if not results:
            return {
                "success": False,
                "error": f"No relevant content found for topic: {topic}",
                "flashcards": []
            }

        # ------------------ CONTEXT ------------------
        context = "\n\n".join(r["text"] for r in results)

        prompt = f"""
Create {num_cards} flashcards about {topic} based on the context below.

Context:
{context}

Each flashcard MUST contain exactly:
Question:
Answer:
Type:

Repeat this format {num_cards} times.
"""

        # ------------------ GENERATION ------------------
        response = self.rag_service.generate(prompt)
        logger.info(f"Generated response length: {len(response)}")

        # ------------------ PARSING ------------------
        flashcards = []
        blocks = response.split("Question:")

        for idx, block in enumerate(blocks[1:], start=1):
            try:
                question_part = block.strip()

                answer = ""
                card_type = "definition"

                if "Answer:" in question_part:
                    question, rest = question_part.split("Answer:", 1)
                else:
                    continue

                if "Type:" in rest:
                    answer, type_part = rest.split("Type:", 1)
                    card_type = type_part.strip().lower()
                else:
                    answer = rest.strip()

                flashcards.append({
                    "id": idx,
                    "question": question.strip(),
                    "answer": answer.strip(),
                    "type": card_type if card_type in card_types else "concept",
                    "difficulty": difficulty,
                    "topic": topic
                })

                if len(flashcards) >= num_cards:
                    break

            except Exception as e:
                logger.warning(f"Skipping malformed flashcard block: {str(e)}")
                continue

        # ------------------ FINAL RESPONSE ------------------
        if not flashcards:
            return {
                "success": False,
                "error": "Failed to parse flashcards from model output",
                "flashcards": []
            }

        return {
            "success": True,
            "flashcards": flashcards,
            "topic": topic,
            "total_cards": len(flashcards),
            "difficulty_level": difficulty,
            "card_types_used": card_types,
            "source_chunks_used": len(results)
        }

    def guess_card_type(self, question: str, card_types: List[str]) -> str:
        """Guess the card type based on question content"""
        question_lower = question.lower()
        for card_type in card_types:
            if card_type in question_lower:
                return card_type
        return "concept"
