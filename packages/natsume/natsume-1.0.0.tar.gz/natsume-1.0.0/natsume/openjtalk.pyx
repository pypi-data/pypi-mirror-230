# coding: utf-8
# cython: boundscheck=True, wraparound=True
# cython: c_string_type=unicode, c_string_encoding=ascii

import numpy as np

cimport numpy as np
np.import_array()

cimport cython
from libc.stdlib cimport calloc, free
from libc.string cimport strdup, strlen
from cpython.bytes cimport PyBytes_FromStringAndSize

from .openjtalk.njd cimport NJD, NJD_initialize, NJD_refresh, NJD_print, NJD_clear
from .openjtalk cimport njd as _njd
from .openjtalk.text2mecab cimport text2mecab
from .openjtalk.mecab2njd cimport mecab2njd

cdef njd_node_get_string(_njd.NJDNode* node):
    return (<bytes>(_njd.NJDNode_get_string(node))).decode("utf-8")

cdef njd_node_get_pos(_njd.NJDNode* node):
    return (<bytes>(_njd.NJDNode_get_pos(node))).decode("utf-8")

cdef njd_node_get_pos_group1(_njd.NJDNode* node):
    return (<bytes>(_njd.NJDNode_get_pos_group1(node))).decode("utf-8")

cdef njd_node_get_pos_group2(_njd.NJDNode* node):
    return (<bytes>(_njd.NJDNode_get_pos_group2(node))).decode("utf-8")

cdef njd_node_get_pos_group3(_njd.NJDNode* node):
    return (<bytes>(_njd.NJDNode_get_pos_group3(node))).decode("utf-8")

cdef njd_node_get_ctype(_njd.NJDNode* node):
    return (<bytes>(_njd.NJDNode_get_ctype(node))).decode("utf-8")

cdef njd_node_get_cform(_njd.NJDNode* node):
    return (<bytes>(_njd.NJDNode_get_cform(node))).decode("utf-8")

cdef njd_node_get_orig(_njd.NJDNode* node):
    return (<bytes>(_njd.NJDNode_get_orig(node))).decode("utf-8")

cdef njd_node_get_read(_njd.NJDNode* node):
    return (<bytes>(_njd.NJDNode_get_read(node))).decode("utf-8")

cdef njd_node_get_pron(_njd.NJDNode* node):
    return (<bytes>(_njd.NJDNode_get_pron(node))).decode("utf-8")

cdef njd_node_get_acc(_njd.NJDNode* node):
    return _njd.NJDNode_get_acc(node)

cdef njd_node_get_mora_size(_njd.NJDNode* node):
    return _njd.NJDNode_get_mora_size(node)

cdef njd_node_get_chain_rule(_njd.NJDNode* node):
    return (<bytes>(_njd.NJDNode_get_chain_rule(node))).decode("utf-8")

cdef njd_node_get_chain_flag(_njd.NJDNode* node):
      return _njd.NJDNode_get_chain_flag(node)


cdef node2feature(_njd.NJDNode* node):
  return {
    "string": njd_node_get_string(node),
    "pos": njd_node_get_pos(node),
    "pos_group1": njd_node_get_pos_group1(node),
    "pos_group2": njd_node_get_pos_group2(node),
    "pos_group3": njd_node_get_pos_group3(node),
    "ctype": njd_node_get_ctype(node),
    "cform": njd_node_get_cform(node),
    "orig": njd_node_get_orig(node),
    "read": njd_node_get_read(node),
    "pron": njd_node_get_pron(node),
    "acc": njd_node_get_acc(node),
    "mora_size": njd_node_get_mora_size(node),
    "chain_rule": njd_node_get_chain_rule(node),
    "chain_flag": njd_node_get_chain_flag(node),
  }


cdef njd2feature(_njd.NJD* njd):
    cdef _njd.NJDNode* node = njd.head
    features = []
    while node is not NULL:
      features.append(node2feature(node))
      node = node.next
    return features

