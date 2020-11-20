#!/usr/bin/env python3

import re

TX_OVERHEAD     = 4 + 4         # 4-byte version, 4-byte locktime
SEGWIT_OVERHEAD = 2             # 1-byte segwit marker and 1-byte segwit flag
INPUT_OVERHEAD  = 32 + 4 + 4    # 32-byte txid, 4-byte pos, and 4-byte seq. no
OUTPUT_OVERHEAD = 8             # 8-byte amount
ECDSA_SIG       = 71            # cf. http://virtu.llc/science/on-bitcoin-script-and-witness-sizes/
ECDSA_PUBKEY    = 33            # cf. http://virtu.llc/science/on-bitcoin-script-and-witness-sizes/
SCHNORR_SIG     = 64            # cf. http://virtu.llc/science/on-bitcoin-script-and-witness-sizes/
SCHNORR_PUBKEY  = 32            # cf. http://virtu.llc/science/on-bitcoins-schnorr-signature-algorithm-and-taproot-script-and-witness-sizes/

def varint(num_bytes):
    if num_bytes < 0xFD:
        return 1
    if num_bytes <= 0xFFFF:
        return 1+2
    if num_bytes <= 0xFFFFFFFF:
        return 1+4
    if num_bytes <= 0xFFFFFFFFFFFFFFFF:
        return 1+8
    raise ValueError(f'{num_bytes} exceeds maximum size of 2^64')

def length(num_bytes):
    if 0 <= num_bytes < 75:
        # direct encoding
        return 1
    if 76 <= num_bytes < (2**(1*8))-1:
        # OP_PUSHDATA1
        return 1+1
    if 2**(1*8) <= num_bytes < (2**(2*8))-1:
        # OP_PUSHDATA2
        return 1+2
    if 2**(2*8) <= num_bytes < (2**(4*8))-1:
        # OP_PUSHDATA4
        return 1+4

    raise ValueError(f'{num_bytes} not in supported range from 0 to 2^64-1')

def witness(data):
    if data['txout_type'] == 'P2WPKH':
        # 0x02 <itemlen> <sig> <len> <pubkey>
        return 1 + varint(ECDSA_SIG) + ECDSA_SIG + varint(ECDSA_PUBKEY) + ECDSA_PUBKEY

    if data['txout_type'] == 'P2WSH-MULTISIG':
        # general: <nitems> <input> <itemlen> <witness script>
        # here: <input> is the same as a MULTISIG script_sig; and
        # <witness script> is the same as a MULTISIG script_pubkey
        helper = {'txout_type': 'MULTISIG', 'm': data['m'], 'n': data['n']}
        input_data = script_sig(helper)
        witness_script = script_pubkey(helper)
        num_items = 1 + (data['m'] * 2) + 2
        return varint(num_items) + input_data + varint(witness_script) + witness_script

    if data['txout_type'] == 'P2SH-P2WSH-MULTISIG':
        # general: <nitems> <input> <itemlen> <witness script>
        # here: <input> uses slightly different encoding than bare multisig
        # <input> is <itemlen> <itemlen> <sig 1> ... <itemlen> <sig m>,
        # with the first itemlen=0, to push an empty string onto the witness
        # stack (same as OP_0 in bare multisig).
        input_data = 1 + data['m'] * (varint(ECDSA_SIG) + ECDSA_SIG)
        # <witness script> is the same as a MULTISIG script_pubkey
        helper = {'txout_type': 'MULTISIG', 'm': data['m'], 'n': data['n']}
        witness_script = script_pubkey(helper)
        num_items = 1 + (data['m'] * 2) + 2
        return varint(num_items) + input_data + varint(witness_script) + witness_script

    if data['txout_type'] == 'P2SH-P2WPKH':
        # fixed: <nitems (0x02)> <itemlen> <ECDSA sig> <itemlen> <ECDSA pubkey>
        return varint(2) + varint(ECDSA_SIG) + ECDSA_SIG + varint(ECDSA_PUBKEY) + ECDSA_PUBKEY

    if data['txout_type'] == 'P2TR':
        if data['path'] == 'key':
            # 0x01 <itemlen> <Schnorr sig>
            return 1 + varint(SCHNORR_SIG) + SCHNORR_SIG
        if data['path'] == 'script':
            raise NotImplementedError(f'P2TR script path not supported')
        raise NotImplementedError(f'unknown P2TR path: {data["path"]}')

    if data['txout_type'] in ('P2PK', 'P2PKH', 'MULTISIG', 'P2SH-MULTISIG'):
        # proof in script_sig, so no witness
        raise ValueError('txout type data["txout_type"] has no witness')

    if data['txout_type'] == 'NULLDATA':
        raise ValueError('no script_sig for txout type NULLDATA')

    raise NotImplementedError(f'unsupported txout type: {data["txout_type"]}')

