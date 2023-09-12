# Copyright (C) 2023 twyleg
import argparse
import logging
import sys
from typing import List, Dict, Union

from ihk_ausbildungsnachweis_utilities import __version__
from pathlib import Path
from ihk_ausbildungsnachweis_utilities import builder, signator
from ihk_ausbildungsnachweis_utilities.builder import InvalidInputFileContentException

FILE_DIR = Path(__file__).parent

INPUT_SUFFIX = ".xml"
OUTPUT_DIR = "output"
OUTPUT_SUFFIX = ".pdf"
OUTPUT_SIGNED_DIR = "signed"
OUTPUT_SIGNED_SUFFIX = "_signed.pdf"

DEFAULT_TEMPLATE_FILEPATH = FILE_DIR / "templates/template_ausbildungsnachweis.docx"
DEFAULT_SIGN_PROFILE_FILEPATH = Path.cwd() / "sign_profile.json"

LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
LOG_FORMAT = "%(asctime)s [%(levelname)s][%(module)s]: %(message)s"


class InvalidInputFileTypeException(Exception):
    def __init__(self, filepath: Path):
        super().__init__(f"Unexpected filetype (expected .xml/.pdf): {filepath.suffix}, {filepath}")


def __validate_input_file_format(input_files: List[str]) -> None:
    for input_file in input_files:
        input_filepath = Path(input_file)

        if input_filepath.suffix not in [".xml", ".pdf"]:
            raise InvalidInputFileTypeException(input_filepath)

        elif not input_filepath.is_file():
            raise FileNotFoundError(input_filepath)


def __parse_arguments_for_subcommand_build(argv: List[str]) -> Dict[str, Union[str, bool, List]]:
    parser = argparse.ArgumentParser(description="Generates an ausbildungsnachweis PDF from a XML file")
    parser.add_argument("input_files", metavar="input_files", type=str, nargs="+", help="Input XML files.")
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        default=str(Path.cwd() / "output"),
        help='Output directory for generated ausbildungsnachweis PDFs. Default="./output"',
    )
    parser.add_argument("--template", nargs="?", default=str(DEFAULT_TEMPLATE_FILEPATH))
    return vars(parser.parse_args(argv[2:]))


def __validate_cli_args_for_subcommand_build(cli_args: Dict[str, Union[str, bool, List]]) -> None:
    assert isinstance(cli_args["output"], str)
    if not Path(cli_args["output"]).is_dir():
        raise FileNotFoundError(Path(cli_args["output"]))

    assert isinstance(cli_args["template"], str)
    if not (Path(cli_args["template"]).is_file() or Path(cli_args["template"]).is_dir()):
        raise FileNotFoundError(Path(cli_args["template"]))

    assert isinstance(cli_args["input_files"], list)
    __validate_input_file_format(cli_args["input_files"])


def __parse_arguments_for_subcommand_sign(argv: List[str]) -> Dict[str, Union[str, bool, List]]:
    parser = argparse.ArgumentParser(description="Signs an ausbildungsnachweis PDF with the given certificate")
    parser.add_argument("input_files", metavar="input_files", type=str, nargs="+", help="Input PDF files.")
    parser.add_argument("--sign_profile", nargs="?", default=str(DEFAULT_SIGN_PROFILE_FILEPATH))
    return vars(parser.parse_args(argv[2:]))


def __validate_cli_args_for_subcommand_sign(cli_args: Dict[str, Union[str, bool, List]]) -> None:
    assert isinstance(cli_args["sign_profile"], str)
    if not Path(cli_args["sign_profile"]).is_file():
        raise FileNotFoundError(Path(cli_args["sign_profile"]))

    assert isinstance(cli_args["input_files"], list)
    __validate_input_file_format(cli_args["input_files"])


def parse_arguments(argv: List[str] = sys.argv) -> Dict[str, Union[str, bool, List]]:
    parser = argparse.ArgumentParser(usage="ausbildungsnachweis_utils <command> [<args>] [<input_files>]")
    parser.add_argument("command", help="ausbildungsnachweis utils commands")
    parser.add_argument("-v", "--version", help="show version and exit", action="version", version=__version__)
    args = parser.parse_args(argv[1:2])

    args_dict: Dict[str, Union[str, bool, List]] = vars(args)

    if args.command == "build":
        args_dict.update(__parse_arguments_for_subcommand_build(argv))
    elif args.command == "sign":
        args_dict.update(__parse_arguments_for_subcommand_sign(argv))
    else:
        raise RuntimeError(f"Unknown command: {args.command}")

    return args_dict


def __build(args_dict: Dict[str, Union[str, bool, List]]):
    assert isinstance(args_dict["input_files"], List)
    ausbildungsnachweis_input_xml_filepaths = [Path(input_file) for input_file in args_dict["input_files"]]
    assert isinstance(args_dict["output"], str)
    output_dirpath = Path(args_dict["output"])
    logging.info("Starting build process. Output directory=%s", output_dirpath)
    try:
        for ausbildungsnachweis_input_xml_filepath in ausbildungsnachweis_input_xml_filepaths:
            logging.info("Building file: %s", ausbildungsnachweis_input_xml_filepath)
            builder.build_ausbildungsnachweis_pdf(
                ausbildungsnachweis_input_xml_filepath=ausbildungsnachweis_input_xml_filepath,
                ausbildungsachweis_output_pdf_dirpath=output_dirpath,
            )
    except InvalidInputFileContentException as e:
        logging.error("%s", e)
        sys.exit(-1)


def __sign(args_dict: Dict[str, Union[str, bool, List]]):
    assert isinstance(args_dict["input_files"], List)
    ausbildungsnachweis_input_pdf_filepaths = [Path(input_file) for input_file in args_dict["input_files"]]
    assert isinstance(args_dict["sign_profile"], str)
    profile_filepath = Path(args_dict["sign_profile"])
    logging.info("Starting signature process. Sign profiley=%s", profile_filepath)

    for ausbildungsnachweis_input_pdf_filepath in ausbildungsnachweis_input_pdf_filepaths:
        logging.info("Signing file: %s", ausbildungsnachweis_input_pdf_filepath)
        signator.sign_ausbildungsnachweis_pdf(
            ausbildungsnachweis_pdf_filepath=ausbildungsnachweis_input_pdf_filepath,
            profile_file_filepath=profile_filepath,
        )


def __init_logging(verbose=False):
    stdout_handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(
        force=True,
        handlers=[stdout_handler],
        level="DEBUG" if verbose else "INFO",
        format=LOG_FORMAT,
    )


def start() -> None:
    __init_logging()
    args_dict = parse_arguments()

    if args_dict["command"] == "build":
        __validate_cli_args_for_subcommand_build(args_dict)
        __build(args_dict)
    elif args_dict["command"] == "sign":
        __validate_cli_args_for_subcommand_sign(args_dict)
        __sign(args_dict)


if __name__ == "__main__":
    start()
