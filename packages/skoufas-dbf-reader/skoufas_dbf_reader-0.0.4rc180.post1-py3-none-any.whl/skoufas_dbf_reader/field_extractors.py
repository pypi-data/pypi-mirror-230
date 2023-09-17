""" Functions that extract information given specific strings """
import re

from collections import OrderedDict
from typing import Optional

from skoufas_dbf_reader.correction_data import *
from skoufas_dbf_reader.utilities import none_if_empty_or_stripped

only_greek = re.compile(r"[Α-ΩΉα-ω0-9 &:;,'!<>ⁿ=$\[\]\+\\\-\(\)\.\"\/]+")


def has_language(a01: Optional[str]) -> bool:
    """Check values for language at the end"""
    if not a01:
        return False
    for code in language_codes().keys():
        if a01.endswith(f" {code}"):
            return True
    return False


def authors_from_a01(a01: Optional[str]) -> list[str]:
    """Get author from A01 DBF record"""
    if not a01:
        return []
    if not has_author(a01):
        return []
    strip_finals = list(language_codes().keys()) + [
        " Ι",
        " .",
    ]
    for final in strip_finals:
        if a01.endswith(" " + final):
            a01 = a01.replace(final, "")
    author = a01.strip()
    author = author_corrections().get(author, author)
    if not author:
        return []
    return author.split("!!")


def language_from_a01_a02(a01: Optional[str], a02: Optional[str]) -> Optional[str]:
    """Check values for language at the end"""
    if not a01:
        return None
    if has_language(a01):
        for language, isolanguage in language_codes().items():
            if a01.endswith(language):
                return isolanguage
    title = title_from_a02(a02)
    if title and only_greek.fullmatch(title):
        return "el"
    return None


def title_from_a02(a02: Optional[str]) -> Optional[str]:
    """Cleanup"""
    return none_if_empty_or_stripped(a02)


def subtitle_from_a03(a03: Optional[str]) -> Optional[str]:
    """Cleanup"""
    return none_if_empty_or_stripped(a03)


def dewey_from_a04_a05(a04: Optional[str], a05: Optional[str]) -> Optional[str]:
    """Cleanup and replace known issues"""
    value4 = none_if_empty_or_stripped(a04)
    if value4:
        correction = field04_corrections().get(value4, value4)
        if correction:
            if isinstance(correction, str):
                value4 = none_if_empty_or_stripped(correction)
            else:
                value4 = None
        else:
            value4 = None

    if value4:
        value4 = value4.replace("Χ. Σ.", "ΧΣ")
        value4 = value4.replace("Χ. Σ", "ΧΣ")

        value4 = value4.replace("X.S.", "ΧΣ")
        value4 = value4.replace("Χ.Σ.", "ΧΣ")

        value4 = value4.replace("Χ.Σ", "ΧΣ")
        value4 = value4.replace("X.S", "ΧΣ")
        value4 = value4.replace("X.Σ", "ΧΣ")
        value4 = value4.replace("Σ.Σ", "ΧΣ")

        value4 = value4.replace("Χ.Χ.", "ΧΧ")
        value4 = value4.replace("Χ.Χ", "ΧΧ")

    if value4:
        for dewey_re in dewey_re1:
            dewey_match = dewey_re.fullmatch(value4)
            if dewey_match:
                return f"{dewey_match[1]}".strip()
        for dewey_re in dewey_re2:
            dewey_match = dewey_re.fullmatch(value4)
            if dewey_match:
                return f"{dewey_match[1]} {dewey_match[2]}".strip()

    value5 = none_if_empty_or_stripped(a05)
    if value5:
        correction = field05_corrections().get(value5, value5)
        if correction:
            if isinstance(correction, dict):
                value5 = correction.get("dewey", None)
            else:
                value5 = None
        else:
            value5 = None
    if value5 and isinstance(value5, str):
        for dewey_re in dewey_re1:
            dewey_match = dewey_re.fullmatch(value5)
            if dewey_match:
                return f"{dewey_match[1]}".strip()
        for dewey_re in dewey_re2:
            dewey_match = dewey_re.fullmatch(value5)
            if dewey_match:
                return f"{dewey_match[1]} {dewey_match[2]}".strip()

    return None


def entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(
    a04: Optional[str],
    a05: Optional[str],
    a06: Optional[str],
    a07: Optional[str],
    a08: Optional[str],
    a18: Optional[str],
    a19: Optional[str],
) -> list[str]:
    """Cleanup, read additional numbers from a06"""

    def cleanup_single_value(
        field_name: str,
        original_value: Optional[str],
        corrections: dict[str, Optional[str | dict[str, str] | dict[str, str | bool]]],
        ignore_if_not_in_correction: bool,
    ) -> str:
        output = none_if_empty_or_stripped(original_value)
        if output:
            if output in corrections:
                correction = corrections[output]
                if correction is None:
                    return ""
                elif isinstance(correction, str):
                    if ignore_if_not_in_correction:
                        return ""
                    else:
                        return "-" + str(correction)
                else:
                    output = dict(correction).get("series", "")
                    if not isinstance(output, str):
                        raise Exception(f"Invalid correction for field {field_name} [{original_value}]")
                    if correction.get("use_dash", True):
                        return "-" + output
                    else:
                        return output
            else:
                if ignore_if_not_in_correction:
                    return ""
                else:
                    return output
        return ""

    value4 = cleanup_single_value("A04", a04, field04_corrections(), True) + "-"  # type: ignore
    value5 = cleanup_single_value("A05", a05, field05_corrections(), False)  # type: ignore
    value6 = cleanup_single_value("A06", a06, field06_corrections(), True)  # type: ignore
    value7 = cleanup_single_value("A07", a07, field07_corrections(), True)  # type: ignore
    value8 = cleanup_single_value("A08", a08, field08_corrections(), True)  # type: ignore
    value18 = cleanup_single_value("A18", a18, field18_corrections(), True)  # type: ignore
    value19 = cleanup_single_value("A19", a19, field19_corrections(), True)  # type: ignore

    value = value4 + value5 + value6 + value7 + value8 + value18 + value19
    # Use a dict to remove duplicates
    entries_dict: dict[str, None] = dict()
    for v in value.split("-"):
        if v.strip():
            entries_dict[v.strip()] = None
    return list(entries_dict)


def translator_from_a06(a06: Optional[str]) -> Optional[str]:
    """Cleanup, replace special cases"""
    value = none_if_empty_or_stripped(a06)
    if not value:
        return None
    if value in field06_corrections():
        correction = field06_corrections()[value]
        if correction is None:
            return None
        elif isinstance(correction, str):
            return None
        else:
            value = dict(correction).get("translator", None)
            if not value:
                return None
            if not isinstance(value, str):
                raise Exception(f"Invalid correction for field A06 [{a06}]")
    value = translator_corrections().get(value, value)
    if not value:
        return None
    return value


def edition_from_a07(a07: Optional[str]) -> Optional[str]:
    """Cleanup, replace special cases"""
    value = none_if_empty_or_stripped(a07)
    if not value:
        return None
    if value in field07_corrections():
        value = field07_corrections().get(value)
        if not isinstance(value, str):
            return None
    if not value:
        return None
    return value


def editor_from_a08_a09(a08: Optional[str], a09: Optional[str]) -> Optional[tuple[Optional[str], Optional[str]]]:
    """Cleanup, replace special cases"""
    a08 = none_if_empty_or_stripped(a08)
    if not a08:
        a08 = None
    else:
        if a08 in field08_corrections():
            correction = field08_corrections().get(a08)
            if not correction:
                a08 = None
            elif isinstance(correction, dict):
                a08 = correction.get("editor", None)
            else:
                a08 = correction
    a09 = none_if_empty_or_stripped(a09)
    if not a09:
        a09 = None
    else:
        if a09 in field09_corrections():
            correction = field09_corrections().get(a09)
            if not correction:
                a09 = None
            elif isinstance(correction, dict):
                a09 = correction.get("place", None)
            else:
                a09 = correction
    if not a08 and not a09:
        return None
    correction = editor_corrections().get(f"{a08} // {a09}")
    if correction:
        correction = correction.split(" // ")
        a08 = correction[0]
        a09 = correction[1]
    return (a08, a09)


