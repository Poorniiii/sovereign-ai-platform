package sovereign

import rego.v1

default allow := false

# Rule 1: developers can run agents
allow if {
    input.role == "developer"
    input.action == "run_agent"
}

# Rule 2: admins can manage policies
allow if {
    input.role == "admin"
    input.action == "manage_policy"
}

# Rule 3: admins can view audit logs
allow if {
    input.role == "admin"
    input.action == "view_audit"
}

# Rule 4: admins can also run agents
allow if {
    input.role == "admin"
    input.action == "run_agent"
}