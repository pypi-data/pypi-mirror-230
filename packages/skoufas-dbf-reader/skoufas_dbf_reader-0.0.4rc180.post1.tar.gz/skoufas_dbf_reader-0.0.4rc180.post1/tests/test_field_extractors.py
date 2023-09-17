from __future__ import annotations

import pytest

from skoufas_dbf_reader.field_extractors import *


def test_has_author():
    assert not has_author(None)
    assert not has_author("")
    assert has_author("BLA")
    assert not has_author("ΧΣ")
    assert not has_author("X,S")
    assert not has_author("X.S.")
    assert not has_author("X.S")
    assert not has_author("X . Σ.")
    assert not has_author("X.Σ.")
    assert not has_author("X.Σ")
    assert not has_author("Χ.Σ")
    assert not has_author("Χ.Σ.")
    assert not has_author("Χ. Σ .")
    assert not has_author("Χ,Σ")
    assert not has_author("Χ. Σ.")
    assert not has_author("Χ.Χ")
    assert not has_author("Χ.Χ.")


def test_language_codes():
    assert language_codes()
    assert type(language_codes()) == dict
    assert len(language_codes()) > 0


def test_has_language():
    assert not has_language(None)
    assert not has_language("")
    assert not has_language("GAL")
    assert not has_language("ΨΑΡΟΜΗΛΙΓΚΟΣ , ΛΑΖΟΥ , ΚΑΡΤΑΛΗΣ ")
    assert has_language("ΩUENEAU RAYMOND                    GAL")
    assert not has_language("ΚΕΛΕΣΙΔΗΣ, ΤΕΛΗΣ                       Ι")
    assert has_language("BITSIOS,DIMITRIS                  AGL")
    assert has_language("FINLAY GEORG                        GER")


def test_authors_from_a01():
    assert authors_from_a01(None) == []
    assert authors_from_a01("") == []
    assert authors_from_a01("X,S") == []
    assert authors_from_a01("GAL") == ["GAL"]
    assert authors_from_a01("ΨΑΡΟΜΗΛΙΓΚΟΣ , ΛΑΖΟΥ , ΚΑΡΤΑΛΗΣ ") == ["ΨΑΡΟΜΗΛΙΓΚΟΣ,", "ΛΑΖΟΥ,", "ΚΑΡΤΑΛΗΣ,"]
    assert authors_from_a01("ΚΕΛΕΣΙΔΗΣ, ΤΕΛΗΣ                       Ι") == ["ΚΕΛΕΣΙΔΗΣ,ΤΕΛΗΣ"]
    assert authors_from_a01("ΩUENEAU RAYMOND                    GAL") == ["QUENEAU,RAYMOND"]
    assert authors_from_a01("BITSIOS,DIMITRIS                  AGL") == ["ΒΙΤΣΙΟΣ,ΔΗΜΗΤΡΗΣ"]
    assert authors_from_a01("FINLAY GEORG                        GER") == ["FINLAY,GEORGE"]
    assert authors_from_a01("ΑΝΑΓΝΩΣΤΑΚΗΣ,ΗΛΙΑΣ    .") == ["ΑΝΑΓΝΩΣΤΑΚΗΣ,ΗΛΙΑΣ"]


def test_language_from_a01_a02():
    assert not language_from_a01_a02(None, None)
    assert not language_from_a01_a02("", "")
    assert not language_from_a01_a02("GAL", "")
    assert not language_from_a01_a02("ΨΑΡΟΜΗΛΙΓΚΟΣ", "Latin title")
    assert not language_from_a01_a02("ΨΑΡΟΜΗΛΙΓΚΟΣ", "")
    assert language_from_a01_a02("ΨΑΡΟ", "ΑΖΣΦ") == "el"
    assert language_from_a01_a02("Latin Author", "ΑΖΣΦ") == "el"
    assert language_from_a01_a02("ΚΕΛΕΣΙΔΗΣ, ΤΕΛΗΣ                       Ι", "ΑΖΣΦ") == "el"
    assert language_from_a01_a02("ΩUENEAU RAYMOND                    GAL", "bon") == "fr"
    assert language_from_a01_a02("BITSIOS,DIMITRIS                  AGL", "english title") == "en"
    assert language_from_a01_a02("FINLAY GEORG                        GER", "german title") == "de"


