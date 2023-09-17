import os
import zipfile
from abc import abstractmethod
from pathlib import Path
from typing import List, Optional, Union
from urllib.request import urlretrieve

import nltk

from .ressources import CACHE_PATH, CORENLP_URL
from .util import DownloadProgressBar


class CoreNLPParserInterface:
    # Path to the corenlp JAR models to use for parsing and create Tree
    # As of july 2023, Stanza does not return a Tree by a dictionary. Thus, we use NLTK API
    # that parse and return a dependency parse tree.
    CORENLP_DIRECTORY = "stanford-corenlp-full-2018-02-27"
    JAR_FILE_NAME = os.path.join(CORENLP_DIRECTORY, "stanford-corenlp-3.9.1.jar")
    JAR_MODEL_FILE_NAME = os.path.join(CORENLP_DIRECTORY, "stanford-corenlp-3.9.1-models.jar")

    def __init__(self, verbose: bool = True, cache_path: Optional[str] = None) -> None:
        """
         Create a constituency parsing model that use CoreNLP constituency parser. To do so, we download the latest
        model from CoreNLP (i.e. 2018) as suggest by this Wiki
        https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK.

        :param verbose: (bool) Either or not to be verbose during the download of CoreNLP model. Default to `True`.
        :param cache_path: (Optional[str]) Optional parameter to set a cache path to download the CoreNP model to.
            If the cache_path is not set, the model are downloaded in the default cache path i.e. `'.cache/aaj'`.
        """

        if cache_path is None:
            cache_path = CACHE_PATH

        self.jar_file_name = os.path.join(cache_path, self.JAR_FILE_NAME)
        self.jar_model_file_name = os.path.join(cache_path, self.JAR_MODEL_FILE_NAME)

        self.verbose = verbose
        if not os.path.exists(self.jar_file_name) and not os.path.exists(self.jar_model_file_name):
            if self.verbose:
                reporthook = DownloadProgressBar()
            else:
                reporthook = None

            # Download zipped file with verbose report
            local_filename, _ = urlretrieve(CORENLP_URL, reporthook=reporthook)

            # Create .cache directory if it does not exist
            Path(cache_path).mkdir(parents=True, exist_ok=True)

            # Unzip the file into the cache directory
            with zipfile.ZipFile(local_filename, "r") as f:
                f.extractall(cache_path)

    @abstractmethod
    def tree_parser_sentences(self, sentences: List[str]) -> List[List[Union[str, nltk.tree.tree.Tree]]]:
        """
        Method to parse sentences into a tree.

        :param sentences: (list) A list of sentence to parse into trees.
        :return: A list of parse tree.
        """

    @property
    def tags_list(self) -> List[str]:
        tags_list = list(self._tags_mapping.keys())

        # We pop the first since it's the "__comment__", which is not a tag but the tags list source details.
        tags_list.pop(0)

        return tags_list
