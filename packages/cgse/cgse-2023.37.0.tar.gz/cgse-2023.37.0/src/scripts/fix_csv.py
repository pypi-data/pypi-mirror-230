"""
Small script to fix some problems with CSV files.

All the functions are written for a specific problem, you might need to run the script for
several functions to fix different problems.

Synopsis:

   $ python3 fix_csv.py original_input.csv out.csv --function newlines
   $ python3 fix_csv.py out.csv out2.csv --function vbar

"""
def fix_newlines_in_fields(input_file, output_file, delimiter: str = ','):
    """
    Sometimes we have seen that a field contains a newline character (usually due to an error
    in processing the response from a device where the trailing newline was not removed). This
    function tries to fix that problem.

    Args:
        input_file: the original CSV file where the problem occurs
        output_file: the file with the fixed lines
        delimiter: the delimiter that is used for the CSV [default=',']

    Returns:
        None.
    """

    with open(input_file, 'r') as fd:
        lines = fd.read().split('\n')
        fixed_lines = []
        prev_line = None

        for line in lines:
            if prev_line is None:
                # We assume the first row in the CSV file has the correct number of fields
                expected_num_delimiters = line.count(delimiter)
                prev_line = line
            elif prev_line.count(delimiter) < expected_num_delimiters:
                prev_line += line
            else:
                fixed_lines.append(prev_line)
                prev_line = line

        if prev_line is not None:
            fixed_lines.append(prev_line)

    with open(output_file, 'w', newline='\n') as fd:
        fd.writelines([f"{x}\n" for x in fixed_lines])

def fix_vertical_bar(input_file, output_file, delimiter: str = ','):
    """Removes all vertical bar '|' characters from the file."""

    with open(input_file, 'r') as fd:
        lines = fd.read().split('\n')
        fixed_lines = [line.replace('|', '') for line in lines]

    with open(output_file, 'w', newline='\n') as fd:
        fd.writelines([f"{x}\n" for x in fixed_lines])


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description="Script to fix several CSV issues")

    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("output_file", help="Path to the output file")

    parser.add_argument('--function', default='newlines', choices=('newlines', 'vbar'),
                        help="Function to apply to the input file. Default: 'newlines'")

    args = parser.parse_args()

    if args.function == "newlines":
        fix_newlines_in_fields(args.input_file, args.output_file)
    elif args.function == "vbar":
        fix_vertical_bar(args.input_file, args.output_file)
    else:
        print(f"Invalid function argument given: {args.function}.")
