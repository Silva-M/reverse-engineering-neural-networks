# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Synthetic Datasets."""

import numpy as np
from itertools import product
from renn import utils

__all__ = ['Unordered']

def constant_sampler(value):
  """Returns a sampling function which always returns the value 'value'"""

  def sample(num_samples):
    return np.full((num_samples, ), value)
  return sample

def uniform_sampler(min_val, max_val):
  """returns a sampling function which samples uniformly between min_val and
  max_val, inclusive"""

  def sample(num_samples):
    return np.random.randint(min_val, max_val+1, size=(num_samples,))
  return sample

def build_vocab(valences=None, num_classes=3):
  """ Builds the vocabulary
  Vocabulary for this dataset consists of tuples, e.g., ('very', 3),
    indicating in this case a token which provides strong evidence of class 3.
  The degree of evidence for each basic word is stored in the WORD_VALENCES
    dictionary
  """

  if valences is None:
    valences = {'very': 2, 'some': 1, 'neutral': 0, 'not': -1}

  words = product(valences, range(num_classes))

  def _score(word):
    """Converts a word like ('very', 1) to a
    vector-valued score, in this case (0,2,0,...)"""
    score = np.zeros(num_classes)
    score[word[1]] = valences[word[0]]
    return valence

  vocab = {i: _score(word) for i, word in enumerate(words)}
  return vocab

class Unordered:
  """Synthetic dataset representing un-ordered classes, to mimic e.g.
  text-classification datasets like AG News (unlike, say, star-prediction or
  sentiment analysis, which features ordered classes"""

  def __init__(self, num_classes=3, batch_size=64, length_sampler='Constant',
               sampler_params={'value': 40}):

    SAMPLERS = {'Constant': constant_sampler,
                'Uniform': uniform_sampler}

    self.num_classes = num_classes
    self.batch_size = batch_size

    if length_sampler in SAMPLERS.keys():
      self.sampler = SAMPLERS[length_sampler](**sampler_params)
    else:
      raise ValueError(f'length_sampler must be one of {SAMPLERS.keys()}')

    vocab = build_vocab(num_classes=num_classes)

  def __iter__(self):
    return self

  def __next__(self):
    """ Samples and returns a batch.  As with the real datasets,
    batch is a dictionary containing 'inputs', 'labels', and 'index' keys.
    'index' specifies the length of the sequence """
    lengths = self.sampler(num_samples=self.batch_size)
    max_length = max(lengths)

    batch = {'inputs': np.random.randint(len(self.vocab),
                                         size=(self.batch_size, max_length)),
             'index': lengths}

    batch['labels'] = self.label_batch(batch)

    return batch

  def label_batch(self, batch):
    """ Calculates class labels for a batch of sentences """
    zipped = zip(batch['inputs'], batch['index'])

    class_scores =  np.array([self.score(s, l) for s, l in zipped])
    return np.argmax(class_scores, axis=1)

  def score(self, sentence, length):
    """ Calculates the score, i.e. the amount of accumulated
    evidence in the sentence, for each class"""
    return sum([self.vocab[word] for word in sentence[:length]])

