import re
import curses
import time
import random


class Tester:
    def __init__(self):
        self.current_quote = "Hello World"
        self.quote_source_file = ""  # for a custom quotes file
        self.max_index = 0
        self.current_index = 0
        self.first_input_timestamp = 0
        self.last_input_timestamp = 0
        self.error_count = 0
        self.started = False
        self.end_test = False

    def get_quote(self):
        if self.quote_source_file:
            """
            May include custom logic for different quote files
            ex. for a quotes.json
            """
            import json

            with open(self.quote_source_file, encoding="utf-8") as file:
                data = json.load(file)

            quotes = data["quotes"]
            # random_quote = r["text"]
            return random.choice(quotes)["quote"] + " "  # extra space

        else:
            from words import english

            random_quote = " ".join(
                [
                    random.choice(english.words)
                    for _ in range(random.randrange(1, 20))
                ]
                + [" "]
            )

        return random_quote

    def set_quote(self):
        self.current_quote = self.get_quote()
        self.current_index = 0
        self.max_index = len(self.current_quote) - 2
        self.error_count = 0

        self.started = False

    def word_count(self, index):
        # Use regex to find all words
        words = re.findall(r"\b\w+\b", self.current_quote[: index + 1])
        return len(words)

    def on_key_press(self, ch, timestamp):
        if not self.started:
            self.first_input_timestamp = timestamp
            self.started = True
        self.last_input_timestamp = timestamp

        if ch == ord(self.current_quote[self.current_index]):
            self.current_index += 1
        else:
            self.error_count += 1

        # At the time there's a extra extra space after the quote
        if self.current_index >= self.max_index:
            self.end_test = True

    def on_special_key_press(self, ch):
        match int(ch):
            case 27:
                self.end_test = True
            case 9:
                self.set_quote()
            case 8:
                self.current_index -= 1
            case 260:
                self.current_index -= 1
            case _:
                # Some other special key was pressed
                pass

    def get_stats(self):
        """
        Returns a ready-made string of stats
        """
        time_passed = self.last_input_timestamp - self.first_input_timestamp
        if time_passed:
            words = self.word_count(self.current_index) - 1
            speed = "{:>6}".format(str(round(((words * 60) / time_passed), 2)))

        else:
            speed = "   N/A"

        if self.current_index:
            accu = "{:>6}".format(
                str(
                    round(
                        (self.current_index - self.error_count)
                        * 100
                        / self.current_index,
                        2,
                    )
                )
            )
        else:
            accu = "    00"

        return (
            speed
            + " w/m "
            + accu
            + " % "
            + "{:>7}".format(
                f"{self.word_count(self.current_index)}/{(self.word_count(self.max_index))}"
            )
        )

    def get_divied_quote(self):
        c = self.current_index
        return self.current_quote[:c], self.current_quote[c:]

    def end(self):
        return self.end_test


def main(scr) -> None:
    test = Tester()
    test.set_quote()
    ch = 0
    while True:
        if 31 < ch < 127:
            test.on_key_press(ch, time.time())
        else:
            test.on_special_key_press(ch)
            scr.clear()

        if test.end():
            break

        s1, s2 = test.get_divied_quote()
        scr.addstr(1, 0, f"---| {test.get_stats()} |------------------")
        scr.addstr(3, 0, "[I]: ")
        scr.addstr(4, 0, s2)
        scr.addstr(6, 0, "[O]: ")
        scr.addstr(7, 0, s1)
        scr.refresh()
        ch = scr.getch()
    print(f"\n--- {test.get_stats()} ------------------\n")
    print(test.current_quote)


if __name__ == "__main__":
    curses.wrapper(main)
