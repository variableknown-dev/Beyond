from core.kashvi import Kashvi


def main():
    kashvi = Kashvi()

    print("Kashvi is online.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Kashvi: Goodbye!")
                break

            reply = kashvi.chat(user_input)

            print(f"\nKashvi: {reply}\n")

        except KeyboardInterrupt:
            print("\nKashvi: Goodbye!")
            break

        except Exception as e:
            print(f"\nKashvi: An error occurred: {e}\n")


if __name__ == "__main__":
    main()
