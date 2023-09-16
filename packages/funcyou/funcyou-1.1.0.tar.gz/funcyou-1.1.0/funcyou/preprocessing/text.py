import json
import re
from collections import Counter
from functools import cache, partial
from typing import Callable, Generator, List, Union

import pandas as pd

__all__ = [
    "contracations_dict",
    "text_cleaning",
    "IntegerVectorizer",
    "Vocabulary",
    "fix_contractions",
]
# with open('contractions.json') as f:
#    contractions_dict = json.load(f)


contractions_dict = {
    "i ain't": "i am not ",
    "you ain't": "you are not",
    "he ain't": "he is not",
    "she ain't": "she is not",
    "it ain't": "it is not",
    "they ain't": "they are not",
    "aren't": "are/am not",
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "didn`t": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he had / he would",
    "he'd've": "he would have",
    "he'll": "he shall / he will",
    "he'll've": "he shall have / he will have",
    "he's": "he has / he is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how has / how is / how does",
    "I'd": "I had / I would",
    "I'd've": "I would have",
    "I'll": "I shall / I will",
    "I'll've": "I shall have / I will have",
    "I'm": "I am",
    "I've": "I have",
    "isn't": "is not",
    "it'd": "it had / it would",
    "it'd've": "it would have",
    "it'll": "it shall / it will",
    "it'll've": "it shall have / it will have",
    "it's": "it has / it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she had / she would",
    "she'd've": "she would have",
    "she'll": "she shall / she will",
    "she'll've": "she shall have / she will have",
    "she's": "she has / she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so as / so is",
    "that'd": "that would / that had",
    "that'd've": "that would have",
    "that's": "that has / that is",
    "there'd": "there had / there would",
    "there'd've": "there would have",
    "there's": "there has / there is",
    "they'd": "they had / they would",
    "they'd've": "they would have",
    "they'll": "they shall / they will",
    "they'll've": "they shall have / they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we had / we would",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what shall / what will",
    "what'll've": "what shall have / what will have",
    "what're": "what are",
    "what's": "what has / what is",
    "what've": "what have",
    "when's": "when has / when is",
    "when've": "when have",
    "where'd": "where did",
    "where's": "where has / where is",
    "where've": "where have",
    "who'll": "who shall / who will",
    "who'll've": "who shall have / who will have",
    "who's": "who has / who is",
    "who've": "who have",
    "why's": "why has / why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you had / you would",
    "you'd've": "you would have",
    "you'll": "you shall / you will",
    "you'll've": "you shall have / you will have",
    "you're": "you are",
    "you've": "you have",
}


# very necessary function you can't tell differece between "’" and "'", I don't even have that symbol in my keyboard
def text_cleaning_apos(text):
    text = str(text)
    text = text.lower()
    return re.sub("’", "'", text)  # removing punctuation
    


# FUNCTIONS TO EXPAND CONTRACTIONS
def fix_contractions(x):
    x = str(x).lower()
    xsplited = x.split(" ")
    exp_sentence = []
    for s in x.split():
        if s in contractions_dict.keys():
            s = contractions_dict.get(s)
        exp_sentence.append(s)

    return " ".join(exp_sentence)


# Compile regex patterns for better performance
PUNCTUATION_REGEX = re.compile(r"[^a-zA-Z]")
SPECIAL_CHARACTERS_REGEX = re.compile(r"[#,@,&]")
DIGIT_REGEX = re.compile(r"\d+")
APOSTROPHE_S_REGEX = re.compile(r"'s")
WWW_REGEX = re.compile(r"w{3}")
URL_REGEX = re.compile(r"http\S+")
MULTIPLE_SPACES_REGEX = re.compile(r"\s+")
SINGLE_CHAR_REGEX = re.compile(r"\s+[a-zA-Z]\s+")


def text_cleaning(text):
    text = str(text)
    text = text.lower()
    text = PUNCTUATION_REGEX.sub(" ", text)  # Remove punctuation
    text = SPECIAL_CHARACTERS_REGEX.sub("", text)
    text = DIGIT_REGEX.sub("", text)
    text = APOSTROPHE_S_REGEX.sub("", text)
    text = WWW_REGEX.sub("", text)
    text = URL_REGEX.sub("", text)
    text = MULTIPLE_SPACES_REGEX.sub(" ", text)
    text = SINGLE_CHAR_REGEX.sub(" ", text)

    return text.strip()


