from __future__ import annotations

import unittest

from tests._support import SRC

from openscreener.parsers._html import Node, parse_html


class HtmlTreeTestCase(unittest.TestCase):
    def test_parse_html_builds_searchable_tree(self) -> None:
        root = parse_html(
            """
            <section id="top" class="hero">
              <h1>Title</h1>
              <div class="body"><p>Alpha <strong>Beta</strong></p></div>
            </section>
            """
        )

        section = root.find("section", id_="top")

        self.assertIsNotNone(section)
        self.assertEqual(section.classes(), ["hero"])
        self.assertEqual(section.find("h1").text(), "Title")
        self.assertEqual(section.find(class_="body").text(), "Alpha Beta")

    def test_node_find_all_and_direct_children_filter_nodes(self) -> None:
        root = parse_html("<div><span>A</span><span>B</span><p>C</p></div>")
        container = root.find("div")

        assert container is not None
        spans = container.find_all("span")

        self.assertEqual(len(spans), 2)
        self.assertEqual([node.text() for node in container.direct_children("span")], ["A", "B"])
        self.assertEqual(container.direct_children("p")[0].text(), "C")

    def test_matches_and_get_support_attribute_filters(self) -> None:
        node = Node(tag="a", attrs={"id": "link", "class": "one two", "href": "https://example.com"})

        self.assertTrue(node.matches("a", id_="link", class_="two"))
        self.assertFalse(node.matches("div"))
        self.assertEqual(node.get("href"), "https://example.com")
        self.assertIsNone(node.get("missing"))

    def test_text_normalizes_block_spacing(self) -> None:
        root = parse_html("<div>Hello<p>World</p><br/>Again</div>")
        container = root.find("div")

        assert container is not None
        self.assertEqual(container.text(), "Hello\nWorld\nAgain")
