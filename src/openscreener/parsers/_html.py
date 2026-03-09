"""Minimal HTML tree helpers built on the standard library."""

from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
import re

_WHITESPACE_RE = re.compile(r"[ \t\r\f\v]+")
_BLOCK_TAGS = {
    "div",
    "p",
    "section",
    "ul",
    "ol",
    "li",
    "table",
    "thead",
    "tbody",
    "tfoot",
    "tr",
    "td",
    "th",
    "br",
    "button",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
}
_VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source"}


@dataclass(slots=True)
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    parent: Node | None = None
    children: list[Node | str] = field(default_factory=list)

    def append(self, child: Node | str) -> None:
        self.children.append(child)

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.attrs.get(key, default)

    def classes(self) -> list[str]:
        return self.attrs.get("class", "").split()

    def matches(
        self,
        tag: str | None = None,
        *,
        id_: str | None = None,
        class_: str | None = None,
    ) -> bool:
        if tag is not None and self.tag != tag:
            return False
        if id_ is not None and self.attrs.get("id") != id_:
            return False
        if class_ is not None and class_ not in self.classes():
            return False
        return True

    def iter_nodes(self) -> list[Node]:
        nodes = [self]
        for child in self.children:
            if isinstance(child, Node):
                nodes.extend(child.iter_nodes())
        return nodes

    def find(
        self,
        tag: str | None = None,
        *,
        id_: str | None = None,
        class_: str | None = None,
    ) -> Node | None:
        for node in self.iter_nodes():
            if node.matches(tag, id_=id_, class_=class_):
                return node
        return None

    def find_all(
        self,
        tag: str | None = None,
        *,
        id_: str | None = None,
        class_: str | None = None,
    ) -> list[Node]:
        return [node for node in self.iter_nodes() if node.matches(tag, id_=id_, class_=class_)]

    def direct_children(self, *tags: str) -> list[Node]:
        selected: list[Node] = []
        for child in self.children:
            if isinstance(child, Node) and (not tags or child.tag in tags):
                selected.append(child)
        return selected

    def text(self) -> str:
        parts: list[str] = []
        self._collect_text(parts)
        text = "".join(parts)
        text = _WHITESPACE_RE.sub(" ", text)
        text = re.sub(r"\n+", "\n", text)
        text = re.sub(r" *\n *", "\n", text)
        return text.strip()

    def _collect_text(self, parts: list[str]) -> None:
        for child in self.children:
            if isinstance(child, str):
                parts.append(child)
                continue
            if child.tag in _BLOCK_TAGS:
                parts.append("\n")
            child._collect_text(parts)
            if child.tag in _BLOCK_TAGS:
                parts.append("\n")


class _TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack: list[Node] = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag=tag, attrs={key: value or "" for key, value in attrs}, parent=self.stack[-1])
        self.stack[-1].append(node)
        if tag not in _VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag=tag, attrs={key: value or "" for key, value in attrs}, parent=self.stack[-1])
        self.stack[-1].append(node)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if data:
            self.stack[-1].append(data)


def parse_html(html: str) -> Node:
    parser = _TreeBuilder()
    parser.feed(html)
    parser.close()
    return parser.root
