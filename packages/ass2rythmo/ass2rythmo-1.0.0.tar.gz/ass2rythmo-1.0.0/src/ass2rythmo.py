# ass2rythmo, generate rythmo band from ass subtitles
# Copyright (C) 2018  Olivier Jolly
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import argparse
import io
import logging
import math
import os
import pprint
import re
import sys
from subprocess import Popen, PIPE
from typing import List

import attr
import progressbar
from PIL import Image
from PIL import ImageDraw, ImageFilter

__date__ = "2018-11-13"
__updated__ = "2023-09-11"
__author__ = "olivier@pcedev.com"


@attr.s
class Style(object):
    name = attr.ib()
    primary_color = attr.ib()
    outline_color = attr.ib()
    index = attr.ib()


@attr.s
class TextChunk(object):
    text = attr.ib()
    start = attr.ib()
    end = attr.ib()


@attr.s
class Dialog(object):
    start = attr.ib()
    end = attr.ib()
    style_name = attr.ib()
    layer = attr.ib(0)
    outline_offset = attr.ib(8)
    style = attr.ib(None)
    _image = attr.ib(None)
    _outline_image = attr.ib(None)
    _baseline = attr.ib(0)
    y = attr.ib(None)
    text_chunks = attr.ib(factory=list)

    def image(self, width=None, duration=None, font_filename=None):
        if self._image is not None:
            return self._image
        self._image, self._baseline = generate_rythmo_image(self.text_chunks, width, duration, font_filename)
        return self._image

    @property
    def text(self):
        return ''.join([c.text for c in self.text_chunks])

    @property
    def outline_image(self):
        if self._outline_image is not None:
            return self._outline_image

        self._outline_image = Image.new("RGBA", (
            self.image().width + 2 * self.outline_offset, self.image().height + 2 * self.outline_offset),
                                        self.style.outline_color)
        #
        # self.image().save("original_dialogue.png", format='PNG', compression_level=4)

        new_alpha = Image.new("L", (self._outline_image.width, self._outline_image.height), 0)

        new_alpha.paste(self.image().split()[3], (self.outline_offset, self.outline_offset))

        # new_alpha.save("alpha.png", format='PNG', compression_level=4)

        new_alpha = new_alpha.filter(ImageFilter.MaxFilter(1 + 2 * (self.outline_offset - 1)))

        # new_alpha.save("filtered_alpha.png", format='PNG', compression_level=4)

        self._outline_image.putalpha(new_alpha)
        #
        # self._outline_image.save("outline.png", format='PNG', compression_level=4)

        return self._outline_image

    @property
    def is_hidden(self):
        return "[norythmo]" in self.actor_name


def time2ms(time_string):
    h, m, s = time_string.split(':')
    s, c = s.split('.')

    return (((((int(h) * 60) + int(m)) * 60) + int(s)) * 100 + int(c)) * 10


def text2chunks(text, start, end):
    # remove comments with {} or []
    text = re.sub(r"{[^\\][^}]*}", "", text)
    text = re.sub(r"\[[^\]]*\]", "", text)

    # split on karaoke tags
    result = []
    for match in re.finditer(r"{\\kf?(\d+)}([^{]*)", text):
        result.append(TextChunk(re.sub(r"\\.", "", match.group(2)), start, start + 10 * int(match.group(1))))
        start += 10 * int(match.group(1))

    if not result:
        result = [TextChunk(re.sub(r"\\.", " ", text), start, end)]

    return result


def alpha_composite_crop(dest, x, y, src):
    if int(x) < 0:
        image_to_paste = src.crop((min(-x, src.width), 0, src.width, src.height))
        x = 0
    else:
        image_to_paste = src

    dest.alpha_composite(image_to_paste, (x, y))


def asscolor2argb(color_str):
    return (int(color_str[8:10], 16),
            int(color_str[6:8], 16),
            int(color_str[4:6], 16),
            int(color_str[2:4], 16)
            )