def script_pubkey(data):
    if data['txout_type'] == 'P2PK':
        # <len> <ECDSA pubkey> OP_CHECKSIG
        return length(ECDSA_PUBKEY) + ECDSA_PUBKEY + 1

    if data['txout_type'] == 'P2PKH':
        # OP_DUP OP_HASH160 0x14 <20-byte hash> OP_EQUALVERIFY OP_CHECKSIG
        return 1 + 1 + 1 + 20 + 1 + 1

    if data['txout_type'] == 'MULTISIG':
        # OP_m <len> <ECDSA pubkey 1> ... <len> <ECDSA pubkey n> OP_n OP_CHECKMULTISIG
        return 1 + (length(ECDSA_PUBKEY) + ECDSA_PUBKEY) * data['n'] + 1 + 1

    if data['txout_type'] in ('P2SH', 'P2SH-MULTISIG', 'P2SH-P2WSH-MULTISIG', 'P2SH-P2WPKH'):
        # OP_HASH160 0x14 <20-byte hash> OP_EQUAL
        return 1 + 1 + 20 + 1

    if data['txout_type'] == 'NULLDATA':
        # general: OP_RETURN <len> <data> [... <len> <data>]
        # here: assume only one data item
        return 1 + length(data['payload']) + data['payload']

    if data['txout_type'] == 'P2WPKH':
        # OP_0 0x14 <20-byte hash>
        return 1 + 1 + 20

    if data['txout_type'] in ('P2WSH', 'P2WSH-MULTISIG'):
        # OP_0 0x20 <32-byte hash>
        return 1 + 1 + 32

    if data['txout_type'] == 'P2TR':
        # OP_1 <len> <Schnorr pubkey>
        return 1 + length(SCHNORR_PUBKEY) + SCHNORR_PUBKEY

    raise NotImplementedError(f'unsupported txout type: {data["txout_type"]}')

def script_sig(data):
    if data['txout_type'] == 'P2PK':
        # <len> <ECDSA sig>
        return length(ECDSA_SIG) + ECDSA_SIG

    if data['txout_type'] == 'P2PKH':
        # <len> <ECDSA sig> <len> <ECDSA pubkey>
        return length(ECDSA_SIG) + ECDSA_SIG + length(ECDSA_PUBKEY) + ECDSA_PUBKEY

    if data['txout_type'] == 'MULTISIG':
        # OP_0 <len> <ECDSA sig 1> ... <len> <ECDSA sig m>
        return 1 + data['m'] * (length(ECDSA_SIG) + ECDSA_SIG)

    if data['txout_type'] == 'P2SH-MULTISIG':
        # general: <input> <len> <redeem script>
        # here: <input> is the same as a MULTISIG script_sig; and
        # <redeem script> is the same as a MULTISIG script_pubkey
        helper = {'txout_type': 'MULTISIG', 'm': data['m'], 'n': data['n']}
        input_data = script_sig(helper)
        redeem_script = script_pubkey(helper)
        return input_data + length(redeem_script) + redeem_script

    if data['txout_type'] == 'P2SH-P2WSH-MULTISIG':
        # general: <input> <len> <redeem script>
        # here: <input> in witness; redeem script is OP_0 0x20 <32-byte hash>
        redeem_script = 1 + 1 + 32
        return length(redeem_script) + redeem_script

    if data['txout_type'] == 'P2SH-P2WPKH':
        # general: <input> <len> <redeem script>
        # here: <input> in witness; redeem script is OP_0 0x16 <20-byte hash>
        redeem_script = 1 + 1 + 20
        return length(redeem_script) + redeem_script

    if data['txout_type'] in ['P2WPKH', 'P2WSH-MULTISIG', 'P2TR']:
        # proof is in witness, so empty script
        return 0

    if data['txout_type'] == 'NULLDATA':
        raise ValueError('no script_sig for txout type NULLDATA')

    raise NotImplementedError(f'unsupported txout type: {data["txout_type"]}')

def multisig_check(m, n, max):
    if not 1 <= m <= max:
        raise ValueError('m = {m} (requirement is 1 <= m <= {max})')
    if not 1 <= n <= max:
        raise ValueError('n = {n} (requirement is 1 <= n <= {max})')

