import json
from sqlalchemy.orm import Session
from backend.services.ollama_service import OllamaService
from backend.tools.executor import ToolExecutor
from backend.tools.registry import ToolRegistry
from backend.database.models import ToolExecution

class AgentOrchestrator:
    def __init__(self, ollama: OllamaService, executor: ToolExecutor, registry: ToolRegistry):
        self.ollama = ollama
        self.executor = executor
        self.registry = registry

    async def process_message(self, question: str, conversation_id: int, db: Session, ollama_url: str, model_name: str) -> dict:
        """
        Orchestration flow:
        1. Receive user question
        2. Load available tools
        3. Ask Gemma which tools are needed
        4. Execute tools
        5. Collect results
        6. Send results back to Gemma
        7. Generate final answer
        """
        # 2. Get available tools
        available_tools = self.registry.get_tools_for_llm()

        # 3. Ask Gemma for tool selection
        selection_json = await self.ollama.generate_tool_selection(question, available_tools, ollama_url, model_name)
        
        tool_calls = selection_json.get("tool_calls", [])
        tool_results = []

        # 4 & 5. Execute tools and collect results
        for call in tool_calls:
            tool_name = call.get("tool")
            arguments = call.get("arguments", {})
            
            result = await self.executor.execute_tool(tool_name, arguments)
            tool_results.append(result)
            
            # Log tool execution to database
            db_exec = ToolExecution(
                conversation_id=conversation_id,
                tool_name=tool_name,
                arguments=arguments,
                response=result.get("response", {}),
                execution_time_ms=result.get("execution_time_ms", 0)
            )
            db.add(db_exec)
            db.commit()

        # 6 & 7. Generate final answer
        if tool_results:
            final_answer = await self.ollama.generate_final_response(question, tool_results, ollama_url, model_name)
        else:
            # If no tools were called, ask Ollama directly
            final_answer = await self.ollama.generate_final_response(question, [{"note": "No external tools were needed."}], ollama_url, model_name)

        return {
            "answer": final_answer,
            "tool_calls": tool_calls,
            "tool_results": tool_results
        }
