# Job Status State Flow

Job Status separates real printer state from locally requested actions. The UI keeps terminal states visible until `SDCARD_RESET_FILE` returns the printer to `standby`.

```mermaid
stateDiagram-v2
    [*] --> Standby: no active file
    Standby --> Starting: Print requested
    Starting --> Printing: print_stats.state=printing
    Starting --> Error: start rejected / klippy error

    Printing --> Pausing: Pause requested
    Pausing --> Paused: print_stats.state=paused
    Pausing --> Printing: pause rejected / unchanged

    Paused --> Resuming: Resume requested
    Resuming --> Printing: print_stats.state=printing
    Resuming --> Paused: resume rejected / unchanged

    Printing --> Cancelling: Cancel confirmed
    Paused --> Cancelling: Cancel confirmed
    Cancelling --> Cancelled: print_stats.state=cancelled

    Printing --> Complete: print_stats.state=complete
    Printing --> Error: print_stats.state=error
    Paused --> Error: print_stats.state=error

    Complete --> Clearing: Clear Status requested
    Cancelled --> Clearing: Clear Status requested
    Error --> Clearing: Clear Status requested
    Clearing --> Standby: SDCARD_RESET_FILE + print_stats.state=standby
    Clearing --> Complete: clear failed
    Clearing --> Cancelled: clear failed
    Clearing --> Error: clear failed
```

Button rules:

- `printing`: show Pause, Cancel, Skip Object, Advanced.
- `paused`: show Resume, Cancel, Skip Object, Advanced.
- `complete`, `cancelled`, `error`: show Clear Status.
- `starting`, `pausing`, `resuming`, `cancelling`, `clearing`: disable job action buttons until Moonraker reports a stable state.
- Only Cancel and Skip Object require confirmation; Pause, Resume, and Clear Status execute directly.
