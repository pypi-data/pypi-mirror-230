import fugashi

from natsume.openjtalk import text_to_mecab


NAISTJDIC_KEYS = ['pos', 'pos_group1', 'pos_group2', 'pos_group3',
                  'ctype', 'cform', 'orig', 'read', 'pron', 'acc_mora_size', 'chain_rule']


class MecabTagger(object):
    """A wrapper around fugashi (a cython wrapper around MeCab)
    """

    def __init__(self, dicdir):
        """Initialize tagger
        """
        self.tagger = fugashi.GenericTagger("-d {}".format(dicdir))
        self.dic_keys = NAISTJDIC_KEYS  # NOTE: currently only supports naist-jdic format

    def parse(self, text):
        features_list = self.parse_nbest(text, num=1)

        return features_list[0]

    def parse_nbest(self, text, num=1):
        """Parse intput text into words.
        """

        text = text_to_mecab(text)
        features_list = []
        results_list = self.tagger.nbestToNodeList(text, num=num)
        for results in results_list:
            # 每个lattice  
            features = []
            for result in results:
                # lattice中的分词结果
                feature = {
                    "surface": result.surface,
                }
                for i, key in enumerate(self.dic_keys):
                    try:
                        feature[key] = result.feature[i]
                    except IndexError:
                        feature[key] = "*"

                features.append(feature)
            features_list.append(features)

        return features_list

