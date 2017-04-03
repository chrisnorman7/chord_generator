"""
A braille chord generator.
"""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from attr import attrs, attrib, Factory

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument(
    '-n',
    '--name',
    default=',blank ,*ord ,template',
    help='The name of the chord'
)
parser.add_argument(
    '-l',
    '--length',
    type=int,
    default=0,
    help='The length of the neck'
)
parser.add_argument(
    '-b',
    '--hide-brief',
    action='store_true',
    help='Hide the brief chord display'
)
parser.add_argument(
    '-X',
    '--extended-brief',
    action='store_true',
    help='Show finger names as well as fret numbers in the brief chord display'
)
parser.add_argument(
    '-D',
    '--delimiter',
    default='4',
    help='The character to put between the fret number and the finger name in '
    'the brief display'
)
parser.add_argument(
    '--number-sign',
    metavar='CHARACTER',
    default='#',
    help='The sign to precede any numbers'
)
parser.add_argument(
    '--numbers',
    default='jabcdefghi',
    help='A list of number characters to be used as numbers'
)
parser.add_argument(
    '-S',
    '--separator',
    default='-',
    help='The character which should separate strings in the brief display'
)
parser.add_argument(
    '--fingers',
    default='#j,#a,#b,#c,#d',
    help='A comma-separated list of finger names'
)
parser.add_argument(
    '--any-finger',
    metavar='STRING',
    default='#x',
    help='The text to be printed when no finger is provided in a marking'
)
parser.add_argument(
    '-s',
    '--strings',
    default=';e,;a,;d,;g,;b,;e',
    help='String names'
)
parser.add_argument(
    '-p',
    '--pad-fret-numbers',
    default=' ',
    metavar='CHARACTER',
    help='The character to print before the fret numbers'
)
parser.add_argument(
    '--empty',
    metavar='STRING',
    default='33',
    help='The text to print for an empty fret'
)
parser.add_argument(
    '--fingered',
    metavar='STRING',
    default='_',
    help='The text to print after a nonempty fret'
)
parser.add_argument(
    '--normal',
    metavar='STRING',
    default='=',
    help='The text to print after an empty fret'
)
parser.add_argument(
    '--pre-fingered',
    metavar='STRING',
    default='l',
    help='The text to print before a finger marking'
)
parser.add_argument(
    '--empty-string',
    metavar='STRING',
    default=';x',
    help='The text to print at the beginning of a string with no finger '
    'markings'
)
parser.add_argument(
    '--muted-string',
    metavar='STRING',
    default='==',
    help='The text to print before a string which should not be played'
)
parser.add_argument(
    'markings',
    nargs='*',
    help='The finger markings to be printed in the form string[.fret.finger]. '
    'If fret and finger are omitted the string will be muted.'
)

args = parser.parse_args()


def convert_numbers(n):
    """Returns the number n as a braille string."""
    res = args.number_sign
    for x in str(n):
        res += args.numbers[int(x)]
    return res


@attrs
class String:
    """A string on an instrument."""
    name = attrib()
    muted = attrib(default=Factory(lambda: False))
    markings = attrib(default=Factory(dict))

    def __str__(self):
        return self.name


@attrs
class Marking:
    """A finger marking."""
    finger = attrib()
    fret = attrib()


def splitter(string, fret=None, finger=None):
    """returns a user-provided finger marking as a tuple of
    (string, fret, finger)
    ."""
    return (string, fret, finger)


# This variable will grow with the length of each string name allowing the code
# to correctly align the fret numbers in the display.
string_name_length = 0
strings = []
for s in args.strings.split(','):
    string_name_length = max(string_name_length, len(s))
    strings.append(String(s))

args.fingers = args.fingers.split(',')
for m in args.markings:
    try:
        res = m.split('.')
        string, fret, finger = splitter(*res)
        try:
            string = int(string)
        except ValueError:
            raise ValueError('Invalid string number: %r.' % string)
        if finger is not None:
            try:
                finger = int(finger)
            except ValueError:
                raise ValueError('Invalid finger number: %r.' % finger)
        try:
            s = strings[string - 1]
        except IndexError:
            raise ValueError('Invalid string number: {}.'.format(string))
        try:
            fret = int(fret)
        except TypeError:
            # fret is None, let's mute the string.
            s.muted = True
            continue
        except ValueError:
            raise ValueError('Invalid fret number: %r.' % fret)
        if args.length < 1:
            args.length = fret
        else:
            args.length = max(args.length, fret)
        try:
            f = args.fingers[finger]
        except TypeError:
            # finger is None, use any finger.
            f = args.any_finger
        except IndexError:
            raise ValueError('Invalid finger number: {}.'.format(finger))
        s.markings[fret] = Marking(f, fret)
    except ValueError as e:
        quit(e)


if __name__ == '__main__':
    # Let's print some tabs!
    if args.length < 1:
        args.length = 5  # There are no finger markings.
    print(args.name)
    # Print the brief tab (if required):
    if args.hide_brief:
        print()
    else:
        display = []
        for s in strings:
            if s.muted:
                display.append(args.muted_string)
                continue
            for m in s.markings.values():  # Only print out 1.
                if args.extended_brief:
                    display.append('%s%s%s' % (
                        convert_numbers(m.fret), args.delimiter, m.finger
                    ))
                else:
                    display.append(convert_numbers(m.fret))
                break
            else:
                display.append(args.empty_string)
        print(args.separator.join(display))
    strings.reverse()
    res = args.pad_fret_numbers * string_name_length + ' '
    for x in range(args.length):
        res = '%s%-3s' % (res, convert_numbers(x + 1))
    print(res)
    for s in strings:
        if 1 not in s.markings:
            if s.muted:
                s.markings[1] = Marking(args.muted_string, 1)
            elif not s.markings:
                s.markings[1] = Marking(args.empty_string, 1)
        res = ''
        for x in range(args.length):
            fret = x + 1
            m = s.markings.get(fret)  # The current marking.
            if m is None:
                res = '%s%s%s' % (
                    res,
                    args.empty,
                    args.normal
                )
            else:
                if x:
                    res = '%s%s' % (res[:-1], args.pre_fingered)
                res = '%s%s%s' % (
                    res,
                    m.finger,
                    args.fingered
                )
        print('%s %s' % (s, res))
