"""String utility functions for demonstration."""


def reverse_string(text: str) -> str:
    """Reverse a string.

    Args:
        text: Input string

    Returns:
        Reversed string
    """
    return text[::-1]


def is_palindrome(text: str) -> bool:
    """Check if a string is a palindrome.

    Args:
        text: Input string

    Returns:
        True if palindrome, False otherwise
    """
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]


def count_vowels(text: str) -> int:
    """Count vowels in a string.

    Args:
        text: Input string

    Returns:
        Number of vowels
    """
    vowels = "aeiouAEIOU"
    return sum(1 for char in text if char in vowels)
