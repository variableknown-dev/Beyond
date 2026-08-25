from core.aarya import Aarya


def main():
    aarya = Aarya()

    print("Aarya is online.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Aarya: Goodbye!")
                break

            reply = aarya.chat(user_input)

            print(f"\nAarya: {reply}\n")

        except KeyboardInterrupt:
            print("\nAarya: Goodbye!")
            break

        except Exception as e:
            print(f"\nAarya: An error occurred: {e}\n")


if __name__ == "__main__":
    main()
