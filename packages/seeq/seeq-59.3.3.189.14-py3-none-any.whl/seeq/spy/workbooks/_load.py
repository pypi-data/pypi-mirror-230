from __future__ import annotations

import glob
import os
import tempfile
import zipfile

from seeq.spy import _common
from seeq.spy._errors import *
from seeq.spy._status import Status
from seeq.spy.workbooks._template import Analysis, AnalysisTemplate, TopicTemplate
from seeq.spy.workbooks._workbook import Workbook, WorkbookList


def load(folder_or_zipfile, *, as_template_with_label: str = None) -> WorkbookList:
    """
    Loads a list of workbooks from a folder on disk into Workbook objects in
    memory.

    Parameters
    ----------
    folder_or_zipfile : str
        A folder or zip file on disk containing workbooks to be loaded. Note
        that any subfolder structure will work -- this function will scan for
        any subfolders that contain a Workbook.json file and assume they should
        be loaded.

    as_template_with_label : str
        Causes the workbooks to be loaded as templates (either AnalysisTemplate
        or TopicTemplate) with the label specified. See the Workbook Templates
        documentation notebook for more information about templates.
    """
    status = Status()

    _common.validate_argument_types([
        (folder_or_zipfile, 'folder_or_zipfile', str),
        (as_template_with_label, 'as_template_with_label', str)
    ])

    folder_or_zipfile = os.path.normpath(folder_or_zipfile)

    try:
        if not os.path.exists(folder_or_zipfile):
            raise SPyRuntimeError('Folder/zipfile "%s" does not exist' % folder_or_zipfile)

        if folder_or_zipfile.lower().endswith('.zip'):
            with tempfile.TemporaryDirectory() as temp:
                with zipfile.ZipFile(folder_or_zipfile, "r") as z:
                    status.update('Unzipping "%s"' % folder_or_zipfile, Status.RUNNING)
                    z.extractall(temp)

                status.update('Loading from "%s"' % temp, Status.RUNNING)
                workbooks = _load_from_folder(temp)
        else:
            status.update('Loading from "%s"' % folder_or_zipfile, Status.RUNNING)
            workbooks = _load_from_folder(folder_or_zipfile)

        if as_template_with_label is not None:
            package = WorkbookList()
            for workbook in workbooks:
                package.append(_get_template_class(workbook)(as_template_with_label, workbook, package=package))
            workbooks = package

        status.update('Success', Status.SUCCESS)
        return workbooks

    except KeyboardInterrupt:
        status.update('Load canceled', Status.CANCELED)


def _get_template_class(workbook):
    return AnalysisTemplate if isinstance(workbook, Analysis) else TopicTemplate


def _load_from_folder(folder):
    workbook_json_files = glob.glob(os.path.join(folder, '**', 'Workbook.json'), recursive=True)

    workbooks = WorkbookList()
    for workbook_json_file in workbook_json_files:
        workbooks.append(Workbook.load(os.path.dirname(workbook_json_file)))

    return workbooks
