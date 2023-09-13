# Copyright (C) 2023, NG:ITL
import unittest


from pathlib import Path

from ihk_ausbildungsnachweis_utilities.starter import parse_arguments

FILE_DIR = Path(__file__).parent

DEFAULT_INPUT_DIR_PATH = Path.cwd()
DEFAULT_OUTPUT_DIRPATH = Path.cwd()
DEFAULT_CERT_FILEPATH = Path(Path.cwd() / "ca/demo2_user1.p12")
DEFAULT_TEMPLATE_DIRPATH = "template"


class CliParserTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_BuildCommandWithSingleInputFileWithoutOutputDir_ParseArguments_ArgDictWithCorrectValuesReturned(self):
        args_dict = parse_arguments(["binary", "build", "example_input_0.xml"])
        self.assertEqual("build", args_dict["command"])
        self.assertEqual("example_input_0.xml", args_dict["input_files"][0])
        self.assertEqual(
            (FILE_DIR / "../ihk_ausbildungsnachweis_utilities/templates/template_ausbildungsnachweis.docx").resolve(),
            Path(args_dict["template"]).resolve(),
        )
        self.assertEqual((Path.cwd() / "output").resolve(), Path(args_dict["output"]).resolve())

    def test_BuildCommandWithMultipleInputFilesWithoutOutputDir_ParseArguments_ArgDictWithCorrectValuesReturned(self):
        args_dict = parse_arguments(["binary", "build", "example_input_0.xml", "example_input_1.xml"])
        self.assertEqual("build", args_dict["command"])
        self.assertEqual("example_input_0.xml", args_dict["input_files"][0])
        self.assertEqual("example_input_1.xml", args_dict["input_files"][1])
        self.assertEqual(
            (FILE_DIR / "../ihk_ausbildungsnachweis_utilities/templates/template_ausbildungsnachweis.docx").resolve(),
            Path(args_dict["template"]).resolve(),
        )
        self.assertEqual((Path.cwd() / "output").resolve(), Path(args_dict["output"]).resolve())

    def test_BuildCommandWithMultipleInputFilesWithSpecificOutputDir_ParseArguments_ArgDictWithCorrectValuesReturned(
        self,
    ):
        args_dict = parse_arguments(
            [
                "binary",
                "build",
                "-o",
                str(Path.cwd() / "alternative_output/"),
                "example_input_0.xml",
                "example_input_1.xml",
            ]
        )
        self.assertEqual("build", args_dict["command"])
        self.assertEqual("example_input_0.xml", args_dict["input_files"][0])
        self.assertEqual("example_input_1.xml", args_dict["input_files"][1])
        self.assertEqual(
            (FILE_DIR / "../ihk_ausbildungsnachweis_utilities/templates/template_ausbildungsnachweis.docx").resolve(),
            Path(args_dict["template"]).resolve(),
        )
        self.assertEqual((Path.cwd() / "alternative_output").resolve(), Path(args_dict["output"]).resolve())

    def test_SignCommandWithSingleInputFileWithoutSignProfile_ParseArguments_ArgDictWithCorrectValuesReturned(self):
        args_dict = parse_arguments(["binary", "sign", "example_input_0.pdf"])
        self.assertEqual(args_dict["command"], "sign")
        self.assertEqual((Path.cwd() / "sign_profile.json").resolve(), Path(args_dict["sign_profile"]).resolve())

    def test_SignCommandWithMultipleInputFilesWithoutSignProfile_ParseArguments_ArgDictWithCorrectValuesReturned(self):
        args_dict = parse_arguments(["binary", "sign", "example_input_0.pdf", "example_input_1.pdf"])
        self.assertEqual(args_dict["command"], "sign")
        self.assertEqual((Path.cwd() / "sign_profile.json").resolve(), Path(args_dict["sign_profile"]).resolve())

    def test_SignCommandWithMultipleInputFilesWithSpecificSignProfile_ParseArguments_ArgDictWithCorrectValuesReturned(
        self,
    ):
        args_dict = parse_arguments(
            [
                "binary",
                "sign",
                "--sign_profile",
                str(Path.cwd() / "alternative_sign_profile.json"),
                "example_input_0.pdf",
                "example_input_1.pdf",
            ]
        )
        self.assertEqual(args_dict["command"], "sign")
        self.assertEqual(
            (Path.cwd() / "alternative_sign_profile.json").resolve(), Path(args_dict["sign_profile"]).resolve()
        )
