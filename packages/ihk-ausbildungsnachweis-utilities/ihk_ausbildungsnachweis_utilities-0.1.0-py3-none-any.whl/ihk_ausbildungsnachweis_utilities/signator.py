# Copyright (C) 2023 twyleg
import datetime
import json
import jsonschema
import fitz

from pathlib import Path
from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12
from endesive.pdf import cms


FILE_DIR = Path(__file__).parent


class Profile:
    def __init__(self, name: str, email: str, p12_certificate_file_filepath: Path, background_image_filepath: Path):
        self.name = name
        self.email = email
        self.p12_certificate_file_filepath = p12_certificate_file_filepath
        self.background_image_filepath = background_image_filepath


def __validate_input_for_sign_pdf(
    ausbildungsachweis_pdf_filepath: Path, certificate_filepath: Path, signature_configuration_filepath: Path
) -> None:
    if not ausbildungsachweis_pdf_filepath.is_file():
        raise FileNotFoundError(ausbildungsachweis_pdf_filepath)

    if not certificate_filepath.is_file():
        raise FileNotFoundError(certificate_filepath)

    if not signature_configuration_filepath.is_file():
        raise FileNotFoundError(signature_configuration_filepath)


def __read_profile(profile_file_filepath: Path) -> Profile:
    with open(profile_file_filepath, "r") as profile_file:
        profile_dict = json.load(profile_file)

        with open(FILE_DIR / "schemas/profile.json") as profile_schema_file:
            profile_schema_dict = json.load(profile_schema_file)
            jsonschema.validate(instance=profile_dict, schema=profile_schema_dict)

        p12_file_filepath = Path(profile_dict["p12_certificate_file_filepath"])
        if not p12_file_filepath.is_absolute():
            p12_file_filepath = profile_file_filepath.parent / p12_file_filepath

        background_image_filepath = Path(profile_dict["background_image_filepath"])
        if not background_image_filepath.is_absolute():
            background_image_filepath = background_image_filepath.parent / background_image_filepath

        return Profile(
            name=profile_dict["name"],
            email=profile_dict["email"],
            p12_certificate_file_filepath=p12_file_filepath,
            background_image_filepath=background_image_filepath,
        )


def sign_ausbildungsnachweis_pdf(ausbildungsnachweis_pdf_filepath: Path, profile_file_filepath: Path) -> None:
    profile = __read_profile(profile_file_filepath)
    date_datetime = datetime.datetime.utcnow()
    date_string = date_datetime.strftime("%d.%m.%Y - %H:%M:%S+00'00'")

    doc = fitz.open(ausbildungsnachweis_pdf_filepath)
    page = doc[0]
    height = page.mediabox.height

    page_number = 0
    instances = []
    page_numbers = []

    for page in doc:
        text = "Ausbildungsbeauftragte"
        text_instances = page.search_for(text)

        for inst in text_instances:
            instances.append(inst)
            page_numbers.append(page_number)

        page_number += 1

    inst_rect = instances[-1]
    img_rect = fitz.Rect(inst_rect.x0, inst_rect.y0, inst_rect.x1, inst_rect.y1)

    text_box = fitz.Rect(inst_rect.x0 - 45, inst_rect.y0 - 40, inst_rect.x1 + 50, inst_rect.y1 - 10)
    text = f"Date: {date_string}\nName: {profile.name}\nContact: {profile.email}"
    doc[-1].insert_textbox(
        text_box, text, fontsize=8, fontname="helv", fontfile=None, align=0  # choose fontsize (float)
    )
    doc.save(ausbildungsnachweis_pdf_filepath, incremental=1, encryption=0)

    dct = {
        "aligned": 0,
        "sigflags": 3,
        "sigflagsft": 132,
        "sigpage": page_numbers[-1],
        "sigfield": "Signature",
        "auto_sigfield": True,
        "signform": False,
        "signaturebox": (img_rect.x0 - 45, height - img_rect.y1 + 10, img_rect.x1 + 50, height - img_rect.y0 + 40),
        "signature_appearance": {
            "background": str(profile.background_image_filepath.absolute()),
            "labels": True,
            "display": [],
            "software": "endesive",
            "outline": [0.1, 0.1, 0.1],
            "border": 0,
        },
        "contact": profile.email,
        "location": "Wolfsburg",
        "signingdate": date_string,
        "reason": "Ausbildungsnachweis signed",
        "password": "1234",
    }

    with open(profile.p12_certificate_file_filepath, "rb") as fp:
        p12 = pkcs12.load_key_and_certificates(fp.read(), b"1234", backends.default_backend())

    unsigned_input_data = None
    with open(ausbildungsnachweis_pdf_filepath, "rb") as input_file:
        unsigned_input_data = input_file.read()

    signed_input_data = cms.sign(unsigned_input_data, dct, p12[0], p12[1], p12[2], "sha256")

    with open(ausbildungsnachweis_pdf_filepath, "wb") as fp:
        fp.write(unsigned_input_data)
        fp.write(signed_input_data)
