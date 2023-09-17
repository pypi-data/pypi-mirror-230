from __future__ import annotations

import os
from collections import defaultdict

import pytest
import yaml

from skoufas_dbf_reader.field_extractors import *
from skoufas_dbf_reader.utilities import all_entries, check_ean, check_isbn, check_issn, is_valid_dewey_strict, romanize


@pytest.fixture
def reports_directory() -> str:
    r = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "reports"))
    os.makedirs(r, exist_ok=True)
    return r


def minimal_entry(input_entry: dict[int, str], fields: list[int]) -> dict[int, str]:
    return {i: input_entry[i] for i in fields if input_entry[i]}


def test_report_single_fields(reports_directory: str):
    field_values: list[set[str]] = [set() for _ in range(31)]
    for entry in all_entries():
        for i in range(1, 31):
            if i in entry and entry[i] and entry[i].strip():
                field_values[i].add(entry[i].strip())
    for i in range(1, 31):
        with open(os.path.join(reports_directory, f"fields_{i:02}.yml"), "w", encoding="utf-8") as outfile:
            yaml.dump(list(sorted(field_values[i])), outfile, default_flow_style=False, allow_unicode=True)


def test_report_single_extracted_fields(reports_directory: str):
    field_values: defaultdict[str, list[str | list[str]]] = defaultdict(list)
    for entry in all_entries():
        authors = authors_from_a01(entry[1])
        for author in authors:
            field_values["author"].append(author)
            if plain_author_re.fullmatch(author) or author in author_corrections().values():
                field_values["plain_author"].append(author)
            else:
                field_values["weird_author"].append(author)

        language = language_from_a01_a02(entry[1], entry[2])
        if language:
            field_values["language"].append(language)

        title = title_from_a02(entry[2])
        if title:
            field_values["title"].append(title)

        subtitle = subtitle_from_a03(entry[3])
        if subtitle:
            field_values["subtitle"].append(subtitle)

        dewey = dewey_from_a04_a05(entry[4], entry[5])
        if dewey:
            field_values["dewey"].append(dewey)

        entry_numbers = entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(
            entry[4], entry[5], entry[6], entry[7], entry[8], entry[18], entry[19]
        )

        field_values["entry_number_lists"].append(entry_numbers)
        for entry_number in entry_numbers:
            field_values["entry_numbers"].append(entry_number)

        translator = translator_from_a06(entry[6])
        if translator:
            translators = translator.split("!!")
            for single_translator in translators:
                field_values["translator"].append(single_translator)
                translator_surname_name = single_translator.split(",", maxsplit=1)
                if len(translator_surname_name) == 2:
                    field_values["translator_family_name"].append(translator_surname_name[0])
                    if translator_surname_name[1].endswith("."):
                        field_values["translator_name_abbreviations"].append(translator_surname_name[1])
                    else:
                        field_values["translator_names"].append(translator_surname_name[1])

        edition = edition_from_a07(entry[7])
        if edition:
            field_values["edition"].append(edition)

        editor = editor_from_a08_a09(entry[8], entry[9])
        if editor:
            if not editor[0] or not editor[1]:
                field_values["editor"].append(f"{editor[0]} // {editor[1]} ({entry[0]})")
            else:
                field_values["editor"].append(f"{editor[0]} // {editor[1]}")

        edition_year = edition_year_from_a09_a10(entry[9], entry[10])
        if edition_year:
            field_values["edition_year"].append(str(edition_year))

        pages = pages_from_a11(entry[11])
        if pages:
            field_values["pages"].append(str(pages))

        topic_list = topics_from_a12_to_a15_a20_a22_to_a24(
            [
                entry[12],
                entry[13],
                entry[14],
                entry[15],
                entry[20],
                entry[22],
                entry[23],
                entry[24],
            ]
        )
        field_values["topic_lists"].append(topic_list)
        for topic in topic_list:
            field_values["topics"].append(topic)

        curator = curator_from_a16(entry[16])
        if curator:
            field_values["curator"].append(curator)

        copies = copies_from_a17_a18_a30(entry[17], entry[18], entry[30])
        if copies:
            field_values["copies"].append(str(copies))

        donation = donation_from_a17_a30(entry[17], entry[30])
        if donation:
            field_values["donation"].append(donation)

        volume = volume_from_a17_a18_a20_a30(entry[17], entry[18], entry[20], entry[30])
        if volume:
            field_values["volume"].append(volume)

        material = material_from_a18_a30(entry[18], entry[30])
        if material:
            field_values["material"].append(material)

        notes = notes_from_a17_a18_a21_a30(entry[17], entry[18], entry[21], entry[30])
        if notes:
            field_values["notes"].append(notes)

        isbn = isbn_from_a17_a18_a19_a22_a30(entry[17], entry[18], entry[19], entry[22], entry[30])
        if isbn:
            if not check_isbn(isbn):
                field_values["isbn"].append(isbn)
            if not check_issn(isbn):
                field_values["issn"].append(isbn)
            if not check_ean(isbn):
                field_values["ean"].append(isbn)

    for k, values in field_values.items():
        with open(os.path.join(reports_directory, f"calculated_field_{k}.yml"), "w", encoding="utf-8") as outfile:
            if values and isinstance(values[0], list):
                yaml.dump(values, outfile, default_flow_style=False, allow_unicode=True)
            else:
                yaml.dump(
                    list(sorted(set(values), key=lambda x: romanize(x))),
                    outfile,
                    default_flow_style=False,
                    allow_unicode=True,
                )


