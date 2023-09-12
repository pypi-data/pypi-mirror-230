# Copyright (C) 2023, NG:ITL
import json
import tempfile
import unittest
import fitz
from pathlib import Path

from ihk_ausbildungsnachweis_utilities.certificate_builder import CentralAuthority, identity_create
from ihk_ausbildungsnachweis_utilities.builder import build_ausbildungsnachweis_pdf, InvalidInputFileContentException
from ihk_ausbildungsnachweis_utilities.signator import sign_ausbildungsnachweis_pdf

#
# Reminder - General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#


FILE_DIR = Path(__file__).parent


class ApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp())

        print(f"{unittest.TestCase.id(self)}: {self.tmp_dir}")

        self.template_dirpath = FILE_DIR.parent / "templates"
        self.ausbildungsnachweis_xml_filepath = self.tmp_dir / "ausbildungsnachweis_input.xml"
        self.profile_file_filepath = self.prepare_profile()

        self.signaturebox_text = "Test Instructor"
        self.signaturebox_position_identifier = "Ausbildungsbeauftragte/r Unterschrift und Datum"
        self.max_distance_of_signature_to_identifier = 35.0
        self.signaturebox_upper_left_point_x = 400.0
        self.signaturebox_lower_right_point_x = 520.0

    def prepare_certificate(self):
        cert_dirpath = self.tmp_dir / "certs"
        cert_dirpath.mkdir(exist_ok=True)

        central_authority = CentralAuthority(
            certificate_filepath=cert_dirpath / "ca.crt.pem",
            private_key_filepath=cert_dirpath / "ca.priv.pem",
            password="1234",
        )

        print("Generating certificates")
        identity_create(cert_dirpath, "test_instructor", "1234", central_authority)

    def prepare_profile(
        self,
        name="Test Instructor",
        email="test.instructor@domain.com",
        p12_certificate_file_filepath="./certs/test_instructor/test_instructor.p12",
        background_image_filepath=FILE_DIR.parent / "examples/signature_background.png",
    ):
        profile_file_filepath = self.tmp_dir / "test_instructor_profile.json"
        self.prepare_certificate()
        with open(profile_file_filepath, "w") as profile_file:
            profile_dict = {
                "name": name,
                "email": email,
                "p12_certificate_file_filepath": p12_certificate_file_filepath,
                "background_image_filepath": str(background_image_filepath),
            }
            profile_json_str = json.dumps(profile_dict, indent=4)
            profile_file.write(profile_json_str)
        return profile_file_filepath

    def prepare_ausbildungsnachweis_xml(
        self,
        ausbildungsnachweis_xml_filepath: Path,
        name="Testvorname",
        surname="Testname",
        number=1,
        year=1,
        week_from="01.01.2023",
        week_to="07.01.2023",
        department="NGITL SE-5/5",
        work="Betriebliche Tätigkeit Stuff",
        courses="Betrieblicher Unterricht Stuff",
        school="Berufsschulstuff",
    ) -> Path:
        xml_string = f"""
        <ausbildungsnachweis>
            <vorname>{name}</vorname>
            <name>{surname}</name>
            <nr>{number}</nr>
            <ausbildungsjahr>{year}</ausbildungsjahr>
            <ausbildungswoche_von>{week_from}</ausbildungswoche_von>
            <ausbildungswoche_bis>{week_to}</ausbildungswoche_bis>
            <abteilung>{department}</abteilung>

            <betriebliche_taetigkeit>
                {work}
            </betriebliche_taetigkeit>

            <betrieblicher_unterricht>
                {courses}
            </betrieblicher_unterricht>

            <berufsschule>
                {school}
            </berufsschule>

        </ausbildungsnachweis>
        """

        with open(ausbildungsnachweis_xml_filepath, "w") as file:
            file.write(xml_string)

        return ausbildungsnachweis_xml_filepath

    def get_space_filler_string(self) -> str:
        string = "First line"
        for i in range(20):
            string += "\n"
        string += "Last line"
        return string

    def get_text_instance_from_pdf(self, pdf_filepath: Path, expected_string: str) -> fitz.Rect:
        doc = fitz.open(pdf_filepath)

        for page in doc:
            text_instances = page.search_for(expected_string)
            if text_instances:
                return text_instances[0]

    def assert_pdf_contains(self, pdf_filepath, expected_string: str):
        doc = fitz.open(pdf_filepath)

        found = False
        for page in doc:
            text_instances = page.search_for(expected_string)
            if text_instances:
                found = True
                break
        self.assertTrue(found)

    def assert_x_position_in_range(self, pdf_filepath: Path, signature: str, x_min: float, x_max: float) -> bool:
        instance_rect = self.get_text_instance_from_pdf(pdf_filepath, signature)
        upper_left_point = instance_rect.x0
        lower_right_point = instance_rect.x1
        in_bounds = False

        if x_min <= upper_left_point and x_max >= lower_right_point:
            in_bounds = True

        return in_bounds

    def assert_y_position_in_range(
        self, pdf_filepath: Path, signature_box_position_identifier: str, signature: str, max_distance: float
    ) -> bool:
        signature_box_position_identifier_instance_rect = self.get_text_instance_from_pdf(
            pdf_filepath, signature_box_position_identifier
        )
        signature_box_position_identifier_upper_point = signature_box_position_identifier_instance_rect.y0
        signature_instance_rect = self.get_text_instance_from_pdf(pdf_filepath, signature)
        signature_box_position_upper_point = signature_instance_rect.y0
        signature_box_position_lower_point = signature_instance_rect.y1
        in_bounds = False

        if (
            signature_box_position_lower_point < signature_box_position_identifier_upper_point
            and signature_box_position_upper_point > signature_box_position_identifier_upper_point - max_distance
        ):
            in_bounds = True

        return in_bounds

    def build_and_sign_pdf_from_xml(self, xml_filepath: Path) -> Path:
        ausbildungsnachweis_pdf_filepath = build_ausbildungsnachweis_pdf(xml_filepath, self.tmp_dir)
        sign_ausbildungsnachweis_pdf(ausbildungsnachweis_pdf_filepath, self.profile_file_filepath)
        return ausbildungsnachweis_pdf_filepath

    def test_ValidInputsProvided_BuildPdfFromAusbildungsnachweisXml_ValidPdfCreated(self):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath)

        valid_ausbildungsnachweis_pdf_filepath = build_ausbildungsnachweis_pdf(
            self.ausbildungsnachweis_xml_filepath, self.tmp_dir
        )
        self.assertTrue(valid_ausbildungsnachweis_pdf_filepath.exists())

        self.assert_pdf_contains(valid_ausbildungsnachweis_pdf_filepath, "Ausbildungsnachweis Nr.: 1")
        self.assert_pdf_contains(valid_ausbildungsnachweis_pdf_filepath, "NGITL SE-5/5")
        self.assert_pdf_contains(valid_ausbildungsnachweis_pdf_filepath, "Testname, Testvorname")

    def test_ValidInputsProvided_BuildAndSignPdfFromAusbildungsnachweisXml_ValidSignPdfCreated(self):
        valid_ausbildungsnachweis_xml_filepath = self.prepare_ausbildungsnachweis_xml(
            self.ausbildungsnachweis_xml_filepath
        )
        self.build_and_sign_pdf_from_xml(valid_ausbildungsnachweis_xml_filepath)

    def test_ValidInputsProvided_BuildAndSignPdfFromAusbildungsnachweisXml_ValidPdfCreatedWithSignatureBoxAtCorrectPosition(
        self,
    ):
        valid_ausbildungsnachweis_xml_filepath = self.prepare_ausbildungsnachweis_xml(
            self.ausbildungsnachweis_xml_filepath
        )
        valid_ausbildungsnachweis_pdf_filepath = self.build_and_sign_pdf_from_xml(
            valid_ausbildungsnachweis_xml_filepath
        )
        x_points_in_bounds = self.assert_x_position_in_range(
            valid_ausbildungsnachweis_pdf_filepath,
            self.signaturebox_text,
            self.signaturebox_upper_left_point_x,
            self.signaturebox_lower_right_point_x,
        )
        y_points_in_bounds = self.assert_y_position_in_range(
            valid_ausbildungsnachweis_pdf_filepath,
            self.signaturebox_position_identifier,
            self.signaturebox_text,
            self.max_distance_of_signature_to_identifier,
        )
        self.assertTrue(x_points_in_bounds and y_points_in_bounds)

    def test_ValidInputsProvided_BuildAndSignPdfFromAusbildungsnachweisXml_ValidTwoSidedPdfCreatedWithSignatureBoxAtCorrectPosition(
        self,
    ):
        valid_ausbildungsnachweis_xml_filepath = self.prepare_ausbildungsnachweis_xml(
            self.ausbildungsnachweis_xml_filepath,
            work=self.get_space_filler_string(),
            courses=self.get_space_filler_string(),
            school=self.get_space_filler_string(),
        )
        valid_ausbildungsnachweis_pdf_filepath = self.build_and_sign_pdf_from_xml(
            valid_ausbildungsnachweis_xml_filepath
        )
        x_points_in_bounds = self.assert_x_position_in_range(
            valid_ausbildungsnachweis_pdf_filepath,
            self.signaturebox_text,
            self.signaturebox_upper_left_point_x,
            self.signaturebox_lower_right_point_x,
        )
        y_points_in_bounds = self.assert_y_position_in_range(
            valid_ausbildungsnachweis_pdf_filepath,
            self.signaturebox_position_identifier,
            self.signaturebox_text,
            self.max_distance_of_signature_to_identifier,
        )
        self.assertTrue(x_points_in_bounds and y_points_in_bounds)

    def test_InvalidInputAusbildungsnachweisXmlWithMissingNumberProvided_BuildPdfFromAusbildungsnachweisXml_MissingInputParameterExceptionThrown(
        self,
    ):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath, number="")
        self.assertRaises(
            InvalidInputFileContentException,
            build_ausbildungsnachweis_pdf,
            self.ausbildungsnachweis_xml_filepath,
            self.tmp_dir,
        )

    def test_InvalidInputAusbildungsnachweisXmlWithMissingNameProvided_BuildPdfFromAusbildungsnachweisXml_MissingInputParameterExceptionThrown(
        self,
    ):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath, name="")
        self.assertRaises(
            InvalidInputFileContentException,
            build_ausbildungsnachweis_pdf,
            self.ausbildungsnachweis_xml_filepath,
            self.tmp_dir,
        )

    def test_InvalidInputAusbildungsnachweisXmlWithMissingSurnameProvided_BuildPdfFromAusbildungsnachweisXml_MissingInputParameterExceptionThrown(
        self,
    ):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath, surname="")
        self.assertRaises(
            InvalidInputFileContentException,
            build_ausbildungsnachweis_pdf,
            self.ausbildungsnachweis_xml_filepath,
            self.tmp_dir,
        )

    def test_InvalidInputAusbildungsnachweisXmlWithMissingYearProvided_BuildPdfFromAusbildungsnachweisXml_MissingInputParameterExceptionThrown(
        self,
    ):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath, year="")
        self.assertRaises(
            InvalidInputFileContentException,
            build_ausbildungsnachweis_pdf,
            self.ausbildungsnachweis_xml_filepath,
            self.tmp_dir,
        )

    def test_InvalidInputAusbildungsnachweisXmlWithMissingWeekFromProvided_BuildPdfFromAusbildungsnachweisXml_MissingInputParameterExceptionThrown(
        self,
    ):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath, week_from="")
        self.assertRaises(
            InvalidInputFileContentException,
            build_ausbildungsnachweis_pdf,
            self.ausbildungsnachweis_xml_filepath,
            self.tmp_dir,
        )

    def test_InvalidInputAusbildungsnachweisXmlWithMissingWeekToProvided_BuildPdfFromAusbildungsnachweisXml_MissingInputParameterExceptionThrown(
        self,
    ):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath, week_to="")
        self.assertRaises(
            InvalidInputFileContentException,
            build_ausbildungsnachweis_pdf,
            self.ausbildungsnachweis_xml_filepath,
            self.tmp_dir,
        )

    def test_InvalidInputAusbildungsnachweisXmlWithMissingDepartmentProvided_BuildPdfFromAusbildungsnachweisXml_MissingInputParameterExceptionThrown(
        self,
    ):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath, department="")
        self.assertRaises(
            InvalidInputFileContentException,
            build_ausbildungsnachweis_pdf,
            self.ausbildungsnachweis_xml_filepath,
            self.tmp_dir,
        )

    def test_InvalidInputAusbildungsnachweisXmlWithNumberThatIsNotANumberProvided_BuildPdfFromAusbildungsnachweisXml_InvalidInputParameterExceptionThrown(
        self,
    ):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath, number="A")
        self.assertRaises(
            InvalidInputFileContentException,
            build_ausbildungsnachweis_pdf,
            self.ausbildungsnachweis_xml_filepath,
            self.tmp_dir,
        )

    def test_InvalidInputAusbildungsnachweisXmlWithYearThatIsNotANumberProvided_BuildPdfFromAusbildungsnachweisXml_InvalidInputParameterExceptionThrown(
        self,
    ):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath, year="A")
        self.assertRaises(
            InvalidInputFileContentException,
            build_ausbildungsnachweis_pdf,
            self.ausbildungsnachweis_xml_filepath,
            self.tmp_dir,
        )

    def test_InvalidInputAusbildungsnachweisXmlWithWrongDateFormatInWeekFrom_BuildPdfFromAusbildungsnachweisXml_InvalidInputParameterExceptionThrown(
        self,
    ):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath, week_from="AA.BB.CCCC")
        self.assertRaises(
            InvalidInputFileContentException,
            build_ausbildungsnachweis_pdf,
            self.ausbildungsnachweis_xml_filepath,
            self.tmp_dir,
        )

    def test_InvalidInputAusbildungsnachweisXmlWithWrongDateFormatInWeekTo_BuildPdfFromAusbildungsnachweisXml_InvalidInputParameterExceptionThrown(
        self,
    ):
        self.prepare_ausbildungsnachweis_xml(self.ausbildungsnachweis_xml_filepath, week_to="AA.BB.CCCC")
        self.assertRaises(
            InvalidInputFileContentException,
            build_ausbildungsnachweis_pdf,
            self.ausbildungsnachweis_xml_filepath,
            self.tmp_dir,
        )
