from typing import List, Tuple

import numpy as np

from .fluency_score_interface import LanguageModelFluencyScoreInterface


class PPL(LanguageModelFluencyScoreInterface):
    def __init__(
        self,
        language_model: str,
        device: str = "cuda",
        tokenizer: str = "treebank",
        do_normalization: bool = False,
        rescale_bound_ab: Tuple = (0, 1),
    ):
        """
        Instantiate a Perplexity metric to compute the PPL score or the WPPPL.

        PPL is equal to the exponential value of the Negative Cross-Entropy (NCE). Namely, the exponential value of the
        probability of occurrence of a given sentence base on the likelihood of a language model normalizes by the
        number of word in the sentence (i.e. sentence length).

        Args:
            language_model (str): The language model to compute the sentence and pre-process word probabilities matrix.
                The supported model are ``"bert-base-uncased"``, ``"bert-large-uncased"`` and ``"roberta-base"``.
            device (str): The device to use such as ``"cpu"``, ``"cuda"`` or ``"cuda:device_int"``.
            tokenizer(str): The tokenizer to use to split the sentence. If the tokenizer is set to ``"treebank"``,
                ``"whitespace"`` or ``"whitespace_lm"`` it will be a PPL metric. If the tokenizer is set to
                ``"wordpiece"``, it is a WPPPL. Other than the tokenizing process, the compute method is similar.
            do_normalization (bool): Either or not to do normalization. By default, set to False. Set to False by
                default, since default rescale bound does not change the value.
            rescale_bound_ab (Tuple): A tuple to specify the rescaling normalization bound, by default the range is
                [0, 1].

        Implementation details:

            See LanguageModelFluencyScoreInterface for implementation details.
        """

        super().__init__(language_model, device, tokenizer, do_normalization, rescale_bound_ab)

        # Set to [0, 1] since exp(-inf) = 0 and exp(0) = 1.
        self.normalisation_min_score = 0
        self.normalisation_max_score = 1

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

        ppl_score: List = list(np.exp(np.divide(sentences_log_prob, sentences_len)))

        if self.do_normalization:
            ppl_score = self._normalize_scores(
                scores=ppl_score,
                x_min=self.normalisation_min_score,
                x_max=self.normalisation_max_score,
                a=self.normalisation_a_score,
                b=self.normalisation_b_score,
            )
        return ppl_score