def test_title_from_a02():
    assert title_from_a02(None) is None
    assert title_from_a02("") is None
    assert title_from_a02(" ") is None
    assert title_from_a02("GAL ") == "GAL"
    assert title_from_a02(" GAL") == "GAL"


def test_subtitle_from_a03():
    assert subtitle_from_a03(None) is None
    assert subtitle_from_a03("") is None
    assert subtitle_from_a03(" ") is None
    assert subtitle_from_a03("GAL ") == "GAL"
    assert subtitle_from_a03(" GAL") == "GAL"


def test_dewey_from_a04_a05():
    assert dewey_from_a04_a05(None, None) is None
    assert dewey_from_a04_a05("", " ") is None
    assert dewey_from_a04_a05(" ", "") is None
    assert dewey_from_a04_a05("001A", "") == "001 A"
    assert dewey_from_a04_a05("001.009ΚΟΝ ", "") == "001.009 ΚΟΝ"
    assert dewey_from_a04_a05(" 001.009ΚΟΝ", "") == "001.009 ΚΟΝ"
    assert dewey_from_a04_a05("O.50ΠΕΡ", "") == "050 ΠΕΡ"
    assert dewey_from_a04_a05("624.183Χ.Σ", "") == "624.183 ΧΣ"
    assert dewey_from_a04_a05("320ΤΣΟ", "") == "320 ΤΣΟ"

    assert dewey_from_a04_a05("HOEMANN", "") is None


def test_entry_numbers_from_a04_a05_a06_a07_a08_a18_a19():
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(None, None, None, None, None, None, None) == []
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19("", "", "", "", "", "", "") == []
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19("", " ", None, "", "", "", "") == []
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(None, None, "", "", "", "", "") == []
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19("8123", "2710-2709", "", "", "", "", "") == [
        "8123",
        "2710",
        "2709",
    ]
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19("098.122 DEW", "2710-2709", None, None, None, None, None) == [
        "2710",
        "2709",
    ]
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(None, "2710-2709", "foobar", "baz", "yum", "foo", "bar") == [
        "2710",
        "2709",
    ]
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(None, "2710-2710", "foobar", "baz", "yum", "foo", "bar") == [
        "2710",
    ]
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(
        "Some Dewey", "2710-2709", "-", "baz", "yum", "lol", "lal"
    ) == ["2710", "2709"]
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(
        "", "2710-2709", "-10450", "baz", "yum", "ooo", "0980980"
    ) == [
        "2710",
        "2709",
        "10450",
    ]
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(
        "", "2710-2709", "1747-1746-1745-", "baz", "yum", "34", "1414241"
    ) == [
        "2710",
        "2709",
        "1747",
        "1746",
        "1745",
    ]
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19("", "10-1", "4", "baz", "yum", "34", "1414241") == [
        "10",
        "14",
    ]
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19("", "10-1", "5", "baz", "yum", "34", "1414241") == [
        "10",
        "15",
    ]
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(
        "", "10-1", "448 ΚΩΣΤΑΣ ΦΙΛΙΝΗΣ", "baz", "yum", "34", "1414241"
    ) == [
        "10",
        "1448",
    ]
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(
        "", "4225-4226-4228-4229-", "4227-4290-4536-4535-", "4537", "ΕΥΡΩΠΑΙΚ.ΚΕΝΤΡ.ΤΕΧΝΗ", "34", "1414241"
    ) == ["4225", "4226", "4228", "4229", "4227", "4290", "4536", "4535", "4537"]
    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(
        "", "5280-5285-5286-5283-", "5284-5278-5277-5279-", "5281-", "5282-6548-6547", "asasa", "1414241"
    ) == "5280-5285-5286-5283-5284-5278-5277-5279-5281-5282-6548-6547".split("-")

    assert entry_numbers_from_a04_a05_a06_a07_a08_a18_a19(
        "",
        "1938-1937-1936-1935-",
        "1933-1870-1869-1866-",
        "1932",
        "ΣΑΚΕΛΛΑΡΙΟΥ",
        "1931-1867-",
        "1868-1934",
    ) == "1938-1937-1936-1935-1933-1870-1869-1866-1932-1931-1867-1868-1934".split("-")