def parse(txout_type):
    # Bare multi-signature
    if re.match('^\d+-(?i)(of)-\d+-(?i)(Multisig)$', txout_type):
        m, n = int(txout_type.split('-')[0]), int(txout_type.split('-')[2])
        multisig_check(m, n, 3)
        return {'txout_type': 'MULTISIG', 'm': m, 'n': n}

    # P2SH multi-signature
    if re.match('^(?i)(P2SH)-\d+-(?i)(of)-\d+-(?i)(Multisig)$', txout_type):
        m, n = int(txout_type.split('-')[1]), int(txout_type.split('-')[3])
        multisig_check(m, n, 16)
        return {'txout_type': 'P2SH-MULTISIG', 'm': m, 'n': n}

    # P2SH-P2WSH multi-signature
    if re.match('^(?i)(P2SH)-(?i)(P2WSH)-\d+-(?i)(of)-\d+-(?i)(Multisig)$', txout_type):
        m, n = int(txout_type.split('-')[2]), int(txout_type.split('-')[4])
        multisig_check(m, n, 16)
        return {'txout_type': 'P2SH-P2WSH-MULTISIG', 'm': m, 'n': n}

    # P2WSH multi-signature
    if re.match('^(?i)(P2WSH)-\d+-(?i)(of)-\d+-(?i)(Multisig)$', txout_type):
        m, n = int(txout_type.split('-')[1]), int(txout_type.split('-')[3])
        multisig_check(m, n, 16)
        return {'txout_type': 'P2WSH-MULTISIG', 'm': m, 'n': n}

    # NULLDATA
    if re.match('^(?i)(NULLDATA)-\d+$', txout_type):
        payload = int(txout_type.split('-')[1])
        if not 0 <= payload <= 80:
            raise ValueError('payload = {payload} (requirement: 1 <= payload <= 80)')
        return {'txout_type': 'NULLDATA', 'payload': payload}

    # P2TR
    if re.match('^(?i)(P2TR)-(?i)(keypath|scriptpath)+$', txout_type):
        path = txout_type.split('-')[1].lower()[:-4]
        return {'txout_type': 'P2TR', 'path': path}

    # Remaining txout_types, no m and n
    return {'txout_type': txout_type}

def input_est(txout_type):
    data = parse(txout_type)
    try:
        script_size = script_sig(data)
        input_size = varint(script_size) + script_size + INPUT_OVERHEAD
        return {'size': input_size, 'vsize': input_size, 'weight': input_size*4}
    except ValueError:
        return {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'}

def output_est(txout_type):
    data = parse(txout_type)
    try:
        script_size = script_pubkey(data)
        output_size = varint(script_size) + script_size + OUTPUT_OVERHEAD
        return {'size': output_size, 'vsize': output_size, 'weight': output_size*4}
    except ValueError:
        return {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'}

def witness_est(txout_type):
    data = parse(txout_type)
    try:
        witness_size = witness(data)
        return {'size': witness_size, 'vsize': witness_size/4, 'weight': witness_size}
    except ValueError:
        return {'size': 'N/A', 'vsize': 'N/A', 'weight': 'N/A'}

def tx_est(inputs, outputs):
    input_bytes = sum([input_est(i)['size'] for i in inputs])
    witness_bytes = sum([(witness_est(i)['size'] if witness_est(i)['size'] != 'N/A' else 0) for i in inputs])
    output_bytes = sum([output_est(o)['size'] for o in outputs])
    # add extra byte(s) to signal lack of witness data for inputs using no
    # witnesses in case of segwit transactions
    if witness_bytes > 0:
        witness_bytes += sum([1 if witness_est(i)['size'] == 'N/A' else 0 for i in inputs])


    legacy_size = TX_OVERHEAD
    legacy_size += varint(len(inputs)) + input_bytes
    legacy_size += varint(len(outputs)) + output_bytes
    witness_size = (witness_bytes + SEGWIT_OVERHEAD) if witness_bytes > 0 else 0

    size = legacy_size + witness_size
    weight = 4 * legacy_size + witness_size
    vsize = weight / 4

    overhead_bytes = TX_OVERHEAD + varint(len(inputs)) + varint(len(outputs)) + (SEGWIT_OVERHEAD if witness_bytes > 0 else 0)
    overhead_weight = 4*TX_OVERHEAD + (SEGWIT_OVERHEAD if witness_bytes > 0 else 0)

    return {'total': {'size': size, 'weight': weight, 'vsize': vsize},
            'inputs': {'size': input_bytes, 'weight': input_bytes*4, 'vsize': input_bytes},
            'witnesses': {'size': witness_bytes, 'weight': witness_bytes, 'vsize': witness_bytes/4},
            'outputs': {'size': output_bytes, 'weight': output_bytes*4, 'vsize': output_bytes/4},
            'overhead': {'size': overhead_bytes, 'weight': overhead_weight, 'vsize': overhead_weight/4}
            }
