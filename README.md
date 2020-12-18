# libtxsize

This Python 3 library provides an easy interface to create estimates of the
size, the weigth, and the virtual size of different transaction input, output,
and witness types, as well as arbitrary transactions.

## Requirements

None.

## Structure

The following files are included:

    libtxsize.py            - Estimate logic and interfaces
    libtxsize-cli.py        - Simple command-line interface
    reference_data.py       - Reference data for validation

## Using the Python interface

The library includes the fuctions `input_est`, `output_est`, `witness_est`, and `tx_est`.

The first three are used to get size, virtual size, and weight estimates for a
particular input, output, or witness. To this end, the function is called with
the desired type.  The functions return a dict using the keys `size`, `vsize`,
and `weight` for the respetictive estimates.

Example:

    from libtxsize import output_est

    output_weight = output_est('P2PKH')['weight']

The forth function, `tx_est` can be used to get size, virtual size, and weight
estimates for arbitray transactions. The functions parameters are a list of
inputs and a list of outputs.  The functions return a dict that uses the keys
`inputs`, `witnesses`, `outputs`, `overhead` and `total` for estimates of
different parts of the transaction or the total transaction. Each of the values
in the dict, in turn, contains a dict using the keys `size`, `vsize`, and
`weight` for the respetictive estimates.


The following example demonstrates the use of the function to estimate the
combined weight of a transaction's inputs as well as the transactions total
size:

    from libtxsize import tx_est

    inputs = ['P2PKH', 'P2SH-2-of-3-multisig', 'P2WPKH']
    outputs = ['P2WSH-1-of-3-multisig', 'P2PK']

    inputs_weight = tx_est(inputs, outputs)['inputs']['weight']
    tx_size = tx_est(inputs, outputs)['total']['size']

## Using the command-line interface

The file `libtxsize-cli.py` provides a simple command-line interface for the library.
The following arguments are supported:

    -h, --help                  - Shows a help message
    -n, --notx                  - Only give estimates for the
                                  specified inputs and/or outputs
    -i list, --inputs list      - A comma-separated list of inputs
    -o list, --outputs list     - A comma-separated list of outputs
    -s, --sanity-check          - Run a sanity check

The following example demonstrates the CLI's use to get estimates only for a P2WPKH
input type:

    $ ./libtxsize-cli.py -i P2WPKH --notx
    +-----------------------------------+-------------+-------------+-------------+
    | Part/Metric                       |    size [B] | weight [WU] |  vsize [vB] |
    +-----------------------------------+-------------+-------------+-------------+
    | INPUTS                            |             |             |             |
    | 1. P2WPKH                         |          41 |         164 |          41 |
    +-----------------------------------+-------------+-------------+-------------+
    | WITNESSES                         |             |             |             |
    | 1. P2WPKH                         |         107 |         107 |       26.75 |
    +-----------------------------------+-------------+-------------+-------------+


The next example demonstrates the CLI's use to get estimates for a transaction
using a P2PKH, a P2WPKH, and P2SH-P2WSH-1-of-2-multisig input; and a P2TR as
well as a P2SH-2-of-3-multisig output:

    $ ./libtxsize-cli.py -i P2PKH,P2WPKH,P2SH-P2WSH-1-of-2-multisig -o P2TR,P2SH-2-of-3-multisig
    +-----------------------------------+-------------+-------------+-------------+
    | Part/Metric                       |    size [B] | weight [WU] |  vsize [vB] |
    +-----------------------------------+-------------+-------------+-------------+
    | INPUTS                            |             |             |             |
    | 1. P2PKH                          |         147 |         588 |         147 |
    | 2. P2WPKH                         |          41 |         164 |          41 |
    | 3. P2SH-P2WSH-1-of-2-multisig     |          76 |         304 |          76 |
    +-----------------------------------+-------------+-------------+-------------+
    | WITNESSES                         |             |             |             |
    | 1. P2PKH                          |         N/A |         N/A |         N/A |
    | 2. P2WPKH                         |         107 |         107 |       26.75 |
    | 3. P2SH-P2WSH-1-of-2-multisig     |         146 |         146 |        36.5 |
    +-----------------------------------+-------------+-------------+-------------+
    | OUTPUTS                           |             |             |             |
    | 1. P2TR                           |          43 |         172 |          43 |
    | 2. P2SH-2-of-3-multisig           |          32 |         128 |          32 |
    +-----------------------------------+-------------+-------------+-------------+
    | INPUT DATA                        |         264 |        1056 |         264 |
    | WITNESS DATA                      |         254 |         254 |        63.5 |
    | OUTPUT DATA                       |          75 |         300 |       18.75 |
    | TRANSACTION OVERHEAD              |          12 |          34 |         8.5 |
    +-----------------------------------+-------------+-------------+-------------+
    | TRANSACTION TOTAL                 |         605 |        1652 |       413.0 |
    +-----------------------------------+-------------+-------------+-------------+



## Validation

The command-line interface can be used to perform a validation using the
reference data provided in `reference_data.py`:

    ./libtxsize-cli.pi -s
