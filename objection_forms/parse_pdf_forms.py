from typing import List

import pypdfium2 as pdfium
import pickle


class CoordinatesNosahBet:
    # left, bottom, right, top
    name_boundaries = (390, 130, 460, 140)
    id_boundaries = (250, 130, 322, 143)
    street_boundaries = (420, 105, 480, 120)
    building_boundaries = (365, 110, 380, 122)
    apt_boundaries = (210, 110, 230, 122)
    email_boundaries = (360, 85, 500, 100)
    phone_boundaries = (210, 90, 282, 100)


class CoordinatesNosahAlef:
    # left, bottom, right, top
    name_boundaries = (390, 155, 455, 170)
    id_boundaries = (200, 160, 270, 170)
    street_boundaries = (400, 135, 480, 148)
    building_boundaries = (370, 138, 380, 150)
    apt_boundaries = (220, 140, 242, 150)
    email_boundaries = (360, 115, 510, 130)
    phone_boundaries = (220, 120, 290, 130)


KNOWN_STREETS = [
    "אפרים קציר",
    "יהודית בירק",
    "אהרון צחנובר",
    "כרמל",
    "ישראל אומן",
    "אברהם הרשקו",
    "יעקב ברמן",
    "יובל נאמן",
    "דניאל כהנמן",
    "חיים הררי",
    "יוספזון",
    "מישל רבל",
    "יחיאל פלדי",
    "דוכיפת",
    "עזרא",
    "גורודיסקי",
    "שדרות בן ציון",
    "הנשיא הראשון",
    "פיאמנטה",
    "קלמן ביאלר",
    "בוסתנאי",
    "פריד",
    "גורדון",
    "שמואל ברגמן",
    "הרב משה צבי נריה",
    "דוד מילשטיין",
    "יוסף קאפח",
    "אלקלעי",
    "הרצל",
    "גולדין",
    "קטלב",
]


def extract_data(pdf_file_path: str) -> List[str]:
    doc = pdfium.PdfDocument(pdf_file_path)
    page = doc.get_page(0)
    parser = page.get_textpage()

    res = [
        parser.get_text(*bounds).strip(" :_\r\n\t")
        for bounds in (
            CoordinatesNosahBet.name_boundaries,
            CoordinatesNosahBet.id_boundaries,
            CoordinatesNosahBet.street_boundaries,
            CoordinatesNosahBet.building_boundaries,
            CoordinatesNosahBet.apt_boundaries,
            CoordinatesNosahBet.email_boundaries,
            CoordinatesNosahBet.phone_boundaries,
        )
    ]
    res[2] = normalize_street(res[2])

    parser.close()
    page.close()
    doc.close()
    return res


def normalize_street(raw: str) -> str:
    raw_words_set = set(raw.split())
    for street in KNOWN_STREETS:
        for word in street.split():
            if word in raw_words_set:
                return street
    print(f"WARN: unidentified street: {raw}")
    return raw


def main():
    extracted_details = []
    err_daily_2 = []

    with open("./signatures_parse/unknown_forms.txt", "r") as f:
        unknown_forms = f.read().split("\n")
    for form_path in unknown_forms:
        try:
            extracted_details.append(extract_data(form_path))
        except Exception as e:
            err_daily_2.append(form_path)
            print("ERROR:::>", form_path, e)

    # create backup
    with open("daily_extracted_pdf", "wb") as f:
        pickle.dump(extracted_details, f)

    # export as data-file
    with open("second_pdf_extraction.tsv", "w") as f:
        lines = ["\t".join(["name", "id", "street", "building", "apartment", "email", "phone"])] + [
            "\t".join(l) for l in extracted_details
        ]
        f.write("\n".join(lines))

    with open("err_daily_2.txt", "w") as f:
        f.write("\n".join(err_daily_2))


if __name__ == "__main__":
    """
    install pdf dependency by
        pip3 install --no-build-isolation -U pypdfium2
    """
    # % history - f pdf_extract.py
    main()
