#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import re
import textwrap
import time
from argparse import RawTextHelpFormatter

import sentry_sdk

from . import __version__
from .dask_setup import setup_scheduler
from .datahandling import prepare_input_data, save
from .metadata import load_metadata

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(f"A climate index package, version {__version__}."),
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "-l",
        "--log-level",
        choices=LOG_LEVELS.keys(),
        default="info",
        help="the lowest priority level of log messages to display",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="write more detailed log messages"
    )
    parser.add_argument(
        "-e",
        "--deactivate-error-tracking",
        action="store_true",
        help="deactivate sentry based error tracking",
    )
    parser.add_argument("-d", "--dask-scheduler", default="distributed-local-cluster")
    parser.add_argument(
        "-k",
        "--keep-open",
        action="store_true",
        help="keep climix running until key press (useful for debugging)",
    )
    parser.add_argument(
        "-p",
        "--period",
        help=textwrap.dedent(
            """\
            Specify period for index (overrides index default period).
            Must be one of annual,seasonal,monthly. For annual period,
            an optional argument can be given to specify a range of months,
            e.g. annual[jja] for multiple months, or annual[feb] for a
            single month.
            """
        ),
    )
    parser.add_argument(
        "-s",
        "--sliced-mode",
        action="store_true",
        help="activate calculation per period to avoid memory problems",
    )
    parser.add_argument(
        "-i",
        "--iterative-storage",
        action="store_true",
        help="store results iteratively per period",
    )
    parser.add_argument(
        "-o", "--output", dest="output_template", help="output filename"
    )
    parser.add_argument(
        "-f",
        "--metadata-file",
        metavar="METADATA_FILE",
        dest="metadata_files",
        action="append",
        help=textwrap.dedent(
            """\
            add an external metadata file (overrides any default definitions),
            can be used multiple times to add several files (the last specified
            file will override any earlier definitions)
            """
        ),
    ),
    parser.add_argument(
        "--activate-config",
        action="store_true",
        dest="activate_config",
        help=textwrap.dedent(
            """\
            specify if the climix configuration should be activated. This will apply
            the default configuration for the output global attributes metadata.
            The default configuration file can be overridden by adding an external
            climix config metadata file.
            """
        ),
    ),
    parser.add_argument(
        "-r",
        "--reference-period",
        help=textwrap.dedent(
            """\
                specify reference period for an index (overrides the default
                reference period in the index definition), accepted formats are
                ISO 8601.
                Examples of usage:
                -r 1971/2000
                -r 1971-06-01/2000
                -r P48Y/2000
                -r P47Y7M/2000
                --reference-period 1971/2000
            """
        ),
    )
    parser.add_argument(
        "-x",
        "--index",
        action="append",
        required=True,
        metavar="INDEX",
        dest="indices",
        help=textwrap.dedent(
            """\
            the index to calculate
            (use "-x list" to get a list of all available indices)
            """
        ),
    )
    parser.add_argument(
        "datafiles", nargs="*", metavar="DATAFILE", help="the input data files"
    )
    return parser.parse_args()


def setup_logging(log_level, verbose=False):
    if verbose:
        format = (
            "%(relativeCreated)8dms:%(filename)s:%(funcName)s() "
            "%(levelname)s:%(name)s:%(message)s"
        )
    else:
        format = "%(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=LOG_LEVELS[log_level], format=format)


def init_sentry():
    logging.info("Activating sentry (automatic error reporting)")
    sentry_sdk.init("https://d3ac73a62877407b848dfc3f318bed85@sentry.io/1458386")


