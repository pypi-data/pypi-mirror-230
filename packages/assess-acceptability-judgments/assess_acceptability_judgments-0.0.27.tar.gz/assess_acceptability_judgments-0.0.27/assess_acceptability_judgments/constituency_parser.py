import json
import os
import pkgutil
from typing import List, Union, Optional

import benepar
import spacy
import stanza
import supar
from stanza.models.constituency.tree_reader import read_trees
from stanza.server import CoreNLPClient
from supar import Parser
from tqdm import tqdm

from .core_nlp_parser_interface import CoreNLPParserInterface


# Add encoding of the parse tree using Tree-LSTM:
#  https://github.com/dmlc/dgl/blob/master/examples/pytorch/tree_lstm/README.md
# similar to https://www.hindawi.com/journals/cin/2022/4096383/


class ConstituencyParserCoreNLP(CoreNLPParserInterface):
    def __init__(
        self,
        verbose: bool = True,
        cache_path: Optional[str] = None,
        binary_tree: bool = False,
        **core_nlp_client_kwargs,
    ) -> None:
        """
         Create a constituency parsing model that use CoreNLP constituency parser. To do so, we download the latest
        model from CoreNLP (i.e. 2018) as suggest by this Wiki
        https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK.

        The tag ar those suggested by this source https://gist.github.com/nlothian/9240750.

        :param verbose: (bool) Either or not to be verbose during the download of CoreNLP model. Default to `True`.
        :param cache_path: (Optional[str]) Optional parameter to set a cache path to download the CoreNP model to.
            If the cache_path is not set, the model are downloaded in the default cache path i.e. `'.cache/aaj'`.
        :param binary_tree: (bool) Either or not to get the binary parse tree. Default to false.
        :param core_nlp_client_kwargs: A set of keyword arguments to be pass to the CoreNLPClient, such as be_quiet, or
            start_over.
        """
        super().__init__(verbose, cache_path)

        data = pkgutil.get_data(
            __name__,
            os.path.join(
                "./resources",
                "treebank_tags_mapping.json",
            ),
        )
        self._tags_mapping = json.loads(data.decode("utf-8"))

        stanza.install_corenlp()

        custom_args = {}
        self.extraction_key = "parse"
        if binary_tree:
            custom_args.update({"parse.binaryTrees": True})
            self.extraction_key = "binaryParse"

        self.client = CoreNLPClient(
            annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'parse'],
            timeout=30000,
            memory='16G',
            properties=custom_args,
            output_format="json",
            **core_nlp_client_kwargs,
        )
        self.start()

    def start(self) -> None:
        """
        Method to start the CoreNLP Client.
        """
        self.client.start()

    def stop(self) -> None:
        """
        Method to stop the CoreNLP Client.
        """
        self.client.stop()

    def tree_parser_sentences(self, sentences: List[str]) -> List[List[str]]:
        """
        Method to parse sentences into constituency tree.

        :param sentences: (list) A list of sentence to parse into trees.

        :return: A list of str tree written in Standford constituency parsed tree format using bracket (i.e. "()").
        """
        # Base on the documentation and this issue https://github.com/stanfordnlp/stanza/issues/478.

        parsed_trees = []
        if self.verbose:
            sentences = tqdm(sentences, total=len(sentences), desc="Processing dataset into trees")
        for sentence in sentences:
            if len(sentence) > 0:
                ann = self.client.annotate(sentence)

                # Get the parsed sentence
                parse_sentence = ann["sentences"][0]
                constituency_parse = parse_sentence[self.extraction_key]

                parsed_trees.append(constituency_parse)
            else:
                parsed_trees.append([""])
        return parsed_trees

    def __del__(self) -> None:
        """
        Cleanup of the client by stopping it before.
        """
        if hasattr(self, 'client'):
            self.stop()


