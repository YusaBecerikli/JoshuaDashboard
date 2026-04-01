import logging
from datetime import datetime
from typing import Optional
from database import supabase

logger = logging.getLogger("memory")

MAX_MEMORY_CHARS = 4000
MAX_HISTORY_LINES = 50

DEFAULT_PROFILE = """# Joshua — Profil

## Kişisel Bilgiler
- Ad: Muhammed Yuşa Becerikli (Joshua)
- Yaş: 17
- Konum: Bingöl
- Hedef: Sabancı Üniversitesi Bilgisayar Mühendisliği
- Sınav: YKS (Haziran 2026)

## Tercihler


## Öğrenme Stili


## Güçlü/Zayıf Yönler


## Notlar
"""

DEFAULT_KNOWLEDGE = """# Bilgi Bankası

## Konu Bilgileri


## Pratik Bilgiler


## Keşfedilen Kaynaklar


## Notlar
"""

DEFAULT_HISTORY = """# Konuşma Özeti

## Son Önemli Etkileşimler


## Gelişmeler


## Açık Konular

"""


def _ensure_memory_exists(key: str, default: str):
    """Ensure a memory key exists in Supabase; insert default if missing."""
    try:
        result = supabase.table("memory").select("key").eq("key", key).execute()
        if not result.data:
            supabase.table("memory").insert({"key": key, "content": default}).execute()
            logger.info(f"Memory initialized: {key}")
    except Exception as e:
        logger.error(f"Memory init error ({key}): {e}")


def _read_memory(key: str) -> str:
    """Read memory content from Supabase."""
    try:
        result = supabase.table("memory").select("content").eq("key", key).execute()
        if result.data:
            return result.data[0]["content"]
    except Exception as e:
        logger.error(f"Memory read error ({key}): {e}")
    return ""


def _write_memory(key: str, content: str):
    """Upsert memory content in Supabase."""
    try:
        supabase.table("memory").upsert({
            "key": key,
            "content": content,
        }).execute()
    except Exception as e:
        logger.error(f"Memory write error ({key}): {e}")


def _update_section(current: str, section: str, content: str) -> str:
    """Replace or append a ## section in markdown content."""
    header = f"## {section}"
    if header in current:
        parts = current.split(header)
        before = parts[0]
        after_parts = parts[1].split("## ", 1)
        after = f"## {after_parts[1]}" if len(after_parts) > 1 else ""
        return f"{before}{header}\n{content}\n\n{after}"
    else:
        return f"{current}\n{header}\n{content}\n"


def init_memory():
    """Ensure all default memory keys exist in Supabase."""
    _ensure_memory_exists("profile", DEFAULT_PROFILE)
    _ensure_memory_exists("knowledge", DEFAULT_KNOWLEDGE)
    _ensure_memory_exists("history_summary", DEFAULT_HISTORY)


def read_profile() -> str:
    return _read_memory("profile")


def read_knowledge() -> str:
    return _read_memory("knowledge")


def read_history() -> str:
    return _read_memory("history_summary")


def update_profile(section: str, content: str):
    """Append or update a section in profile."""
    current = read_profile()
    new_content = _update_section(current, section, content)
    _write_memory("profile", new_content)
    logger.info(f"Profile updated: {section}")


def update_knowledge(section: str, content: str):
    """Append or update a section in knowledge."""
    current = read_knowledge()
    new_content = _update_section(current, section, content)
    _write_memory("knowledge", new_content)
    logger.info(f"Knowledge updated: {section}")


def append_history(entry: str):
    """Append a timestamped entry to history. Trim if too long."""
    current = read_history()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = f"\n### [{timestamp}]\n{entry}"

    lines = (current + new_entry).split("\n")
    if len(lines) > MAX_HISTORY_LINES:
        lines = lines[:3] + lines[-(MAX_HISTORY_LINES - 3):]

    _write_memory("history_summary", "\n".join(lines))
    logger.info(f"History appended: {entry[:50]}...")


def summarize_history(conversation_summary: str):
    """Replace history with a condensed summary."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"# Konuşma Özeti\n\n## Son Önemli Etkileşimler\n\n### [{timestamp}]\n{conversation_summary}\n\n## Gelişmeler\n\n\n## Açık Konular\n\n"
    _write_memory("history_summary", content)
    logger.info("History summarized")


def get_all_memory() -> str:
    """Read all memory from Supabase and return as formatted string for AI context."""
    profile = read_profile()
    knowledge = read_knowledge()
    history = read_history()

    parts = []
    if profile.strip():
        parts.append(f"### PROFİL (Kullanıcı hakkında bilinenler)\n{profile}")
    if knowledge.strip():
        parts.append(f"### BİLGİ BANKASI\n{knowledge}")
    if history.strip():
        parts.append(f"### KONUŞMA GEÇMİŞİ\n{history}")

    result = "\n\n".join(parts)
    if len(result) > MAX_MEMORY_CHARS:
        result = result[:MAX_MEMORY_CHARS] + "\n...(bellek kısaltıldı)"
    return result
