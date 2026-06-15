import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


class Node:
    def __init__(self, node_type: str, name: str, properties: dict = None, node_id: str = None):
        self.id = node_id or str(uuid.uuid4())[:8]
        self.type = node_type
        self.name = name
        self.properties = properties or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(d: dict) -> "Node":
        n = Node(d["type"], d["name"], d.get("properties", {}), d["id"])
        n.created_at = d.get("created_at", n.created_at)
        n.updated_at = d.get("updated_at", n.created_at)
        return n


class Edge:
    def __init__(self, source_id: str, target_id: str, edge_type: str, properties: dict = None, edge_id: str = None):
        self.id = edge_id or str(uuid.uuid4())[:8]
        self.source_id = source_id
        self.target_id = target_id
        self.type = edge_type
        self.properties = properties or {}
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "properties": self.properties,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(d: dict) -> "Edge":
        e = Edge(d["source_id"], d["target_id"], d["type"], d.get("properties", {}), d["id"])
        e.created_at = d.get("created_at", e.created_at)
        return e


class GraphMemory:
    VALID_NODE_TYPES = {"person", "project", "idea", "task", "event", "preference", "thought", "note"}
    VALID_EDGE_TYPES = {"created", "has", "needs", "related_to", "mentions", "follows", "precedes", "belongs_to"}

    def __init__(self, path: str = None):
        if path is None:
            base = Path(__file__).parent.parent / "data"
            base.mkdir(exist_ok=True)
            path = str(base / "nexus.json")
        self.path = path
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self._load()

    def add_node(self, node_type: str, name: str, properties: dict = None) -> dict:
        if node_type not in self.VALID_NODE_TYPES:
            node_type = "note"
        node = Node(node_type, name, properties)
        self.nodes[node.id] = node
        self._save()
        return node.to_dict()

    def add_edge(self, source_id: str, target_id: str, edge_type: str, properties: dict = None) -> dict:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Both nodes must exist before creating an edge")
        if edge_type not in self.VALID_EDGE_TYPES:
            edge_type = "related_to"
        edge = Edge(source_id, target_id, edge_type, properties)
        self.edges.append(edge)
        self._save()
        return edge.to_dict()

    def get_node(self, node_id: str) -> Optional[dict]:
        node = self.nodes.get(node_id)
        return node.to_dict() if node else None

    def update_node(self, node_id: str, name: str = None, properties: dict = None) -> Optional[dict]:
        node = self.nodes.get(node_id)
        if not node:
            return None
        if name:
            node.name = name
        if properties:
            node.properties.update(properties)
        node.updated_at = datetime.now().isoformat()
        self._save()
        return node.to_dict()

    def delete_node(self, node_id: str) -> bool:
        if node_id not in self.nodes:
            return False
        del self.nodes[node_id]
        self.edges = [e for e in self.edges if e.source_id != node_id and e.target_id != node_id]
        self._save()
        return True

    def query_nodes(self, node_type: str = None, query: str = "") -> list[dict]:
        results = []
        for node in self.nodes.values():
            if node_type and node.type != node_type:
                continue
            if query:
                q = query.lower()
                if q not in node.name.lower() and q not in str(node.properties).lower():
                    continue
            results.append(node.to_dict())
        return sorted(results, key=lambda n: n["created_at"], reverse=True)

    def get_connections(self, node_id: str) -> dict:
        connected_edges = [
            e for e in self.edges if e.source_id == node_id or e.target_id == node_id
        ]
        related = []
        for e in connected_edges:
            other_id = e.target_id if e.source_id == node_id else e.source_id
            other = self.nodes.get(other_id)
            related.append({
                "edge": e.to_dict(),
                "node": other.to_dict() if other else None,
            })
        return {"node": self.get_node(node_id), "connections": related}

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        results = []
        for node in self.nodes.values():
            if q in node.name.lower() or q in str(node.properties).lower():
                results.append(node.to_dict())
        return sorted(results, key=lambda n: n["created_at"], reverse=True)[:20]

    def get_stats(self) -> dict:
        type_counts = {}
        for node in self.nodes.values():
            type_counts[node.type] = type_counts.get(node.type, 0) + 1
        edge_counts = {}
        for edge in self.edges:
            edge_counts[edge.type] = edge_counts.get(edge.type, 0) + 1
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes_by_type": type_counts,
            "edges_by_type": edge_counts,
        }

    def get_graph(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
        }

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self._save()

    def _load(self):
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
            self.nodes = {nid: Node.from_dict(nd) for nid, nd in data.get("nodes", {}).items()}
            self.edges = [Edge.from_dict(ed) for ed in data.get("edges", [])]
        except (FileNotFoundError, json.JSONDecodeError):
            self.nodes = {}
            self.edges = {}

    def _save(self):
        with open(self.path, "w") as f:
            json.dump({
                "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
                "edges": [e.to_dict() for e in self.edges],
            }, f, indent=2)
