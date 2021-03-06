#! /usr/bin/env python
"""
This script will reorganize the pictures in the given folder recursive and resort them
based on the date, found in the ExifTag DateTimeOriginal.

Example:
vacation/spain/1234422.JPG with date 2012:03:03 11:11:00
will be moved to 2012/03/03/1234422.JPG
"""

__author__ = "Walter de Valk"
__version__ = 0.1

import os
import shutil
import sys

try:
    import pyexiv2
except ImportError:
    print "This script depends on pyexiv2 to get the date from the files."
    print "Please install python-pyexiv2 and try again."


def Usage():
    message = """
{0} version {1}
Organize your photo's by date.
	
	Usage:
	python {0} <dir>
	
<dir> is the directory where your photo's are stored'


{2}
""".format(sys.argv[0], __version__, __doc__)

    return message


def select_files(folder):
    """Select files recursive starting from folder"""
    for path, dirs, files in os.walk(folder):
        for f in files:
            yield os.path.join(path, f)


def get_date(f):
    """get the date tag with pyexiv2

    returns a String or None
    """
    try:
        metadata = pyexiv2.ImageMetadata(f)
        metadata.read()
    except IOError:
        # print f, 'is not readable'
        return None

    try:
        dt = metadata['Exif.Photo.DateTimeOriginal'].value
        return dt
    except KeyError:
        # print f, 'No valid datetime tag found'
        return None


def parse_date(dt):
    """extract the date from the tag Exif.Photo.DateTimeOriginal"""
    exifdate, exiftime = str(dt).split(' ')

    # get the day, month and year
    # if the day month and year are separated with an '-'
    try:
        ed = exifdate.split('-')
        exifday = ed[2]
        exifmonth = ed[1]
        exifyear = ed[0]
    except IndexError:
        # doesn't work
        # try again with seperator ':'
        try:
            ed = exifdate.split(':')
            exifday = ed[2]
            exifmonth = ed[1]
            exifyear = ed[0]
        except IndexError:
            # try again with seperator '/'
            ed = exifdate.split('/')
            exifday = ed[2]
            exifmonth = ed[1]
            exifyear = ed[0]
    return (exifyear, exifmonth, exifday)


def compare_date_with_folder(f, dt):
    # try to extract date from folder
    d, f = os.path.split(f)
    d = d.split(os.sep)

    try:
        day = d[-1]
        month = d[-2]
        year = d[-3]
    except IndexError:
        return False

    # extract date from exiftag
    try:
        exifyear, exifmonth, exifday = parse_date(dt)
    except IndexError:
        # can't extract date
        # return True, saying the file is already on the right place
        # so this file will be skipped
        print "Skipping file %s can't extract date" % f
        return True

    # compare date with folders
    if year == exifyear and month == exifmonth and day == exifday:
        return True  # folder is same as date
    else:
        return False  # folder is not same as date


def copy_to_destination(filename, destination_folder):
    if not os.path.exists(destination_folder):
       os.makedirs(destination_folder)

    try:
        shutil.move(filename, destination_folder)
        # print to screen what's happening
        print f, '-->', destination_folder
    except:
        print "ERROR can't move %s to %s" % (filename, destination_folder)


if '__main__' in __name__:

    try:
        startfolder = sys.argv[1]
    except IndexError:
        print Usage()
        sys.exit(1)

    folder_for_undetermined_date = os.path.join(startfolder, 'zonder_datum')  # destination to put dateless photo's

    process_list = []

    total_amount = 0
    notOK = 0
    moved = 0

    for f in select_files(startfolder):
        # perform action per file recursive

        # get the date from the file with pyexiv2
        dt = get_date(f)
        destdir = None

        if dt:  # there is a date tag in file
            if not compare_date_with_folder(f, dt):  # if file is not in folder with date, move file to root/year/month/day
                # print f, dt
                fi = os.path.split(f)[1]  # filename

                # create destination directory root/year/month/day
                dr = os.path.join(*parse_date(dt))
                destdir = os.path.join(startfolder, dr)

        else:  # no date tag present
            # print f, dt
            pt, fi = os.path.split(f)
            if pt == folder_for_undetermined_date:
                # if the photo is already in the
                # folder without_date nothing to do
                continue
            else:
                destdir = folder_for_undetermined_date

        if destdir:
            process_list.append( (f, destdir))

    # to process
    print( "There are found "+ str(len( process_list))+' photos to move' )

    print "file", "destination"
    print "----", "-----------"
    for i in process_list:
        print i[0], i[1]

    if raw_input("Would you like to continue? ").upper() in ["YES", "Y", ""]:
        for f,d in process_list:
            try:
                copy_to_destination(f, d)
            except:
                print f, d
                sys.exit( "error moving")
    else:
        sys.exit( "You cancelled the operation")