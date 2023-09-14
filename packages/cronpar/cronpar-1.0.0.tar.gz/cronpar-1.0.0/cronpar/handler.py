def validate_input(input_str: list[str]):
    if len(input_str) < 5:
        raise ValueError(f"Expect input cron expression longer than 5 fields, but got {len((input_str))}")
