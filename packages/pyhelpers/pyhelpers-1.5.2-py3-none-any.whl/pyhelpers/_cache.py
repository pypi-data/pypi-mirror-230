"""Cached functions and constants."""

import copy
import importlib
import importlib.util
import json
import os
import pkgutil
import re
import shutil
import sys

_OPTIONAL_DEPENDENCY = {  # import name: (package/module name, install name)
    "rapidfuzz": ("RapidFuzz", "rapidfuzz"),
    "tqdm": ("tqdm", "tqdm"),
    "matplotlib": ("Matplotlib", "matplotlib"),
    "nltk": ("NLTK", "nltk"),
    "joblib": ("Joblib", "joblib"),
    "openpyxl": ("openpyxl", "openpyxl"),
    "xlsxwriter": ("XlsxWriter", "xlsxwriter"),
    "odf": ("odfpy", "odfpy"),
    "pyarrow": ("PyArrow", "pyarrow"),
    "orjson": ("orjson", "orjson"),
    "rapidjson": ("python-rapidjson", "python-rapidjson"),
    "ujson": ("UltraJSON", "ujson"),
    "pypandoc": ("Pypandoc", "pypandoc"),
    "pdfkit": ("pdfkit", "pdfkit"),
    "psycopg2": ("psycopg2", "psycopg2"),
    "pyodbc": ("pyodbc", "pyodbc"),
}


def _check_dependency(name, package=None):
    """
    Import optional dependency package.

    :param name: name of a package/module as an optional dependency of pyhelpers
    :type name: str
    :param package: [optional] name of a package that contains the module specified by ``name``,
        defaults to ``None``
    :type package: str or None

    **Tests**::

        >>> from pyhelpers._cache import _check_dependency

        >>> psycopg2_ = _check_dependency(name='psycopg2')
        >>> psycopg2_.__name__
        'psycopg2'

        >>> pyodbc_ = _check_dependency(name='pyodbc')
        >>> pyodbc_.__name__
        'pyodbc'

        >>> gdal_ = _check_dependency(name='gdal', package='osgeo')
        >>> gdal_.__name__
        'osgeo.gdal'
    """

    import_name = name.replace('-', '_')
    if package is None:
        if '.' in import_name:
            pkg_name, _ = import_name.split('.', 1)
        else:
            pkg_name = None
    else:
        pkg_name = package.replace('-', '_')
        import_name = '.' + import_name

    if import_name in sys.modules:  # The optional dependency has already been imported
        return sys.modules.get(import_name)

    # elif (package_spec := importlib.util.find_spec(import_name)) is not None:
    elif importlib.util.find_spec(name=import_name, package=pkg_name) is not None:
        # import_package = importlib.util.module_from_spec(package_spec)
        # sys.modules[import_name] = import_package
        # package_spec.loader.exec_module(import_package)
        return importlib.import_module(name=import_name, package=pkg_name)

    else:
        if name.startswith('osgeo') or 'gdal' in import_name:
            package_name, install_name = 'GDAL', 'gdal'
        elif import_name in _OPTIONAL_DEPENDENCY:
            package_name, install_name = _OPTIONAL_DEPENDENCY[import_name]
        else:
            package_name, install_name = name, name.split('.')[0]

        raise ModuleNotFoundError(
            f"Missing optional dependency '{package_name}'. "
            f"Use pip or conda to install it, e.g. 'pip install {install_name}'.")


def _check_rel_pathname(pathname):
    """
    Check for the relative pathname (if a pathname is within the current working directory).

    :param pathname: pathname
    :type pathname: str or os.PathLike[str]
    :return: relative pathname of the input ``pathname`` if it is within the current working directory;
        otherwise, a copy of the input
    :rtype: str

    **Tests**::

        >>> from pyhelpers._cache import _check_rel_pathname
        >>> from pyhelpers.dirs import cd

        >>> _check_rel_pathname(".")
        '.'
        >>> _check_rel_pathname(cd())
        '.'
        >>> _check_rel_pathname("C:\\Program Files")
        'C:\\Program Files'
    """

    try:
        pathname_ = os.path.relpath(pathname)
    except ValueError:
        pathname_ = copy.copy(pathname)

    return pathname_


