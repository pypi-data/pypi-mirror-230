# Find duplicates in multiple lists and return their indices and values.

## Tested against Windows 10 / Python 3.10 / Anaconda

### pip install duplicateindexer


Find duplicates in multiple lists and return their indices and values.

This function takes multiple lists as input and finds the common elements among them.
It then returns a list of dictionaries, where each dictionary corresponds to a common element.
Each dictionary contains keys for the input lists (0, 1, 2, ...), and the values are nested dictionaries.
These nested dictionaries have keys 'indices' and 'value', which represent the indices of the common
element in the input lists and the values of that common element in the input lists, respectively.



```python

Args:
	*args: Multiple lists containing elements to be compared.

Returns:
	List of dictionaries, where each dictionary represents a common element and its indices and values
	in the input lists.

Examples:
	>>> aa = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
	>>> bb = [
	...     [1, 2, 3],
	...     [4, 5, 6],
	...     [7, 8, 9],
	...     [10, 11, 12],
	...     [13, 14, 15],
	...     [1, 2, 3],
	...     [4, 5, 6],
	...     [7, 8, 9],
	...     [10, 11, 12],
	...     [13, 14, 15],
	... ]
	>>> l = find_duplicates_in_multiple_lists(aa, bb)
	>>> print(l)
	[
		{
			0: {
				0: {'indices': [1], 'value': [4, 5, 6]},
				1: {'indices': [1, 6], 'value': [4, 5, 6]}
			}
		},
		{
			1: {
				0: {'indices': [0], 'value': [1, 2, 3]},
				1: {'indices': [0, 5], 'value': [1, 2, 3]}
			}
		},
		{
			2: {
				0: {'indices': [2], 'value': [7, 8, 9]},
				1: {'indices': [2, 7], 'value': [7, 8, 9]}
			}
		},
		{
			3: {
				0: {'indices': [3], 'value': [10, 11, 12]},
				1: {'indices': [3, 8], 'value': [10, 11, 12]}
			}
		}
	]

	>>> cc = list(range(1, 20))
	>>> dd = list(range(11, 30))
	>>> l1 = find_duplicates_in_multiple_lists(cc, dd)
	>>> print(l1)
	[
		{0: {0: {'indices': [10], 'value': 11}, 1: {'indices': [0], 'value': 11}}},
		{1: {0: {'indices': [11], 'value': 12}, 1: {'indices': [1], 'value': 12}}},
		{2: {0: {'indices': [12], 'value': 13}, 1: {'indices': [2], 'value': 13}}},
		{3: {0: {'indices': [13], 'value': 14}, 1: {'indices': [3], 'value': 14}}},
		{4: {0: {'indices': [14], 'value': 15}, 1: {'indices': [4], 'value': 15}}},
		{5: {0: {'indices': [15], 'value': 16}, 1: {'indices': [5], 'value': 16}}},
		{6: {0: {'indices': [16], 'value': 17}, 1: {'indices': [6], 'value': 17}}},
		{7: {0: {'indices': [17], 'value': 18}, 1: {'indices': [7], 'value': 18}}},
		{8: {0: {'indices': [18], 'value': 19}, 1: {'indices': [8], 'value': 19}}}
	]
```