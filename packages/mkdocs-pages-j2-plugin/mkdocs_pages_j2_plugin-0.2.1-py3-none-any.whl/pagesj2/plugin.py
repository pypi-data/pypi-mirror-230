################################################################################
# @brief       : Pages-J2 Plugin for MkDocs
# @author      : Jacques Supcik <jacques.supcik@hefr.ch>
# @date        : 14. June 2023
# ------------------------------------------------------------------------------
# @copyright   : Copyright (c) 2022 HEIA-FR / ISC
#                Haute école d'ingénierie et d'architecture de Fribourg
#                Informatique et Systèmes de Communication
# @attention   : SPDX-License-Identifier: MIT OR Apache-2.0
################################################################################

"""Pages-J2 Plugin for MkDocs"""

import logging
import os

import jinja2
from mkdocs.config.base import Config as BaseConfig
from mkdocs.plugins import BasePlugin

logger = logging.getLogger("mkdocs.plugins." + __name__)
TAG = "[pages-j2] -"


class PagesJ2PluginConfig(BaseConfig):
    """Configuration options for the PagesJ2Plugin"""


# pylint: disable-next=too-few-public-methods
class PagesJ2Plugin(BasePlugin[PagesJ2PluginConfig]):
    """Pages-J2 Plugin for MkDocs"""

    def on_pre_build(self, config):
        """
        Build the `.pages` files from `pages.j2`
        """
        logger.info("%s Building .pages files", TAG)
        for root, _, files in os.walk(config["docs_dir"], topdown=False):
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(root),
            )
            for name in files:
                if name != "pages.j2":
                    continue

                template = env.get_template(name)
                content = template.render(config)
                dst = os.path.join(root, ".pages")
                # Do not write the file if the content is the same.
                # Otherwise, the "watcher" will continuously reload the page.
                if os.path.exists(dst):
                    with open(
                        dst, encoding="utf-8"
                    ) as f:  # pylint: disable=invalid-name
                        orig = f.read()
                    if content == orig:
                        continue
                with open(
                    dst, "w", encoding="utf-8"
                ) as f:  # pylint: disable=invalid-name
                    logger.info("%s Writing %s", TAG, dst)
                    f.write(content)
