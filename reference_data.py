#!/usr/bin/env python3

# Empirical data in line with http://virtu.llc/science/on-bitcoin-transaction-sizes/
REF_PARTS = {}
REF_PARTS['P2PK'] = {'input': {'size': 113, 'vsize': 113, 'weight': 452},
                     'witness': {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'},
                     'output': {'size': 44, 'vsize': 44, 'weight': 176}}
REF_PARTS['P2PKH'] = {'input': {'size': 147, 'vsize': 147, 'weight': 588},
                      'witness': {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'},
                      'output': {'size': 34, 'vsize': 34, 'weight': 136}}
REF_PARTS['1-of-2-MULTISIG'] = {'input': {'size': 114, 'vsize': 114, 'weight': 456},
                                'witness': {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'},
                                'output': {'size': 80, 'vsize': 80, 'weight': 320}}
REF_PARTS['1-of-3-MULTISIG'] = {'input': {'size': 114, 'vsize': 114, 'weight': 456},
                                 'witness': {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'},
                                 'output': {'size': 114, 'vsize': 114, 'weight': 456}}
REF_PARTS['NULLDATA-20'] = {'input': {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'},
                             'witness': {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'},
                             'output': {'size': 31, 'vsize': 31, 'weight': 124}}
REF_PARTS['NULLDATA-80'] = {'input': {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'},
                             'witness': {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'},
                             'output': {'size': 92, 'vsize': 92, 'weight': 368}}
REF_PARTS['P2SH-2-of-2-MULTISIG'] = {'input': {'size': 258, 'vsize': 258, 'weight': 1032},
                                     'witness': {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'},
                                     'output': {'size': 32, 'vsize': 32, 'weight': 128}}
REF_PARTS['P2SH-2-of-3-MULTISIG'] = {'input': {'size': 293, 'vsize': 293, 'weight': 1172},
                                     'witness': {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'},
                                     'output': {'size': 32, 'vsize': 32, 'weight': 128}}
REF_PARTS['P2SH-P2WSH-2-of-2-MULTISIG'] = {'input': {'size': 76, 'vsize': 76, 'weight': 304},
                                           'witness': {'size': 218, 'vsize': 54.5, 'weight': 218},
                                           'output': {'size': 32, 'vsize': 32, 'weight': 128}}
REF_PARTS['P2SH-P2WSH-2-of-3-MULTISIG'] = {'input': {'size': 76, 'vsize': 76, 'weight': 304},
                                           'witness': {'size': 252, 'vsize': 63, 'weight': 252},
                                           'output': {'size': 32, 'vsize': 32, 'weight': 128}}
REF_PARTS['P2SH-P2WPKH'] = {'input': {'size': 64, 'vsize': 64, 'weight': 256},
                            'witness': {'size': 107, 'vsize': 26.75, 'weight': 107},
                            'output': {'size': 32, 'vsize': 32, 'weight': 128}}
REF_PARTS['P2WPKH'] = {'input': {'size': 41, 'vsize': 41, 'weight': 164},
                       'witness': {'size': 107, 'vsize': 26.75, 'weight': 107},
                       'output': {'size': 31, 'vsize': 31, 'weight': 124}}
REF_PARTS['P2WSH-1-of-1-MULTISIG'] = {'input': {'size': 41, 'vsize': 41, 'weight': 164},
                                      'witness': {'size': 112, 'vsize': 28, 'weight': 112},
                                      'output': {'size': 43, 'vsize': 43, 'weight': 172}}
REF_PARTS['P2WSH-2-of-2-MULTISIG'] = {'input': {'size': 41, 'vsize': 41, 'weight': 164},
                                      'witness': {'size': 218, 'vsize': 54.5, 'weight': 218},
                                      'output': {'size': 43, 'vsize': 43, 'weight': 172}}
REF_PARTS['P2WSH-2-of-3-MULTISIG'] = {'input': {'size': 41, 'vsize': 41, 'weight': 164},
                                      'witness': {'size': 252, 'vsize': 63, 'weight': 252},
                                      'output': {'size': 43, 'vsize': 43, 'weight': 172}}
REF_PARTS['P2TR-keypath'] = {'input': {'size': 41, 'vsize': 41, 'weight': 164},
                             'witness': {'size': 66, 'vsize': 16.5, 'weight': 66},
                             'output': {'size': 43, 'vsize': 43, 'weight': 172}}

# reference size and weight from bitcoin core for listed transaction ids.
# vsize is weight from bitcoin core divided by four *without* rounding up!
REF_TXS = {}
REF_TXS['c7b96650f7d12f442ed017b166583486afff7390d5d6dbbe35ed4ca1ef50c930'] = \
    {'inputs': ['P2PKH'],
     'outputs': ['P2PKH', 'P2PKH', 'NULLDATA-20'],
     'reference': {'size': 256, 'weight': 1024, 'vsize': 256}}
REF_TXS['cafee3cf4697040c35ec0f3bd3778e47c569bd4afbdc81f179be9333a1c67afb'] = \
    {'inputs': ['P2WPKH'],
     'outputs': ['P2WPKH', 'P2WPKH'],
     'reference': {'size': 222, 'weight': 561, 'vsize': 561/4}}
REF_TXS['a070eda356c87a7af9bff22eab3b3c38460605eb00938c84a86a1d6d3c608078'] = \
    {'inputs': ['P2PKH', 'P2SH-P2WPKH'],
     'outputs': ['P2PKH', 'P2PKH'],
     'reference': {'size': 399, 'weight': 1266, 'vsize': 1266/4}}
