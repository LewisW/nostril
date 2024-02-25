# Testing utilities.
# .............................................................................
import os

from nostril.nonsense_detector import _msg


def test_unlabeled(input, nonsense_tester, min_length=6, sense='valid',
                   trace_scores=False, save_to=None):
    '''Test against a file or list of strings.  'nonsense_tester' is a
    function that should return True if a given string is nonsense.  'sense'
    indicates whether each input string should be considerd to be a valid
    string, or not.  If value is 'valid', meaning the input strings are to be
    considered valid strings and not junk, then nonsense_detector(...) should
    report False for each one; if the input strings are not valid, then
    nonsense_detector(...) should report True for each one.  Input strings
    that are shorter than 'min_length' are skipped.  This function returns a
    tuple of totals and the time it took: (num_failures, num_successes,
    num_tested, num_skipped, elapsed_time) If the argument 'save_to' is not
    None, then it is assumed to be a filename and any and all stdout output
    will be redirected to the file.

    This returns a tuple of multiple values, as follows:
        number of true positives
        number of true negatives
        number of false positives
        number of false negatives
        number of cases skipped
        elapsed time

    The "positive" and "negative" here is taken from the perspective of
    labeling strings as nonsense if they are known to be nonsense.  Thus, a
    true positive is when something is known to be nonsense and Nostril
    labels it as nonsense; a true negative is when something is known to NOT
    be nonsense and Nostril does not label it as nonsense; a false positive
    is when something is known not to be nonsense but Nostril mistakenly
    labels it as nonsense; and so on.  Whether the inputs handed to this test
    function are valid strings or nonsense strings does not change the
    interpretation of positive or negative: a true positive always occurs
    when nonsense is labeled as nonsense.  If the strings given to this test
    function are all valid strings (sense='valid'), then this function will
    always return 0 true positives and 0 false negatives because there can be
    none in that case; conversely, if the inputs are all nonsense/invalid, then
    it will always return 0 true negatives and 0 false positives.
    '''
    from time import time
    from contextlib import redirect_stdout
    import humanize

    def run_tests(trace_scores):
        skipped = 0
        tp = 0  # true positives
        tn = 0  # true negatives
        fp = 0  # false positives
        fn = 0  # false negatives
        start = time()
        for text in id_list:
            try:
                junk = nonsense_tester(text, trace_scores)
                # This uses the fact that True == 1 in Python numeric contexts.
                if sense != 'valid':
                    # It's supposed to be nonsense.
                    tp += junk  # true positive
                    fn += not junk  # false negative
                else:
                    # It's not supposed to be nonsense.
                    tn += not junk  # true negative
                    fp += junk  # false positive
            except:
                skipped += 1

        elapsed_time = time() - start
        return (tp, tn, fp, fn, skipped, elapsed_time)

    def print_stats(tp, tn, fp, fn, skipped, elapsed_time):
        count = tp + tn + fp + fn
        total_tested = count
        accuracy = 100 * (tp + tn) / count
        fmeasure = 2 * tp / (2 * tp + fp + fn)
        _msg('{:.2f}% accuracy ({} tested in {:.2f}s, '
             '{} true pos, {} true neg, {} false pos, {} false neg, {} skipped)'
             .format(accuracy, humanize.intcomma(total_tested), elapsed_time,
                     humanize.intcomma(tp), humanize.intcomma(tn),
                     humanize.intcomma(fp), humanize.intcomma(fn),
                     humanize.intcomma(skipped)))

    if isinstance(input, list):
        id_list = input
    elif isinstance(input, str):
        # Assume the string is a file name
        file = os.path.join(os.getcwd(), input)
        with open(file, 'r') as f:
            id_list = f.read().splitlines()
    else:
        raise ValueError('First argument not understood: {}'.format(input))

    if save_to:
        with open(save_to, "w") as f:
            with redirect_stdout(f):
                (tp, tn, fp, fn, skipped, time) = run_tests(trace_scores=True)
        _msg('-' * 70)
        if trace_scores:
            print_stats(tp, tn, fp, fn, skipped, time)
        return (tp, tn, fp, fn, skipped, time)
    else:
        (tp, tn, fp, fn, skipped, time) = run_tests(trace_scores=trace_scores)
        if trace_scores:
            print_stats(tp, tn, fp, fn, skipped, time)
        return (tp, tn, fp, fn, skipped, time)


