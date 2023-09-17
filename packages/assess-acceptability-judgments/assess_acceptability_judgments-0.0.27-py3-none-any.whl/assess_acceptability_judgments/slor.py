import json
import os
import pkgutil
from typing import List, Tuple

import math
import numpy as np

from .fluency_score_interface import LanguageModelFluencyScoreInterface


class SLOR(LanguageModelFluencyScoreInterface):
    def __init__(
        self,
        language_model: str,
        device: str = "cuda",
        tokenizer: str = "treebank",
        do_normalization: bool = True,
        rescale_bound_ab: Tuple = (0, 1),
    ):
        """
        Instantiate a SLOR metric to compute the SLOR score or the WPSLOR.

        SLOR was initially proposed in the article Large-Scale Syntactic Language Modeling with Treelets
        (https://aclanthology.org/P12-1101.pdf). We use the clearer definition of SLOR presented in the article
        Grammaticality, Acceptability, and Probability: A Probabilistic View of Linguistic Knowledge
        (https://onlinelibrary.wiley.com/doi/full/10.1111/cogs.12414) which is defined as the log probability of
        the sentence S given by a language model minus the log probability of the sentence unigram (i.e. probability of
        occurrence of each word) normalized (i.e. divided) by the length of the sentence (i.e. the number of
        words).

        Namely, SLOR is equal to the probability of occurrence of a given sentence base on the likelihood of a
        language model normalizes by the probability of occurrence of each word and by the number of
        word in the sentence (i.e. sentence length).

        WPSLOR was proposed in the article Sentence-Level Fluency Evaluation: References Help, But Can Be Spared!
        (https://arxiv.org/pdf/1809.08731v1.pdf). The only difference with SLOR is the tokenization process, namely
        it use wordpiece algorithm or not.

        Args:
            language_model (str): The language model to compute the sentence and pre-process word probabilities matrix.
                The supported model are ``"bert-base-uncased"``, ``"bert-large-uncased"`` and ``"roberta-base"``.
            device (str): The device to use such as ``"cpu"``, ``"cuda"`` or ``"cuda:device_int"``.
            tokenizer(str): The tokenizer to use to split the sentence. If the tokenizer is set to ``"treebank"``,
                ``"whitespace"`` or ``"whitespace_lm"`` it will be a SLOR metric. If the tokenizer is set to
                ``"wordpiece"``, it is a WPSLOR. Other than the tokenizing process, the compute method is similar.
            do_normalization (bool): Either or not to do normalization. By default, set to True.
            rescale_bound_ab (Tuple): A tuple to specify the rescaling normalization bound, by default the range is
                [0, 1].


        Implementation details:

            See LanguageModelFluencyScoreInterface for implementation details.

            # About p_u and out-of-vocabulary (OOV)
            The individual word probabilities have been computed on the HuggingFace Gigaword dataset
            (https://huggingface.co/datasets/gigaword) using all three splits (i.e. train, validation and test) for a
            total of 3,995,559 documents.

            For out-of-vocabulary words, we use the mean of all words probability.


        """
        super().__init__(language_model, device, tokenizer, do_normalization, rescale_bound_ab)

        files_name = f"{tokenizer.lower()}"
        if tokenizer.lower() in ("whitespace_llm", "wordpiece"):
            files_name += f"_{language_model.lower().replace('-', '_')}"

        data = pkgutil.get_data(
            __name__,
            os.path.join(
                "./resources",
                "slor_scores_distribution",
                f"{files_name}.json",
            ),
        )

        # Computed on the Gigaword dataset version 1.2.0
        # The min score is mu - 2 * sigma (i.e. the mean minus 2 standard deviation)
        # The max score is mu + 2 * sigma (i.e. the mean plus 2 standard deviation)
        # Statistically, 95.45% of the scores are include in this range.
        # https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule
        slor_scores_distribution = json.loads(data.decode("utf-8"))
        mu = slor_scores_distribution.get("mean")
        standard_deviation = math.sqrt(slor_scores_distribution.get("variance"))
        self.normalisation_min_score = mu - 2 * standard_deviation
        self.normalisation_max_score = mu + 2 * standard_deviation

        data = pkgutil.get_data(
            __name__,
            os.path.join(
                "./resources",
                "words_probability",
                f"{files_name}.json",
            ),
        )
        self.words_probabilities_model = json.loads(data.decode("utf-8"))

    def compute_score(self, sentences: List[str]) -> List[float]:
        """
        Computed base of this article https://arxiv.org/pdf/1809.08731v1.pdf.
        """

        (
            padded_sentences_words_idx,
            sentences_mask,
            batch_logits,
        ) = self._llm_batch_processing(sentences=sentences)

        sentences_len: List[int] = self._compute_sentences_len(sentences_mask)

        sentences_log_prob = self._compute_pm(padded_sentences_words_idx, sentences_mask, batch_logits, sentences_len)

        words_log_prob = self._compute_pu(padded_sentences_words_idx, batch_logits)

        sentences_log_prob = np.nan_to_num(sentences_log_prob)
        words_log_prob = np.nan_to_num(words_log_prob)

        slor_score: List = list(np.divide(np.subtract(sentences_log_prob, words_log_prob), sentences_len))

        if self.do_normalization:
            slor_score = self._normalize_scores(
                scores=slor_score,
                x_min=self.normalisation_min_score,
                x_max=self.normalisation_max_score,
                a=self.normalisation_a_score,
                b=self.normalisation_b_score,
            )
        return slor_score

    def _compute_pu(
        self,
        padded_sentences_words_idx: List[List[int]],
        sentences_len,
    ) -> List[float]:
        """
        Compute the probability of each word using a pre-computed probability matrix.

        Computed base of this article https://arxiv.org/pdf/1809.08731v1.pdf.

        For out-of-vocabulary words, we use the mean of all words probability.
        """

        batch_size = len(sentences_len)

        words_log_prob: List[float] = [0.0] * batch_size
        for batch_index in range(batch_size):
            tokenize_word_sentence = self.llm_tokenizer.convert_ids_to_tokens(
                padded_sentences_words_idx[batch_index], skip_special_tokens=True
            )
            for word in tokenize_word_sentence:
                word_probability = self.words_probabilities_model.get(word)
                if word_probability is not None:
                    words_log_prob[batch_index] += np.log(word_probability)
                else:
                    words_log_prob[batch_index] += np.log(self.words_probabilities_model.get("<UNK>"))
        return words_log_prob