def test_translator_from_a06():
    assert translator_from_a06(None) is None
    assert translator_from_a06("") is None
    assert translator_from_a06(" ") is None
    assert translator_from_a06("hello") == "hello"
    # Part of field06_corrections
    assert translator_from_a06("-") is None
    assert translator_from_a06("1203") is None
    assert translator_from_a06("3ΕΚΔ") is None
    assert translator_from_a06("2847 ΠΑΠΑΡΡΟΔΟΥ,ΝΙΚ") == "ΠΑΠΑΡΡΟΔΟΥ,ΝΙΚΟΛΑΟΣ"


def test_edition_from_a07():
    assert edition_from_a07(None) is None
    assert edition_from_a07("") is None
    assert edition_from_a07(" ") is None
    assert edition_from_a07("2") == "2"
    assert edition_from_a07("6ΕΚΔ") == "6"
    # invalid
    assert edition_from_a07("ΠΡΟΣΚΗ") is None
    # year
    assert edition_from_a07("1932") is None
    # series
    assert edition_from_a07("4537") is None


def test_editor_from_a08_a09():
    assert editor_from_a08_a09(None, None) is None
    assert editor_from_a08_a09("", "") is None
    assert editor_from_a08_a09(" ", " ") is None
    assert editor_from_a08_a09("hello", " ") == ("hello", None)
    assert editor_from_a08_a09("", "city") == (None, "city")
    assert editor_from_a08_a09("5282-6548-6547", "city") == (None, "city")
    assert editor_from_a08_a09('"Η ΔΑΜΑΣΚΟΣ"', "city") == ("Η ΔΑΜΑΣΚΟΣ", "city")
    assert editor_from_a08_a09("X.E", "city") == (None, "city")
    assert editor_from_a08_a09("hello", "1867") == ("hello", None)
    assert editor_from_a08_a09("hello", "AMSTERDAN") == ("hello", "AMSTERDAM")
    assert editor_from_a08_a09("hello", "ΑΘΗΝΑ 1984") == ("hello", "ΑΘΗΝΑ")
    assert editor_from_a08_a09("hello", "X.T") == ("hello", None)
    assert editor_from_a08_a09("Α.Α. ΛΙΒΑΝΗ", None) == ("ΛΙΒΑΝΗ", "ΑΘΗΝΑ")


def test_edition_year_from_a09_a10():
    assert edition_year_from_a09_a10(None, None) is None
    assert edition_year_from_a09_a10("", None) is None
    assert edition_year_from_a09_a10(" ", "") is None
    assert edition_year_from_a09_a10("", "Χ.Τ") is None
    assert edition_year_from_a09_a10("", "ΑΡΤΑ") is None
    assert edition_year_from_a09_a10("", "Α989") == 1989
    assert edition_year_from_a09_a10("", "MCMX") == 1910
    assert edition_year_from_a09_a10("", "2010") == 2010
    assert edition_year_from_a09_a10("", "197Ο") == 1970
    assert edition_year_from_a09_a10("1867", "197Ο") == 1867

    with pytest.raises(Exception) as e_info:
        edition_year_from_a09_a10("", "foobar")
    assert e_info.exconly() == "Exception: invalid date [foobar]"


def test_pages_from_a11():
    assert pages_from_a11(None) is None
    assert pages_from_a11("") is None
    assert pages_from_a11(" ") is None
    with pytest.raises(Exception) as e_info:
        pages_from_a11("foobar")
    assert e_info.exconly() == "Exception: invalid pages [foobar]"
    assert pages_from_a11("127Σ") == 127
    assert pages_from_a11("447Σ Ε") == 447
    assert pages_from_a11("256ΣΕΓ") == 256
    assert pages_from_a11("29ΙΣ") == 291


