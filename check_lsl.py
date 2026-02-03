from pylsl import resolve_streams

print("Tražim sve LSL streamove (5s)...")
streams = resolve_streams(wait_time=5.0)

for s in streams:
    print(
        "FOUND:",
        "name=", s.name(),
        "| type=", s.type(),
        "| ch=", s.channel_count(),
        "| fs=", s.nominal_srate()
    )