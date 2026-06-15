import httpx
from tools.registry import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for current information"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"]
    }

    def execute(self, query: str = "", **kwargs) -> ToolResult:
        try:
            url = f"https://api.duckduckgo.com/?q={httpx.utils.quote(query)}&format=json&no_html=1"
            resp = httpx.get(url, timeout=10)
            data = resp.json()
            results = []
            if "Abstract" in data and data["Abstract"]:
                results.append(data["Abstract"])
            if "RelatedTopics" in data:
                for topic in data["RelatedTopics"][:3]:
                    if "Text" in topic:
                        results.append(topic["Text"])
            content = "\n\n".join(results) if results else f"No results found for: {query}"
            return ToolResult(tool_name=self.name, content=content[:2000])
        except Exception as e:
            return ToolResult(tool_name=self.name, content=f"Search error: {e}", success=False, error=str(e))
