################################################################################
# @brief       : Pdf2Image Plugin for MkDocs
# @author      : Jacques Supcik <jacques.supcik@hefr.ch>
# @date        : 7. August 2023
# ------------------------------------------------------------------------------
# @copyright   : Copyright (c) 2023 HEIA-FR / ISC
#                Haute école d'ingénierie et d'architecture de Fribourg
#                Informatique et Systèmes de Communication
# @attention   : SPDX-License-Identifier: MIT OR Apache-2.0
################################################################################

"""Pdf2Image Plugin for MkDocs"""

import logging
import os
from pathlib import Path

import pdf2image
from mkdocs.config import config_options as c
from mkdocs.config.base import Config as BaseConfig
from mkdocs.plugins import BasePlugin

logger = logging.getLogger("mkdocs.plugins." + __name__)
TAG = "[Pdf2Image] -"


class Pdf2ImagePluginConfig(BaseConfig):
    """Configuration options for the Pdf2Image"""

    src = c.Type(list, default=[])
    dpi = c.Type(int, default=200)
    fmt = c.Choice(["png", "jpg"], default="jpg")
    size = c.Type(tuple, default=(None, None))
    extension = c.Optional(c.Type(str))
    force = c.Type(bool, default=False)


# pylint: disable-next=too-few-public-methods
class Pdf2ImagePlugin(BasePlugin[Pdf2ImagePluginConfig]):
    """Pdf2Image Plugin for MkDocs"""

    def on_pre_build(self, config):
        """
        Build images from pdf files
        """
        logger.info("%s Building images from pdf", TAG)
        for pattern in self.config.src:
            logger.debug("%s searching %s", TAG, pattern)
            for src in Path(config.docs_dir).glob(pattern):
                extension = self.config.extension or self.config.fmt
                dst = src.with_suffix("." + extension)
                if (
                    not self.config.force
                    and dst.exists()
                    and src.stat().st_mtime <= dst.stat().st_mtime
                ):
                    logger.debug("%s %s already exists", TAG, dst)
                    continue

                logger.debug("%s converting %s -> %s", TAG, src, dst)
                res = pdf2image.convert_from_path(
                    src,
                    output_folder=src.parent,
                    dpi=self.config.dpi,
                    size=self.config.size,
                    fmt=self.config.fmt,
                    single_file=True,
                    paths_only=True,
                )
                os.rename(res[0], dst)