def generate_rythmo_image(chunk_text: List[TextChunk], target_width: int = 1920, scrolling_duration: int = 5000,
                          face_filename: str = 'DejaVuSans.ttf') -> (Image, int):
    """
    Generate image for a given list of text chunks
    :param chunk_text: list of TextChunk to represent
    :param target_width: width of the final png to generate
    :param scrolling_duration: duration of the text traversal to generate
    :param face_filename: font to use for rendering text
    :return: PIL image representing the text chunks and the baseline in px from the bottom of the image
    """
    from freetype import Face
    import numpy as np

    def interpolate(lhs, positions, target_positions):
        result = np.zeros((lhs.shape[0], math.ceil(target_positions[-1][1])), dtype=lhs.dtype)

        src = []

        previous_lhs_pos = 0
        previous_rhs_pos = 0

        for lhs_pos_idx, rhs_pos in target_positions[1:]:
            src = np.append(src, np.linspace(previous_lhs_pos, positions[lhs_pos_idx], int(rhs_pos - previous_rhs_pos)))
            previous_lhs_pos, previous_rhs_pos = positions[lhs_pos_idx], rhs_pos

        src = np.append(src, np.linspace(previous_lhs_pos, positions[-1], result.shape[1] - src.shape[0]))

        for y in range(lhs.shape[0]):
            result[y, :] = np.interp(
                src,
                np.arange(lhs.shape[1]),
                lhs[y, :])

        return result

    # load font
    face = Face(face_filename)
    face.set_char_size(96 * 64)
    slot = face.glyph

    # gather text and delays from chunks
    text = ''.join([c.text for c in chunk_text])

    target_time = [(0, 0)]
    previous_start = chunk_text[0].start
    previous_length = 0

    for c in chunk_text:
        target_time.append((previous_length + len(c.text), c.end - previous_start))
        # previous_start = c.start
        previous_length += len(c.text)

    # convert time targets into position targets for every chunk
    target_position = [(x, target_width * t / scrolling_duration) for (x, t) in target_time]
    if logging.root.isEnabledFor(logging.DEBUG):
        logging.debug(pprint.pformat(target_position))

    # First pass to compute size of canvas and every character position

    positions = []

    width, height, baseline = 0, 0, 0
    previous = 0

    # accumulate separately the space needed above and below the baseline
    need_above_baseline, need_below_baseline = 0, 0

    for c in text:
        positions.append(width)
        face.load_char(c)
        bitmap = slot.bitmap
        char_baseline = slot.bitmap_top - bitmap.rows

        need_below_baseline = min(need_below_baseline, char_baseline)
        need_above_baseline = max(need_above_baseline, slot.bitmap_top)

        # baseline = max(baseline, max(0, -(slot.bitmap_top - bitmap.rows)))

        kerning = face.get_kerning(previous, c)
        width += (max(slot.bitmap.width, slot.advance.x >> 6) + (kerning.x >> 6))
        # width += (slot.bitmap.width + (kerning.x >> 6))

        previous = c

    positions.append(width)

    height = need_above_baseline - need_below_baseline
    baseline = - need_below_baseline

    Z = np.zeros((height, width), dtype=np.ubyte)

    if logging.root.isEnabledFor(logging.DEBUG):
        logging.debug(pprint.pformat(positions))

    # Second pass for actual rendering
    x, y = 0, 0
    previous = 0
    for c in text:
        face.load_char(c)
        bitmap = slot.bitmap
        top = slot.bitmap_top
        left = slot.bitmap_left

        w, h = bitmap.width, bitmap.rows
        y = height - baseline - top
        kerning = face.get_kerning(previous, c)
        x += (kerning.x >> 6)

        if h < 0 or w < 0:
            logging.error("Internal error when rendering %s from %s", c, text)

        Z[y:y + h, x:x + w] += np.array(bitmap.buffer, dtype='ubyte').reshape(h, w)
        x += (slot.advance.x >> 6)
        previous = c

    # stretch every chunk of text to fit their target
    R = 255 * np.ones((height, int(math.ceil(target_position[-1][1])), 4), dtype=np.ubyte)
    R[:, :, 3] = interpolate(Z, positions, target_position)

    im = Image.fromarray(R)
    if logging.root.isEnabledFor(logging.DEBUG):
        im.save(str(chunk_text[0].start) + ".png")

    return im, baseline


