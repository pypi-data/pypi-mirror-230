import pathlib
import random
import string
import typing

from hangman.states import GAME_STATES

Char = typing.NewType('Char', str)


class GallowsGame:
    allowed_characters = frozenset(string.ascii_lowercase)

    def __init__(  # noqa: WPS211
        self,
        secret_word: str,
        game_states: tuple[str, ...] = GAME_STATES,
        print_func: typing.Callable[[str], None] = print,
        input_func: typing.Callable[[], 'str'] = input,
        missed_letters: set[Char] | None = None,
        correct_letters: set[Char] | None = None,
    ) -> None:
        """
        Initialize game.

        :param secret_word: Secret word to guess
        :param game_states: Tuple with gallows states
        """
        self._missed_letters: set[Char] = missed_letters or set()
        self._correct_letters: set[Char] = correct_letters or set()
        self._secret_word = secret_word
        self._states = game_states
        self._print = print_func
        self._input = input_func

        self._is_finished = False

    def run(self) -> None:
        """
        Run gallows game.

        :return: None
        """
        self._print('Gallows game')

        while not self._is_finished:
            self._display_board()
            guess = self._get_valid_guess()

            if guess not in self._secret_word:
                self._missed_letters.add(guess)
                if self._lost:
                    self._display_board()
                    self._display_lost_stat()
                    self._is_finished = True
                continue

            self._correct_letters.add(guess)
            if self._check_win(self._correct_letters):
                self._print(f'Yes! The secret word is "{self._secret_word}"! You have won!')
                self._is_finished = True

    @property
    def _lost(self) -> bool:
        return len(self._missed_letters) >= len(self._states) - 1

    def _display_lost_stat(self) -> None:
        missed = len(self._missed_letters)
        correct = len(self._correct_letters)
        self._print('You have run out of guesses!')
        self._print(
            f'After {missed} missed guesses and {correct} correct guesses, the word was <{self._secret_word}>',
        )

    def _display_board(self) -> None:
        self._print(self._states[len(self._missed_letters)])
        self._print('Missed letters:')
        self._print(' '.join(self._missed_letters))

        hidden_word = ['_' for _ in range(len(self._secret_word))]
        for idx, char in enumerate(self._secret_word):
            if char in self._correct_letters:
                hidden_word[idx] = char

        self._print(''.join(hidden_word))

    def _get_valid_guess(self) -> Char:  # noqa: WPS231 not complex
        while True:
            guess = self._input().lower()

            if len(guess) != 1:
                self._print('Please enter a single letter.')
                continue

            if guess not in self.allowed_characters:
                self._print('Please enter a LETTER.')
                continue

            if (guess in self._missed_letters) or (guess in self._correct_letters):
                self._print('You have already guessed that letter. Choose again.')
                continue

            return Char(guess)

    def _check_win(self, guessed_letters: set[Char]) -> bool:
        for char in self._secret_word:
            if char not in guessed_letters:
                return False

        return True


def load_words(path: str) -> tuple[str, ...]:
    """
    Load words from file.

    :param path: file path
    :return: tuple of lowercase words
    """
    words = []
    with open(path, 'r') as words_file:
        for line in words_file:
            words.append(line.strip().lower())

    return tuple(words)


if __name__ == '__main__':
    directory_path = pathlib.Path(__file__).parent.resolve()
    dictionary_path = f'{directory_path}/dictionary.txt'

    random_word = random.choice(load_words(dictionary_path))  # noqa: S311 not cryptography usage

    game = GallowsGame(secret_word=random_word)
    game.run()
