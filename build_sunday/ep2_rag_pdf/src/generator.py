import httpx
import ollama
from typing import Dict, Any, Callable
from src.prompts import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT_TEMPLATE
from src.utils import time_it

class Generator:
    """
    Communicates with local Ollama service to generate final response.
    Enforces prompt constraints, manages conversation payloads, and handles error state boundaries.
    """

    def __init__(self, ollama_host: str = "http://localhost:11434", model_name: str = "llama3.2"):
        self.ollama_host = ollama_host
        self.model_name = model_name
        
        # Instantiate Ollama Client
        # Ollama by default listens on port 11434
        print(f"🤖 Initializing Generator client using Ollama model '{self.model_name}'...")
        self.client = ollama.Client(host=self.ollama_host)
        
        # Run a quick check to see if Ollama is online
        self._check_connection()

    def _check_connection(self):
        """Verifies if Ollama server is running and accessible."""
        try:
            # Check server response
            response = httpx.get(f"{self.ollama_host}/api/tags", timeout=2.0)
            if response.status_code == 200:
                print("✅ Local Ollama service is ONLINE.")
                # Check if configured model is downloaded
                models_list = response.json().get("models", [])
                downloaded_names = [m["name"] for m in models_list]
                
                # Check for direct or tag matches (e.g. 'llama3.2:latest' vs 'llama3.2')
                matched = False
                for name in downloaded_names:
                    if self.model_name in name or name in self.model_name:
                        matched = True
                        break
                        
                if not matched:
                    print(f"⚠️ Warning: Model '{self.model_name}' was not detected in local download tags.")
                    print(f"👉 Please run: `ollama pull {self.model_name}` in your terminal before execution.")
            else:
                print(f"⚠️ Warning: Ollama returned status code {response.status_code}.")
        except Exception as e:
            print("❌ Error: Unable to connect to local Ollama service.")
            print(f"👉 Is Ollama running? Start the desktop app or run `ollama serve` in a terminal.")

    @time_it
    def generate_answer(self, context_string: str, query: str, stream_callback: Callable[[str], None] = None) -> str:
        """
        Builds RAG prompt, calls local Ollama LLM, and retrieves grounded answers.
        
        Args:
            context_string: Formatted text chunks of retrieved materials.
            query: User's original search question.
            stream_callback: Optional function to stream character/word updates to CLI.
        Returns:
            The generated response string.
        """
        # Interpolate context and query into templates
        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
            context_data=context_string,
            question=query
        )
        
        try:
            # We use chat completion structure
            messages = [
                {"role": "system", "content": RAG_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
            
            if stream_callback:
                # Handle streaming output for real-time console rendering
                stream = self.client.chat(
                    model=self.model_name,
                    messages=messages,
                    stream=True
                )
                full_response = []
                for chunk in stream:
                    content = chunk["message"]["content"]
                    stream_callback(content)
                    full_response.append(content)
                return "".join(full_response)
            else:
                # Synchronous non-streamed call
                response = self.client.chat(
                    model=self.model_name,
                    messages=messages,
                    stream=False
                )
                return response["message"]["content"]
                
        except Exception as e:
            print(f"\n❌ Error during LLM Generation: {str(e)}")
            return f"Error generating answer. Please check if Ollama is running and has model '{self.model_name}' loaded."

# Self-test when executing generator directly
if __name__ == "__main__":
    # Test generation setup
    gen = Generator()
    print("Testing grounded answer with dummy context:")
    dummy_context = "--- \nSOURCE: [Doc.pdf, Page 1]\nCONTENT: Python was created by Guido van Rossum and released in 1991.\n---"
    dummy_query = "Who created Python and when?"
    
    print("Prompting...", end="", flush=True)
    ans = gen.generate_answer(dummy_context, dummy_query)
    print("\nResult:")
    print(ans)
