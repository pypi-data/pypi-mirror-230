# HMS Import

Import utility for encrypted video and metadata files.

# Installation

## From Wheel

This assumes you have [Python 3.8+](https://www.python.org/downloads/) installed and `pip3` is on
your path:

```bash
~$ pip3 install hms-import
...
~$ hms-import -h
usage: hms-import [-h] [--quiet] [--verbose] {b3-upload,o2-upload,log-upload} ...

Script for importing video and metadata in O2 and B3 formats.

options:
  -h, --help            show this help message and exit
  --quiet               Changes the console log level from INFO to WARNING; defers to --verbose
  --verbose             Changes the console log level from INFO to DEBUG; takes precedence over --quiet

Commands:
  {b3-upload,o2-upload,log-upload}
    b3-upload           Imports video and GPS files from unlocked LUKS-encrypted device
    o2-upload           Script for uploading raw, encrypted video files
    log-upload          Uploads a log file Tator
```

## From Source

This assumes you have [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git), [Python
3.8+](https://www.python.org/downloads/), and
[poetry](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions) installed
already.

```bash
~$ git clone git@github.com:cvisionai/hms.git
...
~$ cd hms/scripts/hms-import
hms-import$ poetry install
...
hms-import$ poetry run hms-import -h
```

# Usage

This script contains three sub-commands: `o2-upload`, `b3-upload`, and `log-upload`; their usage is
described below. Additional documentation is available by providing the `-h` flag, e.g. `hms-import
o2-upload -h`.

## o2-upload

The first step is to set up your `config.ini` file. Start by copying the contents of
[sample_hms-config.ini](./sample_hms-config.ini) included below for reference, and replace the
default values:

```ini
[Local]
# The directory containing the video files for import
Directory=dir1
# The extension of the encrypted video files
MediaExtension=.video
# The extension of the encrypted metadata files
MetadataExtension=.log

[Tator]
# The url to the tator deployment
Host=https://hms.tator.io
# The API token for tator
Token=6485c83cf040deadbeef07b7aea13706
# The integer id of the project to upload the videos to
ProjectId=-1
# The integer id of the media type to create, required if the project has more than one video media type
MediaType=-1
# The integer id of the file type to create for the uploaded encrypted sensor data file
FileType=-1
# The integer id of the image type to create for the trip summary image
SummaryType=-1
# The name of the algorithm to launch upon upload of each trip
AlgorithmName=Decrypt Trip
# If true, will skip uploading files and only create media objects; used for legacy O2 importing
SkipDecrypt=False

[Trip]
# The serial number of the hard drive, uncomment and set
# HddSerialNumber=123ABC
```

Once configured, you can run the import utility:

```bash
$ hms-import o2-upload config.ini
```

### Troubleshooting

If an import fails, the logs have more detail than the console, they can be found in the same folder
the command was run from, with the filename `hms_import.log`. These are rotating logs that cycle
daily (if the log file is not current, it will have an `.MM-DD-YY` extension appended to the
filename) and are kept for up to 7 days, so as to not consume disk space without limit.


## b3-upload

The B3 import sub-command, `hms-import b3-upload`, requires the following arguments:

* `--host` the tator hostname (string)
* `--token` the tator API token (string)
* `--media-type-id` the media type id (integer)
* `--file-type-id` the file type id (integer)
* `--multi-type-id` the multiview type id (integer)
* `--state-type-id` the state type id (integer)
* `--image-type-id` the image type id (integer)
* `--hdd-sn` the serial number of the hard drive
* `--directory` the location of the files to upload

Once you have those values, use them to call the script:

```bash
$ hms-import b3-upload \
    --host <TATOR_HOST> \
    --token <TATOR_TOKEN> \
    --media-type-id <id> \
    --file-type-id <id> \
    --multi-type-id <id> \
    --state-type-id <id> \
    --image-type-id <id> \
    --hdd-sn <sn> \
    --directory <path/to/files>
```

## log-upload

There is a third command option, `log-upload`, which is used to upload the log file generated after
running `hms-import`, which can be called like so:

```bash
$ hms-import log-upload \
    --host <TATOR_HOST> \
    --token <TATOR_TOKEN> \
    --log-file-type-id <id>
```

The flag `--log-filename` is optional and defaults to the default location of the log file, only
override it if you know what you're doing.