def _confirmed(prompt=None, confirmation_required=True, resp=False):
    """
    Type to confirm whether to proceed or not.

    See also [`OPS-C-1 <https://code.activestate.com/recipes/541096/>`_].

    :param prompt: a message that prompts a response (Yes/No), defaults to ``None``
    :type prompt: str | None
    :param confirmation_required: whether to require users to confirm and proceed, defaults to ``True``
    :type confirmation_required: bool
    :param resp: default response, defaults to ``False``
    :type resp: bool
    :return: a response
    :rtype: bool

    **Examples**::

        >>> from pyhelpers._cache import _confirmed

        >>> if _confirmed(prompt="Testing if the function works?", resp=True):
        ...     print("Passed.")
        Testing if the function works? [Yes]|No: yes
        Passed.
    """

    if confirmation_required:
        if prompt is None:
            prompt_ = "Confirmed?"
        else:
            prompt_ = copy.copy(prompt)

        if resp is True:  # meaning that default response is True
            prompt_ = "{} [{}]|{}: ".format(prompt_, "Yes", "No")
        else:
            prompt_ = "{} [{}]|{}: ".format(prompt_, "No", "Yes")

        ans = input(prompt_)
        if not ans:
            return resp

        if re.match('[Yy](es)?', ans):
            return True
        if re.match('[Nn](o)?', ans):
            return False

    else:
        return True


def _get_rel_pathname(pathname):
    try:
        rel_path = os.path.relpath(pathname)
    except ValueError:
        rel_path = pathname

    return rel_path


def _check_file_pathname(name, options=None, target=None):
    """
    Check pathname of a specified file given its name or filename.

    :param name: name or filename of the application that is to be called
    :type name: str
    :param options: possible pathnames or directories, defaults to ``None``
    :type options: list | set | None
    :param target: specific pathname (that may be known already), defaults to ``None``
    :type target: str | None
    :return: whether the specified executable file exists and its pathname
    :rtype: tuple[bool, str]

    **Examples**::

        >>> from pyhelpers._cache import _check_file_pathname
        >>> import os

        >>> python_exe = "python.exe"
        >>> possible_paths = ["C:\\Program Files\\Python39", "C:\\Python39\\python.exe"]

        >>> python_exe_exists, path_to_python_exe = _check_file_pathname(python_exe, possible_paths)
        >>> python_exe_exists
        True
        >>> os.path.relpath(path_to_python_exe)
        'venv\\Scripts\\python.exe'

        >>> text_exe = "pyhelpers.exe"  # This file does not actually exist
        >>> test_exe_exists, path_to_test_exe = _check_file_pathname(text_exe, possible_paths)
        >>> test_exe_exists
        False
        >>> os.path.relpath(path_to_test_exe)
        'pyhelpers.exe'
    """

    if target:
        if os.path.isfile(target):
            file_exists, file_pathname = True, target
        else:
            file_exists, file_pathname = None, False

    else:
        file_pathname = copy.copy(name)

        if os.path.isfile(file_pathname):
            file_exists = True

        else:
            file_exists = False
            alt_pathnames = {shutil.which(file_pathname)}

            if options is not None:
                alt_pathnames.update(set(options))

            for x in {x_ for x_ in alt_pathnames if x_}:
                if os.path.isdir(x):
                    file_pathname_ = os.path.join(x, file_pathname)
                else:
                    file_pathname_ = x
                if os.path.isfile(file_pathname_) and file_pathname in file_pathname_:
                    file_pathname = file_pathname_
                    file_exists = True
                    break

    return file_exists, file_pathname


