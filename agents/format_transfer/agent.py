import sys
from pathlib import Path
from typing import Dict, Any, Optional

from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk, ToolMessage

from llm import LLM, get_default_config_path
from promopt import SYSTEM_PROMPT
from tools import fastq2fasta, index_fasta


sys.path.insert(0, str(Path(__file__).parent.parent))
from public_tools import create_output_dir, create_workdir, zip_directory


class FormatTransferAgent:
    """Agent for bioinformatics file format conversion."""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        debug: bool = False
    ):
        """Initialize the format transfer agent.
        
        Args:
            config_path: Path to config file. Uses default if None.
            debug: Enable debug mode. Default False.
        """
        self.config_path = config_path or get_default_config_path()
        self.debug = debug
        
        self.llm = LLM.from_config(self.config_path)
        self.tools = [fastq2fasta, index_fasta, create_output_dir, create_workdir, zip_directory]
        self.agent = create_agent(
            model=self.llm.client,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
            debug=debug
        )
    
    def run(self, query: str) -> Dict[str, Any]:
        """Run agent with a query.
        
        Args:
            query: User query string.
        
        Returns:
            Agent execution result.
        """
        return self.agent.invoke({"messages": [{"role": "user", "content": query}]})
    
    def run_stream(self, query: str):
        """Run agent with streaming output to console.
        
        Args:
            query: User query string.
        """
        for event in self.agent.stream(
            {"messages": [{"role": "user", "content": query}]},
            stream_mode="messages"
        ):
            self._print_event(event)
    
    def _print_event(self, event):
        """Print event with formatting."""
        if not isinstance(event, tuple) or len(event) != 2:
            return
        
        message, metadata = event
        node = metadata.get("langgraph_node", "")
        
        if isinstance(message, AIMessageChunk):
            content = message.content
            if content:
                if node == "model":
                    print(f"\033[96m{content}\033[0m", end="", flush=True)
        elif isinstance(message, ToolMessage):
            tool_name = metadata.get("langgraph_tool_name", "tool")
            print(f"\n\033[93m[调用工具: {tool_name}]\033[0m")
            if message.content:
                content = str(message.content)[:200]
                print(f"\033[90m  结果: {content}...\033[0m")


def main():
    """Main entry point for interactive agent."""
    agent = FormatTransferAgent(debug=False)
    
    print("\033[95m=== 生物信息学格式转换助手 ===\033[0m")
    print("\033[90m输入 'quit' 或 'exit' 退出\033[0m\n")
    
    while True:
        try:
            query = input("\033[94m用户: \033[0m").strip()
            
            if query.lower() in ["quit", "exit"]:
                print("\033[93m再见！\033[0m")
                break
            
            if not query:
                continue
            
            print()
            agent.run_stream(query)
            print("\n")
            
        except KeyboardInterrupt:
            print("\n\033[93m已中断\033[0m")
            break
        except Exception as e:
            print(f"\033[91m错误: {e}\033[0m")


if __name__ == "__main__":
    main()
