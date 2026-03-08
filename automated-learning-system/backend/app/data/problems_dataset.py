"""
100-problem dataset for the Emotion-Aware Coding Practice Platform.

Distribution: 40 Easy · 40 Medium · 20 Hard
Categories: arrays, strings, hash_table, two_pointers, binary_search,
            stack, queue, recursion, dynamic_programming, graphs, trees, math,
            sorting, loops, conditionals, output

Each entry:
    title       : str
    description : str
    difficulty  : "easy" | "medium" | "hard"
    category    : str
    starter_code: str
    examples    : list[dict]   -> serialised to JSON in main.py
    hints       : list[str]    -> serialised to JSON in main.py
    tests       : list[dict]   {stdin, expected_stdout}
"""

PROBLEMS = [
    # =====================================================================
    #  EASY  (40 problems)
    # =====================================================================

    # -- output / warmup --------------------------------------------------
    {
        "title": "Hello World",
        "description": "Print `Hello, World!` to the console.",
        "difficulty": "easy",
        "category": "output",
        "starter_code": "# Write your solution here\n",
        "examples": [{"input": "(none)", "output": "Hello, World!"}],
        "hints": ["Use the print() function."],
        "tests": [
            {"stdin": "", "expected_stdout": "Hello, World!"},
        ],
    },
    {
        "title": "Print Your Name",
        "description": "Read a name from stdin and print: Hello, <name>!",
        "difficulty": "easy",
        "category": "output",
        "starter_code": "name = input()\n",
        "examples": [{"input": "Alice", "output": "Hello, Alice!"}],
        "hints": ["Use an f-string: f'Hello, {name}!'"],
        "tests": [
            {"stdin": "Alice\n", "expected_stdout": "Hello, Alice!"},
            {"stdin": "Bob\n",   "expected_stdout": "Hello, Bob!"},
        ],
    },

    # -- math -------------------------------------------------------------
    {
        "title": "Sum Two Numbers",
        "description": "Read two integers (one per line) and print their sum.",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "a = int(input())\nb = int(input())\n",
        "examples": [{"input": "3\n4", "output": "7"}],
        "hints": ["Print a + b."],
        "tests": [
            {"stdin": "3\n4\n",   "expected_stdout": "7"},
            {"stdin": "10\n-2\n", "expected_stdout": "8"},
            {"stdin": "0\n0\n",   "expected_stdout": "0"},
        ],
    },
    {
        "title": "Multiply Two Numbers",
        "description": "Read two integers (one per line) and print their product.",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "a = int(input())\nb = int(input())\n",
        "examples": [{"input": "3\n4", "output": "12"}],
        "hints": ["Use the * operator."],
        "tests": [
            {"stdin": "3\n4\n",  "expected_stdout": "12"},
            {"stdin": "7\n0\n",  "expected_stdout": "0"},
            {"stdin": "-2\n5\n", "expected_stdout": "-10"},
        ],
    },
    {
        "title": "Absolute Value",
        "description": "Read an integer and print its absolute value.",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "-7", "output": "7"}, {"input": "3", "output": "3"}],
        "hints": ["Use the built-in abs() function."],
        "tests": [
            {"stdin": "-7\n", "expected_stdout": "7"},
            {"stdin": "3\n",  "expected_stdout": "3"},
            {"stdin": "0\n",  "expected_stdout": "0"},
        ],
    },
    {
        "title": "Square of a Number",
        "description": "Read an integer and print its square.",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "5", "output": "25"}],
        "hints": ["n ** 2 computes the square."],
        "tests": [
            {"stdin": "5\n",  "expected_stdout": "25"},
            {"stdin": "-3\n", "expected_stdout": "9"},
            {"stdin": "0\n",  "expected_stdout": "0"},
        ],
    },
    {
        "title": "Integer Division",
        "description": "Read two integers A and B (one per line). Print A // B (floor division).",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "a = int(input())\nb = int(input())\n",
        "examples": [{"input": "7\n2", "output": "3"}],
        "hints": ["Use the // operator."],
        "tests": [
            {"stdin": "7\n2\n",  "expected_stdout": "3"},
            {"stdin": "9\n3\n",  "expected_stdout": "3"},
            {"stdin": "10\n4\n", "expected_stdout": "2"},
        ],
    },
    {
        "title": "Modulo Operation",
        "description": "Read two integers A and B. Print A mod B.",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "a = int(input())\nb = int(input())\n",
        "examples": [{"input": "10\n3", "output": "1"}],
        "hints": ["Use the % operator."],
        "tests": [
            {"stdin": "10\n3\n", "expected_stdout": "1"},
            {"stdin": "15\n5\n", "expected_stdout": "0"},
            {"stdin": "7\n4\n",  "expected_stdout": "3"},
        ],
    },
    {
        "title": "Max of Two Numbers",
        "description": "Read two integers (one per line) and print the larger one.",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "a = int(input())\nb = int(input())\n",
        "examples": [{"input": "3\n7", "output": "7"}],
        "hints": ["Use max(a, b)."],
        "tests": [
            {"stdin": "3\n7\n",   "expected_stdout": "7"},
            {"stdin": "10\n5\n",  "expected_stdout": "10"},
            {"stdin": "-1\n-5\n", "expected_stdout": "-1"},
        ],
    },
    {
        "title": "Min of Three Numbers",
        "description": "Read three integers (one per line) and print the smallest.",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "a = int(input())\nb = int(input())\nc = int(input())\n",
        "examples": [{"input": "5\n3\n8", "output": "3"}],
        "hints": ["Use min(a, b, c)."],
        "tests": [
            {"stdin": "5\n3\n8\n",  "expected_stdout": "3"},
            {"stdin": "1\n1\n1\n",  "expected_stdout": "1"},
            {"stdin": "-1\n0\n1\n", "expected_stdout": "-1"},
        ],
    },
    # -- conditionals -----------------------------------------------------
    {
        "title": "Even or Odd",
        "description": "Read an integer. Print 'Even' if even, 'Odd' otherwise.",
        "difficulty": "easy",
        "category": "conditionals",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "4", "output": "Even"}],
        "hints": ["n % 2 == 0 means even."],
        "tests": [
            {"stdin": "4\n", "expected_stdout": "Even"},
            {"stdin": "7\n", "expected_stdout": "Odd"},
            {"stdin": "0\n", "expected_stdout": "Even"},
        ],
    },
    {
        "title": "Positive Negative Zero",
        "description": "Read an integer. Print 'Positive', 'Negative', or 'Zero'.",
        "difficulty": "easy",
        "category": "conditionals",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "5", "output": "Positive"}],
        "hints": ["Use if/elif/else."],
        "tests": [
            {"stdin": "5\n",  "expected_stdout": "Positive"},
            {"stdin": "-3\n", "expected_stdout": "Negative"},
            {"stdin": "0\n",  "expected_stdout": "Zero"},
        ],
    },
    {
        "title": "Leap Year",
        "description": (
            "Read a year. Print 'Leap' if it is a leap year, 'Not Leap' otherwise. "
            "Divisible by 400 -> Leap. Divisible by 100 but not 400 -> Not Leap. Divisible by 4 -> Leap."
        ),
        "difficulty": "easy",
        "category": "conditionals",
        "starter_code": "year = int(input())\n",
        "examples": [{"input": "2000", "output": "Leap"}, {"input": "1900", "output": "Not Leap"}],
        "hints": ["Check 400, then 100, then 4."],
        "tests": [
            {"stdin": "2000\n", "expected_stdout": "Leap"},
            {"stdin": "1900\n", "expected_stdout": "Not Leap"},
            {"stdin": "2024\n", "expected_stdout": "Leap"},
            {"stdin": "2023\n", "expected_stdout": "Not Leap"},
        ],
    },
    {
        "title": "Grade Calculator",
        "description": (
            "Read an integer score (0-100). Print: A (90-100), B (80-89), "
            "C (70-79), D (60-69), F (below 60)."
        ),
        "difficulty": "easy",
        "category": "conditionals",
        "starter_code": "score = int(input())\n",
        "examples": [{"input": "85", "output": "B"}],
        "hints": ["Use if/elif/else with thresholds 90, 80, 70, 60."],
        "tests": [
            {"stdin": "95\n", "expected_stdout": "A"},
            {"stdin": "85\n", "expected_stdout": "B"},
            {"stdin": "75\n", "expected_stdout": "C"},
            {"stdin": "65\n", "expected_stdout": "D"},
            {"stdin": "55\n", "expected_stdout": "F"},
        ],
    },
    # -- string -----------------------------------------------------------
    {
        "title": "Reverse a String",
        "description": "Read a string and print it reversed.",
        "difficulty": "easy",
        "category": "string",
        "starter_code": "s = input()\n",
        "examples": [{"input": "hello", "output": "olleh"}],
        "hints": ["s[::-1]"],
        "tests": [
            {"stdin": "hello\n", "expected_stdout": "olleh"},
            {"stdin": "abcde\n", "expected_stdout": "edcba"},
            {"stdin": "a\n",     "expected_stdout": "a"},
        ],
    },
    {
        "title": "Count Vowels",
        "description": "Read a string and print the count of vowels (a,e,i,o,u case-insensitive).",
        "difficulty": "easy",
        "category": "string",
        "starter_code": "s = input()\n",
        "examples": [{"input": "Hello", "output": "2"}],
        "hints": ["sum(1 for c in s.lower() if c in 'aeiou')"],
        "tests": [
            {"stdin": "Hello\n", "expected_stdout": "2"},
            {"stdin": "aeiou\n", "expected_stdout": "5"},
            {"stdin": "bcdfg\n", "expected_stdout": "0"},
        ],
    },
    {
        "title": "String Length",
        "description": "Read a string and print its length.",
        "difficulty": "easy",
        "category": "string",
        "starter_code": "s = input()\n",
        "examples": [{"input": "hello", "output": "5"}],
        "hints": ["Use len(s)."],
        "tests": [
            {"stdin": "hello\n", "expected_stdout": "5"},
            {"stdin": "\n",      "expected_stdout": "0"},
            {"stdin": "abc\n",   "expected_stdout": "3"},
        ],
    },
    {
        "title": "Uppercase Converter",
        "description": "Read a string and print it in uppercase.",
        "difficulty": "easy",
        "category": "string",
        "starter_code": "s = input()\n",
        "examples": [{"input": "hello", "output": "HELLO"}],
        "hints": ["s.upper()"],
        "tests": [
            {"stdin": "hello\n",  "expected_stdout": "HELLO"},
            {"stdin": "World\n",  "expected_stdout": "WORLD"},
            {"stdin": "abc123\n", "expected_stdout": "ABC123"},
        ],
    },
    {
        "title": "Count Words",
        "description": "Read a sentence and print the number of words.",
        "difficulty": "easy",
        "category": "string",
        "starter_code": "line = input()\n",
        "examples": [{"input": "hello world", "output": "2"}],
        "hints": ["len(line.split())"],
        "tests": [
            {"stdin": "hello world\n",       "expected_stdout": "2"},
            {"stdin": "one two three four\n", "expected_stdout": "4"},
            {"stdin": "single\n",            "expected_stdout": "1"},
        ],
    },
    {
        "title": "First Character",
        "description": "Read a non-empty string and print its first character.",
        "difficulty": "easy",
        "category": "string",
        "starter_code": "s = input()\n",
        "examples": [{"input": "python", "output": "p"}],
        "hints": ["s[0]"],
        "tests": [
            {"stdin": "python\n", "expected_stdout": "p"},
            {"stdin": "abc\n",    "expected_stdout": "a"},
        ],
    },
    {
        "title": "Last Character",
        "description": "Read a non-empty string and print its last character.",
        "difficulty": "easy",
        "category": "string",
        "starter_code": "s = input()\n",
        "examples": [{"input": "python", "output": "n"}],
        "hints": ["s[-1]"],
        "tests": [
            {"stdin": "python\n", "expected_stdout": "n"},
            {"stdin": "abc\n",    "expected_stdout": "c"},
        ],
    },
    {
        "title": "Count Character Occurrences",
        "description": "Read a string on line 1 and a character on line 2. Print how many times the character appears.",
        "difficulty": "easy",
        "category": "string",
        "starter_code": "s = input()\nch = input()\n",
        "examples": [{"input": "hello\nl", "output": "2"}],
        "hints": ["s.count(ch)"],
        "tests": [
            {"stdin": "hello\nl\n",  "expected_stdout": "2"},
            {"stdin": "banana\na\n", "expected_stdout": "3"},
            {"stdin": "python\nz\n", "expected_stdout": "0"},
        ],
    },
    {
        "title": "Check Anagram",
        "description": "Read two strings. Print 'Yes' if anagrams, 'No' otherwise.",
        "difficulty": "easy",
        "category": "string",
        "starter_code": "s1 = input().lower()\ns2 = input().lower()\n",
        "examples": [{"input": "listen\nsilent", "output": "Yes"}],
        "hints": ["sorted(s1) == sorted(s2)"],
        "tests": [
            {"stdin": "listen\nsilent\n", "expected_stdout": "Yes"},
            {"stdin": "hello\nworld\n",   "expected_stdout": "No"},
            {"stdin": "abc\ncba\n",       "expected_stdout": "Yes"},
        ],
    },
    # -- arrays -----------------------------------------------------------
    {
        "title": "Sum of Array",
        "description": "Read N integers (space-separated) and print their sum.",
        "difficulty": "easy",
        "category": "arrays",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "1 2 3 4 5", "output": "15"}],
        "hints": ["sum(nums)"],
        "tests": [
            {"stdin": "1 2 3 4 5\n", "expected_stdout": "15"},
            {"stdin": "10 20 30\n",  "expected_stdout": "60"},
            {"stdin": "-1 0 1\n",    "expected_stdout": "0"},
        ],
    },
    {
        "title": "Maximum in Array",
        "description": "Read N integers (space-separated) and print the maximum.",
        "difficulty": "easy",
        "category": "arrays",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "3 1 7 2", "output": "7"}],
        "hints": ["max(nums)"],
        "tests": [
            {"stdin": "3 1 7 2\n",  "expected_stdout": "7"},
            {"stdin": "-5 -2 -8\n", "expected_stdout": "-2"},
        ],
    },
    {
        "title": "Minimum in Array",
        "description": "Read N integers (space-separated) and print the minimum.",
        "difficulty": "easy",
        "category": "arrays",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "3 1 7 2", "output": "1"}],
        "hints": ["min(nums)"],
        "tests": [
            {"stdin": "3 1 7 2\n",  "expected_stdout": "1"},
            {"stdin": "-5 -2 -8\n", "expected_stdout": "-8"},
        ],
    },
    {
        "title": "Average of Array",
        "description": "Read N integers (space-separated). Print their average rounded to 2 decimal places.",
        "difficulty": "easy",
        "category": "arrays",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "1 2 3 4 5", "output": "3.00"}],
        "hints": ["f'{sum(nums)/len(nums):.2f}'"],
        "tests": [
            {"stdin": "1 2 3 4 5\n", "expected_stdout": "3.00"},
            {"stdin": "10 20\n",     "expected_stdout": "15.00"},
        ],
    },
    {
        "title": "Reverse Array",
        "description": "Read N integers (space-separated) and print them reversed.",
        "difficulty": "easy",
        "category": "arrays",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "1 2 3 4 5", "output": "5 4 3 2 1"}],
        "hints": ["print(*nums[::-1])"],
        "tests": [
            {"stdin": "1 2 3 4 5\n", "expected_stdout": "5 4 3 2 1"},
            {"stdin": "7 3\n",       "expected_stdout": "3 7"},
        ],
    },
    {
        "title": "Count Even Numbers",
        "description": "Read N integers (space-separated) and print how many are even.",
        "difficulty": "easy",
        "category": "arrays",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "1 2 3 4 5 6", "output": "3"}],
        "hints": ["len([n for n in nums if n % 2 == 0])"],
        "tests": [
            {"stdin": "1 2 3 4 5 6\n", "expected_stdout": "3"},
            {"stdin": "1 3 5\n",       "expected_stdout": "0"},
        ],
    },
    {
        "title": "Second Largest",
        "description": "Read N integers (space-separated, N>=2). Print the second largest distinct value.",
        "difficulty": "easy",
        "category": "arrays",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "3 1 4 1 5 9 2 6", "output": "6"}],
        "hints": ["sorted(set(nums))[-2]"],
        "tests": [
            {"stdin": "3 1 4 1 5 9 2 6\n", "expected_stdout": "6"},
            {"stdin": "1 2\n",             "expected_stdout": "1"},
        ],
    },
    {
        "title": "Remove Duplicates from List",
        "description": "Read N integers (space-separated). Print unique integers in original order.",
        "difficulty": "easy",
        "category": "arrays",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "1 2 2 3 3 3 4", "output": "1 2 3 4"}],
        "hints": ["Use dict.fromkeys(nums).keys()."],
        "tests": [
            {"stdin": "1 2 2 3 3 3 4\n", "expected_stdout": "1 2 3 4"},
            {"stdin": "5 5 5\n",         "expected_stdout": "5"},
        ],
    },
    {
        "title": "Sum 1 to N",
        "description": "Read N and print the sum 1+2+...+N.",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "5", "output": "15"}],
        "hints": ["n*(n+1)//2"],
        "tests": [
            {"stdin": "5\n",  "expected_stdout": "15"},
            {"stdin": "10\n", "expected_stdout": "55"},
        ],
    },
    {
        "title": "Fibonacci Nth Term",
        "description": "Read N (0-indexed). Print the N-th Fibonacci number (F(0)=0, F(1)=1).",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "6", "output": "8"}],
        "hints": ["Iterate from 0 to N keeping previous two."],
        "tests": [
            {"stdin": "0\n",  "expected_stdout": "0"},
            {"stdin": "6\n",  "expected_stdout": "8"},
            {"stdin": "10\n", "expected_stdout": "55"},
        ],
    },
    {
        "title": "Is Prime",
        "description": "Read N>=2. Print 'Yes' if prime, 'No' otherwise.",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "7", "output": "Yes"}],
        "hints": ["Check divisors up to sqrt(n)."],
        "tests": [
            {"stdin": "7\n",  "expected_stdout": "Yes"},
            {"stdin": "9\n",  "expected_stdout": "No"},
            {"stdin": "17\n", "expected_stdout": "Yes"},
        ],
    },
    {
        "title": "GCD of Two Numbers",
        "description": "Read two integers A and B. Print their GCD.",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "a = int(input())\nb = int(input())\n",
        "examples": [{"input": "12\n8", "output": "4"}],
        "hints": ["import math; math.gcd(a,b)"],
        "tests": [
            {"stdin": "12\n8\n",  "expected_stdout": "4"},
            {"stdin": "15\n25\n", "expected_stdout": "5"},
        ],
    },
    {
        "title": "LCM of Two Numbers",
        "description": "Read two integers A and B. Print their LCM.",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "import math\na = int(input())\nb = int(input())\n",
        "examples": [{"input": "4\n6", "output": "12"}],
        "hints": ["a * b // math.gcd(a, b)"],
        "tests": [
            {"stdin": "4\n6\n", "expected_stdout": "12"},
            {"stdin": "3\n5\n", "expected_stdout": "15"},
        ],
    },
    {
        "title": "Count Digits",
        "description": "Read a non-negative integer and print the number of digits.",
        "difficulty": "easy",
        "category": "string",
        "starter_code": "n = input().strip()\n",
        "examples": [{"input": "12345", "output": "5"}],
        "hints": ["len(n)"],
        "tests": [
            {"stdin": "12345\n", "expected_stdout": "5"},
            {"stdin": "0\n",     "expected_stdout": "1"},
        ],
    },
    {
        "title": "Sort Three Numbers",
        "description": "Read three integers (one per line). Print them ascending, space-separated.",
        "difficulty": "easy",
        "category": "sorting",
        "starter_code": "a = int(input())\nb = int(input())\nc = int(input())\n",
        "examples": [{"input": "3\n1\n2", "output": "1 2 3"}],
        "hints": ["print(*sorted([a,b,c]))"],
        "tests": [
            {"stdin": "3\n1\n2\n",  "expected_stdout": "1 2 3"},
            {"stdin": "9\n5\n7\n",  "expected_stdout": "5 7 9"},
        ],
    },
    {
        "title": "Multiplication Table",
        "description": "Read N. Print the N-times table 1xN to 10xN (format: i*N=result).",
        "difficulty": "easy",
        "category": "loops",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "2", "output": "1*2=2\n2*2=4\n..."}],
        "hints": ["for i in range(1, 11): print(f'{i}*{n}={i*n}')"],
        "tests": [
            {
                "stdin": "2\n",
                "expected_stdout": "1*2=2\n2*2=4\n3*2=6\n4*2=8\n5*2=10\n6*2=12\n7*2=14\n8*2=16\n9*2=18\n10*2=20",
            },
            {
                "stdin": "1\n",
                "expected_stdout": "1*1=1\n2*1=2\n3*1=3\n4*1=4\n5*1=5\n6*1=6\n7*1=7\n8*1=8\n9*1=9\n10*1=10",
            },
        ],
    },
    {
        "title": "Swap Without Temp",
        "description": "Read two integers A and B. Swap them and print A then B (each on its own line).",
        "difficulty": "easy",
        "category": "math",
        "starter_code": "a = int(input())\nb = int(input())\n",
        "examples": [{"input": "3\n7", "output": "7\n3"}],
        "hints": ["a, b = b, a"],
        "tests": [
            {"stdin": "3\n7\n",  "expected_stdout": "7\n3"},
            {"stdin": "5\n5\n",  "expected_stdout": "5\n5"},
            {"stdin": "1\n10\n", "expected_stdout": "10\n1"},
        ],
    },

    # =====================================================================
    #  MEDIUM  (40 problems)
    # =====================================================================

    {
        "title": "FizzBuzz",
        "description": (
            "Read N. For each 1..N print FizzBuzz (div by 3&5), Fizz (div by 3), Buzz (div by 5), else the number."
        ),
        "difficulty": "medium",
        "category": "loops",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "5", "output": "1\n2\nFizz\n4\nBuzz"}],
        "hints": ["Check 15 first."],
        "tests": [
            {"stdin": "5\n",
             "expected_stdout": "1\n2\nFizz\n4\nBuzz"},
            {"stdin": "15\n",
             "expected_stdout": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz"},
        ],
    },
    {
        "title": "Factorial",
        "description": "Read N>=0 and print N!.",
        "difficulty": "medium",
        "category": "math",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "5", "output": "120"}],
        "hints": ["math.factorial(n)"],
        "tests": [
            {"stdin": "5\n",  "expected_stdout": "120"},
            {"stdin": "0\n",  "expected_stdout": "1"},
            {"stdin": "10\n", "expected_stdout": "3628800"},
        ],
    },
    {
        "title": "Palindrome Check",
        "description": "Read a string. Print 'Yes' if palindrome, 'No' otherwise.",
        "difficulty": "medium",
        "category": "string",
        "starter_code": "s = input().strip()\n",
        "examples": [{"input": "racecar", "output": "Yes"}],
        "hints": ["s == s[::-1]"],
        "tests": [
            {"stdin": "racecar\n", "expected_stdout": "Yes"},
            {"stdin": "hello\n",   "expected_stdout": "No"},
            {"stdin": "madam\n",   "expected_stdout": "Yes"},
        ],
    },
    {
        "title": "Two Sum",
        "description": (
            "Read space-separated integers on line 1, target on line 2. "
            "Print 0-based indices of two numbers summing to target. "
            "Guaranteed one solution."
        ),
        "difficulty": "medium",
        "category": "hash_table",
        "starter_code": "nums = list(map(int, input().split()))\ntarget = int(input())\n",
        "examples": [{"input": "2 7 11 15\n9", "output": "0 1"}],
        "hints": ["Use a dict mapping value->index."],
        "tests": [
            {"stdin": "2 7 11 15\n9\n", "expected_stdout": "0 1"},
            {"stdin": "3 2 4\n6\n",     "expected_stdout": "1 2"},
            {"stdin": "3 3\n6\n",       "expected_stdout": "0 1"},
        ],
    },
    {
        "title": "Valid Parentheses",
        "description": "Read a bracket string. Print 'Valid' or 'Invalid'.",
        "difficulty": "medium",
        "category": "stack",
        "starter_code": "s = input().strip()\n",
        "examples": [{"input": "()[]{}", "output": "Valid"}],
        "hints": ["Stack-based matching."],
        "tests": [
            {"stdin": "()[]{}\n", "expected_stdout": "Valid"},
            {"stdin": "([)]\n",   "expected_stdout": "Invalid"},
            {"stdin": "{[]}\n",   "expected_stdout": "Valid"},
        ],
    },
    {
        "title": "Count Unique Characters",
        "description": "Read a string. Print the count of unique characters.",
        "difficulty": "medium",
        "category": "hash_table",
        "starter_code": "s = input()\n",
        "examples": [{"input": "hello", "output": "4"}],
        "hints": ["len(set(s))"],
        "tests": [
            {"stdin": "hello\n",  "expected_stdout": "4"},
            {"stdin": "abcabc\n", "expected_stdout": "3"},
        ],
    },
    {
        "title": "Word Frequency",
        "description": "Read a sentence. Print each word and count in alphabetical order (word: count).",
        "difficulty": "medium",
        "category": "hash_table",
        "starter_code": "line = input()\n",
        "examples": [{"input": "the cat sat on the mat", "output": "cat: 1\nmat: 1\non: 1\nsat: 1\nthe: 2"}],
        "hints": ["collections.Counter + sorted keys."],
        "tests": [
            {
                "stdin": "the cat sat on the mat\n",
                "expected_stdout": "cat: 1\nmat: 1\non: 1\nsat: 1\nthe: 2",
            },
            {"stdin": "a b a\n", "expected_stdout": "a: 2\nb: 1"},
        ],
    },
    {
        "title": "Rotate Array",
        "description": "Read integers on line 1 and K on line 2. Rotate right by K. Print result.",
        "difficulty": "medium",
        "category": "arrays",
        "starter_code": "nums = list(map(int, input().split()))\nk = int(input())\n",
        "examples": [{"input": "1 2 3 4 5\n2", "output": "4 5 1 2 3"}],
        "hints": ["k %= len(nums); result = nums[-k:] + nums[:-k]"],
        "tests": [
            {"stdin": "1 2 3 4 5\n2\n", "expected_stdout": "4 5 1 2 3"},
            {"stdin": "1 2 3\n1\n",     "expected_stdout": "3 1 2"},
        ],
    },
    {
        "title": "Missing Number",
        "description": (
            "Read integers (0..N with one missing). Print the missing number."
        ),
        "difficulty": "medium",
        "category": "arrays",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "3 0 1", "output": "2"}],
        "hints": ["expected = N*(N+1)//2; missing = expected - sum(nums)"],
        "tests": [
            {"stdin": "3 0 1\n",             "expected_stdout": "2"},
            {"stdin": "0 1\n",               "expected_stdout": "2"},
            {"stdin": "9 6 4 2 3 5 7 0 1\n", "expected_stdout": "8"},
        ],
    },
    {
        "title": "Maximum Subarray Sum",
        "description": "Read N integers. Print the maximum sum of any contiguous subarray.",
        "difficulty": "medium",
        "category": "arrays",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "-2 1 -3 4 -1 2 1 -5 4", "output": "6"}],
        "hints": ["Kadane's: cur = max(n, cur+n); track max."],
        "tests": [
            {"stdin": "-2 1 -3 4 -1 2 1 -5 4\n", "expected_stdout": "6"},
            {"stdin": "1\n",                      "expected_stdout": "1"},
            {"stdin": "-1 -2 -3\n",               "expected_stdout": "-1"},
        ],
    },
    {
        "title": "Move Zeros to End",
        "description": "Read N integers. Move zeros to end preserving order of non-zeros.",
        "difficulty": "medium",
        "category": "two_pointers",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "0 1 0 3 12", "output": "1 3 12 0 0"}],
        "hints": ["Two-pointer."],
        "tests": [
            {"stdin": "0 1 0 3 12\n", "expected_stdout": "1 3 12 0 0"},
            {"stdin": "1 2 3\n",      "expected_stdout": "1 2 3"},
        ],
    },
    {
        "title": "Two Pointers Pair Sum",
        "description": "Read sorted integers on line 1 and target on line 2. Print indices of pair summing to target using two pointers, or -1.",
        "difficulty": "medium",
        "category": "two_pointers",
        "starter_code": "nums = list(map(int, input().split()))\ntarget = int(input())\n",
        "examples": [{"input": "1 2 3 4 5\n6", "output": "1 4"}],
        "hints": ["left=0, right=len-1; move inward."],
        "tests": [
            {"stdin": "1 2 3 4 5\n6\n",  "expected_stdout": "1 4"},
            {"stdin": "1 2 3 4 5\n10\n", "expected_stdout": "-1"},
        ],
    },
    {
        "title": "Stack Simulation",
        "description": "Read N then N operations (PUSH x / POP). For POP print value or EMPTY.",
        "difficulty": "medium",
        "category": "stack",
        "starter_code": "n = int(input())\nstack = []\n",
        "examples": [{"input": "4\nPUSH 1\nPUSH 2\nPOP\nPOP", "output": "2\n1"}],
        "hints": ["list.append / list.pop"],
        "tests": [
            {"stdin": "4\nPUSH 1\nPUSH 2\nPOP\nPOP\n", "expected_stdout": "2\n1"},
            {"stdin": "2\nPOP\nPUSH 5\n",              "expected_stdout": "EMPTY"},
        ],
    },
    {
        "title": "Queue Simulation",
        "description": "Read N then N operations (ENQUEUE x / DEQUEUE). For DEQUEUE print value or EMPTY.",
        "difficulty": "medium",
        "category": "queue",
        "starter_code": "from collections import deque\nn = int(input())\nq = deque()\n",
        "examples": [{"input": "4\nENQUEUE 1\nENQUEUE 2\nDEQUEUE\nDEQUEUE", "output": "1\n2"}],
        "hints": ["deque.append / deque.popleft"],
        "tests": [
            {"stdin": "4\nENQUEUE 1\nENQUEUE 2\nDEQUEUE\nDEQUEUE\n", "expected_stdout": "1\n2"},
            {"stdin": "1\nDEQUEUE\n",                                  "expected_stdout": "EMPTY"},
        ],
    },
    {
        "title": "Balanced Brackets Cost",
        "description": "Read a parenthesis string. Print minimum additions to balance it.",
        "difficulty": "medium",
        "category": "stack",
        "starter_code": "s = input().strip()\n",
        "examples": [{"input": "(()", "output": "1"}],
        "hints": ["Track open count and close_needed."],
        "tests": [
            {"stdin": "(()\n", "expected_stdout": "1"},
            {"stdin": ")(\n",  "expected_stdout": "2"},
            {"stdin": "()\n",  "expected_stdout": "0"},
        ],
    },
    {
        "title": "Longest Palindromic Substring Length",
        "description": "Read a string. Print the length of the longest palindromic substring.",
        "difficulty": "medium",
        "category": "string",
        "starter_code": "s = input().strip()\n",
        "examples": [{"input": "babad", "output": "3"}],
        "hints": ["Expand around center."],
        "tests": [
            {"stdin": "babad\n",  "expected_stdout": "3"},
            {"stdin": "cbbd\n",   "expected_stdout": "2"},
            {"stdin": "racecar\n","expected_stdout": "7"},
        ],
    },
    {
        "title": "Remove Duplicates Sorted Array",
        "description": "Read sorted integers. Print them with duplicates removed.",
        "difficulty": "medium",
        "category": "two_pointers",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "1 1 2 3 3 4", "output": "1 2 3 4"}],
        "hints": ["Use a seen set or two pointers."],
        "tests": [
            {"stdin": "1 1 2 3 3 4\n", "expected_stdout": "1 2 3 4"},
            {"stdin": "1 1 1\n",       "expected_stdout": "1"},
        ],
    },
    {
        "title": "Bubble Sort",
        "description": "Read N integers. Sort using Bubble Sort. Print result.",
        "difficulty": "medium",
        "category": "sorting",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "5 3 8 1 2", "output": "1 2 3 5 8"}],
        "hints": ["Nested loops, swap adjacent if out of order."],
        "tests": [
            {"stdin": "5 3 8 1 2\n",          "expected_stdout": "1 2 3 5 8"},
            {"stdin": "10 9 8 7 6 5 4 3 2 1\n","expected_stdout": "1 2 3 4 5 6 7 8 9 10"},
        ],
    },
    {
        "title": "Selection Sort",
        "description": "Read N integers. Sort using Selection Sort. Print result.",
        "difficulty": "medium",
        "category": "sorting",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "64 25 12 22 11", "output": "11 12 22 25 64"}],
        "hints": ["For each position, find the minimum in remaining and swap."],
        "tests": [
            {"stdin": "64 25 12 22 11\n", "expected_stdout": "11 12 22 25 64"},
            {"stdin": "3 2 1\n",          "expected_stdout": "1 2 3"},
        ],
    },
    {
        "title": "Count Inversions",
        "description": "Read N integers. Count pairs (i,j) where i<j but nums[i]>nums[j].",
        "difficulty": "medium",
        "category": "sorting",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "2 4 1 3 5", "output": "3"}],
        "hints": ["O(n^2) brute force: nested loop over all pairs."],
        "tests": [
            {"stdin": "2 4 1 3 5\n", "expected_stdout": "3"},
            {"stdin": "1 2 3 4 5\n", "expected_stdout": "0"},
            {"stdin": "5 4 3 2 1\n", "expected_stdout": "10"},
        ],
    },
    {
        "title": "First Non-Repeating Character",
        "description": "Read a string. Print the first character appearing exactly once, or '#'.",
        "difficulty": "medium",
        "category": "hash_table",
        "starter_code": "s = input()\n",
        "examples": [{"input": "leetcode", "output": "l"}],
        "hints": ["Count frequencies; scan for first with count 1."],
        "tests": [
            {"stdin": "leetcode\n", "expected_stdout": "l"},
            {"stdin": "aabb\n",     "expected_stdout": "#"},
            {"stdin": "abacabad\n", "expected_stdout": "c"},
        ],
    },
    {
        "title": "Anagram Groups",
        "description": "Read N words. Group anagrams. Print each group (words sorted) on one line, groups sorted lexicographically by first word.",
        "difficulty": "medium",
        "category": "hash_table",
        "starter_code": "words = input().split()\n",
        "examples": [{"input": "eat tea tan ate nat bat", "output": "ate eat tea\nbat\nant nat tan"}],
        "hints": ["Key = sorted(word). Group words by key."],
        "tests": [
            {
                "stdin": "eat tea tan ate nat bat\n",
                "expected_stdout": "ate eat tea\nbat\nant nat tan",
            },
            {
                "stdin": "abc bca cab\n",
                "expected_stdout": "abc bca cab",
            },
        ],
    },
    {
        "title": "Power Function Recursive",
        "description": "Read B and E. Print B^E using recursion.",
        "difficulty": "medium",
        "category": "recursion",
        "starter_code": "b = int(input())\ne = int(input())\n\ndef power(base, exp):\n    pass\n\nprint(power(b, e))\n",
        "examples": [{"input": "2\n10", "output": "1024"}],
        "hints": ["Base: exp==0 -> 1. Recursive: base * power(base, exp-1)."],
        "tests": [
            {"stdin": "2\n10\n", "expected_stdout": "1024"},
            {"stdin": "3\n3\n",  "expected_stdout": "27"},
            {"stdin": "5\n0\n",  "expected_stdout": "1"},
        ],
    },
    {
        "title": "Sum of Digits Recursive",
        "description": "Read a non-negative integer. Print its digit sum using recursion.",
        "difficulty": "medium",
        "category": "recursion",
        "starter_code": "n = int(input())\n\ndef digit_sum(n):\n    pass\n\nprint(digit_sum(n))\n",
        "examples": [{"input": "1234", "output": "10"}],
        "hints": ["Base: n<10 -> n. Recursive: n%10 + digit_sum(n//10)."],
        "tests": [
            {"stdin": "1234\n", "expected_stdout": "10"},
            {"stdin": "999\n",  "expected_stdout": "27"},
        ],
    },
    {
        "title": "Matrix Transpose",
        "description": "Read N then N lines of N integers. Print the transposed matrix.",
        "difficulty": "medium",
        "category": "arrays",
        "starter_code": "n = int(input())\nmatrix = [list(map(int, input().split())) for _ in range(n)]\n",
        "examples": [{"input": "2\n1 2\n3 4", "output": "1 3\n2 4"}],
        "hints": ["Use zip(*matrix)."],
        "tests": [
            {"stdin": "2\n1 2\n3 4\n",          "expected_stdout": "1 3\n2 4"},
            {"stdin": "3\n1 2 3\n4 5 6\n7 8 9\n","expected_stdout": "1 4 7\n2 5 8\n3 6 9"},
        ],
    },
    {
        "title": "String Compression",
        "description": "Read a string. Apply run-length encoding. If shorter, print compressed; else original.",
        "difficulty": "medium",
        "category": "string",
        "starter_code": "s = input()\n",
        "examples": [{"input": "aabcccccaaa", "output": "a2b1c5a3"}],
        "hints": ["Count consecutive chars. Compare lengths."],
        "tests": [
            {"stdin": "aabcccccaaa\n", "expected_stdout": "a2b1c5a3"},
            {"stdin": "abc\n",         "expected_stdout": "abc"},
            {"stdin": "aaa\n",         "expected_stdout": "a3"},
        ],
    },
    {
        "title": "Binary to Decimal",
        "description": "Read a binary string. Print its decimal value.",
        "difficulty": "medium",
        "category": "math",
        "starter_code": "b = input().strip()\n",
        "examples": [{"input": "1010", "output": "10"}],
        "hints": ["int(b, 2)"],
        "tests": [
            {"stdin": "1010\n", "expected_stdout": "10"},
            {"stdin": "1111\n", "expected_stdout": "15"},
        ],
    },
    {
        "title": "Decimal to Binary",
        "description": "Read a non-negative integer. Print its binary representation (no '0b').",
        "difficulty": "medium",
        "category": "math",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "10", "output": "1010"}],
        "hints": ["bin(n)[2:]"],
        "tests": [
            {"stdin": "10\n", "expected_stdout": "1010"},
            {"stdin": "0\n",  "expected_stdout": "0"},
            {"stdin": "15\n", "expected_stdout": "1111"},
        ],
    },
    {
        "title": "Number of Islands",
        "description": "Read R C then R lines of 0/1. Count connected components of 1s (4-directional).",
        "difficulty": "medium",
        "category": "graphs",
        "starter_code": "r, c = map(int, input().split())\ngrid = [list(map(int, input().split())) for _ in range(r)]\n",
        "examples": [{"input": "3 4\n1 1 0 0\n0 1 0 1\n0 0 0 1", "output": "2"}],
        "hints": ["BFS/DFS flood fill for each unvisited 1."],
        "tests": [
            {"stdin": "3 4\n1 1 0 0\n0 1 0 1\n0 0 0 1\n", "expected_stdout": "2"},
            {"stdin": "2 2\n1 0\n0 1\n",                   "expected_stdout": "2"},
        ],
    },
    {
        "title": "BFS Shortest Path",
        "description": "Read V E then E edges u v, then S D. Print shortest path length or -1.",
        "difficulty": "medium",
        "category": "graphs",
        "starter_code": "from collections import deque\nv, e = map(int, input().split())\ngraph = [[] for _ in range(v+1)]\nfor _ in range(e):\n    u, w = map(int, input().split())\n    graph[u].append(w); graph[w].append(u)\ns, d = map(int, input().split())\n",
        "examples": [{"input": "5 4\n1 2\n2 3\n3 4\n4 5\n1 5", "output": "4"}],
        "hints": ["BFS from S, track distances."],
        "tests": [
            {"stdin": "5 4\n1 2\n2 3\n3 4\n4 5\n1 5\n", "expected_stdout": "4"},
            {"stdin": "3 0\n1 3\n",                      "expected_stdout": "-1"},
        ],
    },
    {
        "title": "Top K Frequent",
        "description": "Read integers on line 1 and K on line 2. Print K most frequent (desc by freq, ties by value asc).",
        "difficulty": "medium",
        "category": "hash_table",
        "starter_code": "nums = list(map(int, input().split()))\nk = int(input())\n",
        "examples": [{"input": "1 1 1 2 2 3\n2", "output": "1 2"}],
        "hints": ["collections.Counter; sort by (-count, value)."],
        "tests": [
            {"stdin": "1 1 1 2 2 3\n2\n", "expected_stdout": "1 2"},
            {"stdin": "1\n1\n",           "expected_stdout": "1"},
        ],
    },
    {
        "title": "Sliding Window Maximum",
        "description": "Read N integers on line 1 and window K on line 2. Print max of each window.",
        "difficulty": "medium",
        "category": "queue",
        "starter_code": "from collections import deque\nnums = list(map(int, input().split()))\nk = int(input())\n",
        "examples": [{"input": "1 3 -1 -3 5 3 6 7\n3", "output": "3 3 5 5 6 7"}],
        "hints": ["Monotonic deque."],
        "tests": [
            {"stdin": "1 3 -1 -3 5 3 6 7\n3\n", "expected_stdout": "3 3 5 5 6 7"},
            {"stdin": "1 2 3\n1\n",              "expected_stdout": "1 2 3"},
        ],
    },
    {
        "title": "Next Greater Element",
        "description": "Read N integers. For each, print the first greater element to its right, or -1.",
        "difficulty": "medium",
        "category": "stack",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "4 1 2", "output": "-1 2 -1"}],
        "hints": ["Monotonic stack traversal right-to-left."],
        "tests": [
            {"stdin": "4 1 2\n", "expected_stdout": "-1 2 -1"},
            {"stdin": "1 2 3\n", "expected_stdout": "2 3 -1"},
        ],
    },
    {
        "title": "Subarray with Given Sum",
        "description": "Read non-negative integers on line 1 and S on line 2. Print 1-based start and end of first subarray summing to S, or -1.",
        "difficulty": "medium",
        "category": "two_pointers",
        "starter_code": "nums = list(map(int, input().split()))\ns = int(input())\n",
        "examples": [{"input": "1 4 20 3 10 5\n33", "output": "3 5"}],
        "hints": ["Sliding window: expand right, shrink left when sum > S."],
        "tests": [
            {"stdin": "1 4 20 3 10 5\n33\n", "expected_stdout": "3 5"},
            {"stdin": "1 2 3\n6\n",          "expected_stdout": "1 3"},
            {"stdin": "1 2 3\n10\n",         "expected_stdout": "-1"},
        ],
    },
    {
        "title": "Decode Caesar Cipher",
        "description": "Read message on line 1 and shift K on line 2. Decode (shift back K). Non-letters unchanged.",
        "difficulty": "medium",
        "category": "string",
        "starter_code": "message = input()\nk = int(input())\n",
        "examples": [{"input": "Khoor Zruog\n3", "output": "Hello World"}],
        "hints": ["Use ord/chr. Wrap with %26."],
        "tests": [
            {"stdin": "Khoor Zruog\n3\n", "expected_stdout": "Hello World"},
            {"stdin": "abc\n1\n",         "expected_stdout": "zab"},
        ],
    },
    {
        "title": "Flatten Nested List",
        "description": "Read a nested list string. Print all integers in order, space-separated.",
        "difficulty": "medium",
        "category": "recursion",
        "starter_code": "import ast\ndata = ast.literal_eval(input())\n\ndef flatten(lst):\n    pass\n\nprint(*flatten(data))\n",
        "examples": [{"input": "[[1,2],[3,[4,5]]]", "output": "1 2 3 4 5"}],
        "hints": ["Recurse if item is a list; else yield integer."],
        "tests": [
            {"stdin": "[[1,2],[3,[4,5]]]\n", "expected_stdout": "1 2 3 4 5"},
            {"stdin": "[1,2,3]\n",           "expected_stdout": "1 2 3"},
        ],
    },
    {
        "title": "Spiral Order Matrix",
        "description": "Read N then NxN matrix. Print elements in spiral order.",
        "difficulty": "medium",
        "category": "arrays",
        "starter_code": "n = int(input())\nmatrix = [list(map(int, input().split())) for _ in range(n)]\n",
        "examples": [{"input": "3\n1 2 3\n4 5 6\n7 8 9", "output": "1 2 3 6 9 8 7 4 5"}],
        "hints": ["Maintain top/bottom/left/right and peel layers."],
        "tests": [
            {"stdin": "3\n1 2 3\n4 5 6\n7 8 9\n", "expected_stdout": "1 2 3 6 9 8 7 4 5"},
        ],
    },
    {
        "title": "Tree Height",
        "description": (
            "Read N (nodes) then N-1 lines each with parent p and child c (root=1). "
            "Print the height (max depth) of the tree."
        ),
        "difficulty": "medium",
        "category": "trees",
        "starter_code": "from collections import defaultdict, deque\nn = int(input())\nchildren = defaultdict(list)\nfor _ in range(n-1):\n    p, c = map(int, input().split())\n    children[p].append(c)\n",
        "examples": [{"input": "4\n1 2\n1 3\n3 4", "output": "2"}],
        "hints": ["BFS from root; track max level."],
        "tests": [
            {"stdin": "4\n1 2\n1 3\n3 4\n", "expected_stdout": "2"},
            {"stdin": "1\n",               "expected_stdout": "0"},
        ],
    },
    {
        "title": "Reverse Words in Sentence",
        "description": "Read a sentence. Print the words in reverse order.",
        "difficulty": "medium",
        "category": "string",
        "starter_code": "line = input()\n",
        "examples": [{"input": "Hello World", "output": "World Hello"}],
        "hints": ["line.split()[::-1]"],
        "tests": [
            {"stdin": "Hello World\n",       "expected_stdout": "World Hello"},
            {"stdin": "one two three\n",     "expected_stdout": "three two one"},
            {"stdin": "single\n",            "expected_stdout": "single"},
        ],
    },
    {
        "title": "Check Subset",
        "description": (
            "Read set A (space-separated) on line 1 and set B on line 2. "
            "Print 'Yes' if A is a subset of B, 'No' otherwise."
        ),
        "difficulty": "medium",
        "category": "hash_table",
        "starter_code": "a = set(input().split())\nb = set(input().split())\n",
        "examples": [{"input": "1 2 3\n1 2 3 4 5", "output": "Yes"}],
        "hints": ["a.issubset(b)"],
        "tests": [
            {"stdin": "1 2 3\n1 2 3 4 5\n", "expected_stdout": "Yes"},
            {"stdin": "1 6\n1 2 3\n",       "expected_stdout": "No"},
            {"stdin": "\n1 2 3\n",           "expected_stdout": "Yes"},
        ],
    },

    # =====================================================================
    #  HARD  (20 problems)
    # =====================================================================

    {
        "title": "Binary Search",
        "description": "Read sorted integers on line 1 and target on line 2. Print index or -1.",
        "difficulty": "hard",
        "category": "binary_search",
        "starter_code": "nums = list(map(int, input().split()))\ntarget = int(input())\n",
        "examples": [{"input": "1 3 5 7 9\n5", "output": "2"}],
        "hints": ["left=0, right=len-1; mid=(left+right)//2."],
        "tests": [
            {"stdin": "1 3 5 7 9\n5\n",        "expected_stdout": "2"},
            {"stdin": "1 3 5 7 9\n4\n",        "expected_stdout": "-1"},
            {"stdin": "1 2 3 4 5 6 7 8 9 10\n10\n", "expected_stdout": "9"},
        ],
    },
    {
        "title": "Longest Common Subsequence",
        "description": "Read two strings. Print length of their LCS.",
        "difficulty": "hard",
        "category": "dynamic_programming",
        "starter_code": "s1 = input()\ns2 = input()\n",
        "examples": [{"input": "abcde\nace", "output": "3"}],
        "hints": ["2D DP. dp[i][j]=dp[i-1][j-1]+1 if match, else max(neighbors)."],
        "tests": [
            {"stdin": "abcde\nace\n",  "expected_stdout": "3"},
            {"stdin": "abc\nabc\n",    "expected_stdout": "3"},
            {"stdin": "abc\ndef\n",    "expected_stdout": "0"},
        ],
    },
    {
        "title": "Merge Sort",
        "description": "Read N integers. Sort using Merge Sort.",
        "difficulty": "hard",
        "category": "sorting",
        "starter_code": "nums = list(map(int, input().split()))\n\ndef merge_sort(arr):\n    pass\n\nprint(*merge_sort(nums))\n",
        "examples": [{"input": "5 2 8 1 9 3", "output": "1 2 3 5 8 9"}],
        "hints": ["Divide at midpoint, sort halves, merge."],
        "tests": [
            {"stdin": "5 2 8 1 9 3\n",          "expected_stdout": "1 2 3 5 8 9"},
            {"stdin": "10 9 8 7 6 5 4 3 2 1\n", "expected_stdout": "1 2 3 4 5 6 7 8 9 10"},
        ],
    },
    {
        "title": "Quick Sort",
        "description": "Read N integers. Sort using Quick Sort.",
        "difficulty": "hard",
        "category": "sorting",
        "starter_code": "nums = list(map(int, input().split()))\n\ndef quick_sort(arr):\n    pass\n\nprint(*quick_sort(nums))\n",
        "examples": [{"input": "3 6 8 10 1 2 1", "output": "1 1 2 3 6 8 10"}],
        "hints": ["Pick pivot, partition, recurse."],
        "tests": [
            {"stdin": "3 6 8 10 1 2 1\n", "expected_stdout": "1 1 2 3 6 8 10"},
            {"stdin": "5 4 3 2 1\n",      "expected_stdout": "1 2 3 4 5"},
        ],
    },
    {
        "title": "Knapsack 0/1",
        "description": "Read N W then N lines of weight value. Print max value within capacity W.",
        "difficulty": "hard",
        "category": "dynamic_programming",
        "starter_code": "n, w = map(int, input().split())\nitems = [tuple(map(int, input().split())) for _ in range(n)]\n",
        "examples": [{"input": "3 50\n10 60\n20 100\n30 120", "output": "220"}],
        "hints": ["dp[i][c]: max value using first i items and capacity c."],
        "tests": [
            {"stdin": "3 50\n10 60\n20 100\n30 120\n", "expected_stdout": "220"},
            {"stdin": "1 1\n2 5\n",                    "expected_stdout": "0"},
        ],
    },
    {
        "title": "Coin Change",
        "description": "Read coin denominations on line 1 and amount A on line 2. Print min coins or -1.",
        "difficulty": "hard",
        "category": "dynamic_programming",
        "starter_code": "coins = list(map(int, input().split()))\namount = int(input())\n",
        "examples": [{"input": "1 5 6 9\n11", "output": "2"}],
        "hints": ["dp[i] = min coins for amount i. dp[0]=0."],
        "tests": [
            {"stdin": "1 5 6 9\n11\n", "expected_stdout": "2"},
            {"stdin": "2\n3\n",        "expected_stdout": "-1"},
            {"stdin": "1 2 5\n11\n",   "expected_stdout": "3"},
        ],
    },
    {
        "title": "Longest Increasing Subsequence",
        "description": "Read N integers. Print length of longest strictly increasing subsequence.",
        "difficulty": "hard",
        "category": "dynamic_programming",
        "starter_code": "nums = list(map(int, input().split()))\n",
        "examples": [{"input": "10 9 2 5 3 7 101 18", "output": "4"}],
        "hints": ["dp[i]=LIS ending at i. Check all j<i where nums[j]<nums[i]."],
        "tests": [
            {"stdin": "10 9 2 5 3 7 101 18\n", "expected_stdout": "4"},
            {"stdin": "0 1 0 3 2 3\n",         "expected_stdout": "4"},
        ],
    },
    {
        "title": "Dijkstra Shortest Path",
        "description": "Read V E then E directed edges u v w, then source S. Print shortest distances from S (space-separated). INF for unreachable.",
        "difficulty": "hard",
        "category": "graphs",
        "starter_code": "import heapq\nv, e = map(int, input().split())\ngraph = [[] for _ in range(v+1)]\nfor _ in range(e):\n    u, w, c = map(int, input().split())\n    graph[u].append((w, c))\ns = int(input())\n",
        "examples": [{"input": "4 4\n1 2 1\n1 3 4\n2 3 2\n3 4 1\n1", "output": "0 1 3 4"}],
        "hints": ["Min-heap priority queue. Relax edges."],
        "tests": [
            {"stdin": "4 4\n1 2 1\n1 3 4\n2 3 2\n3 4 1\n1\n", "expected_stdout": "0 1 3 4"},
            {"stdin": "2 0\n1\n",                              "expected_stdout": "0 INF"},
        ],
    },
    {
        "title": "Topological Sort",
        "description": "Read V E then E directed edges u v. Print topological order or 'CYCLE'.",
        "difficulty": "hard",
        "category": "graphs",
        "starter_code": "from collections import defaultdict, deque\nv, e = map(int, input().split())\ngraph = defaultdict(list)\nindegree = [0] * (v+1)\nfor _ in range(e):\n    u, w = map(int, input().split())\n    graph[u].append(w)\n    indegree[w] += 1\n",
        "examples": [{"input": "4 3\n1 2\n2 3\n3 4", "output": "1 2 3 4"}],
        "hints": ["Kahn's BFS. If result len < V -> CYCLE."],
        "tests": [
            {"stdin": "4 3\n1 2\n2 3\n3 4\n", "expected_stdout": "1 2 3 4"},
            {"stdin": "3 3\n1 2\n2 3\n3 1\n", "expected_stdout": "CYCLE"},
        ],
    },
    {
        "title": "Trapping Rain Water",
        "description": "Read non-negative integers representing elevation. Print total trapped rain water.",
        "difficulty": "hard",
        "category": "two_pointers",
        "starter_code": "heights = list(map(int, input().split()))\n",
        "examples": [{"input": "0 1 0 2 1 0 1 3 2 1 2 1", "output": "6"}],
        "hints": ["Two pointers: left_max, right_max. water[i]=min(lm,rm)-h[i]."],
        "tests": [
            {"stdin": "0 1 0 2 1 0 1 3 2 1 2 1\n", "expected_stdout": "6"},
            {"stdin": "4 2 0 3 2 5\n",             "expected_stdout": "9"},
        ],
    },
    {
        "title": "Longest Substring Without Repeating",
        "description": "Read a string. Print length of longest substring without repeating characters.",
        "difficulty": "hard",
        "category": "binary_search",
        "starter_code": "s = input().strip()\n",
        "examples": [{"input": "abcabcbb", "output": "3"}],
        "hints": ["Sliding window with a set."],
        "tests": [
            {"stdin": "abcabcbb\n", "expected_stdout": "3"},
            {"stdin": "bbbbb\n",    "expected_stdout": "1"},
            {"stdin": "pwwkew\n",   "expected_stdout": "3"},
        ],
    },
    {
        "title": "Median of Two Sorted Arrays",
        "description": "Read two sorted arrays (one per line). Print median rounded to 1 decimal.",
        "difficulty": "hard",
        "category": "binary_search",
        "starter_code": "a = list(map(int, input().split()))\nb = list(map(int, input().split()))\n",
        "examples": [{"input": "1 3\n2", "output": "2.0"}],
        "hints": ["Merge and find middle."],
        "tests": [
            {"stdin": "1 3\n2\n",   "expected_stdout": "2.0"},
            {"stdin": "1 2\n3 4\n", "expected_stdout": "2.5"},
        ],
    },
    {
        "title": "N-Queens Problem",
        "description": "Read N. Print count of distinct solutions for N-Queens.",
        "difficulty": "hard",
        "category": "recursion",
        "starter_code": "n = int(input())\n",
        "examples": [{"input": "4", "output": "2"}],
        "hints": ["Backtracking. Track columns, diagonals, anti-diagonals."],
        "tests": [
            {"stdin": "4\n", "expected_stdout": "2"},
            {"stdin": "1\n", "expected_stdout": "1"},
            {"stdin": "8\n", "expected_stdout": "92"},
        ],
    },
    {
        "title": "Edit Distance",
        "description": "Read two strings. Print minimum edit distance (insert/delete/replace cost 1).",
        "difficulty": "hard",
        "category": "dynamic_programming",
        "starter_code": "s1 = input()\ns2 = input()\n",
        "examples": [{"input": "horse\nros", "output": "3"}],
        "hints": ["dp[i][j]: edit distance s1[:i] vs s2[:j]."],
        "tests": [
            {"stdin": "horse\nros\n",          "expected_stdout": "3"},
            {"stdin": "intention\nexecution\n", "expected_stdout": "5"},
            {"stdin": "abc\nabc\n",            "expected_stdout": "0"},
        ],
    },
    {
        "title": "Balanced BST Check",
        "description": "Read N integers, insert into BST. Print 'Balanced' or 'Unbalanced'.",
        "difficulty": "hard",
        "category": "trees",
        "starter_code": (
            "nums = list(map(int, input().split()))\n\n"
            "class Node:\n    def __init__(self, v):\n        self.val=v; self.left=self.right=None\n\n"
            "def insert(root, v):\n    if not root: return Node(v)\n"
            "    if v<root.val: root.left=insert(root.left,v)\n"
            "    else: root.right=insert(root.right,v)\n    return root\n\n"
            "root = None\nfor n in nums: root = insert(root, n)\n"
        ),
        "examples": [{"input": "4 2 6 1 3 5 7", "output": "Balanced"}],
        "hints": ["Height function returning -1 if unbalanced."],
        "tests": [
            {"stdin": "4 2 6 1 3 5 7\n", "expected_stdout": "Balanced"},
            {"stdin": "1 2 3 4 5\n",     "expected_stdout": "Unbalanced"},
        ],
    },
    {
        "title": "BST Lowest Common Ancestor",
        "description": "Read N integers (build BST), then P and Q. Print value of LCA(P,Q).",
        "difficulty": "hard",
        "category": "trees",
        "starter_code": (
            "nums = list(map(int, input().split()))\np=int(input()); q=int(input())\n\n"
            "class Node:\n    def __init__(self,v): self.val=v; self.left=self.right=None\n\n"
            "def insert(root,v):\n    if not root: return Node(v)\n"
            "    if v<root.val: root.left=insert(root.left,v)\n"
            "    else: root.right=insert(root.right,v)\n    return root\n\n"
            "root=None\nfor n in nums: root=insert(root,n)\n"
        ),
        "examples": [{"input": "6 2 8 0 4 7 9 3 5\n2\n8", "output": "6"}],
        "hints": ["In BST: both<root -> left; both>root -> right; else root is LCA."],
        "tests": [
            {"stdin": "6 2 8 0 4 7 9 3 5\n2\n8\n", "expected_stdout": "6"},
            {"stdin": "6 2 8 0 4 7 9 3 5\n2\n4\n", "expected_stdout": "2"},
        ],
    },
    {
        "title": "Regular Expression Matching",
        "description": "Read string S and pattern P (supports '.' and '*'). Print 'True' or 'False'.",
        "difficulty": "hard",
        "category": "dynamic_programming",
        "starter_code": "s = input()\np = input()\n",
        "examples": [{"input": "aa\na*", "output": "True"}],
        "hints": ["dp[i][j] = True if s[:i] matches p[:j]. Handle '*' separately."],
        "tests": [
            {"stdin": "aa\na*\n",                  "expected_stdout": "True"},
            {"stdin": "mississippi\nmis*is*p*.\n", "expected_stdout": "False"},
            {"stdin": "ab\n.*\n",                  "expected_stdout": "True"},
        ],
    },
    {
        "title": "Detect Cycle Directed Graph",
        "description": "Read V E then E directed edges. Print 'YES' if cycle exists, 'NO' otherwise.",
        "difficulty": "hard",
        "category": "graphs",
        "starter_code": "from collections import defaultdict\nv, e = map(int, input().split())\ngraph = defaultdict(list)\nfor _ in range(e):\n    u, w = map(int, input().split())\n    graph[u].append(w)\n",
        "examples": [{"input": "3 3\n1 2\n2 3\n3 1", "output": "YES"}],
        "hints": ["DFS with WHITE/GRAY/BLACK coloring."],
        "tests": [
            {"stdin": "3 3\n1 2\n2 3\n3 1\n", "expected_stdout": "YES"},
            {"stdin": "3 2\n1 2\n2 3\n",      "expected_stdout": "NO"},
        ],
    },
    {
        "title": "Word Ladder",
        "description": "Read begin word, end word, word list. Print shortest transformation length or 0.",
        "difficulty": "hard",
        "category": "graphs",
        "starter_code": "from collections import deque\nbegin = input().strip()\nend = input().strip()\nword_list = set(input().split())\n",
        "examples": [{"input": "hit\ncog\nhot dot dog lot log cog", "output": "5"}],
        "hints": ["BFS. Each step change one letter to a word in word_list."],
        "tests": [
            {"stdin": "hit\ncog\nhot dot dog lot log cog\n", "expected_stdout": "5"},
            {"stdin": "hit\ncog\nhot dot\n",                 "expected_stdout": "0"},
        ],
    },
    {
        "title": "Matrix Chain Multiplication",
        "description": "Read N then N+1 dimensions p[0..N]. Print min scalar multiplications.",
        "difficulty": "hard",
        "category": "dynamic_programming",
        "starter_code": "n = int(input())\np = list(map(int, input().split()))\n",
        "examples": [{"input": "3\n40 20 30 10", "output": "26000"}],
        "hints": ["m[i][j]=min cost matrices i..j. Try all split points k."],
        "tests": [
            {"stdin": "3\n40 20 30 10\n", "expected_stdout": "26000"},
            {"stdin": "2\n10 20 30\n",    "expected_stdout": "6000"},
        ],
    },
]


def validate_distribution():
    """Assert the expected difficulty distribution."""
    from collections import Counter
    counts = Counter(p["difficulty"] for p in PROBLEMS)
    assert counts["easy"] == 40,   f"Expected 40 easy, got {counts['easy']}"
    assert counts["medium"] == 40, f"Expected 40 medium, got {counts['medium']}"
    assert counts["hard"] == 20,   f"Expected 20 hard, got {counts['hard']}"
    assert len(PROBLEMS) == 100,   f"Expected 100 problems, got {len(PROBLEMS)}"


if __name__ == "__main__":
    validate_distribution()
    from collections import Counter
    counts = Counter(p["difficulty"] for p in PROBLEMS)
    cats = Counter(p["category"] for p in PROBLEMS)
    print(f"Total: {len(PROBLEMS)} problems")
    print(f"Distribution: {dict(counts)}")
    print(f"Categories: {dict(cats)}")
