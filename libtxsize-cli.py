#!/usr/bin/env python3
import argparse
import sys
from libtxsize import tx_est, input_est, output_est, witness_est

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--notx', action='store_true', help='Estimates for individual inputs/outputs')
    parser.add_argument('-i', '--inputs', type=str, required=False, default=None, action='store', help='Comma-separated list of inputs')
    parser.add_argument('-o', '--outputs', type=str, required=False, default=None, action='store', help='Comma-separated list of outputs')
    parser.add_argument('-s', '--sanity-check', action='store_true', help='Run sanity check')
    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_usage()
        return 1

    if args.sanity_check:
        sanity_check()
        return

    if not args.notx and (not args.inputs or not args.outputs):
        raise ValueError('Transaction estimates require at least one input '
                         'and one output.')

    if not args.inputs and not args.outputs:
        raise ValueError('Estimates for individual inputs/outputs require'
                         'at least one input or output')

    args.inputs = [item for item in args.inputs.split(',')] if args.inputs else []
    args.outputs = [item for item in args.outputs.split(',')] if args.outputs else []

    print_estimate(args.inputs, args.outputs, args.notx)

def print_estimate(inputs, outputs, notx):
    table_sep()
    table('Part/Metric', {'size': 'size [B]', 'weight': 'weight [WU]', 'vsize': 'vsize [vB]'})
    table_sep()

    if inputs:
        table('INPUTS', {'size': '', 'weight': '', 'vsize': ''})
        for num, i in enumerate(inputs, 1):
            table(f'{num}. {i}', input_est(i))
        table_sep()

        table('WITNESSES', {'size': '', 'weight': '', 'vsize': ''})
        for num, i in enumerate(inputs, 1):
            table(f'{num}. {i}', witness_est(i))
        table_sep()

    if outputs:
        table('OUTPUTS', {'size': '', 'weight': '', 'vsize': ''})
        for num, i in enumerate(outputs, 1):
            table(f'{num}. {i}', output_est(i))
        table_sep()

    if not notx:
        res = tx_est(inputs, outputs)
        table('INPUT DATA', res['inputs'])
        table('WITNESS DATA', res['witnesses'])
        table('OUTPUT DATA', res['outputs'])
        table('TRANSACTION OVERHEAD', res['overhead'])
        table_sep()
        table('TRANSACTION TOTAL', res['total'])
        table_sep()

def table_sep():
    print('+' + '-'*(33+2) + '+' + '-'*(11+2) + '+' + '-'*(11+2) + '+' + '-'*(11+2) + '+')

def table(label, data):
    print(f'| {label:<33} | {data["size"]:>11} | {data["weight"]:>11} '
          f'| {data["vsize"]:>11} |')

def sanity_check():
    from reference_data import REF_PARTS
    for txout_type in REF_PARTS:
        estimate = {'output': output_est(txout_type),
                    'input': input_est(txout_type),
                    'witness': witness_est(txout_type)}
        for metric in estimate:
            if estimate[metric] != REF_PARTS[txout_type][metric]:
                raise AssertionError(f'{txout_type} {metric} estimate '
                                     f'does match reference value (estimate: '
                                     f'{estimate[metric]} reference: '
                                     f'{REF_PARTS[txout_type][metric]})')

    from reference_data import REF_TXS
    for tx in REF_TXS:
        estimate = tx_est(REF_TXS[tx]['inputs'], REF_TXS[tx]['outputs'])['total']
        for metric in estimate:
            if estimate[metric] != REF_TXS[tx]['reference'][metric]:
                raise AssertionError(f'tx {tx}: {metric} estimate '
                                     f'does match reference value (estimate: '
                                     f'{estimate[metric]} reference: '
                                     f'{REF_TXS[tx]["reference"][metric]})')

    print('Sanity check successful.')

if __name__ == '__main__':
    main()
