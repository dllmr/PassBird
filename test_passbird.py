"""Tests for passbird.py."""

import subprocess

import passbird


class TestParseCode:
    def test_full_code(self):
        assert passbird.parse_code("3b2d1s") == (3, 2, 1)

    def test_birds_only(self):
        assert passbird.parse_code("1b") == (1, 0, 0)

    def test_birds_and_digits(self):
        assert passbird.parse_code("2b3d") == (2, 3, 0)

    def test_zeros_explicit(self):
        assert passbird.parse_code("1b0d0s") == (1, 0, 0)

    def test_large_counts(self):
        assert passbird.parse_code("10b5d3s") == (10, 5, 3)

    def test_zero_birds_exits(self):
        import pytest

        with pytest.raises(SystemExit):
            passbird.parse_code("0b")

    def test_invalid_no_birds(self):
        import pytest

        with pytest.raises(SystemExit):
            passbird.parse_code("3d2s")

    def test_invalid_letters(self):
        import pytest

        with pytest.raises(SystemExit):
            passbird.parse_code("abc")

    def test_invalid_empty(self):
        import pytest

        with pytest.raises(SystemExit):
            passbird.parse_code("")


class TestBirdNames:
    def test_non_empty(self):
        assert len(passbird.BIRD_NAMES) > 0

    def test_single_words(self):
        for name in passbird.BIRD_NAMES:
            assert " " not in name, f"Multi-word name found: {name}"

    def test_no_duplicates(self):
        assert len(passbird.BIRD_NAMES) == len(set(passbird.BIRD_NAMES))

    def test_title_case(self):
        for name in passbird.BIRD_NAMES:
            assert name == name.title(), f"Not title-cased: {name}"

    def test_known_birds_present(self):
        for bird in ["Owl", "Tern", "Goose", "Duck", "Warbler"]:
            assert bird in passbird.BIRD_NAMES, f"Expected '{bird}' in bird names"

    def test_sorted(self):
        assert passbird.BIRD_NAMES == sorted(passbird.BIRD_NAMES)


class TestGeneratePassword:
    def setup_method(self):
        self.names = passbird.BIRD_NAMES

    def test_starts_with_bird_name(self):
        for _ in range(20):
            pw = passbird.generate_password(self.names, 3, 2, 1)
            assert any(pw.startswith(n) for n in self.names), f"Password doesn't start with a bird name: {pw}"

    def test_correct_digit_count(self):
        for _ in range(20):
            pw = passbird.generate_password(self.names, 2, 4, 0)
            digit_count = sum(c.isdigit() for c in pw)
            assert digit_count == 4, f"Expected 4 digits, got {digit_count} in: {pw}"

    def test_correct_symbol_count(self):
        for _ in range(20):
            pw = passbird.generate_password(self.names, 2, 0, 3)
            symbol_count = sum(c in passbird.SYMBOLS for c in pw)
            assert symbol_count == 3, f"Expected 3 symbols, got {symbol_count} in: {pw}"

    def test_birds_only(self):
        for _ in range(20):
            pw = passbird.generate_password(self.names, 2, 0, 0)
            assert pw.isalpha(), f"Expected only letters: {pw}"

    def test_correct_bird_count(self):
        for _ in range(20):
            pw = passbird.generate_password(self.names, 3, 0, 0)
            # With no digits/symbols, the password is just 3 bird names concatenated
            remaining = pw
            count = 0
            while remaining:
                matched = False
                for name in sorted(self.names, key=len, reverse=True):
                    if remaining.startswith(str(name)):
                        remaining = remaining[len(name):]
                        count += 1
                        matched = True
                        break
                if not matched:
                    break
            assert count == 3, f"Expected 3 bird names, found {count} in: {pw}"


class TestCLI:
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["uv", "run", "passbird.py", *args],
            capture_output=True,
            text=True,
        )

    def test_default(self):
        result = self._run()
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0

    def test_custom_code(self):
        result = self._run("2b1d")
        assert result.returncode == 0
        pw = result.stdout.strip()
        digit_count = sum(c.isdigit() for c in pw)
        assert digit_count == 1

    def test_birds_only(self):
        result = self._run("1b")
        assert result.returncode == 0
        pw = result.stdout.strip()
        assert pw.isalpha()

    def test_invalid_code(self):
        result = self._run("abc")
        assert result.returncode == 1
        assert "Usage" in result.stderr

    def test_too_many_args(self):
        result = self._run("3b", "2d")
        assert result.returncode == 1
        assert "Usage" in result.stderr