def test_labeled(input_file, nonsense_tester, min_length=6, trace_scores=False,
                 save_to=None):
    '''Test against a file containing labeled test cases.  'nonsense_tester'
    is a function that should return True if a given string is nonsense.
    Each line in the 'input_file' is assumed to contain two items separated
    by a comma: the letter 'y' or 'n', and then a string.  If an input string
    is labeled with 'y', it means it is a valid (not nonsense) string and
    nonsense_detector(...) should report False; if the input string labeled
    with 'n', it is not valid and nonsense_detector(...)  should report True.
    Input strings that are shorter than 'min_length' are skipped.
    This function returns a tuple of lists and totals and the time it took:
       (list_false_pos, list_false_neg, num_tested, num_skipped, elapsed_time)
    If the argument 'save_to' is not None, then it is assumed to be a
    filename and any and all stdout output will be redirected to the file.
    '''
    from time import time
    from contextlib import redirect_stdout
    import humanize

    labeled_as_nonsense = nonsense_tester

    def run_tests(filename, trace_scores):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            tp = 0
            tn = 0
            fp_list = []
            fn_list = []
            skipped = 0
            count = 0
            lines = f.readlines()
            start = time()
            for line in lines:
                column = line.strip().split(',')
                known_real = (column[0] == 'y')
                s = column[1]
                try:
                    count += 1
                    if known_real:
                        if labeled_as_nonsense(s, trace_scores):
                            fp_list.append(s)
                        else:
                            tn += 1
                    else:
                        if labeled_as_nonsense(s, trace_scores):
                            tp += 1
                        else:
                            fn_list.append(s)
                except:
                    skipped += 1
            elapsed_time = time() - start
            if trace_scores:
                fp = len(fp_list)
                fn = len(fn_list)
                precision = tp / (tp + fp)
                recall = tp / (tp + fn)
                _msg('{} tested in {:.2f}s, {} skipped -- '
                     '{:.2f}% precision, {:.2f}% recall, '
                     '{} true pos, {} true neg, {} false pos, {} false neg'
                     .format(humanize.intcomma(count), elapsed_time,
                             humanize.intcomma(skipped), 100 * precision, 100 * recall,
                             humanize.intcomma(tp), humanize.intcomma(tn),
                             humanize.intcomma(fp), humanize.intcomma(fn)))
            return (fp_list, fn_list, count, skipped, elapsed_time)

    if save_to:
        with open(save_to, "w") as f:
            with redirect_stdout(f):
                return run_tests(input_file, trace_scores=trace_scores)
    else:
        return run_tests(input_file, trace_scores=trace_scores)

# def tabulate_scores(string_list, ngram_freq, show=50, portion='all',
#                     order='descending', precomputed=None, doreturn=False):
#     from operator import itemgetter
#     from tabulate import tabulate
#     if precomputed:
#         sorted_scores = sorted(precomputed, key=itemgetter(1),
#                                reverse=not(order.startswith('ascend')))
#     else:
#         scores = []
#         ngram_length = len(next(iter(ngram_freq.keys())))
#         max_frequency = _highest_total_frequency(ngram_freq)
#         for s in string_list:
#             score = string_score(s, ngram_freq, ngram_length, max_frequency)
#             scores.append([s, score])
#         sorted_scores = sorted(scores, key=itemgetter(1),
#                                reverse=not(order.startswith('ascend')))
#     if isinstance(show, int):
#         if portion == 'all':
#             show_scores = sorted_scores[0::int(len(sorted_scores)/show)]
#         elif portion == 'top':
#             show_scores = sorted_scores[:show]
#         else:
#             show_scores = sorted_scores[-show:]
#     else:
#         show_scores = [s for s in sorted_scores if s[0] == show]
#     print('-'*70)
#     if isinstance(show, int):
#         print('Showing {} values sorted by {} column'.format(show, ordinal(1)))
#     print(tabulate(show_scores, tablefmt=format, headers=['String', 'score ']))
#     print('-'*70)
#     if doreturn:
#         return sorted_scores


# Module exports.
# .............................................................................

# nonsense = generate_nonsense_detector()


# -----------------------------------------------------------------------------
# Saving for history

# This approach of using substring matches is much, much slower than
# using a hash table of all possible n-grams and testing membership.
#
# def num_substring_matches(substr, string):
#     # Implementation based on http://stackoverflow.com/a/6844623/743730
#     return sum(string[i:].startswith(substr) for i in range(len(string)))
#
# def string_score(string, ngram_freq):
#     # Given the _ngram_values, calculate a score for the given string.
#     score = 0
#     for ngram, values in ngram_freq.items():
#         score += num_substring_matches(ngram, string) * values[2]
#     return score/len(string)

# Slower than version using sum() above
#
# def num_substring_matches(substr, string):
#     count = 0
#     for i in range(len(string)):
#         if string[i:].startswith(substr):
#             count += 1
#     return count

# def show_ngram_matches(string, ngram_freq):
#     # Lower-case the string and remove non-letter characters.
#     string = string.lower().translate(_delchars)
#     # Generate list of n-grams for the given string.
#     ngram_length = len(next(iter(ngram_freq.keys())))
#     string_ngrams = ngrams(string, ngram_length)
#     # Count up occurrences of each n-gram.
#     found = defaultdict(int)
#     for ngram in string_ngrams:
#         found[ngram] += 1
#     _msg('{} unique n-grams'.format(len(found)))
#     max_tf = _highest_total_frequency(ngram_freq)
#     for ng, count in found.items():
#         _msg('{}: {} x {} (max {}) score = {}'
#             .format(ng, count, ngram_freq[ng].idf, max_tf,
#                     ngram_freq[ng].idf * pow(count, 1.195) * (0.5 + 0.5*count/ngram_freq[ng].max_frequency)))
