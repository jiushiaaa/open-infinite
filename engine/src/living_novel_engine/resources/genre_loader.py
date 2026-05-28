"""Genre Template Loader — 加载题材风格模板用于 LLM 抽取和生成。"""

from __future__ import annotations

from pathlib import Path

_TEMPLATES_DIR = Path(__file__).resolve().parent / "genre_templates"

SLUG_TO_FILENAME: dict[str, str] = {
    "xianxia": "修仙",
    "xiuxian": "修仙",
    "xuanhuan": "高武",
    "gaowu": "高武",
    "scifi": "科幻",
    "sci-fi": "科幻",
    "kehuan": "科幻",
    "wuxia": "西幻",
    "xihuan": "西幻",
    "western-fantasy": "西幻",
    "cthulhu": "克苏鲁",
    "horror": "黑暗题材",
    "dark": "黑暗题材",
    "suspense": "悬疑灵异",
    "mystery": "悬疑灵异",
    "xuanyi": "悬疑灵异",
    "urban": "都市异能",
    "dushi": "都市异能",
    "history": "历史古代",
    "lishi": "历史古代",
    "romance": "古言",
    "guyan": "古言",
    "apocalypse": "末世",
    "moshi": "末世",
    "infinite": "无限流",
    "wuxian": "无限流",
    "system": "系统流",
    "xitong": "系统流",
    "game": "游戏体育",
    "esports": "电竞",
    "farming": "种田",
    "zhongtian": "种田",
    "palace": "宫斗宅斗",
    "modern-romance": "职场婚恋",
    "sweet": "青春甜宠",
    "fantasy-romance": "幻想言情",
    "rules-horror": "规则怪谈",
    "livestream": "直播文",
    "spy": "抗战谍战",
    "ceo": "豪门总裁",
}


def list_genres() -> list[str]:
    """返回所有可用的英文 slug。"""
    return sorted(SLUG_TO_FILENAME.keys())


def list_genre_files() -> list[str]:
    """返回所有可用的中文模板名（不含 .md）。"""
    return sorted(set(SLUG_TO_FILENAME.values()))


def load_genre_template(genre: str) -> str:
    """按 slug 或中文名加载题材模板内容。找不到时 fallback 到修仙。"""
    filename = SLUG_TO_FILENAME.get(genre.lower())
    if filename is None:
        candidate = _TEMPLATES_DIR / f"{genre}.md"
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
        filename = "修仙"

    path = _TEMPLATES_DIR / f"{filename}.md"
    if not path.exists():
        fallback = _TEMPLATES_DIR / "修仙.md"
        if fallback.exists():
            return fallback.read_text(encoding="utf-8")
        return ""
    return path.read_text(encoding="utf-8")


def get_genre_display_name(genre: str) -> str:
    """将 slug 转为中文展示名。"""
    filename = SLUG_TO_FILENAME.get(genre.lower())
    if filename:
        return filename
    candidate = _TEMPLATES_DIR / f"{genre}.md"
    if candidate.exists():
        return genre
    return "修仙"
