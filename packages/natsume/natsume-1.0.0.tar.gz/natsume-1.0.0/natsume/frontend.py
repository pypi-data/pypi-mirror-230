import os
import pkg_resources
import six
import json

if six.PY2:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve

import tarfile

from .mecab import MecabTagger
from .njd import NJDPredictor
from .utils import MecabFeature, NJDFeature, merge_njd_marine_features, feature_to_string


GLOBAL_CONFIG = {
    "dict_urls": {
        "naist-jdic": "https://github.com/faruzan0820/natsume/releases/download/naist-jdic/naist-jdic.tar.gz",
        "naist-jdic-tdmelodic": "https://github.com/faruzan0820/natsume/releases/download/naist-jdic-tdmelodic/naist-jdic-tdmelodic.tar.gz"
    }
}

class Frontend(object):
    def __init__(self, dict_name=None):
        self._dict_name = dict_name
        self._tagger = None     # mecab tagger
        self._njd = None        # njd predictor
        self._marine = None     # marine predictor
        self._dm = None         # dictionary manager

        self._initialize()

    def _initialize(self):
        self._njd = NJDPredictor()
        self._dm = DictManager()

        # Initialize marine
        # Reference: https://github.com/r9y9/pyopenjtalk/blob/master/pyopenjtalk/__init__.py
        try:
            from marine.predict import Predictor as MarinePredictor
        except BaseException:
            raise ImportError(
                "marine is not installed! Please see {} for more information."
                .format("https://github.com/6gsn/marine")
            )
        
        self._marine = MarinePredictor()
        dict_dir = self._dm.get_dict_dir(self._dict_name)
        self._tagger = MecabTagger(dicdir=dict_dir)

    def set_dict_dir(self, dict_dir):
        self._dict_dir = dict_dir
        self._initialize()

    def get_features(self, text, mode="word", model="rule"):
        features_list = self.get_features_nbest(text, mode=mode, model=model, num=1)
        
        return features_list[0]

    def get_features_nbest(self, text, mode="word", model="rule", num=1):
        features_list = []
        if mode == "word":
            raw_features_list = self.get_mecab_features_nbest(text, num=num)
            for raw_features in raw_features_list:
                # for every lattice
                features = []
                for raw_feature in raw_features:
                    feature = MecabFeature(raw_feature)
                    features.append(feature)
                features_list.append(features)

        elif mode == "phrase":
            if model == "rule":
                # default is rule-based model
                raw_features_list = self.get_njd_features_nbest(text, num=num)
            elif model == "marine":
                # accent sandhi estimation using marine
                from marine.utils.openjtalk_util import convert_njd_feature_to_marine_feature

                raw_features_list = []
                njd_features_list = self.get_njd_features_nbest(text, num=num)
                for njd_features in njd_features_list:
                    marine_features = convert_njd_feature_to_marine_feature(njd_features)
                    marine_results = self._marine.predict(
                        [marine_features], require_open_jtalk_format=True
                    )
                    raw_features = merge_njd_marine_features(njd_features, marine_results)
                    raw_features_list.append(raw_features)
            else:
                # default is rule-based model
                raw_features_list = self.get_njd_features_nbest(text, num=num)

            # raw feature to njd feature
            for raw_features in raw_features_list:
                features = []
                for raw_feature in raw_features:
                    print(raw_feature)
                    feature = NJDFeature(raw_feature)
                    features.append(feature)
                features_list.append(features)

        return features_list

    def get_mecab_features(self, text):
        features = self._tagger.parse(text)

        return features
    
    def get_mecab_features_nbest(self, text, num=1):
        features_list = self._tagger.parse_nbest(text, num)

        return features_list
    
    def get_njd_features(self, text):
        features_list = self.get_njd_features_nbest(text, num=1)

        return features_list[0]

    def get_njd_features_nbest(self, text, num=1):
        mecab_features_list = self._tagger.parse_nbest(text, num=num)
        features_list = []
        for mecab_features in mecab_features_list:
            feature_strings = []
            for mecab_feature in mecab_features:
                feature_string = feature_to_string(mecab_feature)
                feature_strings.append(feature_string)
            features = self._njd.predict(feature_strings)
            features_list.append(features)

        return features_list


# Reference: https://github.com/r9y9/pyopenjtalk/blob/master/pyopenjtalk/__init__.py    
class DictManager(object):
    def __init__(self):
        self._config_path = pkg_resources.resource_filename(__name__, "config.json")   # hardcode
        self._config = self.load_config()
        self._dict_dir = self._config["dict_dir"]

    def get_dict_dir(self, dict_name=None):
        if dict_name is None:
            # use most recently used dict download a default dict
            if self.check_dict_dir(self._dict_dir):
                # most recently used dict is availabel
                return self._dict_dir
            
            default_dict_name = list(GLOBAL_CONFIG["dict_urls"].keys())[0]
            default_dict_dir = pkg_resources.resource_filename(__name__, default_dict_name)
            if self.check_dict_dir(default_dict_dir):
                self._config["dict_name"] = default_dict_name
                self._config["dict_dir"] = default_dict_dir
                self.save_config()
                return default_dict_dir
            
            # download naist-jdic as default dictionary
            print("No dictionary available, download {}.".format(default_dict_name))
            dict_dir = self.download_dict(default_dict_name)
        
        else:
            if dict_name not in GLOBAL_CONFIG["dict_urls"].keys():
                raise ValueError("No such dictionary available. Expected {}."
                                .format(", ".join(list(GLOBAL_CONFIG["dict_urls"].keys()))))

            dict_dir = pkg_resources.resource_filename(__name__, dict_name)
            if not self.check_dict_dir(dict_dir):
                # not available, download one
                print("{} is not available, download one.".format(dict_name))
                self.download_dict(dict_name)

        return dict_dir

    @staticmethod
    def check_dict_dir(dict_dir):
        if os.path.exists(dict_dir) and os.path.isdir(dict_dir):
            return True
        return False
    
    def download_dict(self, dict_name):
        if dict_name not in GLOBAL_CONFIG["dict_urls"].keys():
            raise ValueError("No such dictionary available. Expected {}."
                            .format(", ".join(list(GLOBAL_CONFIG["dict_urls"].keys()))))
        
        dict_url = GLOBAL_CONFIG["dict_urls"][dict_name]
        self._config["dict_name"] = dict_name

        # TODO: add a progress bar
        filename = pkg_resources.resource_filename(__name__, "dic.tar.gz")
        print("Downloading dictionary from {}...".format(dict_url))
        urlretrieve(dict_url, filename)

        print("Extracting tar file {}...".format(filename))
        with tarfile.open(filename, mode="r|gz") as f:
            f.extractall(path=pkg_resources.resource_filename(__name__, ""))

        dict_dir = pkg_resources.resource_filename(__name__, dict_name)
        self._config["dict_dir"] = dict_dir
        self.save_config()
        os.remove(filename)
        print("Successfully downloaded {} to {}.".format(dict_name, dict_dir))

        return dict_dir
    
    def create_config(self):
        config = {
            "dict_name": "",
            "dict_dir": ""
        }
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)

        return config

    def load_config(self):
        if not os.path.exists(self._config_path):
            config = self.create_config()
        else:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

        return config
    
    def save_config(self):
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f)
