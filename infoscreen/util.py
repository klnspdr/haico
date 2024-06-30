import datetime
import io
import os
from io import IOBase
from pathlib import Path

from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.translation import gettext

from slugify import slugify

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

from haico import settings
from haico.settings import MAX_VIDEO_DURATION


def verify_multimedia(metadata: dict):
    width = metadata.get('width')
    height = metadata.get('height')

    target_width = settings.INFOSCREEN_TARGET_WIDTH
    target_height = settings.INFOSCREEN_TARGET_HEIGHT

    if width != target_width or height != target_height:
        raise ValidationError(gettext(
            'Your media file has the dimensions %(width)sx%(height)s. '
            'They need to be %(target_width)sx%(target_height)s.'),
            params={'width': width,
                    'height': height,
                    'target_width': target_width,
                    'target_height': target_height},
            code='mismatched_dimensions')


def verify_infoscreen_file(file: IOBase) -> str:
    file_parser = createParser(file)
    extension = getattr(file_parser, 'filename_suffix', None)
    if not file_parser or not extension:
        raise ValidationError(gettext('Unable to parse file. Is this a '
                                      'multimedia file?'))
    try:
        file_metadata = extractMetadata(file_parser)
    except Exception as err:
        raise ValidationError('Metadata extraction error: %s' % err)

    if file_metadata:
        verify_multimedia(file_metadata)
    else:
        raise ValidationError(gettext('Unsupported file type.'))

    return extension


def get_video_duration(file: IOBase) -> int:
    file_parser = createParser(file)
    if not file_parser:
        raise ValidationError(gettext('Unable to parse file. Is this a '
                                      'multimedia file?'))
    try:
        file_metadata = extractMetadata(file_parser)
    except Exception as err:
        raise ValidationError('Metadata extraction error: %s' % err)
    #extract video duration, if file is not video, set duration as None
    if file_metadata:
        try:
            duration = file_metadata.get('duration').seconds

        except Exception as err:
            duration = None
        if duration is int and duration > MAX_VIDEO_DURATION:
            raise ValidationError(gettext('Video duration exceeds the maximum allowed duration.'))

    return duration or None


def get_infoscreen_file_folder(group: str) -> str:
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    return f'{settings.INFOSCREEN_FILES_FOLDER}/{slugify(group)}/{date}/'


def save_infoscreen_file(file, title: str, group: str, extension: str) -> str:
    folder = get_infoscreen_file_folder(group)
    os.makedirs(folder, exist_ok=True)

    filename = Path(folder, slugify(title) + extension)

    i = 1
    while filename.exists():
        filename = Path(folder, f'{slugify(title)}-{i}{extension}')
        i += 1

    with open(filename, 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return f'{settings.BASE_URL}/{filename}'


def repeat_array_to_slots(slides, target_slots):
    # Calculate the total number of slots in the original array
    total_slots = sum(slide.number_slots for slide in slides)

    if total_slots == 0:
        raise ValueError(
            "The total number of slots in the input array must be greater than zero.")

    if total_slots >= target_slots:
        raise ValueError(
            "The target number of slots must be greater than the current total number of slots.")

    repeated_slides = []
    current_total_slots = 0
    index = 0
    num_slides = len(slides)

    # Repeat the array until we reach the target number of slots
    while current_total_slots < target_slots:
        slide = slides[index % num_slides]
        if current_total_slots + slide.number_slots <= target_slots:
            repeated_slides.append(slide)
            current_total_slots += slide.number_slots
        else:
            break
        index += 1

    return repeated_slides


def merge_slides_arrays(regular, events):
    result = []
    regular_len = len(regular)
    event_index = 0
    regular_index = 0
    event_block = 0

    while regular_index < regular_len:
        # Add the regular slide with slots treated as 1
        result.append(regular[regular_index])
        regular_index += 1

        if event_block == 0:
            # Check if we can add an event slide
            if event_index < len(events):
                event_slide = events[event_index]
                result.append(event_slide)
                event_index += 1
                event_block = event_slide.number_slots - 1
        else:
            event_block -= 1

    return result

def generate_infoscreen_config(infoscreen, slides) -> str:
    config_text = render_to_string('infoscreen/infoscreen.conf',
                                   context={
                                       'infoscreen': infoscreen,
                                       'slides': slides,
                                   })

    file_path = os.path.join(settings.STATIC_INFOSCREEN_ROOT_DIR,
                             infoscreen.name, 'infoscreen.conf')

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as file:
        file.write(config_text)
    return file_path
