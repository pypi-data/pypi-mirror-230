import jsoml

# std lib
import argparse, json, sys
from pathlib import Path


class Main:
    def __init__(self, cmd_line_args=None):
        self.parser = argparse.ArgumentParser(description="JSOML tool")
        self.parser.add_argument("inpath", type=Path, help="input file path")
        self.parser.add_argument(
            "--from",
            dest="inform",
            choices=["json", "jsoml"],
            default="json",
            help="format of source",
        )
        self.parser.parse_args(cmd_line_args, self)

    def run(self):
        sout = sys.stdout
        if self.inform == "json":
            with open(self.inpath) as sin:
                data = json.load(sin)
            jsoml.dump(data, sout)
            sout.write("\n")
        elif self.inform == "jsoml":
            data = jsoml.load(self.inpath)
            json.dump(
                data,
                sout,
                indent=4,
                default=str,
                ensure_ascii=False,
                sort_keys=True,
            )
            sout.write("\n")
        else:
            raise AssertError


def main(args=None):
    return Main(args).run()


if __name__ == "__main__":
    exit(main())
