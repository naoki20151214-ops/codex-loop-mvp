from src.core import greet, today_iso


def main() -> None:
    print(f"Today is {today_iso()}")
    print(greet("Codex"))


if __name__ == "__main__":
    main()
