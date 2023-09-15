from django.conf import settings

from libcoveweb2.models import SuppliedDataFile


def group_data_list_by(data_list, get_key_function):
    out = {}
    for item in data_list:
        key = get_key_function(item)
        if key not in out:
            out[key] = []
        out[key].append(item)
    return out


def get_file_type_for_flatten_tool(supplied_data_file: SuppliedDataFile):
    """Takes a SuppliedDataFile object, and returns a string saying what type it is.
    The string is intended for feeding into the input_format option of flatten tool."""
    # First, just check the extension on the file name
    for extension in settings.ALLOWED_JSON_EXTENSIONS:
        if supplied_data_file.filename.lower().endswith(extension):
            return "json"
    for extension in settings.ALLOWED_SPREADSHEET_EXCEL_EXTENSIONS:
        if supplied_data_file.filename.lower().endswith(extension):
            return "xlsx"
    for extension in settings.ALLOWED_SPREADSHEET_OPENDOCUMENT_EXTENSIONS:
        if supplied_data_file.filename.lower().endswith(extension):
            return "ods"
    for extension in settings.ALLOWED_CSV_EXTENSIONS:
        if supplied_data_file.filename.lower().endswith(extension):
            return "csv"
    # Check the content type
    if (
        supplied_data_file.content_type
        and supplied_data_file.content_type
        not in settings.ALLOWED_UNKNOWN_CONTENT_TYPES
    ):
        if supplied_data_file.content_type in settings.ALLOWED_JSON_CONTENT_TYPES:
            return "json"
        if (
            supplied_data_file.content_type
            in settings.ALLOWED_SPREADSHEET_EXCEL_CONTENT_TYPES
        ):
            return "xlsx"
        if (
            supplied_data_file.content_type
            in settings.ALLOWED_SPREADSHEET_OPENDOCUMENT_CONTENT_TYPES
        ):
            return "ods"
        if supplied_data_file.content_type in settings.ALLOWED_CSV_CONTENT_TYPES:
            return "csv"
    # Try and load the first bit of the file to see if it's JSON?
    try:
        with open(supplied_data_file.upload_dir_and_filename(), "rb") as fp:
            first_byte = fp.read(1)
            if first_byte in [b"{", b"["]:
                return "json"
    except FileNotFoundError:
        pass
    # All right, we give up.
    raise Exception(
        "Could not get file type for file "
        + str(supplied_data_file.id)
        + " with file name "
        + str(supplied_data_file.filename)
        + " and content type "
        + str(supplied_data_file.content_type)
    )
