#!/usr/bin/env python3

import logging
import os

from unmanic.libs.unplugins.settings import PluginSettings


logger = logging.getLogger("Unmanic.Plugin.postprocessor_script")


class Settings(PluginSettings):
    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.settings = {
            "release_group_name": "custom",
        }
        self.form_settings = {
            "release_group_name": {
                "label": "Release group name",
                "description": "The custom release group name to set",
            }
        }


def on_postprocessor_task_results(data):
    """
    Runner function - provides a means for additional postprocessor functions based on the task success.

    The 'data' object argument includes:
        library_id                      - The library that the current task is associated with.
        task_id                         - Integer, unique identifier of the task.
        task_type                       - String, "local" or "remote".
        final_cache_path                - The path to the final cache file that was then used as the source for all destination files.
        task_processing_success         - Boolean, did all task processes complete successfully.
        file_move_processes_success     - Boolean, did all postprocessor movement tasks complete successfully.
        destination_files               - List containing all file paths created by postprocessor file movements.
        source_data                     - Dictionary containing data pertaining to the original source file.
        start_time                      - Float, UNIX timestamp when the task began.
        finish_time                     - Float, UNIX timestamp when the task completed.

    :param data:
    :return:

    """

    settings = Settings(library_id=data["library_id"])
    release_group_name = settings.get_setting("release_group_name")

    if not data["task_processing_success"]:
        # Exit early if the worker did not complete successfully
        return

    new_destinations = []
    for file in data["destination_files"]:
        if not os.path.isfile(file):
            logger.warning(f"File does not exist, skipping rename. ({file})")
            new_destinations.append(file)
            continue

        filename, ext = os.path.splitext(file)
        new_filename = filename.rsplit("]", 1)[0] + "]-" + release_group_name + ext
        logging.debug(f"Renaming '{file}' --> '{new_filename}'")
        os.rename(file, new_filename)
        new_destinations.append(new_filename)