class Ass2Rythmo(object):

    def _parse_ass_file(self):
        self.dialogs = []
        styles = []

        with open(self.ass_filename, 'rt') as f:
            for line in f.readlines():

                if line.startswith("Dialogue: "):

                    # trim and split
                    split_line = line[:-1].split(',')

                    # skip the dialog if the actor contains the string [norythmo]
                    if "[norythmo]" not in split_line[4]:

                        dialog = Dialog(time2ms(split_line[1]), time2ms(split_line[2]), split_line[3],
                                        int(split_line[0][10:]))

                        if dialog.start > dialog.end:
                            logging.warning("Inverted start/end timecode for %s, fixing it for you",
                                            ','.join(split_line[9:]))
                            dialog.start, dialog.end = dialog.end, dialog.start

                        dialog.text_chunks += text2chunks(','.join(split_line[9:]), dialog.start, dialog.end)

                        self.dialogs.append(dialog)

                elif line.startswith("Style: "):

                    # trim and split
                    split_line = line[7:-1].split(',')

                    style = Style(split_line[0], asscolor2argb(split_line[3]), asscolor2argb(split_line[5]),
                                  len(styles))

                    styles.append(style)

        # sort by start time
        self.dialogs.sort(key=lambda x: x.start)
        styles_dict = {s.name: s for s in styles}

        for d in self.dialogs:
            d.style = styles_dict.get(d.style_name, styles[0])

        if logging.root.isEnabledFor(logging.DEBUG):
            logging.debug(pprint.pformat(styles))
            logging.debug(pprint.pformat(self.dialogs))

    def __init__(self, ass_filename, font_filename, target_width=1920, target_height=380, target_fps=29.97,
                 scroll_duration=4000,
                 result_filename_format="%05d.png",
                 sync_point_ratio=0.15, **extra_kw):

        self.ass_filename = ass_filename
        self.result_filename_format = result_filename_format
        self.scroll_duration = scroll_duration
        self.target_width = target_width
        self.target_height = target_height
        self.fps = target_fps
        self.sync_point_ratio = sync_point_ratio
        self.font_filename = font_filename

        self.next_dialog_candidate_idx = 0
        self.y1 = target_height - 80
        self.y2 = target_height - 190
        self.new_y = self.y1
        self._empty_image_file = None

        if '%' not in self.result_filename_format:

            # Force ffv1 codec, which support transparency when generating a .mov, else let ffmpeg autodetects the codec
            if self.result_filename_format.endswith("mov"):
                self.ffmpeg_pipe = Popen(
                    ['ffmpeg', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s',
                     str(self.target_width) + 'x' + str(self.target_height), '-r', str(self.fps), '-i', '-', '-vcodec',
                     'ffv1', self.result_filename_format], stdin=PIPE)
            else:
                self.ffmpeg_pipe = Popen(
                    ['ffmpeg', '-y',
                     '-r', str(self.fps),
                     '-f', 'lavfi', '-i', 'color=c=black:size={0}x{1}'.format(self.target_width, self.target_height),
                     '-f', 'rawvideo', '-pix_fmt', 'rgba',
                     '-s', str(self.target_width) + 'x' + str(self.target_height),
                     '-r', str(self.fps),
                     '-i', '-',
                     '-filter_complex', 'overlay=shortest=1',
                     self.result_filename_format], stdin=PIPE)
        else:
            self.ffmpeg_pipe = None

        self._parse_ass_file()

    def new_active_dialogs(self, dialogs, time):

        result = []

        try:
            previous_dialog = None

            while dialogs[self.next_dialog_candidate_idx].start <= time + self.scroll_duration:

                current_dialog = dialogs[self.next_dialog_candidate_idx]

                result.append(current_dialog)

                current_dialog.x = self.target_width

                # use the dialog layer as indicator of which row should be used, if 0, use style index as fallback
                if current_dialog.layer != 0:
                    current_dialog.y = self.y1 if current_dialog.layer % 2 == 0 else self.y2
                else:
                    current_dialog.y = self.y1 if current_dialog.style.index % 2 == 0 else self.y2

                # if there's a collision risk of 200ms with the previous line, from another style, switch line
                if previous_dialog is not None \
                    and previous_dialog.style.index != current_dialog.style.index \
                    and previous_dialog.y == current_dialog.y \
                    and previous_dialog.end + 200 >= current_dialog.start:
                    current_dialog.y = self.y1 + self.y2 - current_dialog.y

                self.next_dialog_candidate_idx += 1
                previous_dialog = current_dialog

        except IndexError:
            # no more dialogs to check
            pass

        return result

    def inactive_dialog(self, dialog, time):
        return dialog.end + self.scroll_duration >= time

    def default_image(self):
        result = Image.new("RGBA", (self.target_width, self.target_height), (255, 0, 0, 0))

        draw = ImageDraw.Draw(result)
        draw.line([(self.target_width * self.sync_point_ratio, self.y2 - 100),
                   (self.target_width * self.sync_point_ratio, self.target_height - 1)], "red", 8)
        del draw

        return result

    def empty_image_file(self):

        if self._empty_image_file is not None:
            return self._empty_image_file

        image = self.default_image()

        self._empty_image_file = io.BytesIO()

        if self.ffmpeg_pipe:
            self._empty_image_file = image.tobytes()
            # image.save(self._empty_image_file, "TIFF")
        else:
            image.save(self._empty_image_file, "PNG")
            self._empty_image_file = self._empty_image_file.getvalue()

        return self._empty_image_file

    def render_active_dialogs(self, frame, time, active_dialogs):

        if not self.ffmpeg_pipe:
            result_filename = self.result_filename_format % frame

        if active_dialogs:
            if logging.root.isEnabledFor(logging.DEBUG):
                logging.debug(
                    "#{0}/{1} would render dialogs {2}".format(frame, time, "/".join([d.text for d in active_dialogs])))

            image = self.default_image()

            for d in active_dialogs:
                x = self.target_width * self.sync_point_ratio + (
                    d.start - time) * self.target_width / self.scroll_duration

                dialogue_image = d.image(self.target_width, self.scroll_duration, self.font_filename)

                alpha_composite_crop(image, int(x) - d.outline_offset,
                                     int(d.y) - dialogue_image.height + d._baseline - d.outline_offset, d.outline_image)
                alpha_composite_crop(image, int(x), int(d.y) - dialogue_image.height + d._baseline, dialogue_image)

            if self.ffmpeg_pipe:
                # image.save(self.ffmpeg_pipe.stdin, 'SGI')
                self.ffmpeg_pipe.stdin.write(image.tobytes())
            else:
                image.save(result_filename, format='PNG', compression_level=4)

        else:

            # reuse the cached PNG encoded version of an empty file for performance
            if self.ffmpeg_pipe:
                self.ffmpeg_pipe.stdin.write(self.empty_image_file())
            else:
                with open(result_filename, "wb") as f:
                    f.write(self.empty_image_file())

    def render_all_frames(self):

        active_dialogs = []
        frame_range = range(int((self.dialogs[-1].end + self.scroll_duration) / 1000. * self.fps))

        for frame in progressbar.progressbar(frame_range):
            time = 1000. * frame / self.fps  # in ms

            active_dialogs += self.new_active_dialogs(self.dialogs, time)

            self.render_active_dialogs(frame, time, active_dialogs)

            active_dialogs = [d for d in active_dialogs if self.inactive_dialog(d, time)]

        if self.ffmpeg_pipe:
            self.ffmpeg_pipe.stdin.close()
            self.ffmpeg_pipe.wait()

        return 0


