import re
from collections.abc import Callable

from data_collection.globals import config
from src.models.json_structure import Match, ReplaceRule


def _invert_status_map(ordered_status_names: list[tuple[str, str]]):
    """Convert list of (id, name) pairs to dict name -> id. Ids with same name both stored, but only first used."""
    # If multiple statuses with same name are present, they can override each other
    # This is the case with Bleed, so first instance is always used
    ordered_status_names.reverse()
    return {name: id_ for id_, name in ordered_status_names}


def _sort_by_name(items: dict[str, str]) -> list[tuple[str, str]]:
    """Sort dict items by key length in descending order."""
    return sorted(items.items(), key=lambda x: len(x[0]), reverse=True)


def add_status_regex(replace_config: list[ReplaceRule], status_files: list[str]):
    """Replace status names and ids with linked sprites"""
    from data_collection.statuses import base_status_id_name_map, status_id_name_map

    ordered_status_names = _sort_by_name(status_id_name_map)
    status_ids = [re.escape(id_) for id_, _ in ordered_status_names]

    ordered_base_status_names = _sort_by_name(base_status_id_name_map)
    base_status_names = [re.escape(name) for _, name in ordered_base_status_names]

    sprite_fixes = config["statuses"]["spriteFixes"]

    base_name_to_id = _invert_status_map(ordered_base_status_names)

    def _repl_with_sprite(id_: str) -> str:
        sprite = sprite_fixes.get(id_, id_)
        return f'<link="{id_}"><sprite name="{sprite}"></link>'

    def repl_name(match: Match[str]) -> str:
        return _repl_with_sprite(base_name_to_id[match.group(1)])

    def repl_id(match: Match[str]) -> str:
        return _repl_with_sprite(match.group(1))

    def _create_replace_rule(
        from_pattern: str, to_replacement: str | Callable[[Match[str]], str]
    ) -> ReplaceRule:
        return {
            "fields": ["desc"],
            "changes": [{
                "from": from_pattern,
                "to": to_replacement,
                "regex": True
            }],
            "ignoredFiles": status_files
        }

    # Remove status sprites before statuses (for some legacy cases)
    status_sprite_remove = _create_replace_rule(
        r"<sprite [^>]+><color[^>]+><u><link[^>]+>([^>]+)</color></link></u>", r"\1"
    )

    # Replace only status names from BaseKeywords.json due to them being used without id sometimes for some reason
    base_names_pattern = (
        r'(?<!<link=")(?<!sprite name=")(?<!<noparse>)(?<!\[)\b(' + "|".join(base_status_names) +
        r')\b(?![\]">])(?!<\/noparse>)(?!<\/noparse>)(?!\[TabExplain\])'
    )
    base_status_name_replace = _create_replace_rule(base_names_pattern, repl_name)

    # Replace status id with icons
    ids_pattern = r"\[(" + "|".join(status_ids) + r")\]"
    status_id_replace = _create_replace_rule(ids_pattern, repl_id)

    replace_config.extend([status_sprite_remove, base_status_name_replace, status_id_replace])


__all__ = ["add_status_regex"]