cdef feature2njd(_njd.NJD* njd, features):
    cdef _njd.NJDNode* node

    for feature_node in features:
        node = <_njd.NJDNode *> calloc(1, sizeof(_njd.NJDNode))
        _njd.NJDNode_initialize(node)
        # set values
        _njd.NJDNode_set_string(node, feature_node["string"].encode("utf-8"))
        _njd.NJDNode_set_pos(node, feature_node["pos"].encode("utf-8"))
        _njd.NJDNode_set_pos_group1(node, feature_node["pos_group1"].encode("utf-8"))
        _njd.NJDNode_set_pos_group2(node, feature_node["pos_group2"].encode("utf-8"))
        _njd.NJDNode_set_pos_group3(node, feature_node["pos_group3"].encode("utf-8"))
        _njd.NJDNode_set_ctype(node, feature_node["ctype"].encode("utf-8"))
        _njd.NJDNode_set_cform(node, feature_node["cform"].encode("utf-8"))
        _njd.NJDNode_set_orig(node, feature_node["orig"].encode("utf-8"))
        _njd.NJDNode_set_read(node, feature_node["read"].encode("utf-8"))
        _njd.NJDNode_set_pron(node, feature_node["pron"].encode("utf-8"))
        _njd.NJDNode_set_acc(node, feature_node["acc"])
        _njd.NJDNode_set_mora_size(node, feature_node["mora_size"])
        _njd.NJDNode_set_chain_rule(node, feature_node["chain_rule"].encode("utf-8"))
        _njd.NJDNode_set_chain_flag(node, feature_node["chain_flag"])
        _njd.NJD_push_node(njd, node)

def text_to_mecab(text):
    cdef char buff [8192]

    if isinstance(text, str):
        text = text.encode("utf-8")
    text2mecab(buff, text)
    text = PyBytes_FromStringAndSize(buff, strlen(buff))
    text = text.decode("utf-8")

    return text

cdef class NJDRules(object):
    """NJD rule-based accent sandhi estimation
    """
    cdef NJD* njd

    def __cinit__(self):
        self.njd = new NJD()
        NJD_initialize(self.njd)

    def _clear(self):
      NJD_clear(self.njd)


    def predict(self, feature_strings):
        """Run njd pipeline
        """
        size = len(feature_strings)
        # see mecab.cpp
        cdef char** feature = <char**> calloc(size, sizeof(char*))
        for i, feature_string in enumerate(feature_strings):
            # cdef string f = string(feature_string)
            # feature[i] = strdup(feature_string.c_str())
            feature[i] = strdup(feature_string.encode("utf-8"))
        mecab2njd(self.njd, feature, size)
        # feature2njd(self.njd, features)
        _njd.njd_set_pronunciation(self.njd)
        _njd.njd_set_digit(self.njd)
        _njd.njd_set_accent_phrase(self.njd)
        _njd.njd_set_accent_type(self.njd)
        _njd.njd_set_unvoiced_vowel(self.njd)
        _njd.njd_set_long_vowel(self.njd)
        features = njd2feature(self.njd)

        NJD_refresh(self.njd)
        # TODO: better refresh
        for i in range(size):
            free(feature[i])
        free(feature)

        return features

    def set_pronunciation(self, features):
        """Set pronunciation for njd features
        """
        feature2njd(self.njd, features)
        _njd.njd_set_pronunciation(self.njd)
        features = njd2feature(self.njd)
        NJD_refresh(self.njd)

        return features


    def set_digit(self, features):
        """Set digit for njd features
        """
        feature2njd(self.njd, features)
        _njd.njd_set_digit(self.njd)
        features = njd2feature(self.njd)
        NJD_refresh(self.njd)

        return features

    def set_accent_phrase(self, features):
        feature2njd(self.njd, features)
        _njd.njd_set_accent_phrase(self.njd)
        features = njd2feature(self.njd)
        NJD_refresh(self.njd)

        return features

    def set_accent_type(self, features):
        feature2njd(self.njd, features)
        _njd.njd_set_accent_type(self.njd)
        features = njd2feature(self.njd)
        NJD_refresh(self.njd)

        return features

    def set_unvoiced_vowel(self, features):
        feature2njd(self.njd, features)
        _njd.njd_set_unvoiced_vowel(self.njd)
        features = njd2feature(self.njd)
        NJD_refresh(self.njd)

        return features

    def set_long_vowel(self, features):
        feature2njd(self.njd, features)
        _njd.njd_set_long_vowel(self.njd)
        features = njd2feature(self.njd)
        NJD_refresh(self.njd)

        return features

    def __dealloc__(self):
        self._clear()
        del self.njd