def edition_year_from_a09_a10(a09: Optional[str], a10: Optional[str]) -> Optional[int]:
    """Cleanup,handle special cases"""
    a09 = none_if_empty_or_stripped(a09)
    if a09 and a09 in field09_corrections():
        correction = field09_corrections().get(a09)
        if correction and isinstance(correction, dict) and "year" in correction:
            return int(correction["year"])

    a10 = none_if_empty_or_stripped(a10)
    if not a10:
        return None
    corrected = field10_corrections().get(a10, a10)
    if not corrected:
        return None
    if not corrected.isnumeric():
        raise Exception(f"invalid date [{a10}]")
    return int(corrected)


def pages_from_a11(a11: Optional[str]) -> Optional[int]:
    """Cleanup, return an int from various expressions"""
    a11 = none_if_empty_or_stripped(a11)
    if not a11:
        return None
    corrected = field11_corrections().get(a11, a11)
    if not corrected:
        return None
    pages_match = valid_pages_re.fullmatch(corrected)
    if not pages_match:
        raise Exception(f"invalid pages [{a11}]")
    return int(pages_match.group(1))


def topics_from_a12_to_a15_a20_a22_to_a24(
    many_lines: Optional[list[Optional[str]]],
) -> list[str]:
    """Cleanup, make unique, handle special cases"""
    if not many_lines:
        return []
    topics: OrderedDict[str, None] = OrderedDict()
    for line in many_lines:
        line = none_if_empty_or_stripped(line)
        if line:
            match = topic_in_paren_re.fullmatch(line)
            if match:
                in_parenthesis = match[1].strip()
                in_parenthesis = topic_replacements().get(in_parenthesis, in_parenthesis)
                if in_parenthesis and in_parenthesis.strip():
                    topics[in_parenthesis.strip()] = None
                # remove match and parenthesis
                line = line.replace(match[1], "").replace("()", "")
            for topic in line.split("-"):
                if topic:
                    topic = topic_replacements().get(topic, topic)
                    if topic:
                        topics[topic.strip()] = None
    return list(topics.keys())


def curator_from_a16(a16: Optional[str]) -> Optional[str]:
    """Cleanup"""
    a16 = none_if_empty_or_stripped(a16)
    if not a16:
        return None
    if a16 in field16_corrections():
        return field16_corrections()[a16]
    else:
        return a16


def has_cd_from_a02_a03_a12_a13_a14_a17_a18_a22_a30(many_lines: Optional[list[Optional[str]]]) -> bool:
    """Look for CD in the lines passed"""
    if not many_lines:
        return False
    for line in many_lines:
        if line and has_cd_re.search(line):
            return True
    return False


def has_dvd_from_a30(many_lines: Optional[list[Optional[str]]]) -> bool:
    """Look for DVD in the lines passed"""
    if not many_lines:
        return False
    for line in many_lines:
        if line and has_dvd_re.search(line):
            return True
    return False


def copies_from_a17_a18_a30(a17: Optional[str], a18: Optional[str], a30: Optional[str]) -> Optional[int]:
    """Use corrections to look for number of copies"""
    a17 = none_if_empty_or_stripped(a17)
    if a17:
        correction = field17_corrections().get(a17)
        if correction and isinstance(correction, dict):
            copies = correction.get("copies")
            if copies:
                if isinstance(copies, int):
                    return copies
                else:
                    raise Exception(f"Invalid correction for A17 [{a17}]")
    a18 = none_if_empty_or_stripped(a18)
    if a18:
        correction = field18_corrections().get(a18)
        if correction and isinstance(correction, dict):
            copies = correction.get("copies")
            if copies:
                if isinstance(copies, int):
                    return copies
                else:
                    raise Exception(f"Invalid correction for A17 [{a18}]")
    a30 = none_if_empty_or_stripped(a30)
    if a30:
        correction = field30_corrections().get(a30)
        if correction and isinstance(correction, dict):
            copies = correction.get("copies")
            if copies:
                if isinstance(copies, int):
                    return copies
                else:
                    raise Exception(f"Invalid correction for A30 [{a30}]")
    return None


