import zipfile


def zipfile_ls(zipfile_name: str):
    if not zipfile.is_zipfile(zipfile_name):
        raise Exception('zipfile_name is not a zip file')

    zip_file = zipfile.ZipFile(zipfile_name, 'r', zipfile.ZIP_DEFLATED)

    return zip_file.namelist()
