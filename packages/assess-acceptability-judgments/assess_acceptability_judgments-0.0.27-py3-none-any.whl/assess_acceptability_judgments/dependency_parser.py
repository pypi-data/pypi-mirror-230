import json
import os
import pkgutil
from typing import List, Optional, Union

import conllu
import nltk
import supar
from nltk.parse.corenlp import CoreNLPServer, CoreNLPDependencyParser
from supar import Parser
from tqdm import tqdm

from .core_nlp_parser_interface import CoreNLPParserInterface


class DependencyParserCoreNLP(CoreNLPParserInterface):
    def __init__(self, verbose: bool = True, cache_path: Optional[str] = None) -> None:
        """
        Create a dependency parsing model that use CoreNLP dependency parser. To do so, we download the latest
        model from CoreNLP (i.e. 2018) as suggest by this Wiki
        https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK.

        The tags are the Universal Dependencies tag V1 available here
        https://universaldependencies.org/docsv1/u/dep/index.html.

        :param verbose: (bool) Either or not to be verbose during the download of CoreNLP model. Default to `True`.
        :param cache_path: (Optional[str]) Optional parameter to set a cache path to download the CoreNP model to.
            If the cache_path is not set, the model are downloaded in the default cache path i.e. `'.cache/aaj'`.
        """
        super().__init__(verbose, cache_path)

        data = pkgutil.get_data(
            __name__,
            os.path.join(
                "./resources",
                "conll_u_tags_mapping.json",
            ),
        )
        self._tags_mapping = json.loads(data.decode("utf-8"))

    def tree_parser_sentences(
        self, sentences: List[str]
    ) -> List[List[Union[str, nltk.parse.dependencygraph.DependencyGraph]]]:
        """
        Method to parse sentences into dependency tree.

        :param sentences: (list) A list of sentence to parse into trees.
        :return: A list of NLTK dependency parse tree.
        """
        with CoreNLPServer(path_to_jar=self.jar_file_name, path_to_models_jar=self.jar_model_file_name) as server:
            parser = CoreNLPDependencyParser(url=server.url)
            parsed_trees = []
            if self.verbose:
                sentences = tqdm(sentences, total=len(sentences), desc="Processing dataset into trees")

            for sentence in sentences:
                if len(sentence) > 0:
                    # raw_parse return a list iterator, so we convert it into a list
                    # Once converted, it includes a dependency graph inside (seen as a defaultdict).
                    parsed_trees.append(list(parser.raw_parse(sentence)))
                else:
                    parsed_trees.append([""])
            return parsed_trees


class DependencyParserSuPar:
    def __init__(self, model: str, verbose: bool = True):
        """
        Create a dependency parsing model that use SuPar constituency parser.

        Base on the SuPar documentation https://github.com/yzhangcs/parser#usage.

        :param model: (str) The parsing model to use. Choices are
            - `'biaffine'` (https://openreview.net/forum?id=Hk95PK9le),
            - `'crf'` (https://aclanthology.org/2020.acl-main.302/),
            - `'crf2o'` (https://aclanthology.org/2020.acl-main.302/), and
            - `'vi'` (https://aclanthology.org/2020.aacl-main.12).
        :param verbose: (bool) Either or not to be verbose during the download of CoreNLP model. Default to `True`.
        """

        self.process_pipeline = Parser.load(f'{model}-dep-en')

        self.verbose = verbose

    def get_tree(self, sentence: supar.utils.Dataset) -> List[conllu.models.TokenTree]:
        """
        Interface method to get the tree depending on the sentence object.

        :param sentence: A SuPar Dataset.
        :return: Return a list of Tree SuPar Sentence.
        """
        return conllu.parse_tree(str(sentence.sentences[0]))

    def process_sentences(self, sentence: str) -> supar.utils.Dataset:
        """
        Interface method to process sentences.

        :param sentence: A sentence.
        :return: Return a SuPar dataset.
        """
        return self.process_pipeline.predict(sentence, lang="en", prob="False", verbose="False")

    def tree_parser_sentences(self, sentences: List[str]) -> List[List[Union[str, conllu.models.TokenTree]]]:
        """
        Method to parse sentences into constituency tree.

        :param sentences: (list) A list of sentence to parse into trees.
        :return: A list of SuPar parse tree.
        """
        parsed_trees = []

        if self.verbose:
            sentences = tqdm(sentences, total=len(sentences), desc="Processing dataset into trees")

        for sentence in sentences:
            if len(sentence) > 0:
                process_documents = self.process_sentences(sentence)
                parsed_trees.append(self.get_tree(process_documents))
            else:
                parsed_trees.append([""])
        return parsed_trees
