## UglyGrep: Simple Text Search Utility

### Overview

UglyGrep is a desktop application that enables you to perform text searches within multiple files in a directory. Built using Python and PyQt6, it provides an easy-to-use graphical interface for entering search patterns and locating matches across text files with a specified extension.

### Features

- Folder and file extension based search.
- Text pattern matching using the Boyer-Moore search algorithm.
- View the found text in a viewer with the search pattern highlighted.
- Display of the line number, file name, and path for each match.
- Real-time update of matches, file count, and elapsed time.

### Requirements

- Python 3.8
-  6.5.1

### How to Use

1. **Installation**: You can install it using pip.
    ```
    pip install uglygrep
    ```

2. **Launch the Application**: Run the `uglygrep` file to launch UglyGrep.

3. **Select Folder**: Enter the folder directory where you want to perform the search in the 'Starting Directory' field, or click the 'Open Folder' button to browse and select a directory.

4. **File Extension**: Enter the file extension in the 'File Extension' field to filter the search to files of that type. For example, enter `*.txt` for text files.

5. **Enter Search Pattern**: Type the text pattern you wish to search for in the 'Search Pattern' field.

6. **Search**: Click the 'Search' button to initiate the search process. A dialog box will appear indicating that the search is in progress. You can cancel the search by clicking the 'Cancel' button.

7. **View Results**: Once the search is complete, you'll see a table with the line numbers, filenames, and paths where the text pattern was found. Double-click a row to open a viewer that displays the file content with the search pattern highlighted.

8. **Telemetry**: Observe the number of matches, the number of files scanned, and the time elapsed in the labels at the bottom of the window.

### Known Issues

- The application is intended for text-based files and may not work correctly for binary files or exceptionally large files.

### Future Enhancements

- Support for regular expressions.
- More efficient text pattern matching.
- Advanced sorting and filtering options for the result table.



# Boyer-Moore String Search Algorithm

The Boyer-Moore string search algorithm is an efficient string searching (substring searching) algorithm that skips sections of the text to be searched, resulting in a lower number of overall character comparisons. The algorithm pre-processes the pattern string to create two different tables: the Bad Character Table and the Good Suffix Table.

For a detailed explanation and the history of the algorithm, you can refer to its [Wikipedia page](https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-search_algorithm).

## Files
- `uglygrep.py`: The main Python file containing the implementation of the Boyer-Moore algorithm.

## Usage
You can use the `BoyerMooreSearch` class to find the position of the first occurrence of a pattern string within a text string.

```python
from uglygrep import BoyerMooreSearch

pattern = "example"
text = "This is an example text for example."

searcher = BoyerMooreSearch(pattern)
position = searcher.search(text)
print(f"The pattern was found at position {position}.")
```

## Explanation

### 1. Bad Character Heuristic

The Bad Character Heuristic calculates how far to jump when a mismatch is found. This jump is determined based on the rightmost occurrence of the mismatched character in the pattern string.

#### Example
Let's say the pattern is `"example"` and the text is `"This is an example text for example."`.

When a mismatch is found at character 'x' in the text and character 'a' in the pattern, the Bad Character Heuristic would look for the rightmost occurrence of 'x' in the pattern. If it is found, we calculate how far to jump by subtracting the index of that occurrence from the last index of the pattern. In our example, 'x' occurs at index 1 of the pattern, so the jump would be `6 - 1 = 5`.

### 2. Good Suffix Heuristic

The Good Suffix Heuristic comes into play when we have a good suffix in the text that matches with the suffix of the pattern. The algorithm pre-computes shifts for all possible good suffixes in the pattern string.

#### Example
Consider the pattern `"civic"` and the text `"This civic model is better than the previous civic car."`

If a mismatch occurs at character 'v' in the text and character 'i' in the pattern, we have a good suffix "ic" in the text that matches with the pattern. The algorithm uses this information to decide how far to jump.

### 3. Search Algorithm

The `search()` method combines both heuristics to find the starting index of the first occurrence of the pattern in the text.

### Disclaimer

UglyGrep is a simple text search utility. Use it at your own risk. The developers are not responsible for any loss of data or other issues.

### License

GPLv3 License