def guess_output_template(datafiles):
    """
    Form an output filename template based on the names of the input files.

    The approach is as follows. The basenames of the input paths are stripped
    of the file extension and then split at underscores ('_'). The first part,
    usually the variable name, is discarded. The last part, usually a
    timerange, is reformatted to ensure hyphenated form (`start-end`) even in
    the case of a single timestamp, for example a single year. All the other,
    middle parts are reassambled with underscores and are called `base`.

    If the input files are both historical and scenario simulations the respective
    bases are expected to be identical except for one occurrence of a keyword from
    a list of known historical and scenario keywords. The occurring keywords
    will be concatenated with a hyphen in the template base,
    e.g. bases `foo_historical_bar` and `foo_rcp45_bar` will result in
    the template base `foo_historical-rcp45_bar`.

    If the template base contains a frequency keyword ('day') with
    surrounding underscores, the keyword will be replaced by `{frequency}`,
    otherwise `_{frequency}` will be added to the end of the template base.

    The time period of the template will always represent the whole
    period as covered by all files, given that the time periods can be
    parsed from the input file paths.

    If these heuristic rules result in an unambiguous filename base, the template
    will be given as `{var_name}_{base}_{start-end}.nc`, or
    as `{var_name}_{base}.nc` if time period could not be determined.
    Otherwise the fallback `{var_name}_{frequency}.nc` will be returned.

    This works well with CMIP/CORDEX style filenames.

    Parameters
    ----------
    datafiles : list of string
        Input file names.

    Returns
    -------
    output_template : string
        A format string suitable for use in the construction of an output
        filename.
    """
    frequency_keywords = ["day"]
    historical_keywords = ["hist", "historical"]
    scenario_keywords = [r"rcp\d{2}", r"ssp\d{3}"]

    def filename_stripper(path):
        # remove directory part...
        basename = os.path.basename(path)
        # ...and extension
        root, ext = os.path.splitext(basename)
        # split at _...
        parts = root.split("_")
        # and remove
        # first part (usually variable)
        # and last part (usually time)
        base = "_".join(parts[1:-1])
        try:
            time = [int(t) for t in parts[-1].split("-")]
            if len(time) == 1:
                time *= 2
        except ValueError:
            time = [None, None]
        return (base, time[0], time[1])

    def base_merger(bases):
        unique_bases = set(bases)
        if len(unique_bases) == 1:
            return unique_bases.pop()
        elif len(unique_bases) == 2:
            # Possible combination of historical and scenario data.
            hist_re = re.compile(rf"_({r'|'.join(historical_keywords)})_")
            scen_re = re.compile(rf"_({r'|'.join(scenario_keywords)})_")
            # Figure out which base is historical and which is scenario.
            hist_base = [b for b in unique_bases if hist_re.search(b)]
            scen_base = [b for b in unique_bases if scen_re.search(b)]
            if len(hist_base) == 1 and len(scen_base) == 1:
                hist_parts = hist_re.split(hist_base[0])
                scen_parts = scen_re.split(scen_base[0])
                if (
                    len(hist_parts) == 3
                    and len(scen_parts) == 3
                    and hist_parts[0] == scen_parts[0]
                    and hist_parts[2] == scen_parts[2]
                ):
                    concat_keywords = hist_parts[1] + "-" + scen_parts[1]
                    return f"{hist_parts[0]}_{concat_keywords}_{hist_parts[2]}"
        return None

    def add_frequency(base):
        # Replace occurrence of frequency keyword with {frequency}, or add _{frequency}.
        freq_re = re.compile(rf"_({'|'.join(frequency_keywords)})(?=_|$)")
        if freq_re.search(base):
            base = freq_re.sub("_{frequency}", base)
        else:
            base += "_{frequency}"
        return base

    files = [filename_stripper(p) for p in datafiles]
    bases, starts, ends = zip(*files)
    base = base_merger(bases)
    if base:
        base_with_freq = add_frequency(base)
        if None in starts or None in ends:
            output_template = f"{{var_name}}_{base_with_freq}.nc"
        else:
            start = min(starts)
            end = max(ends)
            output_template = f"{{var_name}}_{base_with_freq}_{start}-{end}.nc"
    else:
        output_template = "{var_name}_{frequency}.nc"
    return output_template


def build_output_filename(index, datafiles, output_template):
    if output_template is None:
        output_template = guess_output_template(datafiles)
    period_specialization = index.period.specialization
    if period_specialization is not None:
        var_name = f"{{var_name}}-{period_specialization}"
    else:
        var_name = "{var_name}"
    drs_copy = index.metadata.output.drs.copy()
    drs_copy["var_name"] = var_name.format(**index.metadata.output.drs)
    drs_copy["frequency"] = index.period.label
    return output_template.format(**drs_copy)


def do_main(
    index_catalog,
    climix_config,
    requested_indices,
    period,
    reference_period,
    datafiles,
    output_template,
    sliced_mode,
    iterative_storage,
    scheduler,
):
    logging.debug("Preparing indices")
    indices = index_catalog.prepare_indices(requested_indices, period, reference_period)
    for index_no, index in enumerate(indices):
        logging.info(
            "Starting calculations for index <"
            f"{requested_indices[index_no]}> in {index}"
        )
        logging.debug("Building output filename")
        output_filename = build_output_filename(index, datafiles, output_template)
        logging.debug("Preparing input data")
        input_data = prepare_input_data(datafiles, climix_config)
        logging.debug("Calculating index")
        result = index(
            input_data,
            client=scheduler.client,
            sliced_mode=sliced_mode,
            climix_config=climix_config,
        )
        logging.info(f"Saving result in {os.path.abspath(output_filename)}")
        save(
            result,
            output_filename,
            iterative_storage,
            scheduler.client,
            conventions_override=(climix_config is not None),
        )


def main():
    args = parse_args()
    setup_logging(args.log_level, args.verbose)
    if not args.deactivate_error_tracking:
        init_sentry()

    logging.debug("Loading metadata")
    index_catalog, climix_config = load_metadata(
        args.metadata_files, args.activate_config
    )
    if "list" in args.indices:
        print("Available indices are:")
        print(list(index_catalog.get_list()))
        return

    with setup_scheduler(args) as scheduler:
        logging.debug("Scheduler ready; starting main program.")
        start = time.time()
        try:
            do_main(
                index_catalog,
                climix_config,
                args.indices,
                args.period,
                args.reference_period,
                args.datafiles,
                args.output_template,
                args.sliced_mode,
                args.iterative_storage,
                scheduler,
            )
        finally:
            end = time.time()
            logging.info(f"Calculation took {end-start:.4f} seconds.")
        if args.keep_open:
            input("Press enter to close the cluster ")


if __name__ == "__main__":
    main()
