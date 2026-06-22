from ray.brain.core import RayCore


def main():
    core = RayCore()
    core.startup()

    while True:
        try:
            user_input = input("Pragati: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.strip().lower() == "exit":
            break

        if not user_input.strip():
            continue

        result = core.process_message(user_input)

        print(f"\nRay: {result['ray_response']}\n")

    core.shutdown()


if __name__ == "__main__":
    main()
