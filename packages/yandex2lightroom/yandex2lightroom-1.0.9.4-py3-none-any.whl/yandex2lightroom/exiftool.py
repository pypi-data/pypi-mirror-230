from subprocess import run
import errno
from pathlib import Path


class ExifTool:
    """Class to set tags on images.

    """

    def __init__(self,
                 image_path: Path):
        self.image_path = image_path
        self.completed_process = None

    def set_creator_work_url(self,
                             image_url: str) -> bool:
        # Set the URL
        exiftool_cmd = [r"exiftool", "-overwrite_original", "-quiet", "-CreatorWorkURL=" + image_url,
                        self.image_path.absolute().as_posix()]
        try:
            self.completed_process = run(exiftool_cmd)
            return True

        except OSError as exception:
            if exception.errno == errno.ENOENT:
                print("Fatal: exiftool must be installed and in PATH.")
                return False
            else:
                print(exception)
                return False

        except Exception as exception:
            print(exception)
            return False

    def set_keywords(self,
                     image_keywords: str) -> bool:
        keywords = image_keywords.split(" ")
        # Set keywords
        exiftool_cmd = [r"exiftool", "-overwrite_original", "-quiet"]
        for keyword in keywords:
            exiftool_cmd.extend(["-keywords=" + keyword])
        exiftool_cmd.extend([self.image_path.absolute().as_posix()])

        try:
            self.completed_process = run(exiftool_cmd)
            return True

        except OSError as exception:
            if exception.errno == errno.ENOENT:
                print("Fatal: exiftool must be installed and in PATH.")
                return False
            else:
                print(exception)
                return False

        except Exception as exception:
            print(exception)
            return False
