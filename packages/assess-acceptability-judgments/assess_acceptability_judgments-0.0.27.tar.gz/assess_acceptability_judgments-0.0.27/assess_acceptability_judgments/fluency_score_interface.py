# To fix Torch and Pylint error
# pylint: disable=no-name-in-module

from abc import abstractmethod, ABC
from typing import Tuple, List

import numpy as np
import torch
from nltk import word_tokenize, WhitespaceTokenizer
from torch import LongTensor, FloatTensor, Tensor, softmax
from transformers import AutoTokenizer, AutoModelForMaskedLM


class LanguageModelFluencyScoreInterface(ABC):
    def __init__(
        self,
        language_model: str,
        device: str = "cuda",
        tokenizer: str = "treebank",
        do_normalization: bool = True,
        rescale_bound_ab: Tuple = (0, 1),
    ):
        """

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

            # About tokenizing
            Since we want to leverage recent progress in language modelling (LM) with large language model (LLM) (i.e.
            GPT-like architecture), some adjustment in the potential tokenizing approach has to be made. None of the
            above articles properly define how sentences are tokenized. We hypothesize that two approaches could have
            been
            used to do so: whitespace tokenization or Treebank tokenizer. The first uses whitespace as word
            separation, while the latter uses regular expressions to split words. While recent LLM mostly uses
            either sentencepiece or a similar approach that works with subword unit and byte-pair encoding. Thus, two
            options are available to try to reproduce results using a possible approach, namely, not a sentencepiece
            one.

            The first option, one can use a look-a-like 'whitespace' tokenizer for LLM using the `add_prefix_space`
            (see here for an example
            https://huggingface.co/docs/transformers/model_doc/gpt2#transformers.GPT2Tokenizer) as
            a tokenizing approach. This option is called ``"whitespace_llm"``.

            The second option, we first split the sentence using either NLTK Treebank or whitespace tokenizer before
            using the LLM model pre-trained tokenizer as a mapping matrix using ``convert_tokens_to_ids``.
            These options are call ``"treebank"`` or ``"whitespace"``.
        """

        self.language_model = language_model
        self.do_normalization = do_normalization

        add_prefix_space = self._tokenizer_factory(tokenizer=tokenizer)

        self.model = AutoModelForMaskedLM.from_pretrained(language_model)
        self._model_max_input_size = self.model.config.max_position_embeddings

        self.llm_tokenizer = AutoTokenizer.from_pretrained(
            language_model, add_prefix_space=add_prefix_space, model_max_length=self._model_max_input_size
        )

        self.model.eval()
        self.device = device
        self.model.to(device)

        self.normalisation_a_score = rescale_bound_ab[0]
        self.normalisation_b_score = rescale_bound_ab[1]

    @abstractmethod
    def compute_score(self, sentences: List[str]) -> List[float]:
        pass

    def _llm_batch_processing(self, sentences: List[str]) -> Tuple[List, List[Tensor], Tensor]:
        """
        Processes in batch of a list of sentence. It add padding to the tokenize sequence and process it using a
        LLM to generate the batch logits.
        """
        padded_sentences_words_idx, sentences_mask = self.tokenize_sentence(sentences)
        padded_sentences_words_idx = padded_sentences_words_idx.to(self.device)
        sentences_mask = sentences_mask.to(self.device)

        with torch.no_grad():
            # We set the label as the words idx since we want to get the logits at each step to compute
            # the sentence probability.
            # Logits is of dimension batch_size, sentence length, vocabulary size
            batch_logits = self.model(
                padded_sentences_words_idx,
                labels=padded_sentences_words_idx,
                attention_mask=sentences_mask,
            )[1]

        return padded_sentences_words_idx, sentences_mask, batch_logits

    @staticmethod
    def _compute_sentences_len(sentences_mask: List[Tensor]) -> List[int]:
        """
        To compute the len of a sequence using the mask.
        """
        # |S| in equation (1) of article https://arxiv.org/pdf/1809.08731v1.pdf
        sentences_len: List[int] = [sentence_mask.sum().item() for sentence_mask in sentences_mask]
        return sentences_len

    @staticmethod
    def _compute_pm(
        padded_sentences_words_idx: List[List[int]],
        sentences_mask: List[Tensor],
        batch_logits: Tensor,
        sentences_len: List[int],
    ) -> List[float]:
        """
        To compute the sentence probability we use a similar approach as this implementation
        https://github.com/sgondala/GoogleConceptualCaptioning/commit/981e1b61ca5f84052f6237402319714d7fe70b80
        """

        batch_size = len(sentences_len)

        sentences_log_prob: List[float] = [0.0] * batch_size
        for batch_index in range(batch_size):
            for word_position_in_sentence, word_index in enumerate(padded_sentences_words_idx[batch_index]):
                if sentences_mask[batch_index][word_position_in_sentence]:
                    # We extract the logits at position word_position_in_sentence.
                    # Namely, the prediction of the LLM over all the vocabulary
                    predicted_logits = batch_logits[batch_index][word_position_in_sentence]

                    # We transpose the logits into a probability space (i.e. [0, 1])
                    predicted_prob = softmax(predicted_logits, dim=0)

                    # We accumulate the sum of the log since the equation is the log of a product.
                    sentences_log_prob[batch_index] += np.log(predicted_prob[word_index].item())
        return sentences_log_prob

    def _llm_tokenizing(self, sentences: List[str]) -> Tuple[LongTensor, FloatTensor]:
        """
        Tokenize and add padding of a batch of sentences using a LLM tokenizer.
        """
        batch_encoding = self.llm_tokenizer([sentence.lower() for sentence in sentences], padding="longest")
        return LongTensor(batch_encoding.data.get("input_ids")), FloatTensor(batch_encoding.data.get("attention_mask"))

    def _nltk_tokenizing(self, sentences: List[str]) -> Tuple[LongTensor, FloatTensor]:
        """
        Tokenize and add padding of a batch of sentences using a NLTK tokenizer.
        """
        padding_value: int = 0

        tokenize_sentences = []
        for sentence in sentences:
            tokenize_sentence = self.llm_tokenizer.convert_tokens_to_ids(
                self.word_tokenizer(sentence.lower())[: self._model_max_input_size]
            )
            tokenize_sentences.append(tokenize_sentence)

        longest_sentence = max((len(tokenize_sentence) for tokenize_sentence in tokenize_sentences))
        padded_tokenize_sentences = []
        sentences_mask = []
        for tokenize_sentence in tokenize_sentences:
            padded_tokenize_sentence = tokenize_sentence + [padding_value] * (longest_sentence - len(tokenize_sentence))
            padded_tokenize_sentences.append(padded_tokenize_sentence)
            mask = [1] * len(tokenize_sentence) + [0] * (longest_sentence - len(tokenize_sentence))
            sentences_mask.append(mask)

        return LongTensor(padded_tokenize_sentences), FloatTensor(sentences_mask)

    def _tokenizer_factory(self, tokenizer: str) -> bool:
        if tokenizer.lower() == "treebank":
            self.word_tokenizer = word_tokenize
            self.tokenize_sentence = self._nltk_tokenizing
            add_prefix_space = True
        elif tokenizer.lower() == "whitespace":
            self.word_tokenizer = WhitespaceTokenizer().tokenize
            self.tokenize_sentence = self._nltk_tokenizing
            add_prefix_space = True
        elif tokenizer.lower() == "whitespace_llm":
            self.tokenize_sentence = self._llm_tokenizing
            add_prefix_space = True
        elif tokenizer.lower() == "wordpiece":
            self.tokenize_sentence = self._llm_tokenizing
            add_prefix_space = False
        else:
            raise ValueError(
                f"The tokenizer '{tokenizer}' is not supported. Valid options are: 'treebank', "
                f"'whitespace' and 'whitespace_llm'."
            )
        return add_prefix_space

    @staticmethod
    def _normalize_scores(scores: List[float], x_min: int, x_max: int, a: int, b: int) -> List[float]:
        """
        Normalize a list of score in [x_min, x_max] bound into [a, b] bound using linear interpolation
        (or min-max normalisation technique).

        :param scores: (float) the scores to normalize.
        :param x_min: (int) the minimum value to use for interpolation, namely the previous lower bound.
        :param x_max: (int) the maximum value to use for interpolation, namely the previous upper bound.
        :param a: (int) the new lower bound.
        :param b: (int) the new upper bound.

        :return: (float) the normalize score.
        """
        scores = np.minimum(scores, x_max)
        scores = np.maximum(scores, x_min)

        scores = a + ((scores - x_min) * (b - a)) / (x_max - x_min)
        return list(scores)