def main(argv=None):
    program_name = os.path.basename(sys.argv[0])
    program_dir = os.path.realpath(os.path.dirname(__file__))
    program_version = "v1.0.0"
    program_build_date = "%s" % __updated__

    program_version_string = 'ass2rythmo %s (%s)' % (program_version, program_build_date)
    program_longdesc = '''Convert ASS subtitles to rythmo band as list of transparent png or single transparent movie'''
    program_license = "GPL v3+ 2018 Olivier Jolly"

    if argv is None:
        argv = sys.argv[1:]

    font_name = "DejaVuSans.ttf"

    if os.path.exists(os.path.join(program_dir, "fonts", font_name)):
        default_font_face = os.path.join(program_dir, "fonts", font_name)
    elif os.path.exists(os.path.join(sys.prefix, "fonts", font_name)):
        default_font_face = os.path.join(sys.prefix, "fonts", font_name)
    else:
        logging.warning("No default font could be found")
        default_font_face = None

    try:
        parser = argparse.ArgumentParser(epilog=program_longdesc, description=program_license)
        parser.add_argument("-d", "--debug", dest="debug", action="store_true", default=False,
                            help="print debugging info [default: %(default)s]")
        parser.add_argument("-v", "--version", action="version", version=program_version_string)

        parser.add_argument("-W", "--target_width", dest="target_width", default=1920, type=int,
                            help="Width of the generated png files [default: %(default)s]")
        parser.add_argument("-H", "--target_height", dest="target_height", default=380, type=int,
                            help="Height of the generated png files. Note that it's not meant to support low heights at this time [default: %(default)s]")
        parser.add_argument("-R", "--target_fps", dest="target_fps", default=30, type=float,
                            help="Frame per second to generate. Make sure it matches your subbed video ! [default: %(default)s]")
        parser.add_argument("-F", "--font_face", dest="font_filename", default=default_font_face,
                            help="Filename of the font used to generate text [default: %(default)s]")
        parser.add_argument("-D", "--scroll_duration", dest="scroll_duration", default=4000, type=int,
                            help="Duration of width traversal in ms [default: %(default)s]")
        parser.add_argument("-r", "--result_filename_format", dest="result_filename_format", default="%05d.png",
                            help="Filename template for generated files. "
                                 "May include directory part but won't create any. "
                                 "Including %% in the format will generate a list of png files else will generate a "
                                 "transparent movie with the help of ffmpeg [default: %(default)s]")
        parser.add_argument("-s", "--sync_point_ratio", dest="sync_point_ratio", default=0.15, type=float,
                            help="Position of the sync point on screen, 0 is leftmost, 1 is rightmost  [default: %(default)s]")

        parser.add_argument("ass_filename", help="input file as Ass format")

        # process options

        opts = parser.parse_args(argv)

    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    progressbar.streams.wrap_stderr()
    logging.basicConfig()

    if opts.debug:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    a2r = Ass2Rythmo(**vars(opts))
    a2r.render_all_frames()

    return 0


if __name__ == '__main__':
    sys.exit(main())
