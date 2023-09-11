import os
import pkg_resources
import six
import json

if six.PY2:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve

import tarfile

from .openjtalk import NJDRules


class NJDPredictor(object):
    def __init__(self):
        self._njd = NJDRules()

    def predict(self, feature_strings):
        features = self._njd.predict(feature_strings)

        return features

    def set_pronunciation(self, features):
        features = self._njd.set_pronunciation(features)

        return features

    def set_digit(self, features):
        features = self._njd.set_digit(features)

        return features

    def set_accent_phrase(self, features):
        features = self._njd.set_accent_phrase(features)

        return features

    def set_accent_type(self, features):
        features = self._njd.set_accent_type(features)

        return features

    def set_unvoiced_vowel(self, features):
        features = self._njd.set_unvoiced_vowel(features)

        return features

    def set_long_vowel(self, features):
        features = self._njd.set_long_vowel(features)

        return features