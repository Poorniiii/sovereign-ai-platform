package sovereign

default allow = false

# Phase 2 will fill in the three rules
# Placeholder so the container starts without error
allow {
    input.role == "admin"
}