def test_topics_from_a12_to_a15_a20_a22_to_a24():
    assert topics_from_a12_to_a15_a20_a22_to_a24(None) == []
    assert topics_from_a12_to_a15_a20_a22_to_a24([]) == []
    assert topics_from_a12_to_a15_a20_a22_to_a24(["", ""]) == []
    assert topics_from_a12_to_a15_a20_a22_to_a24(["\\"]) == []
    assert topics_from_a12_to_a15_a20_a22_to_a24(["'"]) == []
    assert topics_from_a12_to_a15_a20_a22_to_a24(["A", "B"]) == ["A", "B"]
    assert topics_from_a12_to_a15_a20_a22_to_a24(["A-B", "B"]) == ["A", "B"]
    assert topics_from_a12_to_a15_a20_a22_to_a24(["19 ΑΙΩΝΑ", "B"]) == ["19 ΑΙΩΝΑΣ", "B"]
    assert topics_from_a12_to_a15_a20_a22_to_a24(["foobar-(12-13)"]) == ["12-13", "foobar"]
    assert topics_from_a12_to_a15_a20_a22_to_a24(["foobar(12-13)"]) == ["12-13", "foobar"]
    assert topics_from_a12_to_a15_a20_a22_to_a24(["foo bar(12-13)"]) == ["12-13", "foo bar"]
    assert topics_from_a12_to_a15_a20_a22_to_a24(["foo-bar-(12-13)"]) == ["12-13", "foo", "bar"]
    assert topics_from_a12_to_a15_a20_a22_to_a24(["foo bar(1213)"]) == ["1213", "foo bar"]
    assert topics_from_a12_to_a15_a20_a22_to_a24(["foo bar(1213qw)"]) == ["1213qw", "foo bar"]
    assert topics_from_a12_to_a15_a20_a22_to_a24(["foobar-(19 ΑΙΩΝΑ)"]) == ["19 ΑΙΩΝΑΣ", "foobar"]


def test_curator_from_a16():
    assert curator_from_a16(None) is None
    assert curator_from_a16("") is None
    assert curator_from_a16(" ") is None
    assert curator_from_a16("woo") == "woo"
    assert curator_from_a16("ΘΕΣΣΑΛΙΑ") is None
    assert curator_from_a16("#") is None
    assert curator_from_a16("ΒΡΑΣΑΣ,ΝΙΚΟΣ") == "ΒΡΑΣΣΑΣ,ΝΙΚΟΛΑΟΣ"


def test_has_cd_from_a02_a03_a12_a13_a14_a17_a18_a22_a30():
    assert not has_cd_from_a02_a03_a12_a13_a14_a17_a18_a22_a30(None)
    assert not has_cd_from_a02_a03_a12_a13_a14_a17_a18_a22_a30([None, "", "", "gooh", "wordwithcdinside hello"])
    assert has_cd_from_a02_a03_a12_a13_a14_a17_a18_a22_a30(["", "ΠΕΡΙΕΧΕΙ CD"])
    assert has_cd_from_a02_a03_a12_a13_a14_a17_a18_a22_a30(["", "ΤΟΜΟΙ Α-Β-Γ  2 ΑΝΤΙΤΥΠΑ ΠΕΡΙΕΧΕΙ CD"])
    assert has_cd_from_a02_a03_a12_a13_a14_a17_a18_a22_a30(["", "ΤΟΜΟΙ Α-Β-Γ  2 ΑΝΤΙΤΥΠΑ ΠΕΡΙΕΧΕΙ CD"])


def test_has_dvd_from_a30():
    assert not has_dvd_from_a30(None)
    assert not has_dvd_from_a30([None, "", "", "gooh", "wordwithDVDinside hello"])
    assert has_dvd_from_a30(["", "ΠΕΡΙΕΧΕΟ DVD"])


def test_copies_from_a17_a18_a30():
    assert copies_from_a17_a18_a30(None, None, None) is None
    assert copies_from_a17_a18_a30("weewv", "ecwecwc", "woo") is None
    assert copies_from_a17_a18_a30("ΑΝΤΙΤΥΠΑ 2", None, None) == 2
    assert copies_from_a17_a18_a30(None, None, "5 ΑΝΤΙΤΥΠΑ") == 5
    assert copies_from_a17_a18_a30(None, "2ΑΝΤΙΤΥΠΑ", "qefqef") == 2
    assert copies_from_a17_a18_a30(None, None, "ΑΝΑΤΥΠΟ") is None


