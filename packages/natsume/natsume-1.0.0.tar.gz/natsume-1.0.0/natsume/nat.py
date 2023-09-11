from .frontend import Frontend
from .utils import (
    features_to_tokens, tokens_to_phonemes, convert_fonts
)

class Natsume(object):
    """A wrapper around natsume frontend
    """
    def __init__(self, dict_name=None):
        self._frontend = Frontend(dict_name=dict_name)
        self._g2p_modes = ["romaji", "ipa"]
        self._token_modes = ["word", "phrase"]
        self._models = ["rule", "marine"]

    def tokenize(self, text, mode="word", model="rule"):
        """Tokenize text into tokens
        """
        tokens_list = self.tokenize_nbest(text, mode=mode, model=model, num=1)

        return tokens_list[0]
    
    def tokenize_nbest(self, text, mode="word", model="rule", num=1):
        """Tokenize text into tokens, returning the best N candidates
        """
        if mode not in self._token_modes:
            raise ValueError(
                "Invalid mode for tokenization. Expected {}, got {} instead."
                .format(", ".join(self._token_modes), mode)
            )

        if model not in self._models:
            raise ValueError(
                "Invalid model for tokenization. Expected {}, got {} instead."
                .format(", ".join(self._models), model)
            )
        
        features_list = self._frontend.get_features_nbest(text, mode=mode, model=model, num=num)
        tokens_list = []
        for features in features_list:
            tokens = features_to_tokens(features, mode=mode)
            tokens_list.append(tokens)

        return tokens_list


    def g2p(self, text, phoneme_mode="romaji", token_mode="word", with_accent=False, model="rule"):
        """Grapheme-to-phoneme conversion
        """
        phonemes_list = self.g2p_nbest(text, phoneme_mode=phoneme_mode, token_mode=token_mode, 
                                       with_accent=with_accent, model=model, num=1)
        
        return phonemes_list[0]

    def g2p_nbest(self, text, phoneme_mode="romaji", token_mode="word", with_accent=False, model="rule", num=1):
        """Grapheme-to-phoneme conversion, returning the best N candidates
        """
        if phoneme_mode not in self._g2p_modes:
            raise ValueError(
                "Invalid mode for g2p. Expected {}, got {} instead."
                .format(", ".join(self._g2p_modes), phoneme_mode)
            )

        tokens_list = self.tokenize_nbest(text, mode=token_mode, model=model, num=num)
        phonemes_list = []
        for tokens in tokens_list:
            phonemes = tokens_to_phonemes(tokens, mode=phoneme_mode, with_accent=with_accent)
            phonemes_list.append(phonemes)

        return phonemes_list


    def convert_fonts(self, text, reverse=False):
        """Convert between new fonts and old fonts
        """
        text = convert_fonts(text, reverse=reverse)

        return text
    
    def get_mecab_features(self, text):
        """Get raw MeCab features
        """
        features_list = self.get_mecab_features_nbest(text, num=1)
        
        return features_list[0]
    
    def get_mecab_features_nbest(self, text, num=1):
        """Get raw MeCab features, returning the best N candidates
        """
        features_list = self._frontend.get_mecab_features_nbest(text, num=num)

        return features_list


    def get_njd_features(self, text):
        """Get raw NJD features
        """
        features_list = self.get_njd_features_nbest(text, num=1)

        return features_list[0]

    def get_njd_features_nbest(self, text, num=1):
        """Get raw NJD features, returning the best N candidates
        """
        features_list = self._frontend.get_njd_features_nbest(text, num=num)
        
        return features_list

    def set_dict_dir(self, dict_dir):
        # TODO: support mannualy setting dictionary directory
        raise NotImplementedError("Method 'set_dict_dir' is not implemented yet.")


