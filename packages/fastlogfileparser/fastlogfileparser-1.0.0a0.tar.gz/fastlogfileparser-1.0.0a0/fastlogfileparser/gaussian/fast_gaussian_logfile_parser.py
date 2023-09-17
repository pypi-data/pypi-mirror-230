# fast_gaussian_logfile_parser.py
# a single function meant to retrieve data from gaussian logfiles quickly,
# using exclusively regular expressions and reading the file only once.
import re
import warnings

from .utils.regexes import COMPILED_PATTERNS
from .utils.preprocessing import crush_ginc_block, split_composite_job
from .utils.postprocessing import POSTPROCESSING_FUNCTIONS


def fast_gaussian_logfile_parser(
    target_file: str,
    verbose: int = 0,
):
    """Parse Gaussian Logfile, but Fast-ly

    Args:
        target_file (str, optional): Logfile path.
        status_only (bool, optional): Retrieve ONLY the status of the job, but nearly instantly. Defaults to False.
        verbose (int, optional): 0 for silent, 1 for info, 2 for debug. Defaults to 0.

    Returns:
        dict: kvp of logfile contents, one per job
    """
    out_dicts = []
    # get the text out of the logfile
    with open(target_file, "r") as file:
        crushed_text = crush_ginc_block(file)
        preprocessed_text_array = split_composite_job(crushed_text)
        # find all the values we want
        for logfile_text in preprocessed_text_array:
            out_dict = {}
            for pattern_name, compiled_pattern in COMPILED_PATTERNS.items():
                result = re.findall(compiled_pattern, logfile_text)
                # post-process where required
                requires_postprocessing = POSTPROCESSING_FUNCTIONS.get(
                    pattern_name, False
                )
                if requires_postprocessing:
                    try:
                        result = requires_postprocessing(result)
                    except Exception as e:
                        if verbose > 0:
                            warnings.warn(
                                "Failed postprocessing for {:s} on file {:s}, error: {:s}".format(
                                    pattern_name,
                                    file,
                                    str(e),
                                )
                            )
                        result = None
                out_dict[pattern_name] = result
            out_dict["number_of_atoms"] = len(out_dict["std_xyz"][0])
            # remove 1 for the initial geometry printout
            out_dict["number_of_optimization_steps"] = len(out_dict["std_xyz"]) - 1
            out_dicts.append(out_dict)

    # debug info
    if verbose > 2:
        import pprint

        pp = pprint.PrettyPrinter(depth=4)
        pp.pprint(out_dict)

    return (*out_dicts,)