def donation_from_a17_a30(a17: Optional[str], a30: Optional[str]) -> Optional[str]:
    """Use corrections to look for donations"""
    a17 = none_if_empty_or_stripped(a17)
    if a17:
        correction = field17_corrections().get(a17)
        if correction and isinstance(correction, dict):
            donation = correction.get("donation")
            if donation:
                if isinstance(donation, str):
                    return donation
                else:
                    raise Exception(f"Invalid correction for A17 [{a17}]")
    a30 = none_if_empty_or_stripped(a30)
    if a30:
        correction = field30_corrections().get(a30)
        if correction and isinstance(correction, dict):
            donation = correction.get("donation")
            if donation:
                if isinstance(donation, str):
                    return donation
                else:
                    raise Exception(f"Invalid correction for A30 [{a30}]")
    return None


def offprint_from_a17_a21_a30(a17: Optional[str], a21: Optional[str], a30: Optional[str]) -> bool:
    """Use corrections to look for offprint or the word ΑΝΑΤΥΠΟ"""
    a17 = none_if_empty_or_stripped(a17)
    if a17:
        correction = field17_corrections().get(a17)
        if correction and isinstance(correction, dict):
            offprint = correction.get("offprint")
            if offprint:
                if isinstance(offprint, bool):
                    return offprint
                else:
                    raise Exception(f"Invalid correction for A17 [{a17}]")
        if "ΑΝΑΤΥΠΟ" in a17:
            return True
    if a21 and "ΑΝΑΤΥΠΟ" in a21:
        return True
    a30 = none_if_empty_or_stripped(a30)
    if a30:
        correction = field30_corrections().get(a30)
        if correction and isinstance(correction, dict):
            offprint = correction.get("offprint")
            if offprint:
                if isinstance(offprint, bool):
                    return offprint
                else:
                    raise Exception(f"Invalid correction for A30 [{a30}]")
        elif "ΑΝΑΤΥΠΟ" in a30:
            return True
    return False


def volume_from_a17_a18_a20_a30(
    a17: Optional[str], a18: Optional[str], a20: Optional[str], a30: Optional[str]
) -> Optional[str]:
    """Use corrections to look for volume"""

    def read_from_single_field(
        field_name: str,
        value: Optional[str],
        corrections: dict[str, str | dict[str, str | bool | int] | None],
        current_result: str,
    ) -> str:
        value = none_if_empty_or_stripped(value)
        if value:
            correction = corrections.get(value)
            if correction and isinstance(correction, dict):
                result = correction.get("volume")
                if result:
                    if isinstance(result, str):
                        if current_result:
                            return current_result + "\n" + result
                        else:
                            return result
                    else:
                        raise Exception(f"Invalid correction for {field_name} [{value}]")
        return current_result

    result = read_from_single_field("A17", a17, field17_corrections(), "")
    result = read_from_single_field("A18", a18, field18_corrections(), result)
    result = read_from_single_field("A20", a20, field20_corrections(), result)
    result = read_from_single_field("A30", a30, field30_corrections(), result)
    return none_if_empty_or_stripped(result)


def material_from_a18_a30(a18: Optional[str], a30: Optional[str]) -> Optional[str]:
    """Use corrections to look for volume"""

    def read_from_single_field(
        field_name: str,
        value: Optional[str],
        corrections: dict[str, str | dict[str, str | bool | int] | None],
        current_result: str,
    ) -> str:
        value = none_if_empty_or_stripped(value)
        if value:
            correction = corrections.get(value)
            if correction and isinstance(correction, dict):
                result = correction.get("material")
                if result:
                    if isinstance(result, str):
                        if current_result:
                            return current_result + "\n" + result
                        else:
                            return result
                    else:
                        raise Exception(f"Invalid correction for {field_name} [{value}]")
        return current_result

    result = read_from_single_field("A18", a18, field18_corrections(), "")
    result = read_from_single_field("A30", a30, field30_corrections(), result)
    return none_if_empty_or_stripped(result)


