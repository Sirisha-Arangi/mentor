# backend/app/services/academic/qa_generator.py
import logging
import json
import re
from typing import List, Dict, Any, Optional
from app.services.rag.chroma_gemini_rag import ChromaGeminiRAG

logger = logging.getLogger(__name__)

class QAGenerator:
    def __init__(self, rag_service: ChromaGeminiRAG):
        self.rag_service = rag_service
        logger.info("Initialized QAGenerator")

    def generate_qa_pairs(
        self, 
        topic: str,
        num_questions: int = 5,
        question_types: List[str] = None,
        difficulty_levels: List[str] = None
    ) -> Dict[str, Any]:
        """Generate question-answer pairs for a specific topic from document content."""
        try:
            if question_types is None:
                question_types = ['conceptual', 'descriptive']
            if difficulty_levels is None:
                difficulty_levels = ['easy', 'medium']
            
            logger.info(f"Generating {num_questions} Q&A pairs for topic: {topic}")
            
            # Multiple search queries to get comprehensive content
            search_queries = [
                f"{topic} definition concept explanation",
                f"{topic} features characteristics properties",
                f"{topic} implementation process methodology",
                f"{topic} advantages benefits disadvantages",
                f"{topic} examples applications use cases"
            ]
            
            all_results = []
            for query in search_queries:
                results = self.rag_service.search(query, k=5)
                all_results.extend(results)
            
            # Remove duplicates and limit results
            unique_results = []
            seen_texts = set()
            for result in all_results:
                if result["text"] not in seen_texts:
                    unique_results.append(result)
                    seen_texts.add(result["text"])
            
            results = unique_results[:20]  # Limit to top 20 unique chunks
            
            if not results:
                return {
                    "success": False,
                    "error": f"No relevant content found for topic: {topic}",
                    "qa_pairs": []
                }
            
            # Extract relevant content
            context = "\n\n".join([r["text"] for r in results])
            
            # Generate Q&A pairs with very specific prompt
            prompt = f"""You are creating educational questions about "{topic}" based ONLY on the following document content.

DOCUMENT CONTENT:
{context}

TASK: Create exactly {num_questions} UNIQUE question-answer pairs specifically about "{topic}".

REQUIREMENTS:
1. Each question MUST be about "{topic}" specifically
2. Questions must be DIFFERENT from each other
3. Use these question types: {', '.join(question_types)}
4. Mix these difficulty levels: {', '.join(difficulty_levels)}
5. Answers must come DIRECTLY from the document content above
6. Do NOT create generic questions - make them specific to "{topic}"

EXAMPLES OF GOOD QUESTIONS:
- "What are the key components of {topic}?"
- "How does {topic} work in practice?"
- "What are the main advantages of using {topic}?"

RETURN ONLY VALID JSON:
{{
    "qa_pairs": [
        {{
            "question": "Specific question about {topic}",
            "answer": "Answer from document content",
            "type": "conceptual",
            "difficulty": "easy",
            "topic": "{topic}"
        }}
    ]
}}"""

            response = self.rag_service.generate(prompt)
            logger.info(f"Generated response length: {len(response)}")
            
            # Try to extract JSON from response
            qa_pairs = self._extract_qa_from_response(response, topic, num_questions)
            
            if qa_pairs:
                logger.info(f"Successfully extracted {len(qa_pairs)} Q&A pairs")
                return {
                    "success": True,
                    "qa_pairs": qa_pairs,
                    "topic": topic,
                    "total_questions": len(qa_pairs),
                    "difficulty_distribution": self._calculate_difficulty_distribution(qa_pairs),
                    "topics_covered": [topic],
                    "source_chunks_used": len(results)
                }
            else:
                logger.error(f"Failed to extract Q&A pairs. Response: {response}")
                return {
                    "success": False,
                    "error": "Failed to generate valid Q&A pairs",
                    "raw_response": response[:500] + "..." if len(response) > 500 else response,
                    "qa_pairs": []
                }
                
        except Exception as e:
            error_msg = f"Error generating Q&A pairs: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg,
                "qa_pairs": []
            }

    def _extract_qa_from_response(self, response: str, topic: str, num_questions: int) -> List[Dict]:
        """Extract Q&A pairs from LLM response with multiple fallback methods"""
        try:
            # Clean response
            response = response.strip()
            
            # Method 1: Try to parse as JSON directly
            if response.startswith('{') or response.startswith('['):
                try:
                    data = json.loads(response)
                    if "qa_pairs" in data and isinstance(data["qa_pairs"], list):
                        return data["qa_pairs"][:num_questions]
                    elif isinstance(data, list):
                        return data[:num_questions]
                except json.JSONDecodeError:
                    logger.warning(f"JSON parsing failed, trying other methods")
            
            # Method 2: Extract JSON from markdown code blocks
            json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            json_matches = re.findall(json_pattern, response, re.DOTALL | re.IGNORECASE)
            for match in json_matches:
                try:
                    data = json.loads(match)
                    if "qa_pairs" in data and isinstance(data["qa_pairs"], list):
                        return data["qa_pairs"][:num_questions]
                except json.JSONDecodeError:
                    continue
            
            # Method 3: Find JSON object in response
            json_obj_pattern = r'\{[^{}]*"qa_pairs"[^{}]*\}'
            json_matches = re.findall(json_obj_pattern, response, re.DOTALL)
            for match in json_matches:
                try:
                    data = json.loads(match)
                    if "qa_pairs" in data and isinstance(data["qa_pairs"], list):
                        return data["qa_pairs"][:num_questions]
                except json.JSONDecodeError:
                    continue
            
            # Method 4: Manual extraction using regex for Q&A patterns
            qa_pairs = []
            
            # Pattern for question-answer pairs
            qa_patterns = [
                r'question["\s]*:\s*"([^"]+)"\s*answer["\s]*:\s*"([^"]*)"',
                r'"question"\s*:\s*"([^"]+)"\s*"answer"\s*:\s*"([^"]*)"',
                r'question:\s*([^\n]+)\nanswer:\s*([^\n]+)',
                r'Q:\s*([^\n]+)\nA:\s*([^\n]+)'
            ]
            
            for pattern in qa_patterns:
                matches = re.findall(pattern, response, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if len(match) >= 2:
                        qa_pairs.append({
                            "question": match[0].strip(),
                            "answer": match[1].strip(),
                            "type": "conceptual",
                            "difficulty": "medium",
                            "topic": topic
                        })
                
                if qa_pairs:
                    break
            
            # Method 5: Line-by-line extraction
            if not qa_pairs:
                lines = response.split('\n')
                current_qa = {}
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    # Look for question indicators
                    if any(keyword in line.lower() for keyword in ['question', 'what is', 'describe', 'explain', 'how', 'why']):
                        if ':' in line:
                            question = line.split(':', 1)[1].strip()
                        else:
                            question = line.strip()
                        
                        if question and len(question) > 10:  # Valid question
                            current_qa['question'] = question
                            current_qa['type'] = self._determine_question_type(question)
                            current_qa['difficulty'] = 'medium'
                            current_qa['topic'] = topic
                            
                            # Look for answer in next few lines
                            answer_lines = []
                            for j in range(i + 1, min(i + 5, len(lines))):
                                next_line = lines[j].strip()
                                if next_line and not any(keyword in next_line.lower() for keyword in ['question', 'what is', 'describe', 'explain', 'how', 'why']):
                                    answer_lines.append(next_line)
                                elif any(keyword in next_line.lower() for keyword in ['question', 'what is', 'describe', 'explain', 'how', 'why']):
                                    break
                            
                            if answer_lines:
                                current_qa['answer'] = ' '.join(answer_lines).strip()
                                qa_pairs.append(current_qa.copy())
                                current_qa = {}
                            
                            if len(qa_pairs) >= num_questions:
                                break
            
            # Ensure we have the requested number of questions
            return qa_pairs[:num_questions] if qa_pairs else []
            
        except Exception as e:
            logger.error(f"Error extracting Q&A from response: {str(e)}")
            return []

    def _determine_question_type(self, question: str) -> str:
        """Determine question type based on question content"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['what is', 'define', 'explain the concept', 'describe the concept']):
            return 'conceptual'
        elif any(word in question_lower for word in ['describe', 'explain', 'how does', 'why does', 'what are the']):
            return 'descriptive'
        elif any(word in question_lower for word in ['how would you', 'apply', 'implement', 'use', 'solve']):
            return 'application'
        else:
            return 'conceptual'

    def _calculate_difficulty_distribution(self, qa_pairs: List[Dict]) -> Dict[str, int]:
        """Calculate difficulty distribution"""
        distribution = {"easy": 0, "medium": 0, "hard": 0}
        for qa in qa_pairs:
            difficulty = qa.get("difficulty", "medium").lower()
            if difficulty in distribution:
                distribution[difficulty] += 1
        return distribution