from collections import Counter


class Vocabulary:
    def __init__(self, special_tokens: list[str, bytes] = None):
        """
        Initialize a Vocabulary object.

        Args:
            special_tokens (list of str or bytes, optional): A list of special tokens to include in the vocabulary.
        """
        self.word_to_idx = {}  # Mapping from words to indices
        self.idx_to_word = {}  # Mapping from indices to words
        self.counter = Counter()  # Counts the frequency of each word

        self.vocab_size = 0  # Total number of unique words in the vocabulary
        self.special_tokens = special_tokens  # List of special tokens to be added
        self.add_special_tokens(special_tokens)

    def add_special_tokens(self, special_tokens):
        """
        Add special tokens to the vocabulary.

        Args:
            special_tokens (list of str or bytes): A list of special tokens to add to the vocabulary.
        """
        if special_tokens is not None:
            for word in special_tokens:
                self.add_word_to_vocab(word)

    def build_vocab(self, tokenized_data, max_tokens, min_freq, reset=False):
        """
        Build the vocabulary from tokenized data.

        Args:
            tokenized_data (list of lists): Tokenized input data.
            max_tokens (int or None): Maximum number of tokens to include in the vocabulary. None for unlimited.
            min_freq (int): Minimum frequency required for a word to be included in the vocabulary.
            reset (bool, optional): Whether to reset the vocabulary before building it.

        """
        if reset:
            self.reset()
            self.add_special_tokens(self.special_tokens)

        for words in tokenized_data:
            self.counter.update(words)

        if max_tokens is not None:
            sorted_tokens = [word for word, _ in self.counter.most_common()]
            for word in sorted_tokens:
                if word not in self.word_to_idx:
                    self.add_word_to_vocab(word)

                if self.vocab_size == max_tokens:
                    break
        else:
            for word, freq in self.counter.items():
                if freq >= min_freq and word not in self.word_to_idx:
                    self.add_word_to_vocab(word)

    def add_word_to_vocab(self, word):
        """
        Add a word to the vocabulary.

        Args:
            word (str or bytes): The word to add to the vocabulary.
        """
        self.word_to_idx[word] = self.vocab_size
        self.idx_to_word[self.vocab_size] = word
        self.vocab_size += 1

    def add_to_dictionary(self, vocabulary):
        """
        Add words from another vocabulary to this vocabulary.

        Args:
            vocabulary (Vocabulary): Another Vocabulary object.
        """
        for word in vocabulary:
            if word not in self.word_to_idx:
                self.add_word_to_vocab(word)

    def reset(self):
        """
        Reset the vocabulary, clearing all word and index mappings.
        """
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.counter = Counter()
        self.vocab_size = 0

    def __call__(self, word):
        """
        Get the index of a word in the vocabulary.

        Args:
            word (str or bytes): The word to look up.

        Returns:
            int: The index of the word in the vocabulary.
        """
        return self.word_to_idx[word]

    def __len__(self):
        """
        Get the size of the vocabulary (number of unique words).

        Returns:
            int: The size of the vocabulary.
        """
        return self.vocab_size


