"""Tests for string_utils module."""

import pytest

from src.string_utils import count_vowels, is_palindrome, reverse_string


class TestReverseString:
    """Test cases for reverse_string function."""

    def test_reverse_simple_string(self):
        """Test reversing a simple string."""
        assert reverse_string("hello") == "olleh"

    def test_reverse_empty_string(self):
        """Test reversing an empty string."""
        assert reverse_string("") == ""

    def test_reverse_single_character(self):
        """Test reversing a single character."""
        assert reverse_string("a") == "a"

    def test_reverse_with_spaces(self):
        """Test reversing a string with spaces."""
        assert reverse_string("hello world") == "dlrow olleh"


class TestIsPalindrome:
    """Test cases for is_palindrome function."""

    def test_simple_palindrome(self):
        """Test a simple palindrome."""
        assert is_palindrome("racecar") is True

    def test_not_palindrome(self):
        """Test a non-palindrome."""
        assert is_palindrome("hello") is False

    def test_palindrome_with_spaces(self):
        """Test palindrome with spaces."""
        assert is_palindrome("race car") is True

    def test_palindrome_mixed_case(self):
        """Test palindrome with mixed case."""
        assert is_palindrome("RaceCar") is True

    def test_empty_string_is_palindrome(self):
        """Test that empty string is considered palindrome."""
        assert is_palindrome("") is True

    def test_single_character_is_palindrome(self):
        """Test that single character is palindrome."""
        assert is_palindrome("a") is True


class TestCountVowels:
    """Test cases for count_vowels function."""

    def test_count_vowels_simple(self):
        """Test counting vowels in simple string."""
        assert count_vowels("hello") == 2

    def test_count_vowels_all_vowels(self):
        """Test string with all vowels."""
        assert count_vowels("aeiou") == 5

    def test_count_vowels_no_vowels(self):
        """Test string with no vowels."""
        assert count_vowels("xyz") == 0

    def test_count_vowels_mixed_case(self):
        """Test counting vowels with mixed case."""
        assert count_vowels("HeLLo WoRLd") == 3

    def test_count_vowels_empty_string(self):
        """Test counting vowels in empty string."""
        assert count_vowels("") == 0


@pytest.mark.parametrize(
    "text,expected",
    [
        ("hello", "olleh"),
        ("python", "nohtyp"),
        ("", ""),
        ("a", "a"),
    ],
)
def test_reverse_string_parametrized(text, expected):
    """Parametrized test for reverse_string."""
    assert reverse_string(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("racecar", True),
        ("hello", False),
        ("A man a plan a canal Panama", True),
        ("", True),
    ],
)
def test_is_palindrome_parametrized(text, expected):
    """Parametrized test for is_palindrome."""
    assert is_palindrome(text) == expected
