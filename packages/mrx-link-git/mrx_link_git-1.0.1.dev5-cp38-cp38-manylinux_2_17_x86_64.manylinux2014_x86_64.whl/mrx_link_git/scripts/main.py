#  MAKINAROCKS CONFIDENTIAL
#  ________________________
#
#  [2017] - [2022] MakinaRocks Co., Ltd.
#  All Rights Reserved.
#
#  NOTICE:  All information contained herein is, and remains
#  the property of MakinaRocks Co., Ltd. and its suppliers, if any.
#  The intellectual and technical concepts contained herein are
#  proprietary to MakinaRocks Co., Ltd. and its suppliers and may be
#  covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law. Dissemination
#  of this information or reproduction of this material is
#  strictly forbidden unless prior written permission is obtained
#  from MakinaRocks Co., Ltd.
#
import argparse
import logging

if __package__ is None:
    from mrx_link_git.scripts.merge_driver.merge_ipynb import merge_files
else:
    from .merge_driver.merge_ipynb import merge_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Incorporates changers that lead from the <base-file> to <incoming-file> into <current-file>."
    )

    parser.add_argument("--current-file", type=str, required=True, dest="current_file")
    parser.add_argument("--base-file", type=str, required=True, dest="base_file")
    parser.add_argument("--incoming-file", type=str, required=True, dest="incoming_file")
    parser.add_argument("--file-path", type=str, dest="file_path")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose")

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    destination_path = args.file_path if args.file_path else args.current_file

    merge_files(
        current_file_path=args.current_file,
        base_file_path=args.base_file,
        incoming_file_path=args.incoming_file,
        file_path=destination_path,
    )