def test_donation_from_a17_a30():
    assert donation_from_a17_a30(None, None) is None
    assert donation_from_a17_a30("weewv", "ecwecwc") is None
    assert donation_from_a17_a30("ΒΙΒΙΟΘΗΚΗ ΓΑΡΟΥΦΑΛΙΑ", None) == "ΒΙΒΛΙΟΘΗΚΗ ΓΑΡΟΥΦΑΛΙΑ"
    assert donation_from_a17_a30(None, "ΔΩΡΑ ΟΛΓΑ ΜΑΝΟΥ") == "ΜΑΝΟΥ,ΟΛΓΑ"
    assert donation_from_a17_a30(None, "ΑΝΑΤΥΠΟ") is None


def test_offprint_from_a17_a30():
    assert not offprint_from_a17_a21_a30(None, None, None)
    assert not offprint_from_a17_a21_a30("", "", "")
    assert not offprint_from_a17_a21_a30("weewv", "foo", "ecwecwc")
    assert offprint_from_a17_a21_a30("weewv", "", "ΑΝΑΤΥΠΟ")
    assert offprint_from_a17_a21_a30("ΑΝΑΤΥΠΟ", "foo", "")
    assert offprint_from_a17_a21_a30(" wfe", "ΑΝΑΤΥΠΟ", "foo")


def test_volume_from_a17_a18_a20_a30():
    assert volume_from_a17_a18_a20_a30(None, None, None, None) is None
    assert volume_from_a17_a18_a20_a30("", "", "", "") is None
    assert volume_from_a17_a18_a20_a30("wffw", "wef", "wef", "wef") is None
    assert volume_from_a17_a18_a20_a30("", "ΤΕΥΧΗ 10", "", "") == "ΤΕΥΧΗ 10"


def test_material_from_a18_a30():
    assert material_from_a18_a30(None, None) is None
    assert material_from_a18_a30("", "") is None
    assert material_from_a18_a30("aaa", "aa") is None
    assert material_from_a18_a30("ΧΑΡΤ", "") == "ΧΑΡΤΕΣ"
    assert material_from_a18_a30("fwfwe", "ΠΕΡΙΕΧΕΙ 12 ΧΑΡΤΕΣ") == "12 ΧΑΡΤΕΣ"


def test_notes_from_a17_a18_a21_a30():
    assert notes_from_a17_a18_a21_a30(None, None, None, None) is None
    assert notes_from_a17_a18_a21_a30("", "", "", "") is None
    assert notes_from_a17_a18_a21_a30("  ", None, "", "") is None
    assert (
        notes_from_a17_a18_a21_a30(
            "foo",
            "ignored",
            "bar",
            "baz",
        )
        == "foo\nbar\nbaz"
    )
    assert (
        notes_from_a17_a18_a21_a30(
            "2607-2 ΑΝΤΙΤΥΠΑ",
            "ignored",
            "bar",
            "baz",
        )
        == "2607\nbar\nbaz"
    )
    assert (
        notes_from_a17_a18_a21_a30("foo", "ignored", "", "2 ΑΝΤΙΤΥΠΑ ΤΟ ΕΝΑ ΞΕΝΟΓΛΩΣΣΟ")
        == "foo\n2 ΑΝΤΙΤΥΠΑ ΤΟ ΕΝΑ ΞΕΝΟΓΛΩΣΣΟ"
    )
    assert (
        notes_from_a17_a18_a21_a30("foo", "0518-2867", "", "2 ΑΝΤΙΤΥΠΑ ΤΟ ΕΝΑ ΞΕΝΟΓΛΩΣΣΟ")
        == "foo\n0518-2867\n2 ΑΝΤΙΤΥΠΑ ΤΟ ΕΝΑ ΞΕΝΟΓΛΩΣΣΟ"
    )


