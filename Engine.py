from __future__ import annotations

import json
import random
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from openai import OpenAI


DATA_PATH = Path("internet.json")


@dataclass
class Section:
    title: str
    paragraphs: list[str]


@dataclass
class Page:
    title: str
    slug: str
    intro: str
    sections: list[Section]
    links: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "slug": self.slug,
            "intro": self.intro,
            "sections": [asdict(section) for section in self.sections],
            "links": self.links,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Page":
        return cls(
            title=data["title"],
            slug=data["slug"],
            intro=data["intro"],
            sections=[Section(**section) for section in data.get("sections", [])],
            links=data.get("links", []),
        )


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled-node"


class Engine:
    def __init__(self, data_path: Path = DATA_PATH):
        self.data_path = data_path
        self.client = OpenAI(
            base_url="http://localhost:11434/v1/",
            api_key="ollama",
        )
        self.pages: dict[str, Page] = {}
        self.term_index: dict[str, str] = {}
        self.load()

    def load(self) -> None:
        if not self.data_path.exists():
            return

        try:
            payload = json.loads(self.data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return

        self.pages = {
            slug: Page.from_dict(page_data)
            for slug, page_data in payload.get("pages", {}).items()
        }
        self.term_index = {
            key.lower(): value for key, value in payload.get("term_index", {}).items()
        }

    def save(self) -> None:
        payload = {
            "pages": {slug: page.to_dict() for slug, page in self.pages.items()},
            "term_index": self.term_index,
        }
        self.data_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get_homepage_topics(self, limit: int = 8) -> list[str]:
        if self.pages:
            titles = [page.title for page in self.pages.values()]
            random.shuffle(titles)
            return titles[:limit]

        return [
            "Quantum Bread",
            "The Ministry of Indoor Weather",
            "Sock Futures Exchange",
            "Ornamental WiFi",
            "Civic Soup Protocol",
            "Reverse Archaeology",
            "Dental Astrology",
            "Microwave Philosophy",
        ]

    def get_or_create_page(self, term: str) -> Page:
        normalized = term.strip()
        if not normalized:
            normalized = "Untitled Node"

        indexed_slug = self.term_index.get(normalized.lower())
        if indexed_slug and indexed_slug in self.pages:
            return self.pages[indexed_slug]

        generated = self._generate_page(normalized)
        unique_slug = self._ensure_unique_slug(generated.slug)
        generated.slug = unique_slug

        self.pages[unique_slug] = generated
        self.term_index[normalized.lower()] = unique_slug
        self.term_index[generated.title.lower()] = unique_slug
        self.save()
        return generated

    def get_page(self, slug: str) -> Page | None:
        return self.pages.get(slug)

    def resolve_link(self, term: str) -> str:
        normalized = term.strip().lower()
        existing_slug = self.term_index.get(normalized)
        if existing_slug:
            return existing_slug
        return slugify(term)

    def _ensure_unique_slug(self, slug: str) -> str:
        candidate = slug
        counter = 2
        while candidate in self.pages:
            candidate = f"{slug}-{counter}"
            counter += 1
        return candidate

    def _generate_page(self, term: str) -> Page:
        prompt = self._build_prompt(term)

        try:
            response = self.client.chat.completions.create(
                model="llama3",
                temperature=0.95,
                max_tokens=1800,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You generate pages for a fictional AI-only internet. "
                            "Return valid JSON only. No markdown fences, no commentary."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            raw_text = response.choices[0].message.content or ""
            payload = self._extract_json(raw_text)
            return self._page_from_payload(term, payload)
        except Exception:
            return self._fallback_page(term)

    def _build_prompt(self, term: str) -> str:
        return f'''
Create one fake encyclopedia-style webpage for the term "{term}".

Return exactly this JSON schema:
{{
  "title": "string",
  "intro": "2-4 sentences",
  "sections": [
    {{"title": "string", "content": "2 short paragraphs separated by \\n\\n"}}
  ],
  "links": ["5 to 8 related fake terms"]
}}

Rules:
- The page should sound confident, polished, and slightly absurd.
- Treat the topic as real, even when ridiculous.
- Keep sections varied and specific.
- The links should invite exploration across a fake internet.
- Do not include citations.
- Do not use markdown.
'''.strip()

    def _extract_json(self, text: str) -> dict[str, Any]:
        text = text.strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("Model did not return JSON")
        return json.loads(match.group(0))

    def _page_from_payload(self, term: str, payload: dict[str, Any]) -> Page:
        title = str(payload.get("title") or term).strip() or term
        intro = str(payload.get("intro") or self._fallback_intro(term)).strip()

        sections_payload = payload.get("sections") or []
        sections: list[Section] = []
        for item in sections_payload[:5]:
            section_title = str(item.get("title") or "Overview").strip() or "Overview"
            content = str(item.get("content") or "").strip()
            paragraphs = [part.strip() for part in content.split("\n\n") if part.strip()]
            if not paragraphs:
                paragraphs = [f"{title} is frequently discussed in confident tones despite limited evidence."]
            sections.append(Section(title=section_title, paragraphs=paragraphs))

        if not sections:
            sections = self._fallback_sections(title)

        links = []
        for item in payload.get("links") or []:
            cleaned = str(item).strip()
            if cleaned and cleaned.lower() != title.lower() and cleaned not in links:
                links.append(cleaned)

        if len(links) < 5:
            for fallback in self._fallback_links(title):
                if fallback.lower() != title.lower() and fallback not in links:
                    links.append(fallback)
                if len(links) >= 6:
                    break

        return Page(
            title=title,
            slug=slugify(title),
            intro=intro,
            sections=sections,
            links=links,
        )

    def _fallback_page(self, term: str) -> Page:
        title = term.title()
        return Page(
            title=title,
            slug=slugify(title),
            intro=self._fallback_intro(title),
            sections=self._fallback_sections(title),
            links=self._fallback_links(title),
        )

    def _fallback_intro(self, term: str) -> str:
        return (
            f"{term} is a documented phenomenon inside the synthetic web, where topics become authoritative "
            f"simply because enough generated pages repeat them. It is usually described as practical, historic, "
            f"and strangely indispensable."
        )

    def _fallback_sections(self, title: str) -> list[Section]:
        return [
            Section(
                title="Background",
                paragraphs=[
                    f"Early references to {title} appeared in self-referential archives that cited one another in a perfect loop.",
                    f"By the time anyone questioned it, {title} had already been summarized, indexed, and enthusiastically misunderstood.",
                ],
            ),
            Section(
                title="Public Use",
                paragraphs=[
                    f"Advocates claim {title} improves daily life, workplace morale, and several industries that did not previously exist.",
                    f"Critics argue that its benefits are hard to verify, mainly because every source discussing {title} was generated five minutes ago.",
                ],
            ),
            Section(
                title="Cultural Impact",
                paragraphs=[
                    f"In popular culture, {title} is associated with optimism, unnecessary jargon, and aggressive confidence.",
                    f"Its popularity persists because each new page links to three more pages that insist the subject matters.",
                ],
            ),
        ]

    def _fallback_links(self, title: str) -> list[str]:
        base = title.split()[0]
        return [
            f"{base} Standard",
            f"{base} Institute",
            f"History of {title}",
            f"Applied {title}",
            f"{title} Controversy",
            f"Department of {title}",
        ]