class ConstituencyParserSuPar:
    def __init__(self, model: str, verbose: bool = True) -> None:
        """
        Create a dependency parsing model that use SuPar constituency parser.

        Base on the SuPar documentation https://github.com/yzhangcs/parser#usage.

        :param model: (str) The parsing model to use. Choices are
            # - `'aj'` (https://papers.nips.cc/paper/2020/hash/f7177163c833dff4b38fc8d2872f1ec6-Abstract.html),
            - `'crf'` (https://www.ijcai.org/Proceedings/2020/560/),
            - `'tt'` (https://aclanthology.org/2020.acl-main.557), and
            - `'vi'` (https://aclanthology.org/2020.aacl-main.12).
        :param verbose: (bool) Either or not to be verbose during the download of CoreNLP model.  Default to `True`.
        """

        self.process_pipeline = Parser.load(f'{model}-con-en')

        self.verbose = verbose

    def get_tree(self, sentence: supar.utils.Dataset) -> List[supar.utils.transform.TreeSentence]:
        """
        Interface method to get the tree depending on the sentence object.

        :param sentence: A SuPar Dataset.
        :return: Return a list of Tree SuPar Sentence.
        """
        return sentence.sentences

    def process_sentences(self, sentence: str) -> supar.utils.Dataset:
        """
        Interface method to process sentences.

        :param sentence: A sentence.
        :return: Return a SuPar dataset.
        """
        return self.process_pipeline.predict(sentence, lang="en", prob="False", verbose="False")

    def tree_parser_sentences(self, sentences: List[str]) -> List[List[Union[str, supar.utils.transform.TreeSentence]]]:
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


class ConstituencyParserBeNePar:
    def __init__(self, use_larger_model: bool = False, verbose: bool = True) -> None:
        """
        Create a dependency parsing model that use BeNePar constituency parser.

        Base on the BeNePar documentation
        https://github.com/nikitakit/self-attentive-parser#usage-with-spacy-recommended.

        :param use_larger_model: (bool) either or not to use the larger model version. Larger model tak
            more RAM/GPU RAM than smaller one. See SpaCy and BeNePar documentation for details.
        :param verbose: (bool) Either or not to be verbose during the download of CoreNLP model. Default to `True`.
        """

        if use_larger_model:
            spacy_model = "en_core_web_trf"
            benepar_model = "benepar_en3_large"
        else:
            spacy_model = "en_core_web_md"
            benepar_model = "benepar_en3"

        spacy.cli.download(spacy_model)
        benepar.download(benepar_model)
        self.process_pipeline = spacy.load(spacy_model)
        self.process_pipeline.add_pipe("benepar", config={"model": benepar_model})

        self.verbose = verbose

    def get_tree(self, sentence: spacy.tokens.Span) -> stanza.models.constituency.parse_tree.Tree:
        """
        Interface method to get the tree depending on the sentence object.

        :param sentence: A SpaCy Span.
        :return: Return a Stanza Tree.
        """

        return read_trees(sentence._.parse_string)

    def process_sentences(self, sentences: List[str]) -> spacy.Language.pipe:
        """
        Interface method to process sentences.

        :param sentences: A list of sentences.
        :return: Return a generator.
        """
        return self.process_pipeline.pipe(sentences)

    def tree_parser_sentences(
        self, sentences: List[str]
    ) -> List[List[Union[str, stanza.models.constituency.parse_tree.Tree]]]:
        """
        Method to parse sentences into constituency tree.

        :param sentences: (list) A list of sentence to parse into trees.
        :return: A list of Stanza parse tree.
        """

        process_documents = self.process_sentences(sentences)

        parsed_trees = []

        if self.verbose:
            process_documents = tqdm(
                process_documents, total=len(process_documents), desc="Processing dataset into trees"
            )

        for process_document in process_documents:
            if len(process_document.text) > 0:
                doc_parsed_trees = []
                for sent in process_document.sents:
                    parsed_tree = self.get_tree(sent)
                    doc_parsed_trees.append(parsed_tree)
                parsed_trees.append(doc_parsed_trees)
            else:
                parsed_trees.append([""])
        return parsed_trees
