import os
from typing import List

import pypdfium2 as pdfium
import pickle


class Coordinates:
    # left, bottom, right, top
    name_boundaries = (390, 155, 455, 170)
    id_boundaries = (200, 160, 270, 170)
    street_boundaries = (400, 135, 480, 148)
    building_boundaries = (370, 138, 380, 150)
    apt_boundaries = (220, 140, 242, 150)
    email_boundaries = (360, 115, 510, 130)
    phone_boundaries = (220, 120, 290, 130)


def extract_data(pdf_file_path: str) -> List[str]:
    doc = pdfium.PdfDocument(pdf_file_path)
    page = doc.get_page(0)
    parser = page.get_textpage()
    res = [parser.get_text(*bounds).strip() for bounds in (
        Coordinates.name_boundaries, Coordinates.id_boundaries, Coordinates.street_boundaries,
        Coordinates.building_boundaries, Coordinates.apt_boundaries,
        Coordinates.email_boundaries, Coordinates.phone_boundaries)]
    parser.close()
    page.close()
    doc.close()
    return res


def main():
    extracted_details = []
    for form in os.listdir('./outcome/'):
        form_path = os.path.join('outcome', form)
        try:
            extracted_details.append(extract_data(form_path))
        except Exception as e:
            print('ERROR:::>', form_path, e)

    # create backup
    with open("nightly_extracted_pdf", 'wb') as f:
        pickle.dump(extracted_details, f)

    # export as data-file
    with open("first_pdf_extraction.tsv", 'w') as f:
        lines = ['\t'.join(['name', 'id', 'street', 'building', 'apartment', 'email', 'phone'])] + \
                ['\t'.join(l) for l in extracted_details]
        f.write('\n'.join(lines))


if __name__ == '__main__':
    """
    install pdf dependency by
        pip3 install --no-build-isolation -U pypdfium2
    """
    # % history - f pdf_extract.py
    main()
