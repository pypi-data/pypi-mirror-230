import argparse
import re
import sys

from cmdu import load_json, load_yaml, as_json, as_yaml
from cmdu.lines import LineNumberAppender


def json2yaml(data: str):
    return as_yaml(load_json(data))


def yaml2json(data: str, indent=None):
    return as_json(load_yaml(data), indent)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='cmdu',
    )
    parser.add_argument("--from-file", default=None)

    sparser = parser.add_subparsers(dest="command")
    line_parser = sparser.add_parser("lines")
    line_nu_parser = line_parser.add_subparsers(dest="sub_command")
    line_numberParser = line_nu_parser.add_parser("set-nu", help="pad line number to each line")
    line_nu_parser.add_parser("count", help="calculate number of lines")
    lines_skip_parser = line_nu_parser.add_parser("skip", help="skip number of lines")
    lines_skip_parser.add_argument("-n", "--number", default=0)
    lines_filter_parser = line_nu_parser.add_parser("filter", help="filter lines by regex [*experimental]")
    lines_filter_parser.add_argument("-r", "--regex", default=None)

    lines_filter_not_parser = line_nu_parser.add_parser("filter-not", help="filter not match lines by regex [*experimental]")
    lines_filter_not_parser.add_argument("-r", "--regex", default=None)

    convert_parser = sparser.add_parser("convert")
    convert_sub_parser = convert_parser.add_subparsers(dest="sub_command")
    json2yamlParser = convert_sub_parser.add_parser("j2y", help="Convert json to yaml")
    yaml2jsonParser = convert_sub_parser.add_parser("y2j", help="Convert yaml to json")
    yaml2jsonParser.add_argument("-p", "--pretty", action=argparse.BooleanOptionalAction, default=False)
    yaml2jsonParser.add_argument("--indent", default=4)
    asJsonParser = convert_sub_parser.add_parser("j2j", help="Convert json string to json of specific format")
    asJsonParser.add_argument("-p", "--pretty", action=argparse.BooleanOptionalAction, default=False)

    args = parser.parse_args()

    ins = sys.stdin
    out = sys.stdout
    sys.stdout = sys.stderr

    if args.from_file is not None:
        f = open(args.from_file)
        ins = f

    if args.command == "lines":
        cmd = args.command
        if args.sub_command == "set-nu":
            appender = LineNumberAppender()
            for l in ins:
                out.write(appender(l))
        elif args.sub_command == "count":
            count = 0
            for l in ins:
                count += 1
            out.write(f"{count}")
        elif args.sub_command == "skip":
            count = 0
            to_be_skipped = int(args.number)
            for l in ins:
                count += 1
                if count > to_be_skipped:
                    out.write(l)
        elif args.sub_command == "filter":
            regex = re.compile(args.regex)
            for l in ins:
                if regex.search(l):
                    out.write(l)
        elif args.sub_command == "filter-not":
            regex = re.compile(args.regex)
            for l in ins:
                if not regex.search(l):
                    out.write(l)
        else:
            raise Exception("Sub command not support")
    elif args.command == "convert":
        if args.sub_command == "j2y":
            data = "\n".join(ins.readlines())
            out.write(json2yaml(data))
        elif args.sub_command == "y2j":
            data = "\n".join(ins.readlines())
            out.write(yaml2json(data, int(args.indent) if args.pretty else None))
        elif args.sub_command == "j2j":
            data = "\n".join(ins.readlines())
            out.write(as_json(load_json(data), int(args.indent) if args.pretty else None))
        else:
            raise Exception("Sub command not support")
    else:
        raise Exception("Command not support")
    out.write("\n")