def notes_from_a17_a18_a21_a30(
    a17: Optional[str], a18: Optional[str], a21: Optional[str], a30: Optional[str]
) -> Optional[str]:
    """Read from all three fields, apply corrections"""

    def read_from_single_field(
        field_name: str,
        value: Optional[str],
        corrections: dict[str, str | dict[str, str | bool | int] | None],
        current_result: str,
    ) -> str:
        result = None
        value = none_if_empty_or_stripped(value)
        if not value:
            result = None
        elif value in corrections:
            correction = corrections.get(value)
            if correction:
                if isinstance(correction, dict):
                    notes_in_dict = correction.get("notes")
                    if not notes_in_dict:
                        result = None
                    elif isinstance(notes_in_dict, str):
                        result = notes_in_dict
                    else:
                        raise Exception(f"Invalid correction for {field_name} [{value}]")
                if isinstance(correction, str):
                    result = correction
            else:
                result = None
        else:
            result = value

        if result:
            if current_result:
                return current_result + "\n" + result
            else:
                return result
        else:
            return current_result

    result = read_from_single_field("A17", a17, field17_corrections(), "")

    a18 = none_if_empty_or_stripped(a18)
    if a18 and a18 in field18_corrections():
        correction = field18_corrections().get(a18)
        if correction:
            if isinstance(correction, dict):
                notes_in_dict = correction.get("notes")
                if notes_in_dict and isinstance(notes_in_dict, str):
                    if result:
                        result += "\n" + notes_in_dict
                    else:
                        result = notes_in_dict

    result = read_from_single_field("A21", a21, {}, result)
    result = read_from_single_field("A30", a30, field30_corrections(), result)

    return none_if_empty_or_stripped(result)


def isbn_from_a17_a18_a19_a22_a30(
    a17in: Optional[str], a18in: Optional[str], a19in: Optional[str], a22in: Optional[str], a30in: Optional[str]
) -> Optional[str]:
    """Cleanup"""

    # Only use corrections from a17
    a17 = none_if_empty_or_stripped(a17in)
    if not a17:
        a17 = ""
    if a17 in field17_corrections():
        correction = field17_corrections()[a17]

        if correction:
            if isinstance(correction, dict):
                if "isbn" in correction:
                    if correction and isinstance(correction["isbn"], str):
                        a17 = correction["isbn"]
                    else:
                        a17 = ""
                else:
                    a17 = ""
            else:
                a17 = ""
        else:
            a17 = ""
    else:
        a17 = ""

    # Use a18 unless there's a correction
    a18 = none_if_empty_or_stripped(a18in)
    if a18:
        if a18 in field18_corrections():
            a18 = ""
    else:
        a18 = ""

    a19 = none_if_empty_or_stripped(a19in)
    if a19:
        if a19 in field19_corrections():
            a19 = ""
    else:
        a19 = ""

    a22 = none_if_empty_or_stripped(a22in)
    if not a22:
        a22 = ""
    if not a22_has_isbn_part_re.fullmatch(a22):
        a22 = ""

    # Only use corrections from a30
    a30 = none_if_empty_or_stripped(a30in)
    if not a30:
        a30 = ""
    if a30 in field30_corrections():
        correction = field30_corrections()[a30]
        if correction:
            if isinstance(correction, dict):
                if "isbn" in correction:
                    if correction and isinstance(correction["isbn"], str):
                        a30 = correction["isbn"]
                    else:
                        a30 = ""
                else:
                    a30 = ""
            else:
                a30 = ""
        else:
            a30 = ""
    else:
        a30 = ""

    result = (a17 + a18 + a19 + a22 + a30).replace(" ", "").replace(".", "")
    result = none_if_empty_or_stripped(result)
    return result