# def _check_exe_pathname(exe_name, exe_pathname, possible_pathnames):
#     """
#     Check about a specified executable file pathname.
#
#     :param exe_name: filename of an executable file
#     :type exe_name: str
#     :param exe_pathname: pathname of an executable file
#     :type exe_pathname: str | None
#     :param possible_pathnames: a number of possible pathnames of the executable file
#     :type possible_pathnames: list | set
#     :return: whether the specified executable file exists and its pathname
#     :rtype: typing.Tuple[bool, str]
#
#     **Tests**::
#
#         >>> from pyhelpers._cache import _check_exe_pathname
#         >>> import os
#
#         >>> options = ["C:\\Python39\\python.exe", "C:\\Program Files\\Python39\\python.exe"]
#
#         >>> python_exists, path_to_exe = _check_exe_pathname("python.exe", None, options)
#         >>> python_exists
#         True
#         >>> os.path.basename(path_to_exe)
#         'python.exe'
#     """
#
#     if exe_pathname is None:
#         exe_exists, exe_pathname_ = _find_file(exe_name, options=possible_pathnames)
#     else:
#         exe_exists, exe_pathname_ = os.path.exists(exe_pathname), copy.copy(exe_pathname)
#
#     return exe_exists, exe_pathname_


def _format_err_msg(e=None, msg=""):
    """
    Format an error message.

    :param e: Exception or any of its subclasses, defaults to ``None``
    :type e: Exception | BaseException | str | None
    :param msg: default error message, defaults to ``""``
    :type msg: str
    :return: an error message
    :rtype: str

    **Examples**::

        >>> from pyhelpers._cache import _format_err_msg

        >>> _format_err_msg("test")
        'test.'

        >>> _format_err_msg("test", msg="Failed.")
        'Failed. test.'
    """

    if e:
        e_ = f"{e}"
        err_msg = e_ + "." if not e_.endswith((".", "!", "?")) else e_
    else:
        err_msg = ""

    if msg:
        err_msg = msg + " " + err_msg

    return err_msg


def _print_failure_msg(e, msg="Failed."):
    """
    Print the error message associated with occurrence of an``Exception``.

    :param e: Exception or any of its subclasses, defaults to ``None``
    :type e: Exception | BaseException | str | None
    """

    err_msg = _format_err_msg(e=e, msg=msg)
    print(err_msg)


def example_dataframe(osgb36=False):
    """
    Create an example dataframe.

    :param osgb36: whether to use data based on OSGB36 National Grid, defaults to ``True``
    :type osgb36: bool
    :return: an example dataframe
    :rtype: pandas.DataFrame

    **Tests**::

        >>> from pyhelpers._cache import example_dataframe

        >>> example_dataframe()
                          Easting       Northing
        City
        London      530039.558844  180371.680166
        Birmingham  406705.887014  286868.166642
        Manchester  383830.039036  398113.055831
        Leeds       430147.447354  433553.327117

        >>> example_dataframe(osgb36=False)
                    Longitude   Latitude
        City
        London      -0.127647  51.507322
        Birmingham  -1.902691  52.479699
        Manchester  -2.245115  53.479489
        Leeds       -1.543794  53.797418
    """

    pd_ = _check_dependency(name='pandas')

    if osgb36:
        _columns = ['Easting', 'Northing']
        _example_df = [
            (530039.5588445, 180371.6801655),  # London
            (406705.8870136, 286868.1666422),  # Birmingham
            (383830.0390357, 398113.0558309),  # Manchester
            (430147.4473539, 433553.3271173),  # Leeds
        ]
    else:
        _columns = ['Longitude', 'Latitude']
        _example_df = [
            (-0.1276474, 51.5073219),  # London
            (-1.9026911, 52.4796992),  # Birmingham
            (-2.2451148, 53.4794892),  # Manchester
            (-1.5437941, 53.7974185),  # Leeds
        ]

    _index = ['London', 'Birmingham', 'Manchester', 'Leeds']

    _example_dataframe = pd_.DataFrame(data=_example_df, index=_index, columns=_columns)

    _example_dataframe.index.name = 'City'

    return _example_dataframe


_USER_AGENT_STRINGS = json.loads(pkgutil.get_data(__name__, "data/user-agent-strings.json").decode())

_ENGLISH_NUMERALS = json.loads(pkgutil.get_data(__name__, "data/english-numerals.json").decode())