def test_report_dewey(reports_directory: str):
    weird_dewey: list[dict[int, str]] = list()
    for entry in all_entries():
        dewey = dewey_from_a04_a05(entry[4], entry[5])
        if dewey:
            if not is_valid_dewey_strict(dewey):
                weird_dewey.append(minimal_entry(entry, [0, 1, 2, 4, 5, 6]))
        else:
            if none_if_empty_or_stripped(entry[4]):
                weird_dewey.append(minimal_entry(entry, [0, 1, 2, 4, 5, 6]))
    with open(os.path.join(reports_directory, f"weird_dewey.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump(weird_dewey, outfile, default_flow_style=False, allow_unicode=True)


def test_report_entry_numbers(reports_directory: str):
    all_entry_numbers: dict[str, dict[int, str]] = dict()
    no_entry_numbers: list[dict[int, str]] = list()
    non_numeric: defaultdict[str, list[dict[int, str]]] = defaultdict(list)
    duplicate_entry_numbers: defaultdict[str, list[dict[int, str]]] = defaultdict(list)
    for entry in all_entries():
        entry_numbers = entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(
            entry[4], entry[5], entry[6], entry[7], entry[8], entry[18], entry[19]
        )
        if not entry_numbers:
            no_entry_numbers.append(minimal_entry(entry, [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 19]))
        else:
            for n in entry_numbers:
                if n in all_entry_numbers:
                    if not duplicate_entry_numbers[n]:
                        duplicate_entry_numbers[n].append(all_entry_numbers[n])
                    duplicate_entry_numbers[n].append(
                        minimal_entry(entry, [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 19])
                    )
                else:
                    all_entry_numbers[n] = minimal_entry(entry, [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 19])
                if not n.isnumeric():
                    non_numeric[n].append(minimal_entry(entry, [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 19]))
    with open(os.path.join(reports_directory, f"entry_numbers_no_entry_numbers.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump(no_entry_numbers, outfile, default_flow_style=False, allow_unicode=True)
    with open(os.path.join(reports_directory, f"entry_numbers_non_numeric.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump(dict(non_numeric), outfile, default_flow_style=False, allow_unicode=True)
    with open(os.path.join(reports_directory, f"entry_numbers_duplicate.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump(dict(duplicate_entry_numbers), outfile, default_flow_style=False, allow_unicode=True)


def test_report_weird_names(reports_directory: str):
    weird_translators: list[str] = []
    weird_authors: list[str] = []
    weird_curators: list[str] = []
    weird_donors: list[str] = []
    valid_name_re = re.compile(r"[A-ZΑ-Ω\-]+,[A-ZΑ-Ω\.]*\.?")
    valid_name2_re = re.compile(r"[A-ZΑ-Ω\-]+,[A-ZΑ-Ω\.]*,[A-ZΑ-Ω\.]*\.?")
    valid_name3_re = re.compile(r"[A-ZΑ-Ω\-]+,[A-ZΑ-Ω\.]*\.?@[A-ZΑ-Ω\-]+")
    valid_name4_re = re.compile(r"[A-ZΑ-Ω\-]+,[A-ZΑ-Ω\.]*,[A-ZΑ-Ω\.]*\.?@[A-ZΑ-Ω\-]+")
    for entry in all_entries():
        translator = translator_from_a06(entry[6])
        if translator:
            translators = translator.split("!!")
            for translator in translators:
                if not valid_name_re.fullmatch(translator):
                    weird_translators.append(translator)
        authors = authors_from_a01(entry[1])
        for author in authors:
            if (
                (not valid_name_re.fullmatch(author))
                and (not valid_name2_re.fullmatch(author))
                and (not valid_name3_re.fullmatch(author))
                and (not valid_name4_re.fullmatch(author))
            ):
                weird_authors.append(author)
        curator = curator_from_a16(entry[16])
        if curator:
            curators = curator.split("!!")
            for curator in curators:
                if not valid_name_re.fullmatch(curator):
                    weird_curators.append(curator)
        donor = donation_from_a17_a30(entry[17], entry[30])
        if donor:
            donors = donor.split("!!")
            for donor in donors:
                if not valid_name_re.fullmatch(donor):
                    weird_donors.append(donor)
    for field, thelist in [
        ("translators", weird_translators),
        ("authors", weird_authors),
        ("curators", weird_curators),
        ("donors", weird_donors),
    ]:
        with open(os.path.join(reports_directory, f"weird_{field}.yml"), "w", encoding="utf-8") as outfile:
            yaml.dump(sorted(set(thelist)), outfile, default_flow_style=False, allow_unicode=True)


def test_report_bools(reports_directory: str):
    entries_with_cd: list[dict[int, str]] = list()
    entries_with_dvd: list[dict[int, str]] = list()
    entries_with_offprint: list[dict[int, str]] = list()
    for entry in all_entries():
        if has_cd_from_a02_a03_a12_a13_a14_a17_a18_a22_a30(
            [
                entry[2],
                entry[3],
                entry[12],
                entry[13],
                entry[14],
                entry[17],
                entry[18],
                entry[22],
                entry[30],
            ]
        ):
            entries_with_cd.append(minimal_entry(entry, list(range(0, 31))))
        if has_dvd_from_a30(
            [
                entry[30],
            ]
        ):
            entries_with_dvd.append(minimal_entry(entry, list(range(0, 31))))
        if offprint_from_a17_a21_a30(entry[17], entry[21], entry[30]):
            entries_with_offprint.append(minimal_entry(entry, list(range(0, 31))))
    with open(os.path.join(reports_directory, f"entries_with_cd.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump(entries_with_cd, outfile, default_flow_style=False, allow_unicode=True)
    with open(os.path.join(reports_directory, f"entries_with_dvd.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump(entries_with_dvd, outfile, default_flow_style=False, allow_unicode=True)
    with open(os.path.join(reports_directory, f"entries_with_offprint.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump(entries_with_offprint, outfile, default_flow_style=False, allow_unicode=True)


def test_report_donors(reports_directory: str):
    count_map: defaultdict[str, int] = defaultdict(int)
    for entry in all_entries():
        donors = donation_from_a17_a30(entry[17], entry[30])
        if donors:
            for donor in donors.split("!!"):
                count_map[donor] = count_map[donor] + 1

    with open(os.path.join(reports_directory, f"donors_count.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump(
            dict(sorted(count_map.items(), key=lambda x: x[1], reverse=True)),
            outfile,
            default_flow_style=False,
            allow_unicode=True,
        )


def test_report_isbns(reports_directory: str):
    entries_with_errors: dict[str, dict[str, str | list[Optional[str]] | dict[int, str]]] = dict()
    for entry in all_entries():
        result = isbn_from_a17_a18_a19_a22_a30(
            entry[17],
            entry[18],
            entry[19],
            entry[22],
            entry[30],
        )
        if not result:
            continue
        checks = [check_isbn(result), check_issn(result), check_ean(result)]
        if None in checks:
            continue
        else:
            entries_with_errors[entry[0]] = {
                "entry": minimal_entry(entry, list(range(0, 31))),
                "isbn": result,
                "errors": checks,
            }
    with open(
        os.path.join(reports_directory, f"entries_with_invalid_isbn_issn_ean.yml"), "w", encoding="utf-8"
    ) as outfile:
        yaml.dump(entries_with_errors, outfile, default_flow_style=False, allow_unicode=True)


def test_report_extracted_fields(reports_directory: str):
    converted_entries: list[dict[str, Optional[str] | int | bool | list[str] | dict[int, str]]] = []
    for entry in all_entries():
        converted_entry: dict[str, Optional[str] | int | bool | list[str] | dict[int, str]] = dict()
        converted_entry["dbase_number"] = entry[0]
        converted_entry["authors"] = authors_from_a01(entry[1])

        language = language_from_a01_a02(entry[1], entry[2])
        if language:
            converted_entry["language"] = language

        title = title_from_a02(entry[2])
        if title:
            converted_entry["title"] = title

        subtitle = subtitle_from_a03(entry[3])
        if subtitle:
            converted_entry["subtitle"] = subtitle

        dewey = dewey_from_a04_a05(entry[4], entry[5])
        if dewey:
            converted_entry["dewey"] = dewey

        converted_entry["entry_numbers"] = entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(
            entry[4], entry[5], entry[6], entry[7], entry[8], entry[18], entry[19]
        )

        translator = translator_from_a06(entry[6])
        if translator:
            converted_entry["translators"] = translator.split("!!")
            # for single_translator in translators:
            #     translator_surname_name = single_translator.split(",", maxsplit=1)
            #     if len(translator_surname_name) == 2:
            #         field_values["translator_family_name"].append(translator_surname_name[0])
            #         if translator_surname_name[1].endswith("."):
            #             field_values["translator_name_abbreviations"].append(translator_surname_name[1])
            #         else:
            #             field_values["translator_names"].append(translator_surname_name[1])

        edition = edition_from_a07(entry[7])
        if edition:
            converted_entry["edition"] = edition

        editor = editor_from_a08_a09(entry[8], entry[9])
        if editor:
            converted_entry["editor"] = f"{editor[0]} // {editor[1]}"

        edition_year = edition_year_from_a09_a10(entry[9], entry[10])
        if edition_year:
            converted_entry["edition_year"] = edition_year

        pages = pages_from_a11(entry[11])
        if pages:
            converted_entry["pages"] = pages

        topic_list = topics_from_a12_to_a15_a20_a22_to_a24(
            [
                entry[12],
                entry[13],
                entry[14],
                entry[15],
                entry[20],
                entry[22],
                entry[23],
                entry[24],
            ]
        )
        converted_entry["topics"] = topic_list

        curator = curator_from_a16(entry[16])
        if curator:
            converted_entry["curator"] = curator

        copies = copies_from_a17_a18_a30(entry[17], entry[18], entry[30])
        if copies:
            converted_entry["copies"] = copies

        donation = donation_from_a17_a30(entry[17], entry[30])
        if donation:
            converted_entry["donors"] = donation.split("!!")

        volume = volume_from_a17_a18_a20_a30(entry[17], entry[18], entry[20], entry[30])
        if volume:
            converted_entry["volume"] = volume

        material = material_from_a18_a30(entry[18], entry[30])
        if material:
            converted_entry["material"] = material

        notes = notes_from_a17_a18_a21_a30(entry[17], entry[18], entry[21], entry[30])
        if notes:
            converted_entry["notes"] = notes

        converted_entry["has_cd"] = has_cd_from_a02_a03_a12_a13_a14_a17_a18_a22_a30(
            [
                entry[2],
                entry[3],
                entry[12],
                entry[13],
                entry[14],
                entry[17],
                entry[18],
                entry[22],
                entry[30],
            ]
        )

        converted_entry["has_dvd"] = has_dvd_from_a30(
            [
                entry[30],
            ]
        )

        converted_entry["offprint"] = offprint_from_a17_a21_a30(entry[17], entry[21], entry[30])

        isbn = isbn_from_a17_a18_a19_a22_a30(entry[17], entry[18], entry[19], entry[22], entry[30])
        if isbn:
            if not check_isbn(isbn):
                converted_entry["isbn"] = isbn
            if not check_issn(isbn):
                converted_entry["issn"] = isbn
            if not check_ean(isbn):
                converted_entry["ean"] = isbn

        converted_entry["original_entry"] = entry
        converted_entries.append(converted_entry)

    with open(
        os.path.join(
            os.path.dirname(__file__), os.pardir, "src", "skoufas_dbf_reader", "data", "converted_entries.yml"
        ),
        "w",
        encoding="utf-8",
    ) as outfile:
        yaml.dump(
            {"converted_entries": converted_entries},
            outfile,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


def test_report_no_language(reports_directory: str):
    titles = []
    for entry in all_entries():
        language = language_from_a01_a02(entry[1], entry[2])
        if not language:
            title = title_from_a02(entry[2])
            if title:
                titles.append(title)
    with open(os.path.join(reports_directory, "titles_with_no_language.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump(
            {"titles": titles},
            outfile,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


def test_report_authors_with_no_correction(reports_directory: str):
    authors = []
    for entry in all_entries():
        a01 = entry[1]
        if not a01:
            continue
        if not has_author(a01):
            continue
        strip_finals = list(language_codes().keys()) + [
            " Ι",
            " .",
        ]
        for final in strip_finals:
            if a01.endswith(" " + final):
                a01 = a01.replace(final, "")
        author = a01.strip()
        if author not in author_corrections():
            authors.append(author)

    def correct_name(name):
        return name.replace("ΚΩΝ/ΝΟΣ", "ΚΩΝΣΤΑΝΤΙΝΟΣ")

    with open(os.path.join(reports_directory, "authors_with_no_correction.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump(
            {"authors_with_no_correction": {k: correct_name(k) for k in sorted(authors)}},
            outfile,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    with open(
        os.path.join(reports_directory, "authors_with_no_correction_phonetic.yml"), "w", encoding="utf-8"
    ) as outfile:
        yaml.dump(
            {"authors_with_no_correction": {k: correct_name(k) for k in sorted(authors, key=lambda x: romanize(x))}},
            outfile,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
