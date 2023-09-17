import json
import os
import pkgutil
from typing import List, Tuple

import math
import numpy as np

from .fluency_score_interface import LanguageModelFluencyScoreInterface


class NCE(LanguageModelFluencyScoreInterface):
    def __init__(
        self,
        language_model: str,
        device: str = "cuda",
        tokenizer: str = "treebank",
        do_normalization: bool = True,
        rescale_bound_ab: Tuple = (0, 1),
    ):
        """
        Instantiate a Negative Cross-Entropy metric to compute the NCE score or the WPNCE.

        NCE is equal to the probability of occurrence of a given sentence base on the likelihood of a
        language model normalizes by the number of word in the sentence (i.e. sentence length).

        Args:
            language_model (str): The language model to compute the sentence and pre-process word probabilities matrix.
                The supported model are ``"bert-base-uncased"``, ``"bert-large-uncased"`` and ``"roberta-base"``.
            device (str): The device to use such as ``"cpu"``, ``"cuda"`` or ``"cuda:device_int"``.
            tokenizer(str): The tokenizer to use to split the sentence. If the tokenizer is set to ``"treebank"``,
                ``"whitespace"`` or ``"whitespace_lm"`` it will be a NCE metric. If the tokenizer is set to
                ``"wordpiece"``, it is a WPNCE. Other than the tokenizing process, the compute method is similar.
            do_normalization (bool): Either or not to do normalization. By default, set to True.
            rescale_bound_ab (Tuple): A tuple to specify the rescaling normalization bound, by default the range is
                [0, 1].

        Implementation details:

            See LanguageModelFluencyScoreInterface for implementation details.
        """

        super().__init__(language_model, device, tokenizer, do_normalization, rescale_bound_ab)

        files_name = f"{tokenizer.lower()}"
        if tokenizer.lower() in ("whitespace_llm", "wordpiece"):
            files_name += f"_{language_model.lower().replace('-', '_')}"

        data = pkgutil.get_data(
            __name__,
            os.path.join(
                "./resources",
                "nce_scores_distribution",
                f"{files_name}.json",
            ),
        )

        # Computed on the Gigaword dataset version 1.2.0
        # The min score is mu - 2 * sigma (i.e. the mean minus 2 standard deviation)
        # The max score is mu + 2 * sigma (i.e. the mean plus 2 standard deviation)
        # Statistically, 95.45% of the scores are include in this range.
        # https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule
        nce_scores_distribution = json.loads(data.decode("utf-8"))
        mu = nce_scores_distribution.get("mean")
        standard_deviation = math.sqrt(nce_scores_distribution.get("variance"))
        self.normalisation_min_score = mu - 2 * standard_deviation
        self.normalisation_max_score = mu + 2 * standard_deviation

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

        sentences_log_prob = np.nan_to_num(sentences_log_prob)

        nce_score: List = list(np.divide(sentences_log_prob, sentences_len))

        if self.do_normalization:
            nce_score = self._normalize_scores(
                scores=nce_score,
                x_min=self.normalisation_min_score,
                x_max=self.normalisation_max_score,
                a=self.normalisation_a_score,
                b=self.normalisation_b_score,
            )
        return nce_score
