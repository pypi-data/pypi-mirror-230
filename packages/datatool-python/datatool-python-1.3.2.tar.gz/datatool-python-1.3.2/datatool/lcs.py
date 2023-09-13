"""
There is an implementation of the longest common subsequence algorithm:
https://en.wikipedia.org/wiki/Longest_common_subsequence_problem
Particularly, it can be used to calculate Levenshtein distance
between the strings.
"""

def lcs_solve_length(lst1, lst2):
    """
    Finds the length of the longest common subsequence of the given lists.
    """
    n1 = len(lst1)
    n2 = len(lst2)

    row = [0 for _ in range(n1)]
    for i2 in range(n2):
        row_p = row[:]
        for i1 in range(n1):
            if lst1[i1] == lst2[i2]:
                row[i1] = (row_p[i1 - 1] if i1 > 0 else 0) + 1
            else:
                row[i1] = max(row[i1 - 1] if i1 > 0 else 0, row_p[i1])

    return row[-1]


def lcs_solve(lst1, lst2):
    """
    Finds longest common subsequence of the given lists.
    """
    n1 = len(lst1)
    n2 = len(lst2)

    row = [[] for _ in range(n1)]
    for i2 in range(n2):
        row_p = row[:]
        for i1 in range(n1):
            if lst1[i1] == lst2[i2]:
                row[i1] = (row_p[i1 - 1] if i1 > 0 else []) + [lst1[i1]]
            else:
                row[i1] = max(
                    row[i1 - 1] if i1 > 0 else [],
                    row_p[i1],
                    key=len
                )

    return row[-1]