def test_isbn_from_a17_a18_a19__a22_a30():
    assert isbn_from_a17_a18_a19_a22_a30(None, None, None, None, None) is None
    assert isbn_from_a17_a18_a19_a22_a30("", "", "", "", "") is None
    assert isbn_from_a17_a18_a19_a22_a30(" ", " ", " ", " ", " ") is None
    assert isbn_from_a17_a18_a19_a22_a30("", None, " ", None, "") is None
    assert isbn_from_a17_a18_a19_a22_a30(" 16 ΤΟΜΟΙ", "9789605039", "332", "foo", None) == "9789605039332"
    assert isbn_from_a17_a18_a19_a22_a30("bla", None, None, "blu", "bla") is None
    assert isbn_from_a17_a18_a19_a22_a30("12 TOMOI", "8440909306", None, None, "ΔΩΡΕΑ Ι.ΠΝΕΥΜΑΤΙΚΟΥ") == "8440909306"
    assert isbn_from_a17_a18_a19_a22_a30("2 ΑΝΤΙΤΥΠΑ", "960-05-034", "3-5", None, None) == "960-05-0343-5"
    assert isbn_from_a17_a18_a19_a22_a30("2 ΑΝΤΙΤΥΠΑ", "960-70-25-", "64-4", None, None) == "960-70-25-64-4"
    assert isbn_from_a17_a18_a19_a22_a30("2 ΑΝΤΙΤΥΠΑ", "978-455-44", "3-0", None, None) == "978-455-443-0"
    assert isbn_from_a17_a18_a19_a22_a30("2 ΑΝΤΙΤΥΠΑ", "978-8778-1", "670-40", None, None) == "978-8778-1670-40"
    assert isbn_from_a17_a18_a19_a22_a30("2 ΑΝΤΙΤΥΠΑ", "978-960-20", "8-813-5", None, None) == "978-960-208-813-5"
    assert isbn_from_a17_a18_a19_a22_a30("2 ΑΝΤΙΤΥΠΑ", "9789603031", "574", None, None) == "9789603031574"
    assert isbn_from_a17_a18_a19_a22_a30("2 ΤΟΜΟΙ", "960-14-005", "6-7", None, None) == "960-14-0056-7"
    assert isbn_from_a17_a18_a19_a22_a30("2 ΤΟΜΟΙ", "960-14-012", "7-Χ", None, None) == "960-14-0127-Χ"
    assert isbn_from_a17_a18_a19_a22_a30("2 ΤΟΜΟΙ", "960239269Χ", None, None, None) == "960239269Χ"
    assert isbn_from_a17_a18_a19_a22_a30("4 ΤΕΥΧΗ", "17927099", None, None, "ΔΩΡΕΑ ΟΛΓΑ ΜΑΝΟΥ") == "17927099"
    assert isbn_from_a17_a18_a19_a22_a30("960-2565-440-7", None, None, None, None) == "960-2565-440-7"
    assert isbn_from_a17_a18_a19_a22_a30("9786180123951", None, None, None, None) == "9786180123951"
    assert isbn_from_a17_a18_a19_a22_a30("9789601419985", None, None, None, None) == "9789601419985"
    assert isbn_from_a17_a18_a19_a22_a30("9789605273941", None, None, None, None) == "9789605273941"
    assert isbn_from_a17_a18_a19_a22_a30("9789606051456", None, None, None, None) == "9789606051456"
    assert (
        isbn_from_a17_a18_a19_a22_a30(
            "ΔΩΡΕΑ ΚΩΝ/ΝΟΥ ΤΣΙΛΙΓΙΑΝΝΗ",
            "960-6601-6",
            "8-4",
            "",
            "                                                      960-6601-68",
        )
        == "960-6601-68-4"
    )
    assert isbn_from_a17_a18_a19_a22_a30("ΔΩΡΕΑ ΓΙΑΝΝΗ ΜΠΑΝΙΑ", None, None, None, "960-88458-3-1") == "960-88458-3-1"
    assert (
        isbn_from_a17_a18_a19_a22_a30("ΔΩΡΕΑ ΔΗΜΗΤΡΙΟΥ ΠΟΡΤΟΑΒΑΡΑ", None, None, None, "978-960-503-483-2")
        == "978-960-503-483-2"
    )

    # assert isbn_from_a17_a18_a19_a22_a30("foo", None, "7027-05-1", "5-6", None) is None
    assert isbn_from_a17_a18_a19_a22_a30("foo", None, "7027-05-1", "5-6", None) == "7027-05-15-6"
