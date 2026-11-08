from core.beyond import Beyond


def main():
    beyond = Beyond()

    print("Beyond is online.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Beyond: Goodbye!")
                break

            reply = beyond.chat(user_input)

            print(f"\nBeyond: {reply}\n")

        except KeyboardInterrupt:
            print("\nBeyond: Goodbye!")
            break

        except Exception as e:
            print(f"\nBeyond: An error occurred: {e}\n")


if __name__ == "__main__":
    main()