class IntegerVectorizer:
    def __init__(
        self,
        tokenizer: Callable[[str], List[str]] = None,
        preprocessing_func: Callable[[str], str] = None,
        max_tokens=None,
        min_freq=1,
        special_tokens: List[str] = None,
        max_seq_length=None,
        pad_to_max=False,
        splitter=" ",  # Not required if tokenizer is passed
        vocabulary: set = None,
        encoding="utf-8",
    ):
        """
        Initialize an IntegerVectorizer object.

        Args:
            tokenizer (Callable[[str], List[str]], optional): A function for tokenizing input data.
            preprocessing_func (Callable[[str], str], optional): A function for preprocessing input data.
            max_tokens (int, optional): Maximum number of tokens to include in the vocabulary. None for unlimited.
            min_freq (int, optional): Minimum frequency required for a word to be included in the vocabulary.
            special_tokens (list of str, optional): A list of special tokens to include in the vocabulary.
            max_seq_length (int, optional): Maximum sequence length for data padding or truncation.
            pad_to_max (bool, optional): Whether to pad sequences to the maximum sequence length.
            splitter (str, optional): A string used for splitting sentences into words (not required if tokenizer is passed).
            vocabulary (set, optional): A set of words to initialize the vocabulary with.(adapt is not required if passed)
            encoding (str, optional): The character encoding to use for text processing.
        """
        self.min_freq = min_freq
        self.max_tokens = max_tokens
        self.max_seq_length = max_seq_length
        self.encoding = encoding
        print("Encoding: ", self.encoding)

        self.tokenizer = (
            partial(self.bytes_string_wrapper, tokenizer, encoding=encoding)
            if tokenizer
            else None
        )
        self.preprocessing_func = (
            partial(self.bytes_string_wrapper, preprocessing_func, encoding=encoding)
            if preprocessing_func
            else None
        )

        self.pad_to_max = pad_to_max

        self.UNK = "<UNK>".encode(self.encoding)
        self.PAD = "<PAD>".encode(self.encoding)
        self.splitter = splitter.encode(self.encoding)

        self.reserved_tokens = [self.PAD, self.UNK]

        if special_tokens:
            self.update_reserved_tokens(special_tokens)
            self.special_tokens = special_tokens

        self.vocab = Vocabulary(self.reserved_tokens)

        if vocabulary:
            vocabulary = [
                token.encode(self.encoding) if isinstance(token, str) else token
                for token in vocabulary
            ]
            self.vocab.add_to_dictionary(vocabulary)

        self.tokenized_data = []

        self.UNK_ID = self.vocab(self.UNK)
        self.PAD_ID = self.vocab(self.PAD)

    def update_reserved_tokens(self, special_tokens):
        """
        Update the reserved tokens with new special tokens.

        Args:
            special_tokens (list of str): A list of special tokens to add to the reserved tokens.
        """
        special_tokens = [
            token.encode(self.encoding) if isinstance(token, str) else token
            for token in special_tokens
        ]
        new_tokens = [
            token for token in special_tokens if token not in self.reserved_tokens
        ]
        new_tokens = self.reserved_tokens + new_tokens
        encoded_tokens = []

        for i in new_tokens:
            if isinstance(i, str):
                encoded_tokens.append(i.encode(self.encoding))
            elif isinstance(i, bytes):
                encoded_tokens.append(i)

        self.reserved_tokens = encoded_tokens
        print("Reserved tokens: ", self.reserved_tokens)

    def bytes_string_wrapper(self, func, *args, encoding):
        """
        Wrap a function to handle byte-encoded strings.

        Args:
            func (Callable): The function to wrap.
            *args: Arguments to pass to the function.
            encoding (str): The character encoding to use for text processing.

        Returns:
            bytes or List[bytes]: The result of the wrapped function.
        """
        encoded_args = [
            arg.decode(encoding) if isinstance(arg, bytes) else arg for arg in args
        ]
        result = func(*encoded_args)

        if isinstance(result, str):
            result = result.encode(encoding)
        elif isinstance(result, list) and all(isinstance(item, str) for item in result):
            result = [item.encode(encoding) for item in result]

        return result

    def adapt(self, data: List[str], reset: bool = False) -> None:
        """
        Build or rebuild the vocabulary based on the provided data.

        Args:
            data (list of str): The input data to build the vocabulary from.
            reset (bool, optional): Whether to reset the vocabulary before building it.
        """
        self.tokenized_data = self.tokenize_data_generator(data)
        self.vocab.build_vocab(
            self.tokenized_data, self.max_tokens, self.min_freq, reset=reset
        )
        print("Vocab size:", len(self.vocab))

    def __call__(self, data: List[str]):
        """
        Transform input data into integer sequences using the vocabulary.

        Args:
            data (list of str): The input data to transform.

        Returns:
            list of list of int: The transformed integer sequences.
        """
        return self.transform(data)

    def preprocess_sentence(self, sentence):
        """
        Preprocess a sentence by applying a preprocessing function.

        Args:
            sentence (str or bytes): The input sentence to preprocess.

        Returns:
            bytes: The preprocessed sentence.
        """
        if isinstance(sentence, str):
            sentence = sentence.encode(self.encoding)

        if not self.preprocessing_func:
            return sentence
        else:
            words = sentence.split()
            preprocessed_words = [
                self.preprocessing_func(word)
                if word not in self.special_tokens
                else word
                for word in words
            ]
            return b" ".join(preprocessed_words)

    def tokenize_data_generator(self, data):
        """
        Tokenize a generator of sentences.

        Args:
            data (generator): A generator yielding input sentences.

        Yields:
            list of str: Tokenized sentences.
        """
        for sentence in data:
            sentence = self.preprocess_sentence(sentence)
            yield self.tokenizer(sentence) if self.tokenizer else sentence.split(
                self.splitter
            )

    def adjust_sequence_length(self, sequence: Generator[int, None, None]) -> list[int]:
        """
        Adjust the length of a sequence by padding or truncating.

        Args:
            sequence (Generator[int, None, None]): A generator yielding integers.

        Returns:
            list of int: The adjusted sequence.
        """
        if self.max_seq_length is not None:
            if isinstance(sequence, Generator):
                sequence = list(sequence)

            if len(sequence) < self.max_seq_length:
                if self.pad_to_max:
                    sequence += [self.PAD_ID] * (self.max_seq_length - len(sequence))
            elif len(sequence) > self.max_seq_length:
                sequence = sequence[: self.max_seq_length]
            return sequence

    def transform(self, data: List[str]):
        """
        Transform input data into integer sequences using the vocabulary.

        Args:
            data (list of str): The input data to transform.

        Returns:
            list of list of int: The transformed integer sequences.
        """
        if not isinstance(data, list):
            raise TypeError("Input data must be a list")

        self.tokenized_data = self.tokenize_data_generator(data)
        vectorized_data = []
        for sentence in self.tokenized_data:
            vectorized_sentence = [
                self.vocab.word_to_idx.get(word, self.UNK_ID) for word in sentence
            ]
            vectorized_sentence = self.adjust_sequence_length(vectorized_sentence)
            vectorized_data.append(vectorized_sentence)
        return vectorized_data

    def reverse_transform(self, vectorized_data: list[list[int]]) -> list[str]:
        """
        Reverse transform integer sequences into original text.

        Args:
            vectorized_data (list of list of int): The integer sequences to reverse transform.

        Returns:
            list of str: The original text sentences.
        """
        original_data = []
        for vector in vectorized_data:
            sentence = [
                self.vocab.idx_to_word[idx] for idx in vector if idx != self.PAD_ID
            ]
            original_data.append(b" ".join(sentence).strip())
        return original_data

    def transform_generator(self, data: list[str]) -> Generator[list[int], None, None]:
        """
        Transform input data into integer sequences using the vocabulary, yielding sequences one at a time.

        Args:
            data (list of str): The input data to transform.

        Yields:
            list of int: The transformed integer sequences.
        """
        if not isinstance(data, list):
            raise TypeError("Input data must be a list of string(s)")

        self.tokenized_data = self.tokenize_data_generator(data)
        for sentence in self.tokenized_data:
            vectorized_sentence = (
                self.vocab.word_to_idx.get(word, self.UNK_ID) for word in sentence
            )
            vectorized_sentence = self.adjust_sequence_length(vectorized_sentence)
            yield list(
                vectorized_sentence
            )  # Convert the generator to a list for yielding

    def reverse_transform_generator(
        self, vectorized_data: list[list[int]]
    ) -> Generator[str, None, None]:
        """
        Reverse transform integer sequences into original text, yielding original text sentences one at a time.

        Args:
            vectorized_data (list of list of int): The integer sequences to reverse transform.

        Yields:
            str: The original text sentences.
        """
        for vector in vectorized_data:
            sentence = (
                self.vocab.idx_to_word[idx] for idx in vector if idx != self.PAD_ID
            )
            yield b" ".join(sentence).strip()

    def __len__(self):
        """
        Get the size of the vocabulary (number of unique words).

        Returns:
            int: The size of the vocabulary.
        """
        return len(self.vocab)


def main():
    ...


if __name__ == "__main__":
    main